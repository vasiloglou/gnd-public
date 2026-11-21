# Draft replies for issues 217 and 214

Drafted at the include-root-routes close, 2026-11-21. Not posted: posting is
the owner's act, outside `auto=true`. Each reply describes the branch
`claude/include-root-routes`; until its pull request is merged and released
the behaviour is not in a published GND.

## Reply to #217

Both routes you asked for are on the `include-root-routes` branch:

- **`gnd judgments check` judges an include root directly**, temporal or
  not. It composes the root as `gnd check` does. Receipts keep binding the
  root file's sha256 (`subject.model_sha256`), which commits to every
  include's pin: an include edited without a new pin refuses
  `include:hash-mismatch`, and an include edited and pinned again makes the
  old receipts stale. `--reference-root` applies to include roots too.
  Include refusals now report `reason: "binding"` with the include code in
  `message`; 0.4.0 wrote the include code as the reason, which
  `judgment.schema.json` does not allow.
- **`gnd flatten MODEL --out DIR`** writes `<stem>.flat.orm.json` and its
  `gnd-flattening/1` record for any include root, temporal ones included.
  It never overwrites a file (exit 11). The flat model keeps reference paths
  relative to the root's directory, so write it there if you want to check
  it. `gnd extract` still refuses temporal models and now names
  `gnd flatten` for a temporal include root.

On the interop fixture, `checking.orm.json` (temporal, two includes, one
reference population) judges with exit 0, and the non-temporal
`extraction.orm.json` gives the same verdicts directly and through its flat
model.

One thing we found on the way: `gnd check` slows down sharply with the
number of object types, with or without includes (7.7 s at 300 extra value
types, 266 s at 1,000 on our machine), and `judgments check` pays it twice.
That is a separate fix.

## Reply to #214, item 1

`gnd export pyrel` now exports an include root through its flat model, in
the default mode and with `--rules duckdb` or `--rules lqp`. The program
records `FLATTENING_RECORD_SHA256` (the sha256 of the `gnd-flattening/1`
record `gnd flatten` writes for the same root) and `MODEL_INCLUDES` (each
include's `(id, path, sha256)` pin), so an include changed and pinned again
gives a different recorded digest. An exported program does not notice
include changes after export.

On temporal models: the default program still refuses them; the `--rules`
programs accept them. On the interop fixture, `extraction.orm.json` exports
in the default mode, and under `--rules` both roots now get past the include
refusal and stop at the anchored constraint `paper_names_parent_method#0`,
which is item 2 of this issue (pyrel-rules-coverage RP2).
