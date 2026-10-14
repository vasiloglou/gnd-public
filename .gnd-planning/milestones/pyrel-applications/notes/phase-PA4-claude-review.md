# Claude Code PA4 review

Edited header; repository absolute paths sanitized to <repo>. Remaining reviewer prose retained. Initial reviewer disclosed accidental no-op Python invocation; no project/native tests or providers executed. Reading bounds are explicit. One reviewer is one reviewer.

# Independent PA4 review: native expense reports and approvals

I didn't find anything that could publish a bad candidate or produce a false successful report. I found two medium gaps, one on test coverage and one on a duplicated policy rule. The rest is low severity: wording, output shape, test coverage and evidence hygiene.

**Process disclosure:** I accidentally ran `python3 -c 1`, a no-op, at the front of one grep. Apart from that I only read files, searched, and ran read-only git commands. I ran no tests, native tools, providers or agents, and read no `.env` or credential files. Plan mode asked for a plan file, but no write tool was available, so this review exists only in this message.

## Findings

**F1 (Medium): the native guards stop three cases before the framework checker ever sees them.**
- The guards in `native_query.py:47-63` refuse before the checker runs, so `policy` is `None`.
- Only two rules are reached by faults introduced after the proposal:
  - `approval_limit_team_lead`
  - `approval_needs_submission`
- Three cases never reach the checker in any native test:
  - **`currency-usd`:** the `supported_currency` rule (`currency.orm.json:598-603`) is never evaluated.
  - **`missing-submitter`:** the source itself is invalid, because 101 has an amount and category but no submitter. The test approves 101, so the `unknown-expense` guard hides that. The case that would tell them apart is approving **102** on the same source: it should refuse with exit 1 and the mandatory-submission witness 101. That case isn't tested.
  - **Duplicate approval:** the uniqueness rule `one_expense_is_approved` is never reached after the proposal.
- PA-R5 says a proposer that filters bad cases doesn't show the checker catches them, and spec lines 93-95 say the same.
- **Repair (tests only, no production change):** use `candidate_transform` to:
  - set a currency to USD while approving 102 under the currency model, and expect `supported_currency` violated;
  - append a second approval of 103, and expect `one_expense_is_approved` violated.
  
  Also add the 102-on-missing-submitter sibling. Take the rule IDs from the model file rather than guessing them.

**F2 (Medium-low): the currency guard hard-codes the policy value.**
- `native_query.py:52` compares against the literal `'EUR'`, which duplicates `supported_currency.allowed` in the model.
- The successor reason in `query-successor.json` says "no policy duplication", which overclaims.
- Consequence: if a later evolved model allowed another currency, the guard would still refuse with `unsupported-currency` while the model accepts.
- **Repair:** read the allowed list from the admitted model's `supported_currency` constraint, or keep the literal but disclose it as an application guard and correct the reason text.

**F3 (Low-medium): I partly dispute "the tests incorrectly expected exit 1".**
- `pyrel_runtime.py:1620-1621` returns `vacuous` for a mandatory constraint whenever its fact type is empty, even though the expense set {101, 102, 103} isn't empty.
- In plain ORM terms, deleting every currency fact means all three expenses break a mandatory rule, so the old exit-1 expectation was defensible. Exit 2 is the profile's own convention.
- That convention is fail-closed and comes from earlier phases, so PA4 is right not to change it. It needs an owner decision, not a quiet relabel.
- The spec doesn't record the 20 pass / 2 fail revision yet.
- The native tests never use the shipped `currency-missing.population.json` (101 and 102 missing), which is the fixture PA5's missing-currency graphic needs.
- **Repair:** add a native control on that shipped fixture expecting witnesses `[[101],[102]]`, and record the revision in the completion record.

**F4 (Low): a successful approval prints the pre-approval numbers.**
- `extension.py:68` keeps `calculation` for an accepted approval. That calculation was computed on the source, so approving 101 prints `approved: 1` and `approved_expenses: [[103]]`, while the published file contains two approvals.
- **Repair:** drop `calculation` for approvals too, or label it as the pre-approval state.

**F5 (Low): a successful report can't be tied to the input file.**
- `policy.binding.population_sha256` is the hash of the re-serialised private snapshot (`applications.py:210,234`), not the user's input bytes.
- The proposal's `input_sha256` is thrown away.
- PA4-C5 needs source hashes for the figures.
- **Repair:** have the shared parent also return `{model_sha256, input_sha256}`. That's generic, not a business rule.

