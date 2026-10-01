# The extraction contract

Normative reference for [`../SKILL.md`](../SKILL.md). Everything here is enforced by code — `gnd verify` loads the sidecar strictly and re-derives the header from the model — so this file restates the contract; it does not create it.

## 1. The two files you write

| Path | Content | Loaded by |
|---|---|---|
| `extracted.population.json` | one population, raw JSON, conforming to `<stem>.projection.schema.json` | the population loader, then the checker |
| `extracted.population.extraction.json` | the extraction sidecar (§3) | `gnd verify MODEL POPULATION --artifacts DIR`, before it composes the checker |

The default sidecar location is the population path with its suffix replaced by `.extraction.json` — `extracted.population.json` → `extracted.population.extraction.json`. `gnd verify --sidecar PATH` overrides it.

The population file itself carries **no** provenance. The interchange format is frozen; provenance lives in the sidecar, which is why the sidecar is mandatory rather than decorative.

## 2. Raw JSON, written by a file-writing tool

The output must be the JSON document and nothing else:

- No ```` ``` ```` fences, no `json` language tag, no leading or trailing prose.
- No comments — JSON has none, and a `//` line makes the file unparseable.
- No trailing commas, no `NaN`, no `Infinity`.
- UTF-8, and a trailing newline is fine.

Emit it with a file-writing tool, not by printing it into a reply for a human to save. A population that exists only as text in a conversation has not been extracted.

**A parse failure is exit 3 (`ill_formed`), with `extraction.state` staying `ran`.** It is never repaired by hand. Re-emit the whole file.

The two fields answer different questions, and this is the distinction to branch on:

| field | question it answers | a fenced or unparseable population |
|---|---|---|
| `extraction.state` | did the handoff happen at all? | `ran` — you did write a file |
| exit code / `outcome` | is the result acceptable? | `3` / `ill_formed` — it is not |

`state: failed` is reserved for the SIDECAR going wrong — absent, invalid, unbound to the population, or carrying a gamed header. A population that exists but will not load is a band outcome, not a failed handoff.

*(Corrected 2026-08-13, owner decision, UAT item 2. This section previously assigned the `failed` state to a parse failure, which the shipped code does not do — measured live in plan 06, deferred-items FINDING 2, where the prior wording is recorded verbatim. Nothing ever looked green under either reading, since both exit 3; the risk was an agent branching on the wrong field. The old sentence is deliberately not reproduced here: a shipped skill should teach current behaviour, and a refuted claim quoted inside the file an agent reads is one skim away from being followed.)*

## 3. Sidecar fields

Every field below is REQUIRED. The loader forbids unknown fields (an unexpected key is a rejection naming the key), requires every digest, and refuses any path that is absolute or contains `..` — under both POSIX and Windows path rules, because this file crosses machines.

| Field | Type | Value |
|---|---|---|
| `schema_version` | integer | `1` |
| `population` | string | RELATIVE path to the population, resolved against the sidecar's own directory (typically `extracted.population.json`) |
| `population_sha256` | string | `shasum -a 256` of the population bytes |
| `model` | string | the model reference as an opaque ID string — recorded, never dereferenced |
| `model_sha256` | string | `shasum -a 256` of the model file |
| `projection_sha256` | string | `shasum -a 256` of `<stem>.projection.schema.json`; also readable from `<stem>.artifacts.json` |
| `document` | string | RELATIVE path to the document the facts were read from (typically `document.md`) |
| `document_sha256` | string | `shasum -a 256` of the document bytes |
| `skill` | string | `gnd-extract` |
| `skill_version` | string | the version of this skill you are running |
| `executing_model` | string | your own model ID string, truthfully — the full identifier the runtime reports, never a family label |

Shape:

```json
{
  "schema_version": 1,
  "population": "extracted.population.json",
  "population_sha256": "…",
  "model": "full_vocabulary.orm.yaml",
  "model_sha256": "…",
  "projection_sha256": "…",
  "document": "document.md",
  "document_sha256": "…",
  "skill": "gnd-extract",
  "skill_version": "1",
  "executing_model": "…"
}
```

