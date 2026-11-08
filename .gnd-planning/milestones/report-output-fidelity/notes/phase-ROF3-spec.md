# Phase ROF3: canonical model identity and its producer (issue 111)

## 1. Status

**Approved (2026-11-08); implementing.** The owner approved the corpus and
spec r2 with "Approve, implement", answering "Approve the ROF3 corpus and spec
r2, so implementation can start?". D1-D7 were ruled as proposed with
"Approve, author corpus". Prior statuses: "r2: corpus authored (2026-11-08);
awaiting owner approval to implement."; "r1 decisions ruled (2026-11-08); corpus
being authored."; "Draft r1. Awaiting owner review at the
spec gate." `auto=false`.

## 2. Provenance

- Plan r3 (approved 2026-11-07, [plan-gate record](../001-plan.md)): §1 (the
  111 probes and the digest census), §2 "Issue 111, identity" and
  "compatibility and migration" items 1-10, §4 ROF3 (C1-C4), §6 risks, §9 ROF3
  row, §10 D3 (no emission, ruled), D4 (identity version 2, ruled and narrowed
  by review P2), D5 (producer surface deferred to this spec, ruled), D7
  (generated plans keep the legacy constant, ruled (a)).
- The owner's go-ahead for this spec: "go ahead" (2026-11-08), answering
  "ROF3 (issue 111) waits for your go-ahead to write its spec".
- Base: branch `claude/rof3-canonical-identity` at `a2b79084` (ROF2's head,
  stacked on PR 127 and PR 124). ROF3 touches none of ROF1/ROF2's code; the
  112 and 111 chains are independent (plan §3).
- Census evidence: [evidence/census-r2/](../evidence/census-r2/). No review
  has read these bytes. Marks: `(o)` an owner decision.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan ROF3-C1 | `model_identity(model, version)` and the canonical document, defined in the normative home; an independent re-implementation in the test file yields the same digest on every tracked loadable model | M1, M3; T1, T2 |
| plan ROF3-C2 | hostile input: a non-string key refused, not coerced; an unrepresentable value refused; deep nesting; the empty case (`reference_populations` absent and `[]`) | M1 refusal; T4-T7 |
| plan ROF3-C3 | time-bound test of the new function near the input cap; legacy `_model_digest` unchanged byte for byte | T8 (experiment recorded first); T3 (D5) |
| plan ROF3-C4 | the producer prints the document and the digest; a subprocess test recomputes the digest with `hashlib` only | M2; T9 |
| plan §2 identity | version 2 = `sha256(canonical_json_bytes({"identity_version": 2, "model": canonical(model_dump excluding warnings, operations, reference_populations)}))`, defined **only** for a model without `reference_populations`; a reference-bearing model keeps version 1 and has no version 2 | M1; T2, T10 |
| plan §2 identity | an operations-only mutation of a reference-bearing model moves version 1; version 2 is refused for it | T10 |
| plan §2 normative home | a new subsection of `representation-format.md` beside "What `population._model_digest` covers (A8)" states the empty case, key order, number and date handling and the refusal | M3; T11 (doc pins) |
| plan §2 item 7 | in-process markers keep the legacy function; the new function's cost is measured before any caller adopts it | out of scope for callers (ROF4); T8 |
| plan §2 item 10 | the canonical walk is not total; its refusal must be a typed refusal a verifier can tell from a mismatch | M1 `ModelIdentityError`; T5, T6 |
| plan rule 1 (frozen) | no report, schema, `--format json` payload or `validate --trace` byte changes; legacy digest unchanged | T3, T12 |
| plan rule 3 (one home) | one implementation in `values.py`; one normative home; consumers call it | M1, M3; T13 |
| plan §6 risks | version 2 weakens a reference-bearing binding; the canonical walk refuses a model legacy accepts; cost; two normative homes | T10; T5-T6; T8; M3 + T11 |
| plan §9 ROF3 row | new ROF3 tests + `tests/test_model_v2.py tests/test_reference_population_corpus.py tests/test_rf1_helper_pins.py` | V2 |
| plan §5 | the `gnd-orm-core` skill reference changes, so the packaged-skill twin and sync guards run | V2 |
| project.md failure class | "an interchange field defined in Python-only terms": canonical JSON, a stated empty case, a shipped producer; non-string keys refused, not coerced; no second re-implementation of the canonical helper | M1-M3; D3 |
| D7 (ruled (a)) | generated Pyrel plans keep the legacy `MODEL_DIGEST`; not touched here | out of scope (ROF4 documents the limitation) |

