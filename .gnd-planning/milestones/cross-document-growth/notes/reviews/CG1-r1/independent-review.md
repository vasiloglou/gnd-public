All 15 SHA-256 values in the brief match the files I read.

**Answer to the question.** Through the CLI, I found no way to publish an invalid or stale located append. Through the public `EvolutionService` API, a preview whose recorded verdict is a refusal can be published (F1). The occurrence rule also lets a redundant observation through as new evidence (F2). I found no legal source occurrence that gets lost.

## 1. Findings

**F1 — `src/gnd/evolve/service.py:2397`, `:2414`, and `_recheck_policy` at `:2051-2075`. Reproduced.**
- **What is wrong:** apply recomputes the policy and refuses only if the new run finds issues. It never compares that result with the reviewed preview's own `policy_issues`, and the preview does not record which sample documents were used.
- **Consequence:**
  1. Preview the append without documents. The preview records `policy_issues = ['fact_types.modify']`.
  2. Build a second service with `sample_documents=(doc,)` and call `.apply(preview)`.
  3. The model is published, and the pending state binds that refused preview's `preview_sha256`. The staged evidence therefore says the policy refused an operation that was published.
- **Before this change:** the same apply re-raised the refusal.
- **Scope:** the CLI is protected, because it requires the reviewed preview to equal a fresh one (`cli_service.py:921`).
- **Reproduce:** use `setup_append` from the new test, then `plain.preview(proposal, policy="additive")` followed by `EvolutionService(..., sample_documents=(str(doc),)).apply(preview)`.

**F2 — `src/gnd/evolve/population_check.py:401-404`. Reproduced.**
- **What is wrong:** a source occurrence is compared by the exact bytes of the span. Plan amendment 2 says a repeated identical tuple at the same source occurrence adds no evidence and must be refused.
- **Input:** append `{order: 10, customer: 1}` citing `source.txt` at `"Order 10 was placed by customer 1"`. That is row 0's own sentence, shortened by one character.
- **Observed:** preview exits 0 and apply exits 0. It should be refused as redundant.
- **Control:** the same input at the exact same span is refused (preview exits 3).

**F3 — diagnostics, low. Reproduced.**
- **What is wrong:** `_located_append` and `verified_sample_appends` give no reason when they refuse. Every refusal surfaces as `fact_types[...]: changed outside the admitted keys: provenance.sample_spans, sample_population`. This covers a redundant observation, a value-constraint violation, a bad citation and an undeclared extra document.
- **Consequence:**
  - Passing a valid append plus one extra workspace file that `source.documents` does not declare refuses the legal append (exit 3) with that same unhelpful message.
  - A document outside the workspace is reported as `population file is outside the workspace`. The label comes from reusing the population helper `workspace_relative` at `service.py:1965`.

**F4 — test coverage in `tests/test_cross_document_growth_phase1.py`.**
- The plan amendment and the implementation gate require cases the suite does not have:
  - an included target;
  - a refusal for a redundant identical observation;
  - different excerpts in the same document (tested separately from different documents);
  - the service API path;
  - recovery with `--sample-document`.

## 2. What I checked and found true

- **Focused tests:** `uv run pytest tests/test_cross_document_growth_phase1.py tests/test_evolve_additive_policy.py` gives 93 passed.
- **Inputs I built and ran** (none of these are in the fixtures):

| Input | Result | Correct? |
|---|---|---|
| Identical tuple and span already in the model | Refused | Yes |
| Same new span used twice in one proposal | Refused | Yes |
| Identical tuple at two separate occurrences in one new document | Accepted | Yes |
| Model-level `value` constraint on `order_no` limited to `[10, 11, 12]`, append order 12 | Accepted | Yes |
| Same constraint, append order 99 | Refused | Yes |
| First append to `customer_listed`, a fact with no prior rows | Accepted | Yes |
| Non-unattended model with `--sample-document` | Refused | Yes |
| Document outside the workspace | Exit 74 | Yes |

- **Recovery:** after a successful apply, applying the same preview again exits 0 with the documents, without them, and with a changed document. The model bytes stay unchanged. This follows the existing recovery branch, where the live model already equals the candidate.
- **Included facts:** an element `modify` on an included fact cannot replay, because `_apply_declared_operations` runs over the root document only. I checked this by reading, not by running it.
- **Matchers checked (standing check):**
  - `_located_append` splits prefixes with list slices over parsed structures and compares them with `canonical_json_bytes`. I tried reordered and edited rows and a removed span; all were refused.
  - Excerpts are verified with the existing `unattended_span_issues`, not a new matcher.
  - Paths go through `os.path.abspath` and the existing lexical `workspace_relative`.
  - I found no regular expression or string split over structured text.

## 3. What I could not check

- **Included-target append:** I did not run it end to end; I found no unattended model with includes in the fixtures.
- **Size limits:** I did not exercise the 64-file and combined-byte limits.
- **Object-scoped constraints:** I checked subtype-partition and object-scoped `cardinality` constraints by reading only.

**Scratch files:** I wrote throwaway workspaces under `/private/tmp/cg1rev-scratch`, outside the repository, and the review summary to the plan file. Nothing in the repository was changed.

VERDICT: CHANGES_REQUESTED
