# Issue 318: the per-command log

Issue 318 item 2 proposes reading each Bash call's command and exit code
from Claude Code hooks instead of from shell text. Where a Bash call's exit
code sits in a hook's input is not documented, so one paid discovery run
looks.

- [001-discovery-gate.md](001-discovery-gate.md): the owner's gate for that
  run, its scope and its USD 3.00 ceiling.
- [evidence/](evidence/): the script, the hook, the owner's words and, after
  the run, the key layout it found.

## What the run showed (2026-11-26)

One run under the gate, as declared: Claude Code 2.1.322, `claude-haiku-5-5`,
two turns, USD 0.0089 in total (USD 0.0040 and 0.0048). Twelve hook events for
six Bash calls; the key layout is in [schema.json](evidence/schema.json), with
host paths, ids and the `date` output (the host's time zone) left out.

- **Every Bash call fires PreToolUse, then exactly one of PostToolUse or
  PostToolUseFailure**, paired by `tool_use_id`. Each carries
  `tool_input.command`, the whole command as the agent sent it (`true && false`
  is one call, one event pair).
- **A zero exit has no exit-code key.** PostToolUse's `tool_response` holds
  `stdout`, `stderr`, `interrupted`, `isImage` and `noOutputExpected`; that the
  event is PostToolUse is what says the call exited 0.
- **A non-zero exit fires PostToolUseFailure**, whose `error` was
  `Exit code N` for every one here (1, 3, 1, 5), with `is_interrupt: false`.
  Each of these commands printed nothing; whether `error` also carries output
  when a failing command prints is not shown by this run.
- **The hooks fired on the resumed turn too**, attached by `--settings` with
  `--setting-sources project`, so user and local settings were not loaded.
- **No denial was observed.** `date` was outside the allow list but ran:
  Claude Code permits read-only commands on its own. What a hook sees for a
  refused call is still unknown; the run's `permission_denials` were empty.
