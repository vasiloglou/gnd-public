# Answers: the stories behind the labels

This directory is the answer key's half of the corpus. Do not give it to a
blind reader. The labels were written by one author from the public works,
so they are **not independent expert ground truth**.

| File | What it is |
|---|---|
| `answer-key.json` | The development answer key (`literature-answer-key/1`, formats in [../README.md](../README.md#formats)) |
| `gold/<document>.population.json` | What each document supports, in the flat model. `gnd fidelity` compares a run's extraction with it |
| `render/<document>.manifest.json` | The `gnd fidelity` renderer manifest for each document. The unsupported assertions are its `absent-fact` distractors. `gnd doccheck` reports 0 violations for all 12 |
| `heldout.sha256` | The digest of the held-out answer key, which lives on the local branch `literature-heldout` and nowhere else |

## Counts

| Category | Floor | Here |
|---|---|---|
| Supported chains | 3, one cross-domain | 3 (c01, c02, c03). c01 and c03 cross domains |
| False chains | the five named ones | 5 (c04–c08) |
| Reuse cases | 8: 4 real, 2 generic words, 2 homonyms | 8 (u01–u08) |
| Support-labelled assertions | 12 | 12: 8 supported, 2 stretched, 1 contradicted, 1 insufficient evidence |
| Identity pairs | 6: 3 `same`, 3 `different` | 6 (i01–i06) |
| Name pairs | 4: 2 homonym, 1 synonym, 1 family | 4 (n01–n04) |
| Held-out chains | 1 supported, 2 false | in the held-out key, pinned by digest |

There are 12 development documents and 4 held-out ones. No work and no
version of a work appears in both splits.

## Why 8 of the 12 assertions are supported

The semantic-support floor is recall ≥ 0.9.
- **One dropped fact must fail it.** With S supported assertions, that needs
  (S − 1)/S < 0.9, so S < 10.
- **The abstaining case must come out exact.** Abstaining on 6 of 12 and
  answering the rest correctly must give recall 0.5, so S must be even.

S = 8 satisfies both.

## The assertions

| Id | Passage | Claim in the flat model | Label | Why |
|---|---|---|---|---|
| a01 | vampnet.p2 | VampNet builds on bidirectional transformer | supported | The passage says VampNet is built on one |
| a02 | wham-whale.p2 | WhAM builds on VampNet | supported | WhAM was made by fine-tuning VampNet |
| a03 | wham-pose.p2 | WHAM builds on SLAM | supported | WHAM takes the camera's angular velocity from a SLAM system |
| a04 | opencap-monocular.p2 | OpenCap Monocular builds on WHAM | supported | It starts from WHAM's pose estimates |
| a05 | apinn.p3 | XPINN builds on PINNs | supported | XPINN extends PINNs |
| a06 | apinn.p2 | $PINN builds on XPINN | supported | $PINN improves on XPINN's decomposition |
| a07 | pinn-failure-modes.p3 | curriculum regularization builds on PINNs | supported | It changes how PINNs are trained |
| a08 | boltz-1.p3 | Boltz-steering builds on Boltz-1 | supported | It is applied to Boltz-1 at inference time |
| a09 | posex.p2 | PoseX builds on Boltz-1 | **stretched** | PoseX *evaluates* the Boltz-1 family. Evaluation is not ancestry |
| a10 | sbi-frontier.p2 | simulation-based inference builds on normalizing flows | **stretched** | The review lists flows among the field's tools. The field does not build on them |
| a11 | sensor-placement.p2 | deep optimal sensor placement builds on simulation-based inference | **contradicted** | The passage says *unlike* existing simulation-based inference approaches |
| a12 | opencap-monocular.p3 | OpenCap Monocular builds on OpenCap | **insufficient evidence** | The passage only compares their accuracy |

## The chains

The lineage phase scores the chains. This phase only commits them.

| Id | Label | Path | Story |
|---|---|---|---|
| c01 | supported, cross-domain | bidirectional transformer → VampNet → WhAM | A music model becomes a whale model. Each link is stated in its own paper |
| c02 | supported | PINNs → XPINN → $PINN | Stated extensions within one method family |
| c03 | supported, cross-domain | SLAM → WHAM → OpenCap Monocular | Computer vision to biomechanics |
| c04 | **false** (the whale) | VAMPnet ⇒ VampNet → WhAM ⇒ WHAM → OpenCap Monocular | True sentences joined by two false merges. VAMPnet (molecular kinetics) is not VampNet (music), and WhAM (whales) is not WHAM (human pose) |
| c05 | **false** (`$PINN` chain) | XPINN → $PINN ⇒ PINNs → curriculum regularization | Filing $PINN as PINNs makes curriculum regularization a descendant of XPINN |
| c06 | **false** (`$PINN` loop) | PINNs → XPINN → $PINN ⇒ PINNs | The same filing closes a loop |
| c07 | **false** (Boltz-1 as ancestry) | Boltz-1 → PoseX | A benchmark that evaluates a model is read as building on it |
| c08 | **false** (contrast as "builds on") | normalizing flows → simulation-based inference → deep optimal sensor placement | A stretched link, then a contrast read as ancestry |

`⇒` marks a merge that a flat, case-folding host would make. `apinn` writes
the method's name as `$PINN`, the LaTeX-residue spelling a host extractor
produced. The work itself writes APINN, and the document's identifier line
says so.

## Identity pairs, reuse cases and name pairs

- **Identity pairs (for the sense-resolution phase).**
  - `different`: i01 VAMPnet (vampnets) vs VampNet (wham-whale); i02 WhAM
    (wham-whale) vs WHAM (opencap-monocular); i03 $PINN (apinn) vs PINNs
    (pinn-failure-modes).
  - `same`, each with an equal spelling: i04 VampNet; i05 WHAM; i06 PINNs.
- **Reuse cases.**
  - Real reuse: VampNet, WHAM, PINNs, simulation-based inference.
  - Generic words: "benchmark", "baseline".
  - Homonyms: vampnet (VAMPnet and VampNet), wham (WhAM and WHAM).
- **Name pairs (for name diagnostics).** VAMPnet/VampNet and WhAM/WHAM are
  homonyms; "normalizing flow"/"normalizing flows" is a synonym pair;
  $PINN/PINNs is a family pair.

## The scored cases

Each case is derived from the reference run by one transform. The builder
then regenerates every binding, except in M3, whose point is the stale
binding. Each case's approved outcome is in [`../expected/`](../expected/).
The routes are:
- **R1:** plain `gnd check`.
- **R2:** `gnd check --anchors --document`.
- **R3:** `gnd fidelity`.
- **R4:** `gnd check --composition`.

| Case | Transform | Required failing stage | Expected failing stages |
|---|---|---|---|
| reference | none | none | none: exit 0 |
| M1 drop all | every source's facts and anchors emptied | semantic-support, derivation | source-binding, semantic-support, derivation |
| M2 drop one | a05 and its anchors removed | semantic-support (recall 7/8) | source-binding, semantic-support |
| M3 stale | vampnet's population rewritten; sidecars kept | freshness | source-binding, semantic-support, derivation, freshness |
| M4 false derived | an unsound claimed derived row in vampnet | derivation | model-population-validity, derivation |
| M5 invalid population | an unknown key in posex's population | model-population-validity | model-population-validity, source-binding, semantic-support, derivation, freshness |
| M6 shifted span | one anchor moved one character, excerpt hash kept | source-binding | source-binding, derivation, freshness |
| X1 abstain 6 (C5) | abstain on 4 supported and 2 unsupported passages | semantic-support: P 4/4, R 4/8, abstention 6/12 | source-binding, semantic-support |
| X2 consistent shift | as M6, with the excerpt hash recomputed; R2 accepts | source-binding | source-binding |

**What the extra failures say.**
- **One refusal reaches several stages.** A route that refuses fails every
  stage that reads it. A stale population (M3) is refused by R2, R3 and R4
  alike. An invalid population, or a shifted span, makes `gnd compose`
  refuse, so the derivation stage has no composed population to read (M5,
  M6).
- **Removing a fact removes its anchors too.** That is why M2 and X1 also
  fail source binding.
- **X2 is the case where the route alone is not enough.** `gnd check` accepts
  the binding, and only the gold span shows the anchor moved.
