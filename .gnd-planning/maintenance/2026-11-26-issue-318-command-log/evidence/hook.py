"""A Claude Code hook for the issue 318 discovery run: append the hook's whole input as one JSON line.

Usage (from a --settings file): python3 -I hook.py LOG. It reads the event from stdin, writes nothing to
stdout and exits 0, so it never changes what Claude Code decides.
"""
import json
import sys

event = sys.stdin.read()
with open(sys.argv[1], "a", encoding="utf-8") as log:
    try:
        log.write(json.dumps(json.loads(event), ensure_ascii=False) + "\n")
    except ValueError:
        log.write(json.dumps({"unparsed": event}, ensure_ascii=False) + "\n")
