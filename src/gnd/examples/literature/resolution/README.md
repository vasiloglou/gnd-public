# Resolution fixtures (LI2)

The fixtures for sense-resolution decisions bound to composition. The rules
and formats will live in the composition reference, section "Resolution",
once LI2 lands (spec: `.gnd-planning/milestones/literature-identity/notes/phase-LI2-spec.md`).
Every text here is a **synthetic fixture**, not a paraphrase of a work.

The whale notes spell `VampNet` and `WHAM` identically in both documents on
purpose. That is the host's case-folding failure from issue 193, rebuilt on
two small documents:
- **`whale-a`.** `VampNet` is the Koopman method (the work writes VAMPnet),
  and `WHAM` is the human-pose model.
- **`whale-b`.** `WHAM` is the whale model (the work writes WhAM), and
  `VampNet` is the music model.

| Path | What it is |
|---|---|
| `model.orm.yaml` | The fixture model: builds-on, its recursive closure `method_has_ancestor_method`, and the `Mention` pattern |
| `cases/<id>/` | One composition directory per case, each with a manifest, sources and, where present, `resolution.json` |
| `cases.json` | Each case's approved outcome: the exit, and for a refusal the exact message |
| `mentions/` | One document, two `VampNet` mentions with two senses (spec §6.5) |
| `baseline.json` | The bytes `gnd compose` wrote before LI2 changed any code (T16) |
| `li1-reference.resolution.json` | The decisions the LI1 reference run will carry once composition understands a resolution (spec D8) |

`tools/build_resolution_fixtures.py` rebuilds everything except
`baseline.json` and `li1-reference.resolution.json`. The literature builder
writes `li1-reference.resolution.json`.

## The cases

Every refusal message begins `composition:invalid: `, and names sources,
indexes and coordinates, never a value.

| Case | Story | Exit | Message after the prefix |
|---|---|---|---|
| `W-flat` | The whale, composed flat: identical spellings join, so the false chain OpenCap Monocular ... DMD is derivable. | 0 | — |
| `W-resolved` | The whale with two different decisions and two separating renamings: four senses stay distinct, the three edges survive, and the false chain is gone. | 0 | — |
| `R-uncovered` | A resolution with no decisions: VampNet is joined across the two notes with no same decision (rule 1). | 3 | `keys at whale-a method_builds_on_method#0.method and whale-b method_builds_on_method#0.base_method (object type method) are joined without a same decision` |
| `R-wrong-decision` | A renaming cites a decision about another key (rule 6). | 3 | `renaming 0 cites decision 1, which does not name its key` |
| `R-no-decision-field` | With a resolution present, a renaming that cites no decision is refused. | 3 | `renaming 0 cites no decision` |
| `R-transitive` | VampNet is same across a-b and b-c, but a and c are recorded different: a transitive merge across different (rule 3). | 3 | `decision 2 (different) keys are connected through same decisions` |
| `R-evidence-fact` | Decision 0's first coordinate points at a fact whose role holds another value. | 3 | `decision 0 evidence 0 (source whale-a, method_builds_on_method#1.method) does not hold key 0` |
| `R-evidence-span` | Decision 0's first coordinate cites a span no anchor has. | 3 | `decision 0 evidence 0 (source whale-a, method_builds_on_method#0.method) has no anchor at its span` |
| `R-stale-input` | Decision 0 was made over another version of whale-b's population. | 3 | `decision 0 input digest for source whale-b differs from its population` |
| `R-digest-and-uncovered` | A wrong resolution digest and an uncovered pair: the digest (step 2) is reported, not the pair (step 5). | 3 | `resolution digest differs from the manifest` |
| `R-evidence-and-uncovered` | A bad coordinate on decision 0 and an uncovered WHAM pair: the evidence (step 3) is reported, not the pair (step 5). | 3 | `decision 0 evidence 0 (source whale-a, method_builds_on_method#1.method) does not hold key 0` |
| `MV-joined-no-same` | A method key and a version key spelled alike are joined with no same decision (R2, rule 1). | 3 | `keys at mv-a method_builds_on_method#0.base_method and mv-b method_builds_on_method#0.base_method (object type method) are joined without a same decision` |
| `MV-distinct` | The same pair recorded different, with mv-b's value renamed to its version: two values. | 0 | — |
| `A-alias` | An evidenced alias: AF3 is AlphaFold3, renamed in both roles where alias-b uses it (R3). | 0 | — |
| `A-same-not-applied` | A same decision the manifest never applies (rule 5). | 3 | `decision 0 (same) keys are not joined` |
| `A-split` | The existing one-value-one-entity refusal still fires with a resolution present: AF3 renamed in one role only. | 3 | `renaming 0 splits a value of source alias-b: method_builds_on_method.base_method still uses the old value; rename it there too` |
| `H-no-decision` | A same-domain homonym with no decision: TRACE is joined, and refused (R3). | 3 | `keys at hom-a method_builds_on_method#0.method and hom-b method_builds_on_method#0.method (object type method) are joined without a same decision` |
| `H-different` | The homonym recorded different, with hom-b renamed to a sense id: two values (R3). | 0 | — |
| `H-unresolved` | The homonym left unresolved: both keys take their placeholders and stay apart (R7). | 0 | — |
| `H-unresolved-wrong` | An unresolved key renamed to something other than its placeholder (rule 4). | 3 | `decision 0 (unresolved) key 1 does not take its placeholder` |

