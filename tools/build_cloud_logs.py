#!/usr/bin/env python3
"""Regenerates index.html's embedded Windows Events DATA.cloud_logs array
from windows/data/cloud_logs.csv, the single source of truth.

Run this after any change to windows/data/cloud_logs.csv, instead of
hand-editing the embedded copy in index.html directly. It also keeps
windows/data/cloud_logs.json in sync (a plain JSON export of the same
CSV). Mirrors tools/build_windows_events.py's approach for events.csv,
applied to the Cloud Logs tab's own data instead - a gap
build_windows_events.py's own docstring assumed was covered by "their
own established per-source workflow", which didn't actually exist for
cloud_logs.csv until this script.

Usage:
    python3 tools/build_cloud_logs.py [--check]

--check   Don't write anything; exit non-zero if index.html/cloud_logs.json
          are out of sync with cloud_logs.csv. Used by CI (see
          .github/workflows/build-check.yml).

Scope: this script only touches the `cloud_logs` key of the `DATA` object
embedded under app-win (the Cloud Logs tab). Windows Events' own
`events` array, the Windows Events reference tables, and the Cloud
Actions Explorer's data (sourced from MicrosoftCloud_Schema.json, its
own separate pipeline) are unaffected.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLOUD_LOGS_CSV = REPO_ROOT / 'windows' / 'data' / 'cloud_logs.csv'
CLOUD_LOGS_JSON = REPO_ROOT / 'windows' / 'data' / 'cloud_logs.json'
HTML_PATH = REPO_ROOT / 'index.html'
# Same container as build_windows_events.py: the Cloud Logs tab lives
# inside the Windows Events app's single embedded DATA object.
CONTAINER_ANCHOR = "getElementById('app-win')"
DATA_DECL = 'const DATA = '

FIELDNAMES = ['platform', 'area', 'resource_type', 'category', 'description',
              'severity_notes', 'config_location', 'cim_mapping', 'nist_800_53_au',
              'windows_equivalent']


def load_csv_rows():
    with open(CLOUD_LOGS_CSV, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        missing = [f for f in FIELDNAMES if f not in r]
        if missing:
            raise ValueError(f"cloud_logs.csv row {r.get('category')} missing column(s): {missing}")
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
    keys = [(r['platform'], r['area'], r['resource_type'], r['category']) for r in rows]
    if len(keys) != len(set(keys)):
        seen = set()
        dupes = [k for k in keys if k in seen or seen.add(k)]
        raise ValueError(f"cloud_logs.csv has duplicate (platform, area, resource_type, category) rows: {dupes}")

    logs = [{k: r.get(k, '') for k in FIELDNAMES} for r in rows]

    html = HTML_PATH.read_text(encoding='utf-8')
    start, end = find_data_object_span(html)
    data = json.loads(html[start:end])
    data['cloud_logs'] = logs
    new_data_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:start] + new_data_json + html[end:]

    total = len(logs)
    new_html, n = re.subn(r'[\d,]+ log categories across', f'{total:,} log categories across', new_html)
    if n != 1:
        raise ValueError(f"expected exactly one 'N log categories across' banner match, found {n}")
    new_json_text = json.dumps(logs, indent=2) + '\n'

    if check:
        html_ok = new_html == html
        json_ok = new_json_text == (CLOUD_LOGS_JSON.read_text(encoding='utf-8') if CLOUD_LOGS_JSON.exists() else None)
        if html_ok and json_ok:
            print(f"OK: index.html and cloud_logs.json already match cloud_logs.csv ({total} rows).")
            return 0
        print("OUT OF SYNC: index.html and/or cloud_logs.json do not match cloud_logs.csv.", file=sys.stderr)
        if not html_ok:
            print("  index.html's embedded DATA.cloud_logs is stale.", file=sys.stderr)
        if not json_ok:
            print("  cloud_logs.json is stale.", file=sys.stderr)
        print("Run `python3 tools/build_cloud_logs.py` and commit the result.", file=sys.stderr)
        return 1

    HTML_PATH.write_text(new_html, encoding='utf-8')
    CLOUD_LOGS_JSON.write_text(new_json_text, encoding='utf-8')
    print(f"cloud_logs.csv: {total} rows")
    print(f"cloud_logs.json: rewritten ({total} rows)")
    print(f"index.html: DATA.cloud_logs rewritten ({total} rows)")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if index.html/cloud_logs.json are out of sync with cloud_logs.csv")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
