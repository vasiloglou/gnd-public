# Round 2 reader 3 -- protocol, authority, compatibility and privacy

Retained text of the reader's returned report. No local edits.

Digests: both subjects match (plan `b0308e35…630e`, WN1 spec `d1c87cb1…6f69`). No mismatch.

**Verdict: approve-with-fixes**

**Scope.** I read the r2 plan, the WN1 spec, the README, the r1 disposition and my round-1 note, and compared them with the r1 snapshots. I checked them against `review-convergence.md`, `spec-note-contract.md` and `standing-rules.md`, and against `docs/reference/cli.md:94-104`, `python-api.md:8-12,270-274` and `capabilities.md:41`. On the code side I checked `src/gnd/witness/{cli,producer,types}.py`, `commands/witness.py`, `extensions.py:56-90`, `branches.py:786`, the schema homes and `VENDORED_SCHEMAS`, and the anonymity precedent in transition-check-performance. I ran no tests and wrote nothing (no scratch files either). All findings are verified by reading; none needed a probe.

## Round-1 findings

| ID | Status | Evidence |
|---|---|---|
| R3-F1 | resolved | Top-level `unavailable` comes from production (spec §6.2 step 3) and maps to exit 4 (WN-D5). Dependency cases are in T1(d)(e). "No relation is read as empty" is stated. A new band defect is R3-2-F2. |
| R3-F2 | resolved | WN-R5 and WN-D4(a) now say the API returns raw values like `api.witness` (matches python-api.md:270-274). The closed allow-list covers descent, the claimed row, reasons and errors. WN2-C2 has the leak test. |
| R3-F3 | resolved (pending WN-D11) | §2 requires exactly one target, else exit 3. WN2-C1 covers zero, two and mismatched targets. |
| R3-F4 | resolved | The plan argues for the package-root home (`src/gnd/report.schema.json` and the others live there; `src/gnd/schema/` holds interchange schemas). `VENDORED_SCHEMAS` is named, `gnd-export` is added to WN3-C4, and `gnd-induce` is noted as not packaged. |
| R3-F5 | partly | Pins listed by path:line. The unit is now explicit (functions vs `__all__` names). The count sentence gets one home. The release note moves to WN2 (§5), but the README still puts it in WN3 (R3-2-F6). |
| R3-F6 | resolved | WN-D5(b) separates `derived` (0) from `unsupported` (2), and cli.md gets a why-not sentence. |
| R3-F7 | resolved | WN-D10 added, spec §11 gives a reason, and WN2 is corpus-first. A gating side effect is R3-2-F5. |
| R3-F8 | partly | Plan §4 and spec §1 now list the same set (D2, D6, D7, D9, D10). Two gaps remain: spec-local D6 ("Proposed", semiderived) is in neither list, and WN-D3 was removed from both while still pending confirmation (R3-2-F1). |
| R3-F9 | resolved | §8 marks the per-phase reader **proposed**, and the r1 digests sit beside the `(o)` WN-D8 entry (plan:12-18). |
| R3-F10 | partly | T13 now uses exact counter values, and the corpus has seeds 0..199 with size limits. T17 is still under-specified (R3-2-F4). |

## New findings

**R3-2-F1 -- hardening, high confidence, self-inflicted.** Where: plan:24-25 and the §10 WN-D3/D4/D5 cells; spec §1 and the §7 D2 row; README:31-34.
- What is wrong: the owner said to "take the proposed answers where a decision is re-argued". The r1 disposition contained no proposed answers for these three decisions:
  - WN-D3 offers two readings;
  - WN-D4 gives three readings without picking one (theme G);
  - WN-D5 leaves `unavailable` open as "(2 or 4)" (theme H).
- So the r2 answers are the author's choices. The plan header says honestly that they "were written after that direction". But other places treat them as ruled:
  - the §10 cells say "(p1, adopted)" with no "pending";
  - the README says "(confirmed at the plan gate)", which reads as past tense;
  - spec §1 drops WN-D3 from the blocked-on list;
  - spec §7 D2 has no readings or costs, which spec-note-contract §7 requires.
