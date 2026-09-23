#!/usr/bin/env python3
"""Fails if this branch's VERSION isn't strictly newer than the base
branch's current VERSION - the exact check that would have caught the
PR #67/#68 collision (both branched from the same commit, each
independently bumping 1.5.2 -> 1.5.3, so the second one to merge landed
with a VERSION that no longer reflected reality and needed a manual
merge-conflict resolution to fix). Run in CI against the PR's base ref;
also runnable locally by passing --base <git-ref>.

Usage:
    python3 tools/check_version.py --base origin/main
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_PATH = REPO_ROOT / 'VERSION'


def parse_version(s):
    s = s.strip()
    m = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', s)
    if not m:
        raise ValueError(f"not a MAJOR.MINOR.PATCH version: {s!r}")
    return tuple(int(x) for x in m.groups())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', required=True, help='git ref to compare against, e.g. origin/main')
    args = parser.parse_args()

    current = parse_version(VERSION_PATH.read_text())

    try:
        base_text = subprocess.run(
            ['git', 'show', f'{args.base}:VERSION'],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        print(f"Could not read VERSION from {args.base}: {exc.stderr.strip()}", file=sys.stderr)
        return 1
    base = parse_version(base_text)

    if current > base:
        print(f"OK: VERSION {'.'.join(map(str, current))} is newer than "
              f"{args.base}'s {'.'.join(map(str, base))}.")
        return 0

    print(f"VERSION {'.'.join(map(str, current))} is not newer than {args.base}'s "
          f"{'.'.join(map(str, base))}.", file=sys.stderr)
    if current == base:
        print("This usually means either VERSION wasn't bumped for this change, or another "
              "PR already bumped it to the same value first - rebase onto the latest base "
              "and bump VERSION again.", file=sys.stderr)
    else:
        print(f"{args.base} has moved past this branch's VERSION - rebase and bump again.",
              file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
