# Phase MG4 diff review (single adversarial reviewer)

Subject: working tree on `claude/process-milestone-model-growth-4cac43` over HEAD `41be029` (MG3):
`src/gnd/extract/guidelines.py` (new), `src/gnd/extract/service.py`, `src/gnd/commands/extract.py`,
`tests/test_extract_guidelines.py`, `evidence/MG4/*`, gnd-extract SKILL.md and extraction-contract §4a,
`docs/guides/documents.md`, `docs/reference/cli.md`, `docs/release-notes.md`, `tools/gnd_layers.json`.
RF1 goldens ignored as instructed. The repository was not modified; probes live beside this file and wrote only to temp dirs.

## Verdict: approve-with-fixes

No blocking finding. The core properties hold under adversarial probing: no constraint other than an
anchoring external uniqueness changes guideline bytes (corpus-wide), no model string forges a line,
output is deterministic, flag-free bundles are byte-identical to `9b069e2` (independently re-captured),
and the fifth file does not disturb any index consumer. The findings are test gaps that let a real
regression through (R-F2, R-F3), one stale-file hazard (R-F1), one over-broad doc claim (R-F4), and hardening.

## Findings

### R-F1 (hardening): a stale guideline survives a flag-free re-extract, and the skill would read it

Re-running `gnd extract` without `--guidelines` into a directory that already holds a guideline leaves
the old `<stem>.guidelines.md` in place. The new index no longer lists it. SKILL.md rule 4 says to read
`<stem>.guidelines.md` "when the bundle has one", so an extractor can read guidance written for an
older model that nothing binds any more.

```
T=$(mktemp -d)
uv run gnd extract tests/fixtures/evolve-policy/base.orm.yaml --out $T/b --guidelines   # exit 0
uv run gnd extract tests/fixtures/evolve-policy/base.orm.yaml --out $T/b                # exit 0
ls $T/b   -> base.applicable.json base.artifacts.json base.guidelines.md base.projection.schema.json base.verbalization.txt
index artifacts -> ['base.applicable.json', 'base.projection.schema.json', 'base.verbalization.txt']
```

Fix: in SKILL.md rule 4, the bundle table and contract §4a, say to read the guideline only when
`<stem>.artifacts.json` lists it, and to check its SHA-256 against the index before reading. This is
documentation only, so MG-R1 holds. Deleting the stale file during a flag-free extract would also work,
but it is a new filesystem effect on the flag-free path and needs an owner decision.

### R-F2 (completeness): T3 never checks a non-anchoring external uniqueness, and a mutant that prints one survives

Spec D2 and the T3 row say the injection uses a non-anchoring external uniqueness.
`_strip_constraints` keeps every external uniqueness, anchoring or not, so the test cannot see a
renderer that reads non-anchoring ones. Mutant X2 adds a line per top-level external uniqueness in
`_role_lines`. It survives T3, and every other recorded mutant is killed:

```
uv run python review-mg4/run_mutants.py
M1..M6 KILLED
X1-identity-from-inline-uc KILLED
X2-print-nonanchoring-external-uc SURVIVED 4 passed
```

The code itself is correct. Appending a non-anchoring external uniqueness to BASE leaves the bytes
unchanged (`probe_adv.py` §2: `nonanchor_external_uc unchanged`). A corpus-wide strip that keeps only
anchoring uniqueness constraints also leaves all 172 strippable accepted models unchanged
(`probe_corpus.py`: `blind_bad []`; 1 non-anchoring UC exists in the corpus).

Fix: in `_strip_constraints`, keep an external uniqueness only when `refscheme._anchors_on(role_refs, oid, model)`
holds for some object type, or add an explicit case that appends a non-anchoring external uniqueness to BASE
and asserts the bytes are unchanged.

### R-F3 (completeness): the T6 verify case is vacuous, and fidelity and doccheck are never run end to end

`test_t6_verify_with_artifacts_exits_alike` runs `gnd verify` against a population that does not
exist. That exits 3 on the missing sidecar before the bundle is opened, and a bundle directory that
does not exist produces the same exit:

```
uv run gnd verify tests/fixtures/evolve-policy/base.orm.yaml $T/missing.population.json --artifacts $T/g            -> exit 3 (extraction:sidecar-missing)
uv run gnd verify tests/fixtures/evolve-policy/base.orm.yaml $T/missing.population.json --artifacts $T/nonexistent  -> exit 3 (same message)
```

