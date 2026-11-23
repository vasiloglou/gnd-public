# literature-host-interfaces — delta from the plan

What the milestone delivered differently from plan r6 as written. Items 1
to 3 are plan amendments, stated in plan §11 "close amendments"; the rest
are phase-level and recorded in the phase specs' implementation findings.

1. **Retained-file ceiling** (A1). D4's 64 MiB ceiling could never be read
   back: every JSON reader of the repository refuses over 10 MiB
   (`gnd.input_policy.MAX_BYTES`). The ceiling is that cap, imported, and
   the ceiling runs use 9 sections at 1 MiB (LH2 refuted premise).
2. **Two pull requests** (A2), the reading pair then the admission pair, so
   that literature-reading-reference's LR3 need not wait for LH4.
3. **Delegated execution** (A3). The owner's `/process-milestone … auto`
   superseded D15's phase-by-phase ruling; every spec was approved by
   delegated ruling.
4. **LH1 size.** `reading.py` grew by 695 lines and lost 159, past the
   400-line split threshold; the split was ruled out by delegation (LH1
   finding 1).
5. **The retained bound is measured per file** from roster strings, input
   pins and saved files, not estimated per row (LH1 review r1-F1, r2-F1).
6. **Handles are keyed as the checker keys them**
   (`gnd.synth.identity.scalar_identity`): `true` and `1` are two
   assertions, `1` and `1.0` one (LH3 review r1-F1).
7. **Rules `reasons`** is a list of value and reason pairs, optional per
   requirement (LH4 finding 1, review r1-F2).
8. **The model loads before the judgment route**, so rules are checked
   first and an edited include refuses `input:model` before the route
   (LH4 finding 2).
9. **The `/2` admission record names the shape kind** (`caller` or
   `packaged`) beside `shape_sha256` (LH4 finding 3).
10. **Saved receipts are checked at input time** for everything knowable
    before a call: decision, basis, excerpt digest, digest shape and size
    (LH1 review r2-F1, r2-F2).
