#!/usr/bin/env python3
"""Regenerates windows/data/MicrosoftCloud_Schema.json from
windows/data/MicrosoftCloud_Schema.xlsx (the "schema (gap-filled)" sheet,
the single source of truth for the Cloud Actions Explorer tab), then
splices the result into index.html's embedded DATA.cloud_actions array.

Run this after any change to MicrosoftCloud_Schema.xlsx, instead of
hand-editing MicrosoftCloud_Schema.json or index.html's embedded copy
directly. This closes the same class of gap tools/build_cloud_logs.py
closed for cloud_logs.csv: windows/tools/export_schema_json.py already
regenerates MicrosoftCloud_Schema.json from the xlsx, but nothing kept
index.html's embedded DATA.cloud_actions in sync with that JSON - a
hand-edit to the xlsx (or a run of export_schema_json.py alone) would
silently drift from the running Cloud Actions Explorer tab.

Usage:
    python3 tools/build_cloud_actions.py [--check]

--check   Don't write anything; exit non-zero if MicrosoftCloud_Schema.json
          is out of sync with the xlsx, or index.html is out of sync with
          MicrosoftCloud_Schema.json. Used by CI (see
          .github/workflows/build-check.yml).

Scope: this script only touches the `cloud_actions` key of the `DATA`
object embedded under app-win (the Cloud Actions Explorer tab). Windows
Events' own `events` array, the Windows Events reference tables, and the
Cloud Logs tab's own data are unaffected.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_SCRIPT = REPO_ROOT / 'windows' / 'tools' / 'export_schema_json.py'
SCHEMA_JSON = REPO_ROOT / 'windows' / 'data' / 'MicrosoftCloud_Schema.json'
HTML_PATH = REPO_ROOT / 'index.html'
CONTAINER_ANCHOR = "getElementById('app-win')"
DATA_DECL = 'const DATA = '


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
    before = SCHEMA_JSON.read_text(encoding='utf-8') if SCHEMA_JSON.exists() else None
    result = subprocess.run([sys.executable, str(EXPORT_SCRIPT)], capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError("windows/tools/export_schema_json.py failed")
    after = SCHEMA_JSON.read_text(encoding='utf-8')
    json_ok = before == after

    if check and not json_ok:
        SCHEMA_JSON.write_text(before, encoding='utf-8')  # restore, --check must not write

    cloud_actions = json.loads(after)
    total = len(cloud_actions)

    html = HTML_PATH.read_text(encoding='utf-8')
    start, end = find_data_object_span(html)
    data = json.loads(html[start:end])
    embedded_matches = data.get('cloud_actions') == cloud_actions

    if check:
        if json_ok and embedded_matches:
            print(f"OK: MicrosoftCloud_Schema.json and index.html's embedded DATA.cloud_actions already match the xlsx ({total} rows).")
            return 0
        print("OUT OF SYNC: Cloud Actions Explorer data is stale.", file=sys.stderr)
        if not json_ok:
            print("  MicrosoftCloud_Schema.json does not match MicrosoftCloud_Schema.xlsx.", file=sys.stderr)
        if not embedded_matches:
            print("  index.html's embedded DATA.cloud_actions does not match MicrosoftCloud_Schema.json.", file=sys.stderr)
        print("Run `python3 tools/build_cloud_actions.py` and commit the result.", file=sys.stderr)
        return 1

    data['cloud_actions'] = cloud_actions
    new_data_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:start] + new_data_json + html[end:]
    HTML_PATH.write_text(new_html, encoding='utf-8')
    print(f"MicrosoftCloud_Schema.json: {total} rows (regenerated from the xlsx)")
    print(f"index.html: DATA.cloud_actions rewritten ({total} rows)")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if the schema JSON/index.html are out of sync")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
