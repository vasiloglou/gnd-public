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
5. **The retained bound is measured per file.** Before the first call, a
   file that carries answers or receipts is bounded by its eligible
   sections times the response cap, plus each attempt row measured from the
   roster's own strings; saved tables and copied inputs by their measured
   size; the rest by the input pins and identifiers. A saved receipt is held
   to the response cap at input time. LH1-C14 (`test_t20_*`, `test_r1_*`,
   `test_r5_*`) runs at the response ceiling and reads every file back;
   LH2-C3 (`test_t3_the_response_ceiling_run_replays_in_time`) replays it
   (LH1 review r1-F1, r2-F1).
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
11. **The focused lanes add `tests/test_ld1_competency_examples.py`**, the
    direct test of `depth.py`, which LH1 changed (LH1 finding 9); the LH2
    lane and the close lanes include it.
12. **An accepted answer may not carry an empty fact list**, and a question
    is `supported` only when its fact has rows (close panel, Codex;
    `test_r10_an_empty_fact_list_is_not_support`).
13. **Handles compare as the checker compares values**, documented in the
    admission README's "Identity" bullet (close panel, Qwen).
