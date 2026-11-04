# Reader 1 -- correctness against production semantics

Retained text of the reader's returned report, lightly edited for layout.
One review round covered both milestones; this file is cited by the
[composition-and-type-induction round-1 disposition](../../composition-and-type-induction/notes/plan-review-r1-disposition.md).
Scratch paths read `<scratch>`.

**Digest check:** all four snapshots match their stated SHA-256 (MG plan
`32a851f0…`, MG1 spec `d44bf94e…`, CT plan `48430d1a…`, CT1 spec
`51dd6948…`). HEAD `1446f909`.

**Verdict:** request-changes

**Scope.** Read the four snapshots, issue #74, and `model_verbalization.py`,
`api.py`, `evolve/models.py`, `evolve/service.py`, `refscheme.py`,
`extract/service.py`, `extract/vocabulary.py`, `verbalize.py`,
`model/_validation.py`, `schema/orm-meta.schema.json`, `anchors.py`,
`checker/_core.py:1895-2015`, `verbalize_population.py`,
`export/verification_service.py`, `checking_service.py`, `discover/`,
`witness/io.py`, the witness schema, `tools/gnd_layers.json`, the four
`__all__` pins. Probes under `<scratch>/plan-review/reader1/`: `sweep.py`
(MG1 sweep plus the T3 predicate), `sweep2.py` (sweep widened to JSON
models), `api_conv.py` (gnd.api refusal conventions), `sidecar_cap.py`
(sidecar size cap). Not done: test suites; MG2/MG5 fixtures end to end.
Nothing written to the repository.

**What holds.**

- The MG1 sweep reproduces exactly over `*.orm.yaml`: 61 models, 116 rules,
  18 prose rules, 0 aggregate/term/atom fallbacks, 0 exceptions.
- Accurate anchors: `_derivation_cnl` :176; the `_fact_type_cnl` prose branch
  :119-124; `api.__all__` :124 and all four exact pins, including
  `__all__[-1] == "DisclosureRefused"` (`test_why_not_near_misses_public.py:225`);
  `release-notes.md:56`; evolve kinds :219-223; `_enforce_operations_gate`
  :592 and its re-run in apply :1574-1577; `breaking` :1336-1340;
  `ModelIndex` :213/:264/:276; `extract/service.py:137-172`, and
  `_artifact_index_issue` checks only required files, so an extra artifact is
  accepted; `anchors.py:105-139` and the duplicate refusal :133-135;
  `checker/_core.py:1916`; `checking_service.py:222-223`; discover `FAMILIES`
  holds 7.
- Layering holds: `gnd.refscheme`, `model_index`, `model_queries` at `model`;
  `anchors` at `infrastructure`; `model_verbalization` at `checking`.
- Preview checks declared operations equal the canonical candidate
  (`service.py:1319-1320`), so an additive policy over `proposal.operations`
  cannot be fooled by undeclared candidate edits.
- Discover already emits an `induced`/`proposed`/`deontic` envelope
  (`discover/output.py:40-54`), so CT-D8 (a) is plausible.

**Findings.**

**R1-F1 (blocking) -- MG1 spec T3.** T3 says the rendered text runs from
"This fact type is derived: " to the end of the line. False: the line
continues with optional " Admission depends on …", then `reading=…
derivation_rule={json} … canonical=…` (`model_verbalization.py:569-574`), and
passes through `line_text`, which escapes control characters
(`verbalize.py:22-28,125-134`). Reproduced: the literal predicate fails for
all 98 structured rules; a plain substring check passes 98/98. Repair: state
parity as a prefix match of `line_text("[fact-type:{id}] " + prefix + " This
fact type is derived: " + text)`, or compare with `_fact_type_cnl`; decide
whether `text` is `line_text`-escaped; add a control-character constant case.

**R1-F2 (hardening) -- MG1 spec T2 and sweep; plan MG1-C2.** The corpus
misses JSON models (`model.orm.json` under `plan_apps`, `dispatch`,
`release`). "15 example models" contradicts the sweep's own glob (4).
Reproduced: with JSON included, 118 valid models (15 examples), 301 rules, 19
prose; fallbacks still 0. Repair: define the corpus by explicit globs and
record the real floor.

**R1-F3 (hardening) -- MG1 spec Design/D1, standing rule 1; plan §2.1.** The
payload uses `"exit"`; every gnd.api payload uses `"exit_code"`
(`api.py:775,818,862`). Bad argument types raise `TypeError` today rather
than returning 64. Reproduced: `api.validate(5)` raises `TypeError`;
`api.validate(missing)` returns `exit_code: 3`. The `failure(code, kind,
message)` helper is a closure inside `_run_verbalize` (`api.py:817`), not a
shared helper. Repair: `exit_code`; follow the TypeError convention or
justify 64; fix D1's "like every other gnd.api function".

