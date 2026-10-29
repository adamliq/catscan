#!/usr/bin/env python3
"""Regenerates index.html's embedded Windows Events DATA.sql_audit,
DATA.sql_audit_class_types, and DATA.sql_audit_action_ids arrays from
their respective windows/data/sql_audit_*.csv files, the single sources
of truth.

Run this after any change to one of those CSVs, instead of hand-editing
the embedded copies in index.html directly. It also keeps each CSV's
sibling .json file in sync (a plain JSON export of the same CSV).
Mirrors tools/build_cloud_logs.py's approach, applied to the SQL Audit
tab's own data instead.

Usage:
    python3 tools/build_sql_audit.py [--check]

--check   Don't write anything; exit non-zero if index.html or any of
          the sql_audit_*.json files are out of sync with their source
          CSV. Used by CI (see .github/workflows/build-check.yml).

Scope: this script only touches the `sql_audit`, `sql_audit_class_types`,
and `sql_audit_action_ids` keys of the `DATA` object embedded under
app-win (the SQL Audit tab). Windows Events' own `events` array, the
Windows Events reference tables, Cloud Logs, and the Cloud Actions
Explorer's data are unaffected.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / 'windows' / 'data'
HTML_PATH = REPO_ROOT / 'index.html'
# Same container as build_cloud_logs.py: the SQL Audit tab lives inside
# the Windows Events app's single embedded DATA object.
CONTAINER_ANCHOR = "getElementById('app-win')"
DATA_DECL = 'const DATA = '

# Each dataset: (DATA key, csv stem, required fieldnames, dedup key(s) or None).
DATASETS = [
    ('sql_audit', 'sql_audit_actions', ['level', 'action', 'description'], ['level', 'action']),
    ('sql_audit_class_types', 'sql_audit_class_types', ['class_type', 'class_type_desc', 'description'], ['class_type']),
    ('sql_audit_action_ids', 'sql_audit_action_ids', ['action_id', 'name', 'numeric_filter_value', 'notes'], ['action_id']),
]


def load_csv_rows(stem, fieldnames):
    csv_path = DATA_DIR / f'{stem}.csv'
    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        missing = [f for f in fieldnames if f not in r]
        if missing:
            raise ValueError(f"{stem}.csv row {r} missing column(s): {missing}")
    return rows


def find_data_object_span(html):
    anchor_idx = html.index(CONTAINER_ANCHOR)
    decl_idx = html.index(DATA_DECL, anchor_idx)
    start = decl_idx + len(DATA_DECL)
    depth = 0
    in_str = False
    esc = False
    i = start
    end = -1
    while i < len(html):
        c = html[i]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
        elif c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    if end == -1:
        raise ValueError("could not find the end of the embedded DATA object in index.html")
    return start, end


def build(check=False):
    html = HTML_PATH.read_text(encoding='utf-8')
    start, end = find_data_object_span(html)
    data = json.loads(html[start:end])

    all_ok = True
    json_texts = {}
    counts = {}
    for data_key, stem, fieldnames, dedup_keys in DATASETS:
        rows = load_csv_rows(stem, fieldnames)
        if dedup_keys:
            keys = [tuple(r[k] for k in dedup_keys) for r in rows]
            if len(keys) != len(set(keys)):
                seen = set()
                dupes = [k for k in keys if k in seen or seen.add(k)]
                raise ValueError(f"{stem}.csv has duplicate {dedup_keys} rows: {dupes}")
        records = [{k: r.get(k, '') for k in fieldnames} for r in rows]
        data[data_key] = records
        json_texts[data_key] = json.dumps(records, indent=2) + '\n'
        counts[data_key] = len(records)

    new_data_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:start] + new_data_json + html[end:]

    total = counts['sql_audit']
    new_html, n = re.subn(r'[\d,]+ SQL Server Audit action groups and actions',
                           f'{total:,} SQL Server Audit action groups and actions', new_html)
    if n != 1:
        raise ValueError(f"expected exactly one 'N SQL Server Audit action groups and actions' banner match, found {n}")

    if check:
        html_ok = new_html == html
        stale = [] if html_ok else ["index.html's embedded DATA is stale"]
        for data_key, stem, _, _ in DATASETS:
            json_path = DATA_DIR / f'{stem}.json'
            existing = json_path.read_text(encoding='utf-8') if json_path.exists() else None
            if json_texts[data_key] != existing:
                stale.append(f'{stem}.json is stale')
        if not stale:
            print(f"OK: index.html and sql_audit_*.json already match their source CSVs "
                  f"({counts['sql_audit']} actions, {counts['sql_audit_class_types']} class types, "
                  f"{counts['sql_audit_action_ids']} action IDs).")
            return 0
        print("OUT OF SYNC:", file=sys.stderr)
        for s in stale:
            print(f"  {s}", file=sys.stderr)
        print("Run `python3 tools/build_sql_audit.py` and commit the result.", file=sys.stderr)
        return 1

    HTML_PATH.write_text(new_html, encoding='utf-8')
    for data_key, stem, _, _ in DATASETS:
        (DATA_DIR / f'{stem}.json').write_text(json_texts[data_key], encoding='utf-8')
        print(f"{stem}.csv: {counts[data_key]} rows -> {stem}.json and index.html rewritten")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if index.html or any sql_audit_*.json is out of sync with its source CSV")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
