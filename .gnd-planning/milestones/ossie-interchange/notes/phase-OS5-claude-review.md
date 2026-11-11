**Decision: conditional approve.** I found nothing that refutes the candidate's scope, but there are four wording or evidence items to fix or confirm before 854f6671 is treated as closed. I read the diff, the five planning files and the Ossie section of `representation-format.md` (lines 1827–1925). I ran nothing and did not open the refunds model, the OS4 evidence JSON or any rendered output.

## Checked claims

**Scope (holds).**
- The diff touches the explanation, the how-to, one SVG, the README line, the `gnd-export` skill, `zensical.toml` and the 023 record. That matches the spec's four obligation rows.
- It adds no reader or admission code. Nothing names the downstream apps.
- The README adds exactly one entry, and it points at `docs/explanation/ossie.md`.

**Pins and version (holds on the numbers).**
- `0.3.0.dev0`, `ee89dbdc…` and `83ddc294…` all match the normative section (`representation-format.md:1830-1834`).

**Duration (holds).**
- "Counts whole days" is supported by `representation-format.md:1623`, which defines Duration as an integer calendar-day count.
- "Integer on the Ossie side, sidecar keeps the source type" matches line 1841.

**Optional consumer claim (mostly holds).**
- The normative text calls the converter an "optional parser oracle".
- The explanation says PyRel is optional, GND alone is enough, and links `what-is-pyrel.md`. The target file exists.
- "36 of 38" and "no `require` in the converter output" match OS4.
- OS5-C1 also asks for a link to the normative format, and the `!!! info` callout provides it.

**Sidecar instructions (mostly hold).**
- "Keep the sidecar beside the ontology" matches the normative text.
- The three file names follow the `FILE.gnd.json` / `FILE.loss.json` convention.
- The `--strict` behaviour (stop before publication) matches line 1877.
- The skill's relative link to `../gnd-orm-core/references/representation-format.md#ossie-interchange` resolves, and the heading exists.

**Refund relationship (holds).**
- "ManyToOne, at most one requester per refund" matches the normative mapping of an n−1 determinant. Mandatory stays in the sidecar, so "at most one" is correct and "exactly one" would have been wrong.
- The SVG arrow direction (Refund → Customer) is consistent with that.

## Findings

1. **Unverifiable "RelationalAI 1.39.0" (medium).**
   - `ossie.md:110` names this version, but it appears in none of the authorized sources. OS4 only says the observed limits "attach to the converter and SDK versions".
   - Confirm it against the reviewed consumer-limitations record before merge.

2. **Spec requirement only partly met (medium).**
   - The spec requires the explanation to distinguish export validation and consumer declaration comparison from executing formulas.
   - `ossie.md:115-117` says "GND checks formula cases against hand-authored verdicts". That phrase is not in the authorized sources, and a reader could take it to mean the exported `requires` formulas were checked.
   - The page never says outright that no Ossie consumer executed those formulas. I suggest adding one sentence saying so.
   - I also suggest saying that the declaration comparison covers names and identifier edges only. OS4 says it does not check multiplicities, role targets, readings or compound-key grouping, so "matched" overstates it.

3. **Pin wording (low).**
   - The page says the "validator and schema" are pinned to the Ossie commit, and that the "parser and optional converter" are pinned to Converters.
   - The normative text only says "schema" for the first commit and "parser oracle" for the second. "Validator" and "parser … converter" are unsupported by the authorized sources.
   - Align the wording with the normative text.

4. **Limit attribution (low).**
   - The explanation says "the pinned converter" matched 36 of 38. It also lists "inherited identifiers and a derivation chain" as the two limits.
   - OS4 attributes the chain failure to an SDK source-generation assertion, and it never says the two refusals are exactly those two items. OS4 also names a "composition chain" and a "reviewed corpus chain", which makes the count ambiguous.
   - Say "converter and SDK" and confirm that the 2 refusals are the 2 limits named.

5. **Refunds replay gaps (low to medium).**
   - **Record versus how-to:** the 023 record says "four entailment comparisons", but the how-to says "two rules". Four could be two rules in both directions, but neither document says so.
   - **No relationship excerpt:** the how-to asserts `refund_by` is ManyToOne but shows no excerpt of the output. The spec asked for the actual relationship to be verified and shown. The SVG is hand-authored, not taken from the run.
   - **Rerun collides:** the commands are create-once. Repeating them fails with exit 11 (output collision), and the page doesn't say so.
   - **Missing import report:** `restored.orm.json` is also accompanied by an import loss report, which the three-row table omits.
   - **Command prefix:** the commands use bare `gnd`, while the 023 record's checks use `.venv/bin/…`.
   - **Unchecked refunds claims:** "policy about refund amounts", and the refunds model recording "how it was paid", I could not check without opening the model.

6. **Sidecar instructions miss an integrity warning (low).**
   - Import verifies the exact ontology SHA-256 against the sidecar (`representation-format.md:1900`). Reformatting or editing the shared ontology will therefore break restore. The how-to and the skill say only "keep together".
   - The sidecar and loss report also carry GND-specific source details, so sharing them with a partner discloses more than the ontology alone. The page doesn't mention this.

7. **023 verification record may be stale (low).**
   - The quoted focused results ("6 passed, 86 deselected") are not tied to the final tree.
   - The record says the affected-page tests passed "after adding the callouts", but it does not say the strict build and the link check were rerun after that change.
   - The 141-word `grow-a-model.md` paragraph is disclosed honestly, but the full page-policy test still fails.

8. **Links to `main` (informational).** The callouts link to `blob/main/...#ossie-interchange`. Those links won't resolve to the new section until the change is merged, and the local link checker can't catch that.

## Limits of this review

- **Unchecked:** I did not open the refunds model, the OS4 consumer-limitations JSON, the real CLI output or the loss reports. I did not render the site. The "replay exported and imported" results, the digest `5998…` and the 16,441 link count rest on the 023 record alone.
- **Not independent:** every OS4 and OS3 fact above is secondhand from the planning notes. One reviewer is one reviewer.

I can re-review once items 1–3 are fixed and 4–6 are confirmed or edited.
