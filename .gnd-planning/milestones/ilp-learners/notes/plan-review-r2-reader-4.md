# Round 2 — Reader 4: measurability, falsifiability and reproducibility

**Digests matched:** yes. Plan r2 is `e0668e30…3bb9` and IL1 spec r2 is `4a06f583…f5af8`; both match.

**Verdict: approve-with-fixes.**

**Scope:** I checked whether R4-F1 and R4-F7 are resolved by the r2 bytes, and looked only for defects that r2's own changed text introduced.

**Probes:**
- I simulated the r2 tokenizer: `_TOKEN` with `\\[0-7]{1,7}\\` inserted before `\\.`, over every T4 and T4b case. Script: `<scratchpad>/review2/reader-4/tok.py`.
- I checked the octal arithmetic for every case.
- I read the import command's report and proposal emission at `63f7f1f`.
- No repository file was touched.

## Round-1 blockers

| Finding | Status | Evidence |
|---|---|---|
| R4-F1 (T4 "beyond Unicode" case was valid Unicode) | **Resolved** | **Spec:** spec:316–317 now uses `'\4177777\'` as the accepted boundary, `'\4200000\'` as beyond Unicode and `'\154000\'` as the surrogate. Plan:392–397 (IL1-C3) agrees.<br>**Arithmetic:** octal 4177777 = 0x10FFFF, 4200000 = 0x110000, 154000 = 0xD800, 101 = 0x41, 7 = 0x7, 1 = 0x1.<br>**Tokenizer simulation:** the accepted cases and both token-boundary cases tokenize as spec:316 claims. `f(A,B,'\001\'),g(A,B,'x')` gives two quoted tokens. `'a\1\'),g(A,B,'b')` gives `'a\1\'` and `'b'`, so the octal reading wins. `'\4200000\'` and `'\154000\'` reach `_unquote` as whole tokens, where the hex form's scalar check (`ilp_popper.py:255`) can refuse them. |
| R4-F7 (no test could fail IL1-C4; no outcome for "no output") | **Partially resolved** | **Landed:**<br>- the closed outcome list (plan:130 IL-R9; spec:232–242);<br>- Popper's own timeout of 540 s, below the 600 s wall clock (spec:227–228);<br>- all six `ProcessLimits` fields (spec:228, which match `process.py:39–44`);<br>- numbered, retained invocations (spec:267–273);<br>- a default-gate replay test, T9 (spec:325; plan:399–408).<br>For an outcome that has a program, T9 now asserts the recorded exit, which can fail.<br>**Still open:**<br>- the report-digest half of T9 cannot reproduce as written (R4-2-F1);<br>- the list does not yield exactly one outcome (R4-2-F2);<br>- for outcomes with no program, T9 checks only that the outcome is on the list. Nothing ties `program.pl`, or its absence, to the committed raw stdout (R4-2-F4). |

## Self-inflicted findings (r2-introduced only)

- **R4-2-F1** (hardening, high): T9's "assert the recorded … report SHA-256" cannot reproduce, so T9 as written would fail on every machine.
  - **Cites:**
    - spec:325 and plan:406–408 add the report-digest assertion.
    - The import report embeds the paths of the model, labels, clauses, run record and `--out` proposal (`src/gnd/export/ilp_service.py:456–462`).
    - The proposal embeds `requested_at`, which defaults to `datetime.now(UTC)` (`ilp_service.py:418`). The `--requested-at` help in `commands/checking.py` says to "fix it for reproducible output".
    - On exit 3 no report is written; only stderr is (`ilp_service.py:428–430`). Yet spec:256 always retains `import-report.json`.
  - **Problem:** the evidence script runs under scratch paths that are later redacted to `<scratch>`, while the replay runs under pytest temporary paths. The report bytes therefore differ.
  - **Reproduce:** the bridge's own determinism test has to fix `--requested-at` and set `report["proposal"] = None` before it can compare two runs (`tests/test_ilp_bridge.py:433–443`).
  - **Repair:**
    - Fix `--requested-at` and `--format json` in both the script and the replay.
    - Run both with identical relative argv from a fixed working directory, or digest the report with every `path` and `proposal` field normalized.
    - Also assert the proposal's SHA-256.
    - For an exit-3 outcome, assert the redacted stderr refusal line instead of a report.

- **R4-2-F2** (hardening, medium): the closed list does not give "exactly one outcome" (spec:232), because its members overlap.
  - **Cites:** spec:234–242 and spec:230.
  - **Overlap 1:** the list mixes how the learner ended with what the import did. If Popper hits its own 540 s timeout and still prints a best-so-far program, both `learner-timeout` and `admitted` or `refused:*` apply. Confirm that anytime behaviour against the pinned version.
  - **Overlap 2:** `unparsable` duplicates `refused:unparsable`, since the import's parse refusals are exit 3 `unparsable: …` (`ilp_popper.py:249–257`).
  - **Overlap 3:** extraction over `CLAUSES_CAP` is labelled `unparsable` (spec:230). The importer would actually refuse it with "exceeds the …-byte cap" (`ilp_service.py:86–87`), so a replay could not reproduce the label.
  - **Overlap 4:** a kill for exceeding the output limit has no name of its own and falls under `wall-clock-kill`.
  - **Repair:** record two fields:
    - termination: `rendering-rejected` | `completed` | `learner-timeout` | `wall-clock-kill` | `output-limit`;
    - import: `none` | `refused:<name>` | `admitted`.

    Alternatively, state a precedence order, and define `unparsable` as `refused:unparsable`.

- **R4-2-F3** (hardening, medium): T4b's 8-digit case cannot carry "the octal-specific message" (spec:317) under the stated tokenizer change.
  - **Cites:** spec:202–204 (`\\[0-7]{1,7}\\`) and spec:210.
  - **Problem:** with `{1,7}`, the input `'\12345670\'` never forms a token, so the tokenizer fails with its generic "unexpected" error before `_unquote` runs.
  - **Context dependence:** if another quote follows on the same line, the token swallows the boundary. `f(A,B,'\12345670\'),g(A,B,'x')` yields the single token `'\12345670\'),g(A,B,'` followed by a failure. The message therefore depends on the context.
  - **Reproduce:** run `<scratchpad>/review2/reader-4/tok.py`.
  - **Repair:** either:
    - tokenize `\\[0-7]+\\` and refuse more than 7 digits in `_unquote` with the octal message; or
    - specify the tokenizer-failure diagnosis.

    Also add the two-quote context as a T4b case.

- **R4-2-F4** (completeness, medium): the program-block extraction rule is underdefined, and nothing checks it during replay.
  - **Cites:** spec:230 and spec:325.
  - **What is not fixed:**
    - "Popper's solution banner" is not spelled, unlike the timeout option, which is recorded at the gate.
    - "the maximal run" does not say which run when several follow banners.
    - In Popper's solution block, a scores line sits between the banner and the clauses.
  - **What T9 misses:** T9 never re-runs the extractor over the committed `raw-stdout.txt`. So "`program.pl` is what Popper printed" and "`no-solution` means no block" (spec:237) are unchecked claims.
  - **Repair:**
    - Record the banner string from the pinned version at the gate.
    - Define the program as "the first maximal run of `^wrong\(.*\.$` lines after the last banner".
    - Put the extractor in one function that both the script and T9 use.
    - Have T9 assert that the extractor's output over the committed raw stdout equals `program.pl`, or is empty for outcomes with no program.