**The digest IS the binding.** `gnd verify MODEL POPULATION --artifacts DIR` recomputes all four digests from the population, model, bundle projection, and sidecar-relative document, then compares them. A sidecar written before a final edit, or copied from a previous run, does not bind — and a handoff that does not bind is not a handoff.

Digests are computed AFTER the last write to each file. Write the population, then digest it, then write the sidecar.

## 4. The header comes from `header_template`

`<stem>.artifacts.json` carries a `header_template` object. Copy it into the population's `population` block verbatim:

```json
"header_template": {
  "covers": ["assignment_has_hours", "…", "project_ran_from_date_to_date"],
  "model": "tests/fixtures/models/full_vocabulary.orm.yaml",
  "source": "agent-output"
}
```

`model_id` appears in the template when the model declares one; copy it if present, and never invent it if absent.

Fields you must not author, and what `gnd verify` does if you do:

| Field | Owner | On disagreement |
|---|---|---|
| `covers` | derived from the model — asserted and legacy-opaque fact-type ids included, structured-derived ids excluded, sorted; see the [normative extraction consequence](../../gnd-orm-core/references/population-format.md#deterministic-document-extraction-covers) | `extraction:header-mismatch`, exit 3, state `failed` |
| `source` | fixed at `agent-output` for an extraction | same |
| `model` | the model reference the bundle was built from | same |
| `model_id` | the model's own declaration | same |

`covers` is a **completeness claim**, not a summary of what you found. Shortening it to the fact types you extracted would convert every missed fact type into an unexamined one, and the population would score as vacuously fine. That is the specific gaming path this rule closes.

## 5. Failure semantics

| What happened | Machine-readable form | Exit | What you do |
|---|---|---|---|
| The population file does not parse | population fails to load | 3 | re-emit the whole file (§2); never hand-repair |
| The sidecar is absent | `extraction:sidecar-missing`, state `failed` | 3 | write it; absence is a FAILURE, never a skip |
| The sidecar has an unknown field, a missing digest, or an unsafe path | `extraction:sidecar-invalid`, state `failed` | 3 | fix the sidecar against §3 |
| A recorded digest does not match the file bytes | `extraction:binding-mismatch`, state `failed` | 3 | recompute digests after the last write and rewrite the sidecar |
| The header disagrees with the model | `extraction:header-mismatch`, state `failed` | 3 | re-copy `header_template` verbatim (§4) |
| The checker found an alethic violation | verdicts on the checker channel, state `ran` | 1 | REPORT IT — the document describes a world that violates the model |
| The population is vacuous | state `ran` | 2 | report it; a document that supports no facts is a finding |
| The checker could not decide | state `ran` | 4 | report it |
| Everything held | state `ran` | 0 | report it |

The three states are `ran`, `skipped` and `failed`. **`skipped` is written only by the intentional opt-out `gnd verify --no-extraction`** — you never write it, and a missing file never produces it. A measurement that did not happen must not read as green.

Exit 0 with state `ran` is **checker acceptance**, not proof of faithfulness. A hallucinated, well-shaped, conforming population exits 0. That is a real extractor error and it is exactly what `gnd fidelity` exists to measure; nothing in a `verify` payload speaks to it, and no rate ever appears there.

## 6. What is out of scope

- **Verifier-guided repair** — re-reading the verdict and adjusting facts until the population passes. Deferred by name to EXP-02. It makes the extraction a function of the checker and destroys the independence the measurement rests on.
- **Choosing the header.** §4.
- **Calibration.** The round trip measures the round trip; recall is flattered because a renderer authored the ground truth. `gnd fidelity` reports `calibration.state: "uncalibrated"` and `publishable: false`, and emits no interval at all while that holds. Do not present a fidelity number as a quality claim.

When explicitly selected, saved source opinions use the separate [judgment contract](../../gnd-dev-session/references/judgment-contract.md); source hashes do not establish truth or grant assurance.