`gnd fidelity` and `gnd doccheck` are covered only by calling `_artifact_index_issue` directly. That
call is the shared helper, which is reasonable partial coverage, but the spec's T6 row names the
commands. An end-to-end probe over the committed roundtrip case shows the fifth file is harmless:

```
M=tests/fixtures/checker/setfam.orm.yaml; plain bundle vs --guidelines bundle
fidelity (cases=roundtrip/faithful) exit 0 / 0, JSON payloads equal, cases ran=1
doccheck roundtrip/faithful/document.manifest.json  exit 0 / 0
verify   roundtrip/faithful/extracted.population.json  exit 3 / 3 (header-mismatch, reached after the index check)
```

Fix: replace the missing-population case with the roundtrip `faithful` case (the
`tests/test_fidelity_stub_gate.py` pattern) and run all three commands against both bundles.

### R-F4 (completeness, docs): contract §4a says any constraint change leaves the bytes unchanged

Contract §4a: "No constraint is read except the external uniqueness that **is** an entity's composite
reference scheme ... so adding, removing or changing a constraint leaves the file's bytes unchanged."
The conclusion contradicts its own exception, and D2 accepts that exception. Adding one anchoring
external uniqueness changes two lines (`probe_anchor.py`):

```
-- Identified by: no printable reference value
+- Identified by: a combination of roles (composite reference)
```

(The probe uses an entity subtype with `inherits_reference: false`. A `reference.mode: external` entity
without an anchoring UC is refused by `load_model`, so the change shows up on subtypes.)

Fix: "... so adding, removing or changing any other constraint leaves the file's bytes unchanged."

### R-F5 (hardening): raw HTML in a model string becomes a heading when the file is rendered as Markdown

The line structure holds: control characters, CR/LF, U+2028/2029, U+0085, quotes and backslashes are
all escaped, and the structure parse finds exactly one `##`/`###` per fact type and role
(`probe_adv.py` §1). Markdown metacharacters, however, pass through. A description summary of
`<h2>Fact type <code>evil</code></h2>`, rendered with Python-Markdown (the docs toolchain library),
produces 4 `<h2>` elements for 3 fact types (`probe_html.py`). Inline backticks inside a quoted name
also render as code, and U+202E (bidi override) passes through unchanged. An agent that reads the raw
file is not affected. The contract's sentence "no description, reading or name can start a heading" is
true of the text but not of a rendered view.

Fix: escape `<`, `>` and `&` (and optionally backticks) inside `_quoted`, or state in §4a that the file
is plain text and must not be rendered.

### R-F6 (hardening, performance): T12 measures only value-type players; the entity path grows with constraints

T12 renders 5,000 fact types whose role players are all value types, so `entity_reference` never runs.
With entity players, each role calls `entity_reference`, and `reference_identity` scans
`model.constraints` and rebuilds lookup maps on every call (`probe_perf.py`, `Model.model_validate`
models, entities with `reference.mode: external`):

```
N=2000 fact types, 2000 entities, 0 UCs:   guidelines 1.07s  (verbalization 1.52s)
N=5000, 5000 entities, 0 UCs:              guidelines 4.75s  (verbalization 7.93s)
N=5000, 5000 entities, 50 external UCs:    guidelines 56.55s (verbalization 56.49s)
N=5000, 1000 entities, 200 external UCs:   guidelines 205.37s (verbalization 40.36s)
```

The per-call cost comes from the shared refscheme helper, which the existing verbalization artifact
also pays. The guideline, however, calls it once per role rather than once per object type. When an
entity plays several roles, the guideline is therefore several times slower than the existing
artifact: 5x in the last row, where each entity plays 5 roles. Spec standing rule 2 ("one pass") is
not true of the entity path.

Fix: memoize `entity_reference` per object type inside `render_guidelines`, since an object type
repeats across roles, and add an entity-player variant to T12.

### R-F7 (completeness): T7's sample-row non-leak has no case

T3b checks four value-constraint literals on BASE. Nothing checks a `sample_population` value. BASE's
sample channel `web` is also an allowed literal and is not checked. A probe with unique tokens finds no
leak (`probe_adv.py` §3: `sample leak False`).

Fix: add a case that sets `sample_population` to unique tokens and asserts none of them appear.

