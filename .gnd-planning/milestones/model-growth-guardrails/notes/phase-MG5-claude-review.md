# Phase MG5 diff review (single adversarial reviewer)

Subject: the working-tree diff against `HEAD` (`9e36e70`) plus untracked MG5 files in
`<repo>`,
reviewed against `phase-MG5-spec.md` r1 `(d1)` and plan §0, §2.5 and §4 MG5.

Note on the subject: the tree changed while I was reviewing it. `_validation.py` gained a
`rule_id=` keyword refactor, `representation-format.md` gained the eight-row rule-id table,
and `tests/test_model_validation.py` gained the inventory row. I re-ran every probe below,
and the targeted test selection, against the tree as it stood at about 02:54 local time. All
findings still reproduce there.

## Verdict

**approve-with-fixes.** No blocking finding. Every §2.5 branch is enforced on the right
subject: inline and top-level constraints through `_iter_constraints`, operations and
obligations through `_iter_provenance_bearing` for U2, and subtypes and derived fact types
because they live in `object_types` and `fact_types`. The mode gate holds. Corpus parity
reproduces independently. Every recorded mutant is killed. The fixes below are hardening
and record or documentation corrections. R-F1 to R-F4 should land before the record; the
rest can be carried.

## Findings

### R-F1 (hardening): digest shape accepts a trailing newline (U1 and U7 satisfied by a non-digest)

`_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")` is used with `.match`. In Python, `$` also
matches before a final `\n`, so `"<64 hex>\n"` passes as a declared `documents[].sha256` and
as a span `document_sha256` or `excerpt_sha256`. `gnd.anchors` already uses `[0-9a-f]{64}\Z`
for this reason.

Reproduction: `probes/p2.py` case "trailing-newline e2e". Append `\n` to the declared
document digest and to every occurrence of it in the conforming fixture, then run
`gnd validate m.json --format json`. It exits 0. `probes/p1.py` case
"trailing-newline-doc-sha" shows that object-type spans carrying the `\n` digest pass U7,
while the unchanged spans are flagged as undeclared.

Fix: use `re.fullmatch(r"[0-9a-f]{64}", ...)` or `\Z`, and add a U1 case and a U7 case.

### R-F2 (hardening / record): the induced-provenance schema change moves validation for models without the mode

D3 adds `spans` to the closed `induced` provenance branch, and the branch is not gated on
the mode. As a result, a model with no `source.mode` whose induced constraint carries
`provenance.spans` gives different results:

- at `9b069e2`: exit 3, `jsonschema:additionalProperties ('spans' was unexpected)`
- now: exit 0

The new spans are never checked against declared documents, because U7 runs only in the
mode.