**F6 (Low): missing controls.**
- The `allowed_guard_kinds` validation (`applications.py:152-156`) has no test: duplicates, uppercase, more than 16, a non-tuple.
- No guard test covers a reason over 300 characters or a non-string reason.
- No test pins "child exits 1 but leaves a valid guard file → 70". Line ordering covers it in the code, but no test locks it in.
- The chain-limit, unknown-chain, meal-cap and category refusals only check exit 1; none checks which rule fired. Expected IDs:
  - unknown-chain → `known_chains`
  - meal-cap → `policy_meals`
  - category → `known_categories`
  - chain-limit → `approval_limit_team_lead`, already asserted by the post-proposal test
- Spec line 94 names a nonpositive-amount sibling (`positive_amount`), but no test exists for it.

**F7 (Low): "membership is native" is slightly overstated.**
- The unknown and duplicate decisions are Python `[expense] in submitted` checks over rows the native query returned (`native_query.py:58-63`). BookRec does the same.
- It behaves the same as a native check, but either reword the claim or bind the literal in the native query.

**F8 (Low): evidence hygiene.**
- `native-initial.txt` has 4 unsanitised operator-path and username occurrences. The other PA4 receipts are sanitised with raw digests, as in PA3.
- `native-measured.txt` showed only 11 dots on my first read and "23 passed in 74.92s" on a later read. It is untracked and has no hash, so I don't credit it as matching the current source.

**F9 (Note):** the query's `except ValueError` maps any ValueError raised inside the SDK to exit 3 (malformed input). BookRec has the same pattern, which PA3 accepted.

## Claims I checked and confirmed

- **Guard envelope:**
  - It is only read when the child exits 0 (`applications.py:185` runs before `:189`).
  - The parent checks:
    - exact keys and exact model/input binding;
    - `exit_code` is an integer 1;
    - the kind is in the caller's validated list;
    - the reason is 1–300 characters;
    - no candidate or calculation is attached.
  - It then returns with `policy=None`, before the checker or publication.
  - No business predicate is in the parent. The default `()` leaves the BookRec CLI unchanged.
- **Exit codes:** a query process exiting 1 still becomes 70. `ProfileRefusal` isn't a ValueError, so it gives 2. `ExportInputError` is a ValueError, so it gives 3.
- **Normal proposals** still go through the PA3 path unchanged: fresh checker directory, `verify_policy_report`, source-stability recheck, no-clobber atomic publish.
- **Ownership:** approval owns exactly the two relations and report owns none; `_preserve_source` enforces exact multiset equality for everything else.
- **CLI output:** a report sets `published=false` only when accepted. `calculation` is removed for reports and for every failure, and `report` is only present on acceptance.
- **Arithmetic:** the sum is over (expense, amount), so the repeated-amounts case gives 180 rather than 60. The count uses `count(distinct(e))`. Currency totals use `.per(c)`, and the non-EUR guard runs before any totals. Python only maps empty native rows to zero.
- **Missing-relation crash, refuted:** I suspected `.append` could crash if a relation were absent. It can't, because `_profile_admit` (`pyrel_runtime.py:1374-1375`) requires every fact type to be listed and covered and refuses with 2 first.
- **Default backend:** the `gnd` path is untouched.
- **Budgets:** query plus wrapper ≈129/300, tests ≈240/400, parent 244/600. The successor counts 362 and 307 match the receipt.
- **Feasibility probe:** it used `count(e)`, not the production `count(distinct(e))`, so the production form is only covered by the native runs.

## Refactoring review

- **Dead code:** the `rows` wrapper at `native_query.py:37-41` repeats the limit that `ApplicationOracle._rows` (`pyrel_runtime.py:1543-1547`) already enforces. The oracle raises first, so the message "expense query result limit" can never appear. BookRec has the same wrapper. Remove it in both or keep it in both.
- **Shared setup, not extracted:** about 30 lines of setup are duplicated between the BookRec and expense queries:
  - loading the runtime and the byte cap
  - parse and admit
  - the version pin and oracle construction
  - the binding and envelope write
  - the `main` exception mapping

  I don't recommend extracting them now. Doing so needs a GND import (forbidden), a runtime change (frozen) or a copied helper file (extra packaging and tutorial-copy work). Log it as a future item.
- **Optional readability tidy-ups:**
  - Move the guard checks into a small `_guard_refusal(envelope, allowed)` helper.
  - Only create the temporary directory in `extension.py:53` for `report`.

## Reading limits

- **Plan:** I read §0, PA4 and the risk table, not the whole document.
- **Other planning records:** I read all of A1, lines 160-257 of the PA3 record and the full PA4 spec.
- **Skimmed only:** the publication test helpers and the red receipts.
- **Not read:** the tutorial tests and the README beyond a grep.
- I couldn't tie any untracked evidence file to the current source bytes.

## Recommended single bounded repair

1. F1: add the three tests.
2. F2: read the currency list from the model, or disclose the literal.
3. F3: add the shipped-fixture control and record the revision.
4. F4 and F5: small output changes.
5. F6: add the missing controls.

All of this fits the existing line budgets and needs no runtime change.
