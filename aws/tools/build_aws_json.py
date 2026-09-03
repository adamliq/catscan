#!/usr/bin/env python3
"""Regenerate aws/data/aws_iam_actions.json from Events_Other's CSV.

The AWS Events tab (Action Explorer) fetches the JSON this produces at
runtime rather than embedding it in index.html — see the top-level
README's "How the merge was built" section. Run this after
Events_Other/aws_iam_actions_expanded.csv is updated, then regenerate
index.html as usual; this script never touches index.html itself.

Usage: python3 aws/tools/build_aws_json.py
(run from the repo root, or any directory — paths below are relative to
this file's location)
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
CSV_PATH = os.path.join(REPO_ROOT, 'Events_Other', 'aws_iam_actions_expanded.csv')
JSON_PATH = os.path.join(HERE, '..', 'data', 'aws_iam_actions.json')


def clean(v):
    v = (v or '').strip()
    return '' if v in ('', 'N/A') else v


def main():
    rows_out = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            service = clean(row.get('service'))
            action = clean(row.get('action'))
            rows_out.append({
                'id': service + ':' + action,
                'service': service,
                'action': action,
                'awsService': clean(row.get('AWS Service')),
                'description': clean(row.get('Description')),
                'resourceTypeConsole': clean(row.get('Resource type (console)')),
                'resourceType': clean(row.get('resources.type')),
                'eventType': clean(row.get('eventType')),
                'eventCategory': clean(row.get('eventCategory')),
                'eventName': clean(row.get('eventName')),
                'acscRecommended': clean(row.get('ACSC Recommended')) == 'Y',
                'acscLoggingCondition': clean(row.get('ACSC Logging Condition')),
            })

    services = sorted(set(r['service'] for r in rows_out))
    out = {
        'generatedFrom': 'Events_Other/aws_iam_actions_expanded.csv',
        'actionCount': len(rows_out),
        'serviceCount': len(services),
        'actions': rows_out,
    }
    out_path = os.path.normpath(JSON_PATH)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'wrote {out_path}: {len(rows_out)} actions across {len(services)} services')


if __name__ == '__main__':
    main()