## 4. The standing rules, bound to this phase

| Rule | Binding |
|---|---|
| 1 Totality | `model_identity` answers every loaded model: a document or a typed `ModelIdentityError` (rule `model:identity-unrepresentable`, D4), never an uncaught `TypeError`/`UnicodeEncodeError`/`ValueError`. Probed: a lone surrogate in a quoted provenance string **loads** and then makes `canonical_json_bytes` raise `UnicodeEncodeError`; non-string keys and NaN/Infinity are refused at load, so those two refusals are reachable only through a constructed model object (T4-T6). The existing walk `_canonical` is recursive: a free field nested 500 deep in a model object raises an uncaught `RecursionError` (probed). The loader refuses model JSON nested 100 deep (50 loads), so a file cannot reach it; `model_identity_bytes` converts `RecursionError` to `ModelIdentityError` as well (T7). |
| 2 Algorithm bound | linear in the dumped model; T8 time-bounds it on a model near `MAX_MODEL_BYTES` (10 MB), ceiling recorded before it runs. |
| 3 Validation order | `--identity` runs after validation: a model that does not load gets the ordinary `validate` refusal (exit 3); only a loaded model reaches the identity. |
| 4 One walk | the document uses the one existing walk, `values.canonical` (`_canonical`), and the one byte form, `artifacts.canonical_json_bytes`; nothing re-implements either. |
| 5 One home | normative text: the new subsection of `representation-format.md` (M3); `docs/reference/formats.md` cites it. Implementation: `values.py`. |
| 6 Measure | number spelling, value kinds and refusals were measured over the tracked models (section 6 probes), not argued. |
| plan 0.1 Frozen | `_model_digest`, `reference_model_digest`, `operations_digest`, every report version, `validate --format json` and `validate --trace` output are byte-identical (T3, T12). The only CLI bytes that move: `gnd validate -h` (one new option) and its pinned golden. |
| Failure classes | *Python-only terms*: D3 decides the number spelling and the normative text states it as an algorithm with test vectors, so a non-Python caller can implement it. *Coerced keys*: refused (T4). *Second re-implementation*: T13 asserts `model_identity` calls `values.canonical` and `artifacts.canonical_json_bytes`. *A rule unfalsifiable by fixtures*: the vectors include floats with and without a fractional part, `-0.0`, a non-ASCII string, a date, and a reference-bearing model, each a case where a naive re-implementation differs. |

## 5. Goal

`gnd.values.model_identity(model)` returns `sha256:<64 hex>` over a canonical
JSON document a caller can recompute from the document's bytes alone;
`gnd validate MODEL --identity` prints that document and its digest and exits
0 for a loaded model whose document is representable, 3 for a model that does
not load or whose document is not representable. A model without reference
populations has identity version 2; a reference-bearing model has its existing
version 1. The legacy digest, every report and every existing CLI output except
`gnd validate -h` are byte-identical. No consumer calls the new function yet
(ROF4).

## 6. Design

**Probes (2026-11-08, at `a2b79084`, read-only, scratch copies only).**

| Question | Observed |
|---|---|
| tracked models | 379 model files; 313 load; 14 are reference-bearing (identity version 1), 299 are plain (identity version 2). The plan's 306 was measured at `12daa5b7`. |
| value kinds in plain dumps | `str` 30,327, `int` 1,025, `bool` 229, `None` 50, `float` 10, and ruamel subclasses `FoldedScalarString` 3, `ScalarInt` 34, `ScalarFloat` 2 (they serialize as their base type). No non-ASCII key, no astral key; 7 non-ASCII strings. |
| floats | 12 occurrences in 6 files, among them `0.30000000000000004`, `-0.0`, `1.0`, `200.0`, `2.5`: Python's JSON spells them `0.30000000000000004`, `-0.0`, `1.0`, `200.0`; RFC 8785 (JCS) would spell the last three `0`, `1`, `200`. |
| non-string key | refused at load (`object key '7' is not a JSON string`), in YAML and JSON |
| NaN / Infinity | refused at load (`model JSON input refused`) |
| unquoted YAML date in a provenance note | loads; the canonical walk writes ISO text |
| lone surrogate in a quoted string | **loads**; `canonical_json_bytes` raises `UnicodeEncodeError` (the legacy `repr` digest encodes with `surrogatepass` and does not) |
| deep nesting | a model JSON nested 50 deep in a provenance field loads and canonicalizes; 100 deep is refused at load (`model JSON input refused`); a model object mutated to 500 deep makes `_canonical` raise `RecursionError` |
| existing producer | `validate --trace` prints the legacy `model_digest` and `operations_digest`; its help calls it "the only shipped producer of operations_digest". The version-1 identity has no producer today. |

