#!/usr/bin/env python3
"""Rolls windows/data/MicrosoftCloud_Schema.json into
windows/data/azureresourcetypes.json - the reverse direction of
enrich_microsoft_schema.py/export_schema_json.py (those look up each
schema row's ARM resource type; this looks up each ARM resource type's
schema rows).

For every row in azureresourcetypes.json, adds a `schemaOperations` array
- one entry per MicrosoftCloud_Schema.json row whose (provider + "/" +
resource_type), lowercased, matches that row's own resourceType - each
entry trimmed to {service, category, operation, source} (provider/
resource_type dropped since they're already the parent row's own
resourceType). Rows with no matching schema entries are left exactly as
they were - no empty array added, no other field touched.

Run this again after MicrosoftCloud_Schema.json changes:
    python3 windows/tools/roll_schema_into_arm_types.py
(run from the repo root, or any directory - paths below are relative to
this file's location)
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, '..', 'data')
SCHEMA_PATH = os.path.join(DATA_DIR, 'MicrosoftCloud_Schema.json')
ARM_PATH = os.path.join(DATA_DIR, 'azureresourcetypes.json')


def main():
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema_rows = json.load(f)
    with open(ARM_PATH, encoding='utf-8') as f:
        arm_rows = json.load(f)

    ops_by_key = defaultdict(list)
    for row in schema_rows:
        provider = row['provider']
        rtype = row['resource_type']
        if not provider or provider == 'N/A' or not rtype or rtype.startswith('N/A'):
            continue
        key = (provider + '/' + rtype).lower()
        ops_by_key[key].append({
            'service': row['service'],
            'category': row['category'],
            'operation': row['operation'],
            'source': row['source'],
        })

    # start from a clean copy of each row's original fields (minus any
    # schemaOperations left over from a previous run), so this script is
    # idempotent rather than only ever accumulating duplicates
    matched_types = 0
    matched_ops = 0
    out_rows = []
    seen_keys = set()
    for row in arm_rows:
        row = {k: v for k, v in row.items() if k != 'schemaOperations'}
        key = row['resourceType'].strip().lower()
        seen_keys.add(key)
        ops = ops_by_key.get(key)
        if ops:
            row['schemaOperations'] = ops
            matched_types += 1
            matched_ops += len(ops)
        out_rows.append(row)

    unmatched_keys = set(ops_by_key) - seen_keys
    if unmatched_keys:
        print(f'note: {len(unmatched_keys)} schema resourceType(s) have no row in '
              f'azureresourcetypes.json at all (not just unmatched): {sorted(unmatched_keys)[:5]}...')

    with open(ARM_PATH, 'w', encoding='utf-8') as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f'wrote {ARM_PATH}: {len(out_rows)} ARM resource types, '
          f'{matched_types} carry schemaOperations ({matched_ops} schema rows total)')


if __name__ == '__main__':
    main()
