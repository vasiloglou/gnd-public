# LI5 independent reserve follow-up

Draft for the corpus approval recorded as required in
[close record 026](../026-milestone-close.md). The original reserved
score remains part of the acceptance history.

## Obligations

| Source | Obligation for the follow-up |
|---|---|
| [Plan §4, L1 and C6](literature-identity-plan.md) | Keep the supported chain and exclude both false chains in a fresh three-case reserve. Bind all scoring inputs and record the independent first score separately from development and the original reserve. |
| [LI5 spec, D1–D4 and T1](phase-LI5-spec.md) | Use the frozen directed-path policy, existing contextual admission and composition, and witness checks for each exact edge and the resulting ancestry. Keep the private key and per-path evidence local. |
| [021](../021-phase-LI5-rule-freeze.md), [022](../022-phase-LI5-reserved-input-freeze.md), [023](../023-phase-LI5-reserved-input-amendment.md) and [024](../024-phase-LI5.md) | Retain the original pre-score freeze and the corrected-input smoke result. Disclose the known failure mode and bind the new first result before any feedback can reach the annotator. |
| [025](../025-panel.md) and [026](../026-milestone-close.md) | Keep the original independent acceptance condition open until a separately approved fresh measurement supports a new ruling. The next ruling cites this evidence independently of the prior panel. |
| Plan §§0, 5–9 | Reuse the bounded readers and producer. The evidence-only follow-up edits neither public schemas nor skill surfaces. The date control, host-scale evaluation and successor assignments remain with their recorded targets. |

## Frozen route

Start at `01d9e6c65b9b02b80b07663bdf311554e9081415` with a clean
checkout. Record the commit and SHA-256s of the model, path policy,
assembly/scoring module and assertion rubric. Use the current scorer
with the admission-marker binding repair from 024. Freeze the approach,
including the annotation instruction below, before the source pack is
chosen. The prior model and policy freeze still applies.

The annotation instructions apply to every source. Use exact supporting
UTF-8 source spans. Identify the method, version or component actually
asserted by the source. Preserve its encoder, experimental condition or
interface in the appropriate qualification when the text supports both
a base relationship and the qualification. Preserve version-specific
or component-specific endpoints whenever they change the asserted
relation. Add a cross-source identity decision only when evidence
supports it. The annotator asks questions about the public format
before receiving the source pack.

## Private corpus and custody

1. The owner appoints a corpus author/custodian and a separate annotator.
   The corpus author chooses unused public source passages, documents
   stable work identifiers and provenance, and prepares the
   `literature-answer-key/1` key. The annotation session receives only
   the source pack, the public annotation instructions and the input
   shape. It has no access to the key, expected paths, original reserve,
   implementation checkout or score. The corpus author does not edit
   the annotations.
2. The proposed denominator is one supported multi-step chain spanning
   sources and two independently labelled false chains. The positive
   should exercise a qualified relationship of the same general sort
   as the original miss. Each negative should name locally grounded
   participants and a reason the exact chain is invalid. Suggested
   controls are unsupported cross-source identity and a non-chaining
   relationship. Use fresh sources and paths outside both prior sets,
   with no substitutions after scoring.
3. The owner approves the private corpus by its source manifest and
   key hashes while the annotator still lacks the key. The custodian
   keeps both local and records the exact paths and labels privately.
   Public evidence contains the hashes and aggregate counts. Annotation
   and score sessions use separate private directories outside Git.
4. Freeze the exact annotations before assembly and the generated
   composition record before score. The custodian verifies the frozen
   hashes and three-case roster, then invokes the score command once.
   Before any feedback or correction, retain the command exit, stdout
   digest and aggregate counts. The public record keeps no case IDs,
   endpoints, source text, raw scores or answer key.

## Existing commands and exit gate

The private `example` directory contains the fresh source files and a
byte-identical copy of the pinned `assertions/rubric.json`. Its paths
are resolved regular files. `model` is the pinned LI5 model, `annotations`
the frozen input, `run` a new output directory, and `key` the private
precommitted answer key.

```sh
uv run python -m gnd.examples.literature.lineage_run assemble \
  "$example" "$model" "$annotations" "$run"
uv run python -m gnd.examples.literature.lineage_run score \
  "$model" "$run" "$key" > "$private_score"
```

| Check | Expected exit and evidence |
|---|---|
| Existing public controls | `test_named_development_paths` verifies 3/3 supported and 5/5 excluded. `test_false_chain_exclusion_can_fail` verifies that a promoted false path produces score exit 1. |
| Fresh assemble | Exit 0, with the record and retained admission bundles bound to the independent input. Any refusal leaves the acceptance gate open. |
| Fresh first score | Exit 0 with `supported: [1, 1]` and `excluded: [2, 2]`. Exit 1 records an outcome mismatch. Exit 3 records a procedure or input refusal. Any other outcome leaves the gate open. |
| Reproducibility | Verify the three-case key roster, frozen hashes and aggregate extraction against captured output. A replay of the same result cannot replace the first score. |
| Close | Revisit 026 only after the fresh result. A new milestone close needs its separately authorized close review and a recorded ruling over the new evidence. |

The existing source reader takes files relative to the `example`
directory and binds each document by SHA-256. The existing grader
parses the case key and verifies the composition and retained
admission markers before it tests the ordered edges and endpoint
ancestry. Both public controls run through that route, so the fresh
pack needs no scorer or model change. If a procedure refusal or
first-score miss occurs, record it before considering a further
corpus or product decision. Do not tune against an exposed reserve.

## Owner decisions

Approve the corpus-first follow-up and name who will supply the
sealed source pack and answer key and who will independently annotate
the pack. The owner can hold the key with the corpus author if they
remain outside the annotation session. No new paid calls are assumed.
