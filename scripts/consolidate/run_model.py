#!/usr/bin/env python3
"""Test, build, verify, and check model reproducibility."""

import argparse
import json
from pathlib import Path
import sys
import unittest

from merge_model import build_run
from model_common import read_config
from verify_model import verify_run


def compare_runs(first, second):
    files = [
        {
            str(path.relative_to(directory))
            for path in directory.rglob("*")
            if path.is_file()
        }
        for directory in (first, second)
    ]
    if files[0] != files[1]:
        raise ValueError("Reproducibility failed: artifact file sets differ")
    for name in sorted(files[0] - {"model-config.json", "model-map.json"}):
        if (first / name).read_bytes() != (second / name).read_bytes():
            raise ValueError(f"Reproducibility failed: {name} differs")
    for name in ("model-config.json", "model-map.json"):
        documents = [
            json.loads((directory / name).read_text()) for directory in (first, second)
        ]
        for document in documents:
            del document["outputs"]
        if documents[0] != documents[1]:
            raise ValueError(
                f"Reproducibility failed: {name} differs beyond output paths"
            )
    print("Reproducibility check passed.", flush=True)


def main(argv=None):
    model_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Uses the current Python environment. Relative config paths use your current "
            "directory. Keeps a timestamped run and a second run with a -repeat suffix."
        ),
    )
    parser.add_argument(
        "config", nargs="?", type=Path, default=model_dir / "model-config.json"
    )
    args = parser.parse_args(argv)
    config = args.config.resolve()
    if not config.is_file():
        print(f"Configuration not found: {config}", file=sys.stderr)
        return 1
    if sys.version_info < (3, 10):
        print("Python 3.10+ is required", file=sys.stderr)
        return 1

    try:
        config, root = read_config(config)
        suite = unittest.TestLoader().discover(str(model_dir / "tests"))
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
            return 1

        print("Building model", flush=True)
        run_dir, _ = build_run(config, root)
        saved_config, saved_root = read_config(run_dir / "model-config.json")
        report = verify_run(saved_config, saved_root)
        print(
            f"100% coverage: {report['constructs']} constructs; SHACL syntax valid.",
            flush=True,
        )

        repeat_dir = run_dir.with_name(run_dir.name + "-repeat")
        print(f"Checking reproducibility in {repeat_dir}", flush=True)
        build_run(saved_config, saved_root, repeat_dir)
        compare_runs(run_dir, repeat_dir)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Model workflow failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Completed. Review the report: {run_dir / 'model-map.html'}\n"
        f"Repeat run: {repeat_dir}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