**Reuse table** (searched 2026-11-08: `components_index.py search "canonical
json digest identity"`, `"model digest"`, plus `git grep canonical_json_bytes`).

| Capability | Found | Decision |
|---|---|---|
| canonical value walk (dates to ISO, closed set, refuses non-string keys) | `values._canonical` | **reuse** |
| canonical byte form | `artifacts.canonical_json_bytes` | **reuse** |
| version-1 envelope | `values.reference_model_digest` | **reuse** unchanged; `model_identity` delegates to it for a reference-bearing model |
| legacy digest | `values._model_digest` | **unchanged** |
| a CLI producer of model digests | `output._print_trace` (`validate --trace`) | **not extended** (D2: a trace line moves the trace pins and cannot carry the document) |

**M1. `src/gnd/values.py`, about 60 lines.**

```python
IDENTITY_VERSION = 2

class ModelIdentityError(ValueError):
    rule_id = "model:identity-unrepresentable"     # D4
    def __init__(self, path: str, message: str) -> None: ...

def model_identity_document(model: Model) -> dict[str, Any]:
    # version 2 for a model without reference populations:
    #   {"identity_version": 2, "model": canonical(model.model_dump(exclude=
    #    {"warnings", "operations", "reference_populations"}), "$")}
    # version 1 for a reference-bearing model: the existing envelope, built as
    # reference_model_digest builds it.
    # Raises ModelIdentityError for an unrepresentable model.

def model_identity_bytes(model: Model) -> bytes:
    # canonical_json_bytes(model_identity_document(model)); UnicodeEncodeError
    # and the canonical walk's refusal become ModelIdentityError.

def model_identity(model: Model, version: int | None = None) -> str:
    # "sha256:" + sha256(model_identity_bytes(model)).hexdigest()
    # version None: the model's own (2 plain, 1 reference-bearing).
    # version=2 on a reference-bearing model, version=1 on a plain one, or any
    # other value: ModelIdentityError("$", "identity version N is not defined
    # for this model").
```

For a reference-bearing model `model_identity(model)` equals
`reference_model_digest(model)` exactly (T10). To keep one home of the
version-1 envelope, `model_identity_document` and `reference_model_digest`
share one private builder `_reference_identity_document(model)`; the bytes
`reference_model_digest` returns are unchanged (T3 pins them). The canonical
walk's refusal today raises `TransitionLoadError` with rule
`transition:operations-digest-unrepresentable`; `model_identity_document`
converts it to `ModelIdentityError`, keeping the walk's path.

**M2. `gnd validate MODEL --identity` (D2), about 35 lines** in
`commands/checking.py` and the validate argument definition.

- After a successful load, prints exactly two lines and exits 0:
  `MODEL IDENTITY sha256:<64 hex> (identity_version <N>)`, then the canonical
  document as one line (the hashed bytes without their trailing newline).
  `sha256(line 2 + "\n")` equals the digest on line 1, so
  `gnd validate M --identity | sed -n 2p | shasum -a 256` reproduces it.
- A model that does not load: the ordinary `validate` refusal (issue lines,
  exit 3), unchanged.
- A loaded model whose document is not representable:
  `ERROR at <path>: <message> [model:identity-unrepresentable]`, exit 3 (D5).
- `--identity` with `--trace`, `--document` or `--format json` is a usage
  error (exit 64): the JSON payload's schema is closed (rule 1), and the
  combinations have no defined layout.
- Redaction: the identity document is the model, which carries no population
  value; the projected route is not involved (`validate`'s projection applies
  to the report, which `--identity` does not print).

