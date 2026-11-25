# Close review: dispositions

Light panel, effort high, 2026-11-25, run sha256
`11fdf71260e1313d53f6c40c43c594ce5a853db2574a7db9ed8b6573019afc93`
([report](PANEL-REVIEW.md), [synthesis](synthesis.json)). Five of six seats
succeeded; the Kimi seat failed because its provider refused the request for
quota. All five asked for revision. Effort high was bound per run for Claude
and Codex only. The panel is advisory.

Each concern was checked against the bytes before it was believed. Class is
assigned here, not by the reviewer.

| Concern (seats) | Reproduced | Class | Disposition |
|---|---|---|---|
| `binding:name-collision` upper-cases every name (codex, claude, glm) | yes: a binding with `fin.cust` and `FIN.CUST` was refused; the pinned validator accepts two such datasets | blocking (a legal binding refused, against A14) | **fixed**: the check compares Ossie's normalized form; `test_close_names_collide_by_ossies_normalized_form`; the comment and the normative sentence updated |
| Predicate 2 denies a second new default failure (claude) | yes: OB3's T8 shows `ossie:output-size` on a default run that fits under `--ontology-only` | blocking (a false predicate and a release note that omits it) | **fixed**: plan A17; results predicate 2; release note |
| Names are unquoted in the semantic model (gemini) | **no**. A dataset or field `name` is a declared name and is written as given; only a reference in an expression is quoted. The pinned validator accepts the files of a binding with a space, a dot and a hyphen in its names (`test_external_irregular_binding_names`, passed at `7a6ccfe9`). Quoting the declared name would make the validator keep the quotes as part of the name. | not a defect | **rejected** |
| A14 cites plan §2.2 for wording that is not there (claude, gemini, glm, qwen) | yes | completeness | **fixed**: A14 now quotes the OB3 normative sentence and says the plan stated none |
| Dispositions not final or without an owner (claude, gemini, qwen) | yes | completeness | **fixed**: every row is closed, carried with an owner, or an accepted residual; OB5-Q1 is stated once, as ruled by the owner |
| One home names one section; no falsifying evidence (glm, qwen) | yes | hardening | **fixed**: plan A18; results predicate 6 names the tests and states the boundary (prose restatement is checked by review only) |
| The guard block's failure is called pre-existing without evidence (qwen) | yes, the evidence was not cited | completeness | **fixed**: record `004`'s proof and an empty `git diff --stat` over the test and the files it reads |
| A8's note reads like a fourth output (qwen) | yes | completeness | **fixed**: one line on standard error, not a file |
| The scale test's size is unrecorded (qwen) | yes | completeness | **fixed**: A6 and predicate 3 give the sizes |
| The close lane omits consumers §9 names (qwen) | yes, as labelled | completeness | **fixed**: the lane is named for what it runs; the other consumers run in the guard block |
| The no-review list omits the relational renderer (qwen) | no: the OB5 review read it after the quoting fix | not a defect at the time | **answered** in the results; the file changed again after this review and is listed there |
| D5's ruling and measurement are absent (qwen) | yes | completeness | **fixed**: predicate 3 cites the gate and the measurement note |
| `--max-input-bytes` listed as beyond the plan (glm) | yes | completeness | **fixed** in the delta |
| The oracle lane ran at another commit (qwen) | yes, equality was only asserted | completeness | **fixed**: the diff command is given. The lane was re-run on the final code at `98344052` on the owner's request: 91 passed |
| D11 closed on a proxy ratio (qwen) | yes | hardening | **fixed**: the two measurements are stated apart; D11 stays open to the reporter's answer |
| OB5-Q1 "proposed" but listed as accepted (qwen) | yes | completeness | **fixed** with the dispositions row above |
| The release-note section has no evidence row (qwen) | yes | completeness | **fixed**: predicate 6 names its test |

**Repaired bytes carry no review opinion.** Plan r3 with its `(c2)` rows, the
results, the delta, `src/gnd/export/physical_binding.py`,
`src/gnd/export/ossie_relational.py`, the normative section and the release
note changed after the panel read them. No second panel round has run.
