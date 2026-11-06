# RC2 corpus answer key

The expected results for the cases in `../README.md`.

## How it was written

- `<case>.v7.json`: `gnd check <model> <population> --format json` at
  c5fe86bb, before any RC2 change. These are frozen controls.
- `<case>.json` for cases 1-3 and 5: the `--rule-ids --format json` output
  at c5fe86bb, with the failing verdict's `offending_facts` and `message`
  replaced by the answer of an independent brute-force oracle (transitive
  closure; two components share a loop when each reaches the other; a
  component is a loop of one when it uses itself), not by the
  implementation's algorithm. Rows are `[user, used]`, sorted. For the
  composite, the loop's rows come first, then the `intransitive` witnesses
  as today. The message is
  `<n> strongly connected group(s) (size(s) <sizes, largest first>) hold(s) <m> edge(s)`.
- `clean.json`: the `--rule-ids --format json` output at c5fe86bb,
  unchanged (the rule passes).
- `two-groups.txt`: the text output at c5fe86bb with the one message
  replaced as in `two-groups.json`.
- `exits.json`: the exit code of every case.