**R1-F4 (hardening) -- MG1 spec unsupported-branch table.** Incomplete:
`_guarded_atom` also falls back to canonical JSON for a non-dict atom
(:166-167); a non-dict `aggregate` is silently dropped (:195); paths under
`/derivation_rule/clauses/N/…` are wrong for root keys (`aggregate`, `where`)
that `iter_derivation_clauses` copies into every clause. Repair: a reason for
each, or the validator rule that makes it unreachable; define the root-key
path mapping. Reachability unproved.

**R1-F5 (blocking) -- MG plan §2.2, MG-R3, MG2-C3.** `preview_sha256` is an
unkeyed canonical hash anyone can recompute (`models.py:817-819`). If
`apply` reads the policy from the preview, a hand edit can delete `policy`,
`policy_issues` and the `populated` set, recompute the hash, and apply
publishes. The operations gate is safe only because it is unconditional.
MG2-C3's "apply refuses a hand-edited preview that drops them" cannot be met
as designed. From code reading; no probe. **Owner:** where apply gets the
policy (an `apply --policy additive` flag, or a policy declared in the
project or model); `populated` also needs a source outside the preview.

**R1-F6 (blocking) -- MG-D2 (a), MG-R1; CT plan §2.4, CT4-C4.** Preview and
proposal versions are tied ("preview and proposal versions must match",
`models.py:~792`); preview and apply refuse anything but
`EVOLUTION_SCHEMA_VERSION` = 3 (`service.py:1263-1267,1557-1561`). A new
preview version makes every policy-free v3 preview unappliable, contradicting
MG-R1's "a preview without the new options keeps the old version"; CT4's
schema-3 proposal cannot yield a v4 policy preview. Repair: specify the
version scheme (optional fields within v3, omitted when unset; or relax both
checks) and update CT4.

**R1-F7 (blocking, Owner) -- MG plan §2.5, MG-D8.** (a) Object types and fact
types have no `source` or `status` (`additionalProperties: false`,
`orm-meta.schema.json` `$defs.object_type`/`fact_type`), so "every object
type, fact type … whose source is explicit, sample or llm-inferred" has no
meaning for them; issue #74 asks for a span on every fact. (b) Today
`explicit`/`user-supplied` ⇒ `status: confirmed` (`_validation.py:884`,
`semantic:status-source`); unattended refuses `confirmed`, so no `explicit`
constraint can be valid there and the span rule for `explicit` is vacuous.
Issue #74 lists only `sample`, `common-sense`, `llm-inferred`. Repair: spans
on all object types and fact types regardless of source; state that
`explicit` is refused in unattended mode, or the owner rules otherwise.

**R1-F8 (completeness) -- MG plan §1, §3.** `orm-meta.schema.json` is at
`src/gnd/schema/`, with a byte-identical twin at
`skills/gnd-orm-core/references/orm-meta.schema.json` pinned by
`tests/test_schema_sync.py`; MG5's home must list the twin.
`reference_identity` is at `src/gnd/refscheme.py:97`; `extract/refscheme.py`
is a 57-line module.

**R1-F9 (blocking) -- CT1 spec standing rule 1, T2, T8.** "10,000 anchors on
one role → parse ok" cannot pass: `MAX_SIDECAR_BYTES` is 1 MiB
(`anchors.py:71-72`). Reproduced: 5,000 compact anchors (977 KB) parse;
7,000 (1.37 MB) and 10,000 (1.96 MB) are refused "sidecar exceeds 1 MiB".
Repair: about 5,000, or decide to raise the cap.

**R1-F10 (hardening) -- CT1 spec `_core.py` design.** "A row fails once even
if several records fail" misdescribes v1: `failed.append` runs once per
failing role (`_core.py:~1980-2005`), so without `role` a row can appear more
than once; deduplicating per row breaks v1 parity. Repair: at most one entry
per (row, role). The lexical index requests a set of occurrences per value
(:1918-1921), not a maximum; only recogniser limits use the maximum. Restate
this and T8's "index request count".

**R1-F11 (hardening) -- CT1 spec T12.** `_excerpts` drops repeated excerpt
text per role (`if value not in bucket`, `verbalize_population.py:133-135`);
two anchors with the same text give one excerpt, so "excerpts listed per
anchor" fails unless code changes, contradicting "no code change is
expected". Repair: "distinct excerpts per role", or plan the change.

**R1-F12 (completeness) -- CT plan §2.2, CT2-C4 vs CT-D4.** §2.2 and CT2-C4
refuse cross-source functional conflicts with exit 3; CT-D4 proposes (b),
compose and let check report. Pick one. CT2's anchored check over composed
facts must use each source fact's pre-renaming value and its own document;
today's checker takes one `document_bytes` (`_core.py:1909`). State this in
the CT2 spec.
