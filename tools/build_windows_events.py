#!/usr/bin/env python3
"""Regenerates index.html's embedded Windows Events DATA.events array from
windows/data/events.csv, the single source of truth.

Run this after any change to windows/data/events.csv, instead of
hand-editing the embedded copy in index.html directly. It also keeps
windows/data/events.json in sync (a plain JSON export of the same CSV) and
updates the "N events indexed" footer count.

Usage:
    python3 tools/build_windows_events.py [--check]

--check   Don't write anything; exit non-zero if index.html/events.json
          are out of sync with events.csv. Used by CI (see
          .github/workflows/build-check.yml) so a PR that edits
          events.csv without regenerating the derived files fails
          before merge, instead of silently drifting the way
          index.html and events.csv/.json drifted apart before this
          script existed (see README's `1.5.8` changelog entry for
          the reconciliation that prompted this).

Scope: this script only touches the Windows Events `events` array (the
`DATA` object's `events` key and the page footer count). The Windows
Events reference tables (NTLM/Kerberos/NTSTATUS code lookups etc.,
`DATA`'s other ~15 keys) and the Linux Events / Threat Detection / AWS
Events / Other Events apps are unaffected - those are edited far less
often and via their own established per-source workflows.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_CSV = REPO_ROOT / 'windows' / 'data' / 'events.csv'
EVENTS_JSON = REPO_ROOT / 'windows' / 'data' / 'events.json'
HTML_PATH = REPO_ROOT / 'index.html'
# The Windows Events app is the only one of this page's several
# self-contained IIFEs whose container id is 'app-win'; anchoring on that
# (rather than on which event_id happens to be first in the array) keeps
# this script working even after it reorders the array - which it always
# will, since it writes events in events.csv's own row order, not
# whatever order a previous regeneration left the embedded copy in.
CONTAINER_ANCHOR = "getElementById('app-win')"
DATA_DECL = 'const DATA = '

FIELDNAMES = ['event_id', 'log', 'source', 'category', 'subcategory', 'description',
              'sample', 'reference', 'how_to_collect', 'sample_type', 'mitre_techniques',
              'acsc_priority_log', 'nist_800_53_au', 'ad_compromise_techniques',
              'field_schema', 'group_policy_path', 'opposite_event_id', 'cim_mapping']


def load_csv_rows():
    with open(EVENTS_CSV, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        missing = [f for f in FIELDNAMES if f not in r]
        if missing:
            raise ValueError(f"events.csv row {r.get('event_id')} missing column(s): {missing}")
    return rows


def csv_rows_to_json_events(rows):
    events = []
    for r in rows:
        e = {k: r.get(k, '') for k in FIELDNAMES if k != 'field_schema'}
        raw_schema = r.get('field_schema', '') or '{}'
        try:
            e['field_schema'] = json.loads(raw_schema)
        except json.JSONDecodeError as exc:
            raise ValueError(f"event {r.get('event_id')} ({r.get('log')}/{r.get('source')}): "
                              f"invalid field_schema JSON: {exc}") from exc
        events.append(e)
    return events


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
    keys = [(r['log'], r.get('source', ''), r['event_id'], r.get('subcategory', '')) for r in rows]
    if len(keys) != len(set(keys)):
        seen = set()
        dupes = [k for k in keys if k in seen or seen.add(k)]
        raise ValueError(f"events.csv has duplicate (log, source, event_id, subcategory) rows: {dupes}")

    events = csv_rows_to_json_events(rows)

    html = HTML_PATH.read_text(encoding='utf-8')
    start, end = find_data_object_span(html)
    data = json.loads(html[start:end])
    old_count = len(data['events'])
    data['events'] = events
    new_data_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:start] + new_data_json + html[end:]

    total = len(events)
    new_html, n = re.subn(r'[\d,]+ events indexed', f'{total:,} events indexed', new_html)
    if n != 1:
        raise ValueError(f"expected exactly one 'events indexed' footer match, found {n}")

    new_json_text = json.dumps(events, indent=2) + '\n'

    if check:
        html_ok = new_html == html
        json_ok = new_json_text == (EVENTS_JSON.read_text(encoding='utf-8') if EVENTS_JSON.exists() else None)
        if html_ok and json_ok:
            print(f"OK: index.html and events.json already match events.csv ({total} events).")
            return 0
        if not html_ok:
            print("OUT OF SYNC: index.html's embedded DATA.events does not match events.csv.", file=sys.stderr)
        if not json_ok:
            print("OUT OF SYNC: events.json does not match events.csv.", file=sys.stderr)
        print("Run `python3 tools/build_windows_events.py` and commit the result.", file=sys.stderr)
        return 1

    HTML_PATH.write_text(new_html, encoding='utf-8')
    EVENTS_JSON.write_text(new_json_text, encoding='utf-8')
    print(f"events.csv: {total} rows")
    print(f"events.json: rewritten ({total} events)")
    print(f"index.html: DATA.events rewritten ({old_count} -> {total} events), footer updated")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if index.html/events.json are out of sync with events.csv")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
