#!/usr/bin/env python3
"""Regenerates index.html's embedded Windows Events DATA.sql_audit array
from windows/data/sql_audit_actions.csv, the single source of truth.

Run this after any change to windows/data/sql_audit_actions.csv, instead
of hand-editing the embedded copy in index.html directly. It also keeps
windows/data/sql_audit_actions.json in sync (a plain JSON export of the
same CSV). Mirrors tools/build_cloud_logs.py's approach, applied to the
SQL Audit tab's own data instead.

Usage:
    python3 tools/build_sql_audit.py [--check]

--check   Don't write anything; exit non-zero if index.html/
          sql_audit_actions.json are out of sync with
          sql_audit_actions.csv. Used by CI (see
          .github/workflows/build-check.yml).

Scope: this script only touches the `sql_audit` key of the `DATA` object
embedded under app-win (the SQL Audit tab). Windows Events' own `events`
array, the Windows Events reference tables, Cloud Logs, and the Cloud
Actions Explorer's data are unaffected.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SQL_AUDIT_CSV = REPO_ROOT / 'windows' / 'data' / 'sql_audit_actions.csv'
SQL_AUDIT_JSON = REPO_ROOT / 'windows' / 'data' / 'sql_audit_actions.json'
HTML_PATH = REPO_ROOT / 'index.html'
# Same container as build_cloud_logs.py: the SQL Audit tab lives inside
# the Windows Events app's single embedded DATA object.
CONTAINER_ANCHOR = "getElementById('app-win')"
DATA_DECL = 'const DATA = '

FIELDNAMES = ['level', 'action', 'description']


def load_csv_rows():
    with open(SQL_AUDIT_CSV, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        missing = [f for f in FIELDNAMES if f not in r]
        if missing:
            raise ValueError(f"sql_audit_actions.csv row {r.get('action')} missing column(s): {missing}")
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
    rows = load_csv_rows()
    keys = [(r['level'], r['action']) for r in rows]
    if len(keys) != len(set(keys)):
        seen = set()
        dupes = [k for k in keys if k in seen or seen.add(k)]
        raise ValueError(f"sql_audit_actions.csv has duplicate (level, action) rows: {dupes}")

    actions = [{k: r.get(k, '') for k in FIELDNAMES} for r in rows]

    html = HTML_PATH.read_text(encoding='utf-8')
    start, end = find_data_object_span(html)
    data = json.loads(html[start:end])
    data['sql_audit'] = actions
    new_data_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:start] + new_data_json + html[end:]

    total = len(actions)
    new_html, n = re.subn(r'[\d,]+ SQL Server Audit action groups and actions',
                           f'{total:,} SQL Server Audit action groups and actions', new_html)
    if n != 1:
        raise ValueError(f"expected exactly one 'N SQL Server Audit action groups and actions' banner match, found {n}")
    new_json_text = json.dumps(actions, indent=2) + '\n'

    if check:
        html_ok = new_html == html
        json_ok = new_json_text == (SQL_AUDIT_JSON.read_text(encoding='utf-8') if SQL_AUDIT_JSON.exists() else None)
        if html_ok and json_ok:
            print(f"OK: index.html and sql_audit_actions.json already match sql_audit_actions.csv ({total} rows).")
            return 0
        print("OUT OF SYNC: index.html and/or sql_audit_actions.json do not match sql_audit_actions.csv.", file=sys.stderr)
        if not html_ok:
            print("  index.html's embedded DATA.sql_audit is stale.", file=sys.stderr)
        if not json_ok:
            print("  sql_audit_actions.json is stale.", file=sys.stderr)
        print("Run `python3 tools/build_sql_audit.py` and commit the result.", file=sys.stderr)
        return 1

    HTML_PATH.write_text(new_html, encoding='utf-8')
    SQL_AUDIT_JSON.write_text(new_json_text, encoding='utf-8')
    print(f"sql_audit_actions.csv: {total} rows")
    print(f"sql_audit_actions.json: rewritten ({total} rows)")
    print(f"index.html: DATA.sql_audit rewritten ({total} rows)")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if index.html/sql_audit_actions.json are out of sync with sql_audit_actions.csv")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