## What a case shows

- **R1, the whale.**
  - *Flat.* `W-flat` composes, and `gnd witness` proves `OpenCap Monocular has ancestor DMD` (exit 0), a chain made of true sentences joined by two false merges.
  - *Resolved.* `W-resolved` records both pairs as `different` and renames whale-b's values to sense ids. The four senses stay distinct and the three edges survive. The same witness reports the chain `missing` (exit 2).
- **R2, two senses in one document.** `mentions/` keeps two `VampNet` mentions with two senses without rewriting the text, and `gnd check --anchors` passes.
- **R2, a method and its version.** In `MV-*`, a method and its version spelled alike are refused when nothing decides them (`MV-joined-no-same`). Recorded `different`, they compose into two values (`MV-distinct`).
- **R3, aliases and homonyms.**
  - *An alias joins.* An evidenced alias joins (`A-alias`).
  - *A homonym needs a decision.* With no decision a same-domain homonym is refused (`H-no-decision`). Recorded `different`, it composes into two values (`H-different`).
- **R7, unresolved keys.** `unresolved` keys take their placeholders and stay apart (`H-unresolved`).
- **R4, the refusals.**
  - *Coverage.* An uncovered pair (`R-uncovered`), a renaming citing the wrong decision (`R-wrong-decision`), a transitive merge across `different` (`R-transitive`), an unapplied `same` (`A-same-not-applied`).
  - *Evidence.* Bad evidence (`R-evidence-fact`, `R-evidence-span`), and a decision made over other inputs (`R-stale-input`).
  - *Order.* With two faults at once the earlier step is reported (`R-digest-and-uncovered`, `R-evidence-and-uncovered`).
- **Strictness kept.** The existing one-value-one-entity refusal still fires with a resolution present (`A-split`).

## The LI1 harness

The literature assurance report's `identity-decisions` stage becomes active.
The LI1 reference run gains `li1-reference.resolution.json`:
- `same` for the three equal spellings composition joins: VampNet, WHAM and PINNs (i04–i06);
- `different` for the three homonym and family pairs (i01–i03).

The new case `M7-false-merge` merges VAMPnet into VampNet with a `same`
decision. Composition accepts it because the decision exists, and the
harness then fails `identity-decisions` (precision 3/4). The merge also
makes a derived row no source claims (`arXiv:1710.06012 builds on
bidirectional transformer`), so `derivation` fails too: a false merge
produces false lineage. The amended expected outcomes of all ten LI1 cases
are in `../expected/`.