Reproduction: take `tests/fixtures/evolve-policy/base.orm.yaml`, add `spans` to its induced
constraint, save it as JSON, and validate it with both the `9b069e2` archive tree and the
current tree (shared `.venv`, with `PYTHONPATH` pointing at each tree's `src`).

This contradicts two statements:

- `representation-format.md`: "Every other model validates exactly as before."
- the spec's compatibility line: "every model without the mode validates unchanged (MG-R1)".

The release-notes bullet "induced constraints may carry spans" does disclose it. MG-R1 says
a phase that cannot keep byte-identity "lists the exception and stops for an owner ruling".
T4 cannot catch this, because no corpus model carries the key.

Fix, either of:

- Name the exception explicitly in the MG5 record, as the MG-R1 exception ruled under D3,
  and correct the reference sentence to "exactly as before, except that an `induced`
  constraint may now carry `spans`".
- Gate it: keep the schema key and add a non-mode rule. This is probably not worth doing.

### R-F3 (hardening): a `--document` refusal drops the model's warnings, in both JSON and text

`_cmd_validate_documents` builds a fresh `build_validate_payload(..., issues=issues)` with
no `warnings=`. In text mode it prints only the issues.

Reproduction (`probes/p3.py`): an unattended model with a top-level `imported` alethic
`textual` constraint validates at 0 with `warnings: ['semantic:textual-alethic']`. Make one
excerpt digest wrong and add `--document`. The result is exit 3, `warnings: []`, and the
text output carries no WARNING line either.

Fix: pass `warnings=result.payload["warnings"]` (or the projected warnings) into the payload,
and print the warnings in text mode before the issues. Add a JSON/text parity case.

### R-F4 (hardening): a document over 10 MiB is reported as "undeclared" with the digest of a truncated prefix

`_read_validate_documents` reads `MAX_DOCUMENT_BYTES + 1` bytes and hashes that prefix
before `canonical_document_text` can apply its size cap. A declared 10 MiB + 5 B document
therefore exits 3 with:

> unattended:document-undeclared: document sha256 4ea73d… is not declared

The real digest is `fb9399…`, so the message names a digest that is not the file's.

Reproduction: `probes/p2.py` case "big declared".

Fix: when `len(data) > MAX_DOCUMENT_BYTES`, refuse with a named "document exceeds 10 MiB"
issue, or exit 74, before hashing.

### R-F5 (hardening): `sample_spans` accepts rows that are duplicate, negative or out of range, and is ignored where there are no rows

Coverage is checked only one way (`range(n) - covered`). The following are all silently
accepted:

- `{row: 0}` twice
- `{row: -1}`
- `{row: 999}` on a two-row fact type
- `sample_spans` on a fact type with no `sample_population`, even with a malformed span
  `{bogus: 1}` (the function returns early)

Reproduction: `probes/p1.py` cases "sample_spans-dup-and-out-of-range" and
"sample_spans-on-fact-without-rows". Both return `[]`.

Fix: emit U6 for a row outside `0..n-1` and for a duplicate row. Run U7 over every
`sample_spans` entry regardless of row count.

### R-F6 (hardening): malformed spans on `common-sense` constraints escape U7

U5 skips `common-sense`, and U7 runs only inside `_require_spans`. A
`common-sense` constraint carrying `provenance.spans: [{x: 1}]` therefore validates clean.
`--document` does walk these spans, but it silently skips malformed ones.

Reproduction: `probes/p1.py` case "malformed-span-on-common-sense" returns `[]`.

Fix: when `spans` is present on any constraint, run `_span_issue` over it. Spans stay
optional for `common-sense`.

### R-F7 (hardening): `--document` re-hash cost is span count × span length, which T10 does not cover

Each span slices the whole NFC text, encodes it and hashes it. I measured 6.4 ms per
full-length span over a 10 MiB document (200 spans took 1.28 s; `probes/p5.py`). A model
within the 10 MiB input cap can carry about 50k inline spans, which is roughly 5 minutes for
one `gnd validate`. YAML aliases (1M-event cap) can push this further.

The spec's standing rule 2 ("input cap bounds the algorithm") is measured only for
`_rule_unattended`.

Fix, either of:

- Bound the total excerpt length per run and refuse past it with a named issue.
- Memoize the digest by `(document, start, end)`. This defeats the alias amplification.

Add a T10 row for `--document`.

### R-F8 (completeness): `unattended:document-unreadable` is undocumented and its message says "anchor:sidecar-invalid"

A non-UTF-8 declared document exits 3 with the message
`anchor:sidecar-invalid: 'utf-8' codec can't decode byte 0xff in position 0…`. The
`anchor:sidecar-invalid` prefix is borrowed from the anchor sidecar and is misleading here.
The message also carries one document byte value. That is negligible, but it bends the
"never document text" claim.

Neither the reference section, the CLI doc nor T5 covers this rule id.

Reproduction: `probes/p2.py` case "non-utf8 declared".

Fix: write an own message ("document is not strict UTF-8 at byte N") and list the id in
"Unattended source".

### R-F9 (completeness): `--document` exits and outcomes diverge from the spec wording

- The spec Design says `_cmd_validate` "reads each path (66 when missing …), runs validation
  as today, and only when validation exits 0 calls" the re-hash. The code reads documents
  only after validation exits 0. A missing `--document` together with an invalid model
  therefore exits 3, not 66 (`probes/p2.py` "missing doc + invalid model").
- Exits 66 and 74 emit a payload with `"outcome": "internal_error"`, because neither code is
  in `payloads._OUTCOMES`. That is a wrong machine discriminator for a missing or
  unreadable input.
- For comparison, a missing model under `gnd validate` and a missing population under
  `gnd check` both exit 3 with `ill_formed`. The spec's "as other inputs" is therefore not
  what the sibling inputs do.

Fix: rule which order is intended and correct the spec or the code. Either map 66 and 74 to
a real outcome, or record that the `internal_error` label is the existing behaviour for
those exits. I did not check for precedent elsewhere.

### R-F10 (completeness): plan MG5-C1 "the `source` keys of §2.5" is not in the schema

Both copies keep `properties.source: {"type": "object"}`. Neither `mode` (with
`unattended`), `reviewer` nor `documents` is described.

The spec's obligation row for MG5-C1 maps this to "Schema; T1", but no T1 case checks it.
The rules enforce the keys, so behaviour is correct; the gap is in the plan contract.

Fix: add optional, non-required `reviewer` and `documents` property descriptions, with the
existing open `additionalProperties` (parity-neutral). Alternatively, record a ruling that
the keys are rule-enforced only.

### R-F11 (completeness): skipped spans are invisible on a `--document` run

Spans whose declared document was not supplied are skipped. An exit 0 then means "every span
over the documents you gave matched", but nothing reports how many spans went unchecked. A
caller who supplies one of two documents gets an unqualified OK.

This is by design under MG-D9 (re-hash is optional). Suggest a count line in text mode and a
note in the reference.

### R-F12 (completeness): skill text overstates U8

`gnd-model-from-text/SKILL.md` says "Every constraint stays `proposed` and `deontic`". U8
refuses alethic only for `sample`, `llm-inferred`, `common-sense` and `induced`, so an
`imported` alethic constraint validates at 0 (probe in `probes/p3.py`). The reference table
is accurate.

Fix: say "deontic unless `imported`" in the skill, or extend U8. Extending U8 would be a
plan change.

### R-F13 (completeness): test rows with weaker assertions than the spec states

- T2b claims "the exit equals the model's exit without the family". The test asserts only
  that no `semantic:unattended-*` id appears.
- T10 times `_rule_unattended` only (see R-F7).
- T5 does not cover `document-unreadable`.
- There is no case for an empty or whitespace `label`, or for a non-string `reviewer`.
- Standing rule 3 says issues come in rule order "then path order". The code keeps walk
  order (object types, fact types, constraints, sample spans) within a rule. T2f checks rule
  order only. Fix the wording, or sort.
- The spec says `source.txt` has "a combining character". It has precomposed é and è; the
  combining case is covered by the NFD test instead. This is a wording fix.

### R-F14 (completeness): totality of the rule under collection-level hostile shapes

Calling `semantic_validate` directly on an unattended document with `object_types: 5`,
`fact_types: 5`, `constraints: 5`, inline `constraints: 5` or `operations: 5` makes
`_rule_unattended` raise. It becomes `internal:rule-raised`, and so do about 20 pre-existing
rules on the same shape (`probes/p1.py` HOSTILE rows).

This is not reachable through the CLI: layer 1 refuses first, with `jsonschema:type` only,
as I checked with `fact_types[0].constraints: 5`. The T2d shapes the spec names are all
guarded.

Fix (optional): guard with `isinstance(..., list)`, as `_sample_span_issues` already does.

### Process note (not a finding)

During my run, one execution of `probes/p3.py` reported `excerpt-mismatch` on every span of
an otherwise-matching model. On re-run the result was correct and did not reproduce. The
timing fits an in-place mutant (M2, byte offsets) being applied to the shared tree while I
probed.

Separately, when I re-ran the recorded mutants in a scratch copy, M4 first "survived". The
cause was a stale `.pyc`: M3 and M4 each shorten the file by 8 characters within the same
second, so mtime plus size did not invalidate the bytecode. With `PYTHONDONTWRITEBYTECODE=1`
and a cleared `__pycache__`, all eight are killed. If the phase's own mutant evidence was
produced by rewriting files in place in quick succession, re-run it with bytecode writing
disabled.

## What I ran

- `uv run pytest -q tests/test_unattended_mode.py tests/test_schema_sync.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_induced_provenance.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_rf1_pin_harness.py`: 609 passed.
- After the tree changed, `tests/test_unattended_mode.py tests/test_model_validation.py tests/test_schema_sync.py tests/test_rf1_pin_harness.py tests/test_rf1_cli_pins.py`: 304 passed.
- An independent T4 parity check. I ran `git archive 9b069e2` into a temp dir, then ran the
  evidence `capture_parity.py` there with `PYTHONPATH` set to that tree's `src`, and again on
  the current tree.
  - Before: 322 models; after: 323 (the new fixture). Zero digest differences on the shared
    322.
  - Both runs match `evidence/MG5/parity-{before,after}.json` byte-for-byte as dicts.
- The eight recorded mutants (`evidence/MG5/mutants.json`), plus two of my own (U3 removed,
  out-of-range check removed), in an rsync copy of the tree with bytecode disabled. All ten
  were killed.
- Probes `probes/p1.py` to `probes/p5.py` (paths below). They cover the rule branches and
  the vacuity attempts: uppercase hex, float or bool offsets, huge offsets, duplicate or
  out-of-range rows, reused spans, mode-casing, top-level constraints, rejected_proposals,
  operations, hostile shapes. They also cover the `--document` behaviours: matching,
  mismatch, out of range, directory (74), missing (66), invalid model with missing document
  (3), non-UTF-8 declared (3), over 10 MiB declared, the same document twice, the same bytes
  under two paths (0), the JSON payload shape against a normal exit-3 payload, text versus
  JSON output, and the cost measurement.
- Read the docs diff: `cli.md`, release notes, `representation-format.md` "Unattended
  source", and the skill's Unattended mode.

## What I did not run

- `tools/run_tutorials.py`, `zensical build --strict` and `tools/check_docs.py site`.
- The anonymity scan (T8).
- Broad test lanes.
- `tests/test_conformance_payload.py`, `tests/test_public_api.py`, `tests/test_rf3_core.py`
  and `tests/test_rf4_peripheral.py`.
- The corpus `source.mode` re-count (I did not re-measure the 349, 271 or 163 numbers).
- A full-CLI timing of 2,000 × 50 rows.
- Precedent for `internal_error` at exit 66 or 74 in other validate paths.

Probe sources are in
`<scratch>/review-mg5/probes/`
(`p1.py` rule probes, `p2.py` `--document` CLI, `p3.py` warnings and imported alethic,
`p4.py` model_dump check, `p5.py` cost, `mutants.py` mutant runner). They wrote only to
system temp dirs.
