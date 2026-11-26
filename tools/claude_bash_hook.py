"""A Claude Code hook that appends its whole input, as one JSON line, to the log file it is given.

The session recorders attach it to Bash's PreToolUse, PostToolUse and PostToolUseFailure events with
`--settings`, so each Bash call's command and outcome are logged as Claude Code runs it (issue 318). Usage:
python3 -I claude_bash_hook.py LOG. It writes nothing to stdout and exits 0, so it never changes what
Claude Code decides. What the events hold was measured in the issue 318 discovery run
(.gnd-planning/maintenance/2026-11-26-issue-318-command-log/).
"""
import json
import sys

event = sys.stdin.read()
with open(sys.argv[1], "a", encoding="utf-8") as log:
    try:
        log.write(json.dumps(json.loads(event), ensure_ascii=False) + "\n")
    except ValueError:
        log.write(json.dumps({"unparsed": event}, ensure_ascii=False) + "\n")
