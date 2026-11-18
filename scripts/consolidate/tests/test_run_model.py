"""Check runner failure handling, paths, and artifact reproducibility with direct Python calls."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_model


def write_artifacts(directory, root=None):
    directory.mkdir(parents=True)
    for name in ('model.rdfs.ttl', 'model.shacl.ttl', 'model-map.html'):
        (directory / name).write_text('same bytes\n')
    for name in ('model-config.json', 'model-map.json'):
        (directory / name).write_text(json.dumps({
            'root': str(root or directory.parent), 'outputs': {'map': str(directory)}, 'terms': {},
        }))


class RunnerTests(unittest.TestCase):
    def test_missing_config_stops_before_tests_or_builds(self):
        with TemporaryDirectory() as directory, redirect_stderr(io.StringIO()) as errors, \
                patch.object(run_model, 'build_run') as build, \
                patch.object(run_model.unittest, 'TextTestRunner') as tests:
            config = Path(directory) / 'missing config.json'
            self.assertEqual(run_model.main([str(config)]), 1)
            self.assertIn(str(config.resolve()), errors.getvalue())
            build.assert_not_called()
            tests.assert_not_called()

    def test_help_and_extra_arguments(self):
        with redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as exit:
            run_model.main(['--help'])
        self.assertEqual(exit.exception.code, 0)
        self.assertIn('current Python environment', output.getvalue())
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit:
            run_model.main(['one', 'two'])
        self.assertEqual(exit.exception.code, 2)

    def test_reproducibility_ignores_only_output_paths(self):
        with TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            first, second = Path(directory) / 'first', Path(directory) / 'second'
            write_artifacts(first)
            write_artifacts(second)
            run_model.compare_runs(first, second)
            for name in ('model.rdfs.ttl', 'model.shacl.ttl', 'model-map.html',
                         'model-config.json', 'model-map.json'):
                with self.subTest(artifact=name):
                    original = (second / name).read_text()
                    changed = (original + 'changed' if name.endswith(('.ttl', '.html')) else
                               json.dumps({'outputs': {}, 'terms': {'unexpected': {}}}))
                    (second / name).write_text(changed)
                    with self.assertRaisesRegex(ValueError, name.replace('.', r'\.')):
                        run_model.compare_runs(first, second)
                    (second / name).write_text(original)
            (second / 'model-map.html').unlink()
            with self.assertRaisesRegex(ValueError, 'artifact file sets differ'):
                run_model.compare_runs(first, second)

    def test_reproducibility_checks_nested_external_files_and_file_sets(self):
        with TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            first, second = Path(directory) / 'first', Path(directory) / 'second'
            write_artifacts(first)
            write_artifacts(second)
            name = 'external/example.rdfs.ttl'
            for run in (first, second):
                (run / name).parent.mkdir(parents=True)
                (run / name).write_text('same bytes')
            run_model.compare_runs(first, second)
            (second / name).write_text('altered definition')
            with self.assertRaisesRegex(ValueError, name):
                run_model.compare_runs(first, second)
            (second / name).unlink()
            with self.assertRaisesRegex(ValueError, 'artifact file sets differ'):
                run_model.compare_runs(first, second)
            (second / name).write_text('same bytes')
            (second / 'external/unexpected.ttl').write_text('unexpected')
            with self.assertRaisesRegex(ValueError, 'artifact file sets differ'):
                run_model.compare_runs(first, second)

    def test_workflow_stops_on_failures_and_keeps_both_successful_runs(self):
        for failure in ('tests', 'build', 'verify', None):
            with self.subTest(failure=failure), TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                script_dir = root / 'scripts/consolidate'
                script_dir.mkdir(parents=True)
                (script_dir / 'model-config.json').write_text(json.dumps({'root': '../..'}))
                builds = []

                def build(config, source_root, destination=None):
                    if failure == 'build':
                        raise ValueError('build failed')
                    self.assertEqual(source_root, root)
                    destination = destination or root / 'model/runs/first'
                    write_artifacts(destination, root)
                    builds.append(destination)
                    return destination, {}

                output, errors = io.StringIO(), io.StringIO()
                with patch.object(run_model, '__file__', str(script_dir / 'run_model.py')), \
                        patch.object(run_model.unittest, 'TestLoader'), \
                        patch.object(run_model.unittest, 'TextTestRunner') as tests, \
                        patch.object(run_model, 'build_run', side_effect=build) as builder, \
                        patch.object(run_model, 'verify_run') as verify, \
                        redirect_stdout(output), redirect_stderr(errors):
                    tests.return_value.run.return_value.wasSuccessful.return_value = failure != 'tests'
                    verify.return_value = {'constructs': 2}
                    if failure == 'verify':
                        verify.side_effect = ValueError('verification failed')
                    status = run_model.main([])

                if failure:
                    self.assertEqual(status, 1)
                    self.assertNotIn('Completed.', output.getvalue())
                    self.assertLessEqual(builder.call_count, 1)
                    if failure != 'verify':
                        verify.assert_not_called()
                else:
                    self.assertEqual(status, 0, errors.getvalue())
                    self.assertEqual(len(builds), 2)
                    self.assertEqual(builds[1].name, builds[0].name + '-repeat')
                    self.assertEqual(verify.call_args.args[0]['outputs']['map'], str(builds[0]))
                    self.assertEqual(verify.call_args.args[1], root)
                    self.assertIn(str(builds[0] / 'model-map.html'), output.getvalue())
                    self.assertTrue(all(path.is_dir() for path in builds))


if __name__ == '__main__':
    unittest.main()
