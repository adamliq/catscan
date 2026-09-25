#!/usr/bin/env python3
"""Regenerates linux/data/events.json from linux/data/events.csv, the
single source of truth for the Linux Events catalogue's main table.

Run this after any change to linux/data/events.csv. It only handles the
CSV -> events.json step; pushing events.json (and every other Linux
reference table) into index.html's embedded DATA object is
tools/build_linux_reference.py's job - run that afterwards, or just run
both in sequence.

This closes the same class of gap tools/build_cloud_logs.py closed for
windows/data/cloud_logs.csv: build_linux_reference.py's own docstring
says each Linux reference table "already keep[s] each table's .csv and
.json in sync as part of making an edit" via its own per-table
add/update script, but no such script ever existed for events.csv
specifically - a hand-edit to the CSV alone would silently drift from
events.json (and, downstream, from the embedded copy) exactly the way
Windows Events once did before the `1.5.8` reconciliation.

Usage:
    python3 tools/build_linux_events.py [--check]

--check   Don't write anything; exit non-zero if events.json is out of
          sync with events.csv. Used by CI (see
          .github/workflows/build-check.yml).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_CSV = REPO_ROOT / 'linux' / 'data' / 'events.csv'
EVENTS_JSON = REPO_ROOT / 'linux' / 'data' / 'events.json'

FIELDNAMES = ['event_id', 'log', 'source', 'category', 'subcategory', 'description',
              'sample', 'reference', 'how_to_collect', 'sample_type', 'mitre_techniques',
              'priority_signal', 'acsc_ism_control', 'cis_control', 'disa_stig_id',
              'nist_800_53_au', 'field_schema']


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


def build(check=False):
    rows = load_csv_rows()
    # Not (event_id, log, source, category, subcategory) alone: one pre-existing
    # pair (1305/audit/SYSCALL/auditctl/Policy Change/Audit Configuration) is two
    # genuinely different CONFIG_CHANGE messages under that same 5-tuple, so
    # description is part of the real key too - this still catches an exact
    # full-row duplicate, which is the actual mistake worth failing CI over.
    keys = [(r['event_id'], r['log'], r.get('source', ''), r.get('category', ''),
              r.get('subcategory', ''), r.get('description', '')) for r in rows]
    if len(keys) != len(set(keys)):
        seen = set()
        dupes = [k for k in keys if k in seen or seen.add(k)]
        raise ValueError(f"events.csv has duplicate (event_id, log, source, category, subcategory, description) rows: {dupes}")

    events = csv_rows_to_json_events(rows)
    total = len(events)
    new_json_text = json.dumps(events, indent=2) + '\n'

    if check:
        current = EVENTS_JSON.read_text(encoding='utf-8') if EVENTS_JSON.exists() else None
        if new_json_text == current:
            print(f"OK: events.json already matches events.csv ({total} events).")
            return 0
        print("OUT OF SYNC: events.json does not match events.csv.", file=sys.stderr)
        print("Run `python3 tools/build_linux_events.py` (then build_linux_reference.py) and commit the result.",
              file=sys.stderr)
        return 1

    EVENTS_JSON.write_text(new_json_text, encoding='utf-8')
    print(f"events.csv: {total} rows")
    print(f"events.json: rewritten ({total} events)")
    print("Now run `python3 tools/build_linux_reference.py` to push this into index.html.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if events.json is out of sync with events.csv")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
