"""Small checks for the standalone map report; no RDF dependencies needed."""
from contextlib import redirect_stdout
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import visualize_model_map
from visualize_model_map import render, triple_text


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.mapping_rows = []
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'tr' and 'data-kind' in attrs:
            self.mapping_rows.append(attrs)
        if tag == 'script':
            self.scripts += 1


class ReportTests(unittest.TestCase):
    def test_escapes_content_and_preserves_filter_values(self):
        source = 'a/"quoted" & <source>.ttl'
        report = render({
            'namespace': '<namespace>', 'selected': {source: 3},
            'terms': {'javascript:alert(1)': {
                'target': 'https://example.org/a?x=1&y=2', 'kind': 'class',
                'english_label': '</script><script>alert(1)</script>', 'sources': [source],
            }},
        })
        parser = ReportParser()
        parser.feed(report)
        self.assertEqual(parser.scripts, 1)
        self.assertEqual(json.loads(parser.mapping_rows[0]['data-sources']), [source])
        self.assertNotIn('href="javascript:', report)
        self.assertIn('href="https://example.org/a?x=1&amp;y=2"', report)
        self.assertIn('&lt;/script&gt;&lt;script&gt;', report)
        self.assertNotIn('<!-- ROWS -->', report)
        self.assertEqual(triple_text(None), '—')
        self.assertEqual(triple_text([{'bnode': 'author'}]), '_:author')
        self.assertIn('@nl', triple_text([{'literal': 'kleur', 'language': 'nl'}]))

    def test_cli_reads_map_beside_script(self):
        data = {'namespace': 'https://example.org/', 'selected': {'source.ttl': 1}, 'terms': {
            'https://example.org/Person': {'target': 'https://example.org/Person',
                'kind': 'class', 'english_label': 'Person', 'sources': ['source.ttl']},
        }}
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / 'tool'
            tool.mkdir()
            script = tool / 'visualize_model_map.py'
            script.with_name('model-map.json').write_text(json.dumps(data), encoding='utf-8')
            output = Path(directory) / 'report.html'
            with patch.object(visualize_model_map, '__file__', str(script)), \
                    redirect_stdout(io.StringIO()) as message:
                visualize_model_map.main(['-o', str(output)])
            parser = ReportParser()
            parser.feed(output.read_text(encoding='utf-8'))
        self.assertIn('Wrote', message.getvalue())
        self.assertEqual(len(parser.mapping_rows), len(data['terms']))
        self.assertEqual({row['data-kind'] for row in parser.mapping_rows},
                         {term['kind'] for term in data['terms'].values()})


if __name__ == '__main__':
    unittest.main()