**M3. Normative text, about 60 lines.** A new subsection of
`src/gnd/skills/gnd-orm-core/references/representation-format.md`, after
"What `population._model_digest` covers (A8)": **"Model identity (canonical,
versions 1 and 2)"**. It states, as one home:

1. the document: the loaded model (defaults filled, as `gnd validate
   --identity` prints it), with `warnings`, `operations` and
   `reference_populations` removed, wrapped as `{"identity_version": 2,
   "model": …}`; for a reference-bearing model, the version-1 envelope (what
   `reference_model_digest` hashes), and no version 2;
2. the byte form, as an algorithm: UTF-8; object keys sorted by Unicode code
   point; separators `,` and `:` with no whitespace; strings escaped as JSON
   requires (`"`, `\`, and U+0000-U+001F as `\b \f \n \r \t` or `\u00XX`
   lowercase hex), every other character literal; integers in decimal;
   floats per D3; `true`, `false`, `null`; one trailing `\n`;
3. dates: ISO 8601 text (`YYYY-MM-DD`, `…T…` for datetimes);
4. the empty case: a model with no reference populations (`[]` or absent) is
   version 2; `operations` is excluded, so a model whose only change is its
   operations keeps its version-2 identity (operations are bound by
   `operations_digest`);
5. refusals: a string that is not encodable as UTF-8 (a lone surrogate), a
   non-string key, a value outside the closed set:
   `model:identity-unrepresentable`, never coerced;
6. the legacy identity (`legacy-repr`, `_model_digest`) is unchanged and is
   still what reports, `validate --trace` and generated plans carry (D3 of the
   plan; D7);
7. test vectors: three documents and their digests from the ROF3 corpus.

The "Three digests, three bases" table gains one row (`model identity`,
canonical JSON over the loaded model, "reproducible by a caller; accepted
beside `model_digest` from ROF4"); `docs/reference/formats.md` gets one
sentence citing the new subsection. Nothing restates the algorithm.

Estimated: about 155 source and doc lines (M1 60, M2 35, M3 60) and 230 test
lines, plus the corpus. The plan's estimate was 120 source and 220 test lines;
the normative text was not in it.

### Normative order and home

The identity's definition: the new `representation-format.md` subsection.
Its implementation: `values.model_identity_document` /
`model_identity_bytes` / `model_identity`. Its producer: `gnd validate
--identity`. Nothing else defines, computes or prints it in this phase.

## 7. Decisions

| D | Question | Readings and cost |
|---|---|---|
| D1 | Approval instrument | **Ruled (o, 2026-11-08): corpus of test vectors, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). **corpus of test vectors** (proposed): a handful of fixture models (copied, so they never move) with their expected identity documents and digests split out in `expected/`, derived by a script that uses only `json` and `hashlib` over the dumped model, not `gnd.values`; the owner approves by reading the spellings (floats, dates, non-ASCII, the version-1 case). Alternative: prose only. A serialized format is the shape the protocol defaults to corpus-first. **Open** |
| D2 | The producer surface (plan D5) | **Ruled (o, 2026-11-08): (a) `gnd validate --identity`, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). (a) **`gnd validate --identity`** (proposed): prints the digest and the document; moves only the `gnd validate -h` golden; the document is printable, so a caller can hash it. (b) a `validate --trace` line: moves every trace pin (`test_public_transition_trace.py`, `test_v62_phase1_trace.py`, ROF1 T13) and cannot carry the document. (c) a new subcommand: moves the top-level help and the command tree golden. No exit-code difference between them. **Open** |
| D3 | Number spelling in the canonical bytes | **Ruled (o, 2026-11-08): (a) the existing canonical byte form, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). (a) **the existing `canonical_json_bytes` spelling** (proposed): Python's shortest round-trip float text (`1.0`, `-0.0`, `0.30000000000000004`, `1e+16`, `5e-324`), stated as an algorithm with vectors; the same bytes `operations_digest` and the version-1 identity already use, so one canonical form. The identity keeps `1` and `1.0` apart, as the legacy digest does. (b) RFC 8785 (JCS): a published standard with libraries, but `1.0` and `1` (and `-0.0` and `0`) hash alike, which merges models the legacy digest keeps apart (so the version-2 classes stop being a bijection with the legacy ones, which the plan's census measured), and a second canonical form beside `canonical_json_bytes`. **Open** |
| D4 | Rule id of the refusal | **Ruled (o, 2026-11-08): (a) `model:identity-unrepresentable`, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). (a) **`model:identity-unrepresentable`** (proposed): its own id and message. (b) the plan's wording, `transition:operations-digest-unrepresentable`, which is the walk's current id but says "operations digest" about a model. Flagged: (a) departs from plan §2's text, which named (b). No exit-code difference. **Open** |
| D5 | Exit code of `--identity` on an unrepresentable document | **Ruled (o, 2026-11-08): 3, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). **3** (proposed): the input cannot be given the identity, the same band as any other refused input. Alternative: 70, which would call a property of the input an internal error. **Open** |
| D6 | Scope of the legacy pin (C3, "the 306-model digest list pinned") | **Ruled (o, 2026-11-08): (a) corpus pin plus census evidence, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). (a) **the corpus's copied models pinned in the test, plus the full tracked-model census recorded once as evidence** (proposed): the pin never moves when an unrelated fixture changes. (b) the plan's literal list over all tracked files: any later fixture edit anywhere breaks it. The live differential (T1) still runs over every tracked model. **Open** |
| D7 | Review over the spec bytes | **Ruled (o, 2026-11-08): none, as proposed** ("Approve, author corpus", answering "Approve ROF3 D1–D7 as proposed, so I author the test-vector corpus?"). none (proposed), as ROF1 and ROF2; the diff review covers the identity code. ROF4 (comparison sites) is where the plan asks for the owner's independent reviewer. **Open** |

## 8. Tests

`tests/test_rof3_model_identity.py` unless named.

| T | Case | Expected |
|---|---|---|
| T1 | every tracked loadable model (299 plain, 14 reference-bearing at the base) | `model_identity(m)` equals a re-implementation in the test file (its own envelope, its own `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)` and its own date handling; no import of `gnd.values` or `gnd.artifacts` helpers) |
| T2 | each corpus model | `model_identity_bytes(m)` equals `expected/<case>.identity.json` byte for byte; `model_identity(m)` equals `expected/<case>.digest` |
| T3 | each corpus model | the legacy `_model_digest` and, for the reference-bearing case, `reference_model_digest` equal their pinned values (D6) |
| T4 | a model object constructed with a non-string key in a free field | `ModelIdentityError`, rule `model:identity-unrepresentable`, path names the field; never a digest |
| T5 | a model file with a lone surrogate in a quoted string | loads; `model_identity` raises `ModelIdentityError`; `_model_digest` still returns (legacy is total) |
| T6 | a model object carrying a `set`, a `Decimal`, a `bytes` value | `ModelIdentityError` |
| T7 | deep nesting: a model file nested to the deepest level the loader accepts (probed between 50 and 99), and a model object mutated to 1,000 deep; the empty cases (`reference_populations` absent and `[]`) | the file: a digest; the object: `ModelIdentityError`, never `RecursionError`; absent and `[]` give one identity |
| T8 | a model near 10 MB | under a ceiling measured before the run (6x the slowest of three runs); legacy and identity timed side by side |
| T9 | subprocess `gnd validate M --identity` over each corpus model | exit 0; two lines; `hashlib.sha256((line2 + "\n").encode()).hexdigest()` equals line 1's digest; no `gnd` import in the recomputation |
| T9b | `--identity` with `--trace`, `--document`, `--format json` | exit 64 each |
| T9c | `--identity` on a model that does not load; on the surrogate model | exit 3; the ordinary issue lines; `ERROR at … [model:identity-unrepresentable]` |
| T10 | a reference-bearing corpus model and the same model with only `operations` changed | version-1 identity moves; `model_identity(m, 2)` raises; `model_identity(plain, 1)` raises; a plain model whose only change is `operations` keeps its identity |
| T11 | `representation-format.md` | contains the subsection once; the vectors it quotes equal the corpus's `expected/` digests |
| T12 | `validate` text, `--trace`, `--format json` on the corpus models; existing digest suites | byte-identical; exits as before |
| T13 | source assertions | `model_identity_document` calls `canonical(`; `model_identity_bytes` calls `canonical_json_bytes(`; no `json.dumps` in either |

Every declared branch has a case that can fail it: version 2 (T1, T2), version
1 (T10), version refusal (T10), each refusal kind (T4-T6), producer success
(T9), producer refusals (T9b, T9c), legacy unchanged (T3, T12).

## 9. Out of scope for this phase

Any site that compares a supplied identity (ROF4); emitting the identity in a
report (ROF5, D3 "not now"); generated Pyrel plans (D7); retiring the legacy
identity; issue 112.

## 10. Size

Estimate: about 155 source and doc lines and 230 test lines, plus the corpus.
Stop at 1.5x.

## 11. Approval instrument

Proposed (D1): `tests/fixtures/rof3-model-identity/`, entry point `README.md`
(the stories: which model, what in it makes the spelling interesting),
answers in `expected/` (`<case>.identity.json`, `<case>.digest`,
`<case>.legacy`, `derive_vectors.py`), runner
`tests/test_rof3_model_identity.py`, red first. Planned cases: `plain-small`
(a short model, readable vector), `floats` (from
`tests/fixtures/v62-phase5/models/floats.orm.yaml` and a `pyrel-rules`
model with `-0.0` and `0.30000000000000004`), `dates-and-text` (an unquoted
date in a provenance note and a non-ASCII quote), `reference-bearing` (a copy
of a tracked version-1 model), `operations-only` (a plain model and its twin
differing only in `operations`), `surrogate` (refusal).

**Changed bytes, listed before code (rule 1):** the `gnd validate -h` golden
under `tests/fixtures/rf1-pins/goldens/cli-help/` (to be confirmed by the
same stub-and-diff census ROF2 used), its manifest line and pinned digest, and
any CLI tree golden that lists `validate`'s options
(`tests/fixtures/rf1-pins/goldens/cli/tree.json` names `--trace`, so it
likely moves). `representation-format.md` has one tracked copy (the `.claude/skills/gnd-orm-core` entry is a symlink to it) and is read by
`tests/test_guarded_corpus.py`, `tests/test_marketplace_plugins.py`, `tests/test_packaged_skills.py`, `tests/test_model_v2.py` and
`tests/test_model_validation.py`; any of them that pins the file's bytes or digest moves with M3, and the census lists which.
No report, trace or JSON output moves.

## Verification ledger

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | base record | run before any edit | ROF2's head run (`evidence/ROF2/full-suite-rof2-8287d5b6.txt`) is the base for unchanged files; the census of tracked models is re-run at the base |
| V2 | focused gate | run | `.venv/bin/python -m pytest -q tests/test_rof3_model_identity.py tests/test_model_v2.py tests/test_reference_population_corpus.py tests/test_rf1_helper_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_public_transition_trace.py tests/test_v62_phase1_trace.py tests/test_guarded_corpus.py tests/test_marketplace_plugins.py tests/test_packaged_skills.py tests/test_model_validation.py` plus the RF5/RF6 guard suites |
| V3 | lint | run | `ruff check` on touched files |
| V4 | layers and homes | run | `tools/gnd_layers.json` import check and the RF structure suites |
| V5 | full default suite vs base | run (sharded, on a clean tree) | failure set ⊆ the base's |
| V6 | component index | at record time | `scripts/components_index.py changed --base <base> --strict` |

## Corpus (authored 2026-11-08, r2)

`tests/fixtures/rof3-model-identity/`: entry point `README.md` (stories
only), answers in `expected/` (`<case>.identity.json`, `<case>.digest`,
`<case>.stdout.txt`, `<case>.legacy`, `vectors.json`, `README.md`,
`derive_vectors.py`), runner `tests/test_rof3_model_identity.py`.

Ten models, all copies: `plain-small`, `floats` (`1.0`, `200.0`),
`float-spellings` (`0.30000000000000004`, `2.5`), `negative-zero` (`-0.0`),
`dates-and-text` (an unquoted date, Greek text), `operations-a` /
`operations-b` (twins differing only in an operation's reading),
`reference` and `reference-operations` (version 1; the twin adds one
operation), `surrogate` (refusal). Changes from the section 11 plan (r2): the
floats case is three models, so each float spelling has its own vector, and
the reference case has its operations-only twin.

`derive_vectors.py` builds the envelope and bytes from the definition with
`json` and `hashlib` only, over each loaded model's dump; a second run
reproduced every file. Cross-check: the existing helpers
(`values.canonical` + `artifacts.canonical_json_bytes`, and
`values.reference_model_digest` for version 1) agree on all nine digests,
which is the evidence that D3's byte form is the existing one.

Observed in the vectors: the plain operations twins share one identity
(`sha256:72bd4f2f…`); the reference twins differ (`fab46dd5…` vs
`cc98b9ac…`); `-0.0`, `1.0`, `200.0` and `0.30000000000000004` keep those
spellings; the date is `"2025-01-01"`; the Greek text is literal UTF-8.

State at commit: 32 tests, **21 red** (9 vector cases, 9 producer cases, the
surrogate refusal, the version rules, the twins through the function), 11
green (10 legacy pins, the corpus self-check).

## An experiment, recorded before it runs (T8, 2026-11-08)

Measures: wall time of `model_identity(model)` and of the legacy
`_model_digest(model)` on one loaded model built near `MAX_MODEL_BYTES`
(10 MB): the `plain-small` corpus model with value object types and fact types
added until its JSON file is between 9 and 10 MB; three runs each, on the
development machine; and the same at about 1 MB to show the growth is linear.
Loading is not timed. Cannot measure: other machines; the cost a caller pays
(ROF4 decides which sites call it). Liveness: a quadratic walk would take
minutes at 10 MB. Ceiling rule: 6x the slowest measured identity run at 10 MB,
rounded up to the next whole second; the legacy time is reported beside it,
not bounded.

Result: at 9,695,013 bytes (load 7.75 s, not timed) identity 0.472, 0.425,
0.653 s and legacy 0.100, 0.152, 0.149 s; at 1,923,013 bytes identity 0.061,
0.080, 0.050 s and legacy 0.019, 0.018, 0.043 s: linear, and the identity
costs about 4x the legacy digest. Ceiling: 6 x 0.653 = 3.9, rounded up to
**4 s**, written into `test_t8_identity_is_linear_near_the_input_cap`. The
test builds and loads the 9.7 MB model, so it takes about 10 s.

## Implementation findings (2026-11-08)

- **I1.** The corpus went from 21 red / 11 green to 32 of 32 green with M1 and
  M2 alone; the vectors needed no change.
- **I2.** `model_identity_document` wraps the existing walk's refusal
  (`TransitionLoadError`, rule `transition:operations-digest-unrepresentable`)
  and `RecursionError` into `ModelIdentityError`; `model_identity_bytes` wraps
  the byte form's `UnicodeEncodeError`, `TypeError`/`ValueError` and
  `RecursionError`. The surrogate model's refusal path is `$` (the byte form
  does not say which string); the walk's refusals keep their path
  (`$.fact_types…`, T4/T6).
- **I3.** M3 departed from the spec in one place: the "Three digests, three
  bases" table did not gain a row, because a fourth row under a heading that
  says "three" would be wrong; a sentence after the table names the fourth
  value and cites the new subsection instead. The normative text also states
  one rule the spec's list left implicit, measured with `json.dumps`: the
  exponent of the scientific form is signed and has at least two digits
  (`1e-05`).
- **I4.** The CLI goldens were not edited. As RC1, RC3 and RC4 did for `gnd
  check`, a successor fixture (`tests/fixtures/model-identity-cli/expected.json`:
  the one new action at index 3, the help and the exit probe) is applied by
  `tests/test_rf1_cli_pins.py` for `gnd validate`; the new help differs from
  the frozen golden only by the usage line's wrap and the `--identity` entry.
- **I5.** Guards moved as expected: the RF5 row for `_cmd_validate` (chained
  onto its ROF1 row); a query-policy successor
  (`evidence/ROF3/query-successor.json`: the one counted `d['fact_types']`
  read moves from `reference_model_digest` to `_reference_identity_document`,
  no widening, metric 309 of ceiling 310); a dynamic-query successor (2 rows
  added in `values.py`) chained after ROF2's; the `model.scalar_identity`,
  `cli.checking_command` and `infra.text_output` index entries.
- **I6.** Three of my own first-draft tests were wrong and were fixed before
  any code review: T12 asserted that `identity_version` never appears in a
  validate JSON payload, but a reference model's existing payload already
  contains it; T12 then read `model_digest` from a fixed key, which a frozen
  version-3 payload does not carry and which is `null` under `transition`;
  T7's "empty" twin changed the model's `version`, which is a different model.