### R-F8 (completeness, nit): parts of the T4 case are unreachable or brittle

- A role name with a backtick can never load, because `identifier` is `^[a-z][a-z0-9_]*$`, so the
  bare `except Exception` fallback always runs. The `_code` path is covered by T4b instead. The bare
  except would also hide a render error.
- U+2028 is written into the test source as a raw, invisible character (lines 196, 198, 200 and 205).

Fix: catch `ModelValidationError` only (or drop that branch), and write U+2028 as the `" "` escape.

### R-F9 (docs, nit): small statements that disagree with the code

- Contract §4a and `documents.md` say the guideline repeats descriptions "verbatim". They are escaped
  (`\'`, `\\`, `\n`).
- The SKILL.md bundle table still describes `<stem>.artifacts.json` as holding "sha256 digests of the
  three files above". With `--guidelines` it holds four.
- In contract §4a, `` `## Fact type `ID`` `` and `` `### Role `NAME`` `` nest backticks inside
  single-backtick code, which renders broken. Use double-backtick delimiters.

## Hunted and found sound (reproduced)

- **Constraint blindness.** A corpus-wide strip keeps only anchoring external uniqueness constraints.
  All 172 strippable accepted models render identically to the original (5 reference-corpus models
  could not be re-loaded from a temp path because of their relative reference descriptors). The
  constraint families covered include value, frequency, ring, guarded, anchored, textual, inline and
  top-level. Inline uniqueness cannot affect identity: mutant X1 is killed, and `reference_identity`
  reads only top-level external uniqueness constraints.
- **Totality.** `render_guidelines` raises on none of the 177 models that `gnd extract` accepts. A
  model that extract refuses is refused before the guideline is rendered (T6b, plus code order).
- **Structure.** Heading counts equal the fact-type and role counts on all 177 models. The forgery
  probe covers name, description and inverse reading with U+2028, U+0085, CRLF, quotes, backslash,
  `<!--` and U+202E. `splitlines` and `split("\n")` agree.
- **Determinism.** The guideline digest is identical under `PYTHONHASHSEED=0` and `12345`, and two
  renders per model agree.
- **MG-R1.** I re-captured `parity-before.json` from a `git archive 9b069e2` tree with
  `PYTHONPATH=<archive>/src`, and `parity-after.json` from the working tree. Both are byte-identical to
  the committed evidence (238 models; exits 0:177, 3:61).
- **Same role players.** Multiple buckets are correct, and role order does not matter: `order_has_channel`
  and `channel_of_order` list each other. A fact type with a unique signature prints no line.
- **Layering and RF6.** `gnd.extract.guidelines` is mapped `extract`/`lanes`. It reads the model only
  through `ModelIndex` plus `entity_reference`, the spec'd identity home. The dynamic-query successor
  adds syntax census entries only, and the RF6 and layering tests pass.
- **Anonymity.** No downstream-app names in the diff, the new files or the evidence.

## What I ran

- `uv run pytest -q tests/test_extract_guidelines.py`: 20 passed.
- The spec's §9 gate list plus the impact closure (test_rf1_pin_harness, test_disclosure_docs,
  test_skill_prose_sync, test_packaged_skills, and the 18 gate files): 486 passed.
- Probes, all beside this file:
  - `probe_corpus.py`: totality, structure and corpus blindness.
  - `probe_adv.py`: forgery, non-anchoring UC injection and the sample leak.
  - `probe_html.py`: rendered Markdown.
  - `probe_anchor.py`: the D2 byte change and multi-bucket Same role players.
  - `probe_perf.py`: scaling.
  - `run_mutants.py`: recorded mutants M1 to M6 plus X1 and X2, each in a temp copy of `src` via `PYTHONPATH`.
- Parity re-capture at `9b069e2` and at the working tree.
- CLI probes: stale file; verify, fidelity and doccheck over plain and flagged bundles; PYTHONHASHSEED.

## Not run

- `tests/test_conformance_payload.py`, `tests/test_rf3_core.py`, `tests/test_rf4_peripheral.py`, and the MG3 gate.
- T9 docs tooling: `tools/run_tutorials.py`, `zensical build --strict` and `tools/check_docs.py site`.
- Broad lanes.
- T5b codegen digests beyond `tests/test_public_legacy_codegen_pins.py` and `tests/test_fidelity_stub_gate.py`, which are in the gate run.
