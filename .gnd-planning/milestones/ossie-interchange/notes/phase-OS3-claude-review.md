# OS3 review of a380e9a6: changes requested

I did not run anything. Findings come from reading the diff, the named sources, the spec and the candidate record. The pytest results and the Flights counts in the record are unverified.

## Blocking

**B1. An empty `verbalizes` crashes the foreign path instead of giving a value-free refusal.**
- The ontology schema declares `verbalizes` as an array of non-empty strings with no `minItems`, so `[]` validates.
- `_foreign_fact` (`src/gnd/ossie_import.py`, ≈ line 462) and `_foreign_identifiers` (≈ line 541) both evaluate `relationship["verbalizes"][0]` inside a `try` that only catches `OssieImportError`. An `IndexError` escapes.
- `_cmd_import_ossie` also catches only `OssieImportError`, so the CLI would not return exit 3 with an `ossie-import:*` ID.
- Repro lead (no sidecar):
  ```json
  {"version":"0.3.0.dev0","name":"x","ontology":[{"concept":"Code","type":"ValueType","extends":["String"],"relationships":[{"name":"r","verbalizes":[],"roles":[{"concept":"Code"}]}]}]}
  ```
- `Code` becomes an available value type, so `_foreign_fact` reaches the `[0]` index.
- Fix: treat an empty list as a `reading` refusal, so the fact gets a refused row.
- No test covers this.

**B2. Lossless identity verification depends on an unauthenticated companion.** `expected_identity` is set only when a report is present and has no `refused` row.
- **Report deleted.** Delete `X.loss.json` and edit a sidecar literal. The importer skips the identity check. The output report still carries the original `source_model_identity` beside a model with a different identity.
- **Bogus refused row.** Keep the report and append `{"pointer":"/zz","disposition":"refused","reason":"population:out-of-scope"}`. `_source_dispositions` accepts it, because a non-retained pointer only has to be `refused`, and the identity check is then skipped.
- Fix for the second case: the report schema allows `refused` only with `population:out-of-scope`, so restrict refused pointers to population roots.
- For the first case, always compute the restored identity and record whether it matched.
- `test_lossless_bundle_requires_restored_source_identity` covers only the untampered-report case.
- Spec decision D1 accepts the missing-report path. The silent downgrade is still worth an explicit owner decision.

**B3. The stated work and size bounds have no tests.** Spec §8 asks for work-bound and scaled tests. The suite has none for `reference-budget`, `loss-size`, `model-size`, the pointer `MAX_DEPTH` refusal, `concept-name`, `relationship-name`, `foreign-empty` or `sidecar-header`.
- The budget is also a false-refusal risk. It is `max(2048, 32·(n+edges))`, and the per-concept inherited-identifier walk costs about `n²` on a linear chain.
- A valid inheritance chain of roughly 70 or more concepts, each with `identify_by` on an inherited relationship, should therefore fail with `reference-budget`.
- Repro lead: generate that chain.

## Non-blocking

- **Modality on imported constraints.** Imported constraints are emitted `status: proposed` with `modality: alethic`. `_rule_modality_policy` warns only for induced, llm-inferred and common-sense sources, not imported. D-03 says unconfirmed claims default to deontic. Check whether a proposed alethic constraint gates `check`.
- **Constants and counts.**
  - `_OSSIE_COMMIT` and the artifact path are hard-coded, and the test hard-codes the commit again instead of reading `PINNED.json["commit"]`.
  - The record's 45/48/55/607/146 counts are not asserted. The test only checks `>= 10` constraints and three object names.
- **n-ary multiplicity.** `ManyToOne` on more than two roles becomes uniqueness over all but the last source role. Its meaning for n-ary relationships is unevidenced.
- **Report reasons.**
  - Foreign rows use `foreign:unsupported` and `foreign:decimal-domain`, outside the shipped `gnd-ossie-loss/1` reason enum.
  - The output report is never schema-validated.
  - I could not find a schema for `gnd-ossie-import-loss/1` in the authorized scope.
- **Offline `$ref` to the core schema.** The `ontology_mappings[].semantic_model` reference needs the core `$id` to register on crawl. There is no positive test of that or of `ai_context`. If it fails, it fails closed as `schema`, which refuses a valid document.
- **Stray braces.** Readings with unmatched `{` or `}` may fail whole-model admission as `model` instead of getting a per-fact refused row. I did not verify this.
- **Include refusal.** `load_model_bytes` refuses sidecar-declared includes with `_refuse("unresolved")` and never reads disk. I could not read `_includes.py`, so I could not confirm `_refuse` raises one of the exception types `_bounded_model` catches. Confirm that.

## Claims checked by reading

- **Bounded parsing:**
  - Reads cap at `MAX_BYTES+1`.
  - JSON uses the shared decoder, which gives a depth cap of 64 and refuses duplicates and nonfinite numbers.
  - YAML runs `guard_yaml` (aliases, events, depth) first. `json_document` then refuses non-string keys, dates and non-finite floats.
  - Lone surrogates are caught by the UTF-8 re-encode.
  - Sidecar and report are JSON-only.
- **Network access:** `Registry()` has no retriever, so an unregistered `$ref` raises `Unresolvable`, which is caught. No pattern in the vendored schemas shows ReDoS risk.
- **Graph resolution:**
  - Duplicate names, unknown references and cycles are refused.
  - `resolve` is iterative with a `seen` set, a cache and a shared budget.
  - Topological ordering is linear.
- **Validation order:**
  - Matches spec §4.3: read, parse, schema, graph, sidecar read and parse, header, digest, report, restore, admission.
  - The digest check precedes interpreting any entry.
- **Sidecar pointers:**
  - Pointer tokens are canonical and injective, depth-capped, unique across groups, and every non-root entry needs a parent entry.
  - Literal and copy nodes cannot have children, array indices must be exact `0..n-1`, and `copy` must target a scalar. Every entry is reachable from the root.
  - Output is bounded during serialization, so `copy` fan-out cannot amplify.
- **Provenance and dispositions:**
  - `_walk` emits one row per source pointer, so unprojected nodes default to refused.
  - Constraint provenance satisfies `IMPORTED_PROVENANCE_FIELDS`. The Flights-only gate keys on the byte digest, so altered bytes lose the multiplicity mapping.
  - Foreign loss rows are capped before accumulation.
- **Create-once publication:**
  - `publish_new_files` stages with `O_EXCL` and hard-links with `follow_symlinks=False`, so an existing leaf, including a dangling symlink, gives `FileExistsError` and exit 11.
  - Distinct-target checks use `(dev, ino, name)`, the model is linked last, and earlier links are withdrawn on failure.
  - Input is fully planned before any write.

## Limits

I did not read `_includes.py`, `artifacts.py`, the CLI entry point or `representation-format.md`. I did not check the YAML 1.1 export round trip beyond what the census tests are claimed to cover. I counted the Flights fixture by grep only.

## Decision

Changes requested. Fix B1 and add its test. B2 needs a fix or an explicit owner acceptance of the downgrade. Add B3's bound tests. Then re-review those deltas.
