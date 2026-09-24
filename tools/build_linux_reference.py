#!/usr/bin/env python3
"""Regenerates index.html's embedded Linux Events DATA object from every
JSON file under linux/data/ - linux/data/events.json (the `events` key)
and every linux/data/reference/*.json file (one DATA key per file, named
after the file's stem).

Run this after any change to one of those JSON files, instead of
hand-editing the embedded copy in index.html directly. Every prior update
to e.g. log_file_locations.json this project's history relied on an ad
hoc, uncommitted scratchpad script to do this same sync by hand; this
script replaces that with a committed, generic tool covering every Linux
reference table at once, and its --check mode closes the same class of
silent-drift gap that tools/build_windows_events.py closed for Windows
Events (see the README's `1.5.8` changelog entry).

Usage:
    python3 tools/build_linux_reference.py [--check]

--check   Don't write anything; exit non-zero if index.html's embedded
          DATA object is out of sync with any of the source JSON files.
          Used by CI (see .github/workflows/build-check.yml).

Scope: this syncs JSON -> embedded DATA only. It does not regenerate a
table's .json from its .csv (unlike the Windows Events script, where CSV
is the single source of truth) - each Linux reference table has its own
CSV schema, and this project's existing per-table add/update scripts
already keep each table's .csv and .json in sync with each other as part
of making an edit. A handful of DATA keys (auditd_command_cheatsheet,
auditd_record_type_tip, command_logging_guides,
fapolicyd_command_cheatsheet, fapolicyd_rule_eval_tip) are short,
hand-authored text/list values with no backing JSON file; this script
leaves those untouched.
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINUX_DATA_DIR = REPO_ROOT / 'linux' / 'data'
REFERENCE_DIR = LINUX_DATA_DIR / 'reference'
EVENTS_JSON = LINUX_DATA_DIR / 'events.json'
HTML_PATH = REPO_ROOT / 'index.html'
# Mirrors tools/build_windows_events.py's anchor technique: each app's IIFE
# opens with `var __container = document.getElementById('app-XXX');`
# immediately before its own `const DATA = ` declaration, specifically so a
# build script can find that declaration reliably rather than by matching
# some value expected to be first in an array - which a regeneration can
# reorder.
CONTAINER_ANCHOR = "getElementById('app-lnx')"
DATA_DECL = 'const DATA = '


def discover_sources():
    """Maps each DATA key this script owns to its source JSON file."""
    sources = {'events': EVENTS_JSON}
    for path in sorted(REFERENCE_DIR.glob('*.json')):
        sources[path.stem] = path
    return sources


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
    sources = discover_sources()

    html = HTML_PATH.read_text(encoding='utf-8')
    start, end = find_data_object_span(html)
    data = json.loads(html[start:end])

    changed = []
    new_keys = []
    for key, path in sources.items():
        loaded = json.loads(path.read_text(encoding='utf-8'))
        if key not in data:
            new_keys.append(key)
        elif data[key] != loaded:
            changed.append(key)
        data[key] = loaded

    new_data_json = json.dumps(data, separators=(',', ':'))
    new_html = html[:start] + new_data_json + html[end:]

    if check:
        if new_html == html:
            print(f"OK: index.html's embedded DATA already matches all {len(sources)} "
                  f"source JSON files under linux/data/.")
            return 0
        print("OUT OF SYNC: index.html's embedded DATA does not match one or more "
              "source JSON files under linux/data/.", file=sys.stderr)
        if changed:
            print(f"  changed: {', '.join(sorted(changed))}", file=sys.stderr)
        if new_keys:
            print(f"  new (not yet embedded): {', '.join(sorted(new_keys))}", file=sys.stderr)
        print("Run `python3 tools/build_linux_reference.py` and commit the result.", file=sys.stderr)
        return 1

    HTML_PATH.write_text(new_html, encoding='utf-8')
    print(f"synced {len(sources)} keys from linux/data/ into index.html's embedded DATA")
    if changed:
        print(f"  changed: {', '.join(sorted(changed))}")
    if new_keys:
        print(f"  newly added: {', '.join(sorted(new_keys))}")
    if not changed and not new_keys:
        print("  (already up to date)")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                         help="don't write anything; fail if index.html's embedded DATA is out of "
                              "sync with any source JSON file under linux/data/")
    args = parser.parse_args()
    sys.exit(build(check=args.check))


if __name__ == '__main__':
    main()
