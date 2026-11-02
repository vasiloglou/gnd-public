# Phase NM4 -- independent docs review (NM4-C5, T8)

Reviewer: a Claude subagent with read-only repository access, given the
uncommitted NM4 docs and the code that defines the behaviour, not the
author's conclusions. It ran commands from a scratch directory. Machine paths
are replaced by `<scratch>`. Report condensed; findings in its words where
they matter.

## Verdict

Nothing blocking. Two should-fix accuracy gaps, two minor.

## Findings

| ID | Severity | Page | Finding (reproduced by the reviewer) | Disposition |
|---|---|---|---|---|
| R1 | should-fix | `docs/reference/disclosure.md`, resolution rules 1-2 | The page said every command that can emit values refuses a malformed `GND_DISCLOSURE` or a loosening option. The CLI resolves the mode only on commands with a site or spawner row (`disclosure.bearing`), so `discover`, `export ilp`, `fidelity` and `doccheck` ignore both: `GND_DISCLOSURE=bogus gnd discover …` exits 0, as does `GND_DISCLOSURE=customer gnd --disclosure internal discover …`. The plan (§2.2) says "Other commands ignore it", so the code is as designed. The author reproduced the first run. | fixed: the rules now name the commands the mode governs, and a sentence says the every-mode and value-free commands ignore the variable and the option's value |
| R2 | should-fix | `disclosure.md`, three-states table, unset row | "The Python functions return raw values" holds only for `api.witness`, `api.replay` and `api.why_not`; the export functions default to `raw=False` and return value-free output unless `raw=True` (read in `src/gnd/export/service.py`). | fixed: the row names the three functions and says "unless `--raw` or `raw=True`" |
| R3 | minor | `disclosure.md`, generated table | The view-site rows said "`raw=True` refused", but `api.witness`, `api.replay` and `api.why_not` take no `raw` keyword; only the export functions do (each confirmed to raise `DisclosureRefused` under `customer`). | fixed: the generator's two class texts say "where taken"; the table was re-pasted and T5 passes |
| R4 | minor | `docs/how-to/disclosure-mode.md:34-35` | The page said the filter prints three fields; `show.py` prints two. | fixed |

## Verified by running

- Tutorial groups `disclosure`, `why-not` and `api`, plus
  `tests/test_disclosure_docs.py`: 9 passed. Every `gnd-run` block reproduced,
  including both exit-64 usage errors, the refusal messages, the near-miss
  "1 redacted" and the Python block under `customer`.
- The option is accepted only at the root (`gnd check --disclosure customer …`
  exits 64). A bad value is exit 64 even on an ungoverned command.
- Under `customer`, `--raw` is refused (exit 3, empty stdout) on `witness` and
  `export souffle`; `api.export_lean` and `api.export_souffle` raise on
  `raw=True`.
- `forward()` returns nothing under unset and `internal`, and
  `GND_DISCLOSURE=customer` under `customer`, including inside an invocation
  with the environment unset.
- Under `internal`, `api.check` shows the email values. Under `customer`,
  `api.witness` has no `certificate`, `api.why_not` returns the redacted view,
  a malformed environment makes `api.why_not` raise, and `DisclosureRefused` is
  a `ValueError`.

## Verified by reading

- `api.replay`'s customer view; the four spawners that forward only `customer`
  (session, declared adapter, reviewer seats, solve), each marking the value
  as disclosed; context-variable precedence.
- Every link and anchor the new text uses.
- `NFKC` only in `docs/reference/why-not.md`; no downstream application names.

## Unproved

- The `discover` and ILP-bridge claims about redacted roles (they match the
  table's notes; the reviewer's runs stopped before that path).
- Real child-process environments for `exp run`, `solve` and `review panel`
  (code read, not spawned; NM2 T30-T33 cover them).