- How verified: compared the disposition's theme F/G/H text and its "New owner decisions surfaced" table with the plan, spec and README.
- Fix:
  - relabel the three as "proposed under the owner direction of 2026-10-30; the owner confirms at the plan gate";
  - keep WN-D3 in both blocked-on lists until it is confirmed;
  - restore the readings and costs in spec D2;
  - fix the README tense.

**R3-2-F2 -- hardening, high confidence, self-inflicted (p1-H/p1-B).** Where: the plan WN-D5 exit-4 row (plan:252); §2 step 1; spec §6.1; completion predicate 1.
- What is wrong: exit 4's reason is listed as "`term:…`/`opaque` origin", but §2 and §6.1 classify an opaque value anywhere in the closure as `unsupported`/`opaque-value`, which is exit 2. On top of that, `check` reports opaque-value as `unchecked` (`branches.py:786`), which is band 4, while witness reports it as band 2 `value-unknown` (`types.py:62`). So predicate 1 ("status agrees with `check`") is undefined for the opaque case.
- How verified: read the cited lines.
- Fix: pick one band for opaque, and remove "opaque" from the exit-4 row or from the §6.1 table. State that why-not follows witness's band 2, not check's band 4, and define "agrees" for this case in T8.

**R3-2-F3 -- hardening, medium confidence, self-inflicted.** Where: spec §4 rule 3, tagged "(p1-E)".
- What is wrong: r2 reverses the validation order (a malformed row is now refused before the unsupported fragment is reported). No round-1 finding or theme asked for this. Theme E covers branch cases only, so the owner's acceptance of A-K does not cover it, and the tag misattributes it.
- The new order is defensible, and has a better reason than the one given: witness intake refuses malformed targets (exit 3, `io.load_targets`) before `classify_targets` reports unsupported (exit 2, `producer.py:204-206`).
- How verified: grepped every r1 reader note and the disposition, and compared with the r1 snapshot lines 65-69.
- Fix: make this an explicit proposed decision row in spec §7, give the sibling-lane parity as the reason, and drop the p1-E tag.

**R3-2-F4 -- hardening, high confidence, self-inflicted (p1-K).** Where: spec T17; WN-R8.
- What is wrong: the owner file's path is unnamed. Behavior when the file is absent is unstated, and a skip would mean the test cannot fail on a clean clone (standing-rules). "The milestone's new files" is undefined. There is no negative control (review-convergence: an instrument is believed only after a negative control).
- How verified: read the spec, and compared with transition-check-performance R2-5, which proposed a committed digest list.
- Fix: commit SHA-256 digests of normalized forbidden tokens, so nothing is named in the repository. Scan files added since `fb03739`. Add a negative control that plants a token whose digest is in a test-only list. If an owner-local file is kept instead, fail rather than skip at the gate.

**R3-2-F5 -- completeness, medium confidence, self-inflicted (p1-K).** Where: completion predicate 4 ("golden payloads were committed before the code"); §4 WN2 ("Approval instrument: corpus-first (WN-D10)"); WN2-C1 (WN-D11).
- What is wrong: these proposals are written as closing conditions. §2's "proposed unless marked" disclaimer covers only §2, and review-convergence says the instrument "is asked, never inherited".
- Fix: make them conditional on the rulings ("if WN-D10 is ruled as proposed").

**R3-2-F6 -- completeness, high confidence, original (made stale by p1-I).** Where: README:16 says WN3 has the "how-to and release note"; plan §5 says "Release note in WN2". Fix: update the README.

**R3-2-F7 -- completeness, medium confidence, original.** Where: the r1 disposition "Convergence" section; plan §8.
- What is wrong: review-convergence.md requires the convergence ledger table as soon as a second round is contemplated, but the disposition gives only prose. §8 also does not say what the stop rule decides after the single confirmation round (for example, whether blocking/total = 0 sends the plan to the owner gate).
- Fix: add the ledger with round-1 values, and state the decision rule in one line.

Stop-rule inputs from this reader: 7 findings, 5 self-inflicted (5/7, above one half), 0 blocking.
