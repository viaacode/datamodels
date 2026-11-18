#!/usr/bin/env python3
"""Run all OntoCheck task-agnostic metrics on a completed run's ontology."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
import sys

from model_common import ModelError, json_write, read_config


def check_quality(config, root):
    enabled = config.get('ontology_quality_check', True)
    if not isinstance(enabled, bool):
        raise ModelError('ontology_quality_check must be a boolean')
    if not enabled:
        return None
    ontology = (root / config['outputs']['rdfs']).resolve()
    log_path = ontology.parent / 'ontology-quality.log'
    csv_path = ontology.parent / 'ontology-quality.csv'
    report_path = ontology.parent / 'ontology-quality.json'
    report = {'engine': 'OntoCheck', 'ontology': str(ontology), 'metrics': 'all',
              'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'error'}
    failure = None
    try:
        report['ontology_sha256'] = sha256(ontology.read_bytes()).hexdigest()
        report['engine_version'] = version('OntoCheck')
        # Do not mistake an earlier report for output from a failed assessment.
        csv_path.write_text('', encoding='utf-8')
        from ontocheck import run_assessment
        run_assessment(ttl_files=str(ontology), metrics='all',
                       output_log_file=str(log_path), output_csv_file=str(csv_path))
        with csv_path.open(newline='', encoding='utf-8') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ['Metric', 'Score', 'Status']:
                raise ModelError('OntoCheck did not produce a valid metric report')
            results = list(reader)
        if not results or any(not row.get('Metric') or not row.get('Status') for row in results):
            raise ModelError('OntoCheck produced an empty or incomplete metric report')
        report['results'] = results
        counts = Counter('success' if row['Status'] == 'Success' else
                         'skipped' if row['Status'].startswith('Skipped') else 'error'
                         for row in results)
        report['counts'] = {status: counts[status] for status in ('success', 'skipped', 'error')}
        if counts['error']:
            raise ModelError(f"OntoCheck could not evaluate {counts['error']} metric(s); inspect the log and CSV")
        report['status'] = 'complete'
    except Exception as exc:
        report['error'] = str(exc)
        failure = exc
    json_write(report_path, report)
    if failure is not None:
        raise ModelError(f'OntoCheck quality check failed: {failure}; details: {report_path}') from failure
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, help='Saved model-config.json from the completed run')
    args = parser.parse_args()
    try:
        config, root = read_config(args.config)
        report = check_quality(config, root)
        if report is None:
            print('OntoCheck ontology quality check disabled by config.')
        else:
            counts = report['counts']
            print(f"OntoCheck assessment complete: {counts['success']} metrics evaluated, "
                  f"{counts['skipped']} skipped. Review: "
                  f"{Path(report['ontology']).with_name('ontology-quality.json')}")
    except (ModelError, OSError, ValueError) as exc:
        print(f'Ontology quality check failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
