# IK4-Q2 — evolve over reference-bearing models

## 1. Status

**r1, awaiting owner review.** No code exists. Nothing in this file is approved.
Implementation starts only after the owner rules on §7 and approves these bytes.

## 2. Provenance

- **Source:** open question IK4-Q2 from IK4 spec F12 and the 005 record.
  - Owner ruling 2026-10-25 (IK4 spec §18): "schedule before IK6's end-to-end
    walk".
  - On 2026-10-26 the owner agreed it runs as its own phase before IK6.
- **Plan:** r4 (SHA-256 `8afbdcbd…cd51a`). IK4-Q2 is not a plan phase. It is a
  carried defect whose fix §8's protocol covers as a phase-shaped unit. Its
  record is numbered after 008.
- **Plan clauses it serves:**
  - §4 IK4-C2, "the output is a valid evolve proposal that IK2's gate admits
    and `evolve preview` renders". That holds today only for reference-free
    models.
  - IK6-C1, "labels → measure → discover and learn → evolve preview".
- **Base commit B:** `8f89af4` (`main`, after PR #41). PR #42 (IK5-Q1) is open
  and touches no file this phase touches.
- **Harvest:** done by the author: IK4 spec §17–§18, the 005 record,
  `src/gnd/evolve/service.py`, `src/gnd/model/__init__.py` and
  `src/gnd/discover/service.py`.
- **Review:** none has run over these bytes.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| `gnd evolve preview` handles reference-bearing models | IK4-Q2; F12 | §6; T1 |
| IK4-C2's "evolve preview renders" holds for every model discover can propose for | plan §4 | T5 |
| A reference that cannot be bound is a named refusal (3), never an internal defect (70) | standing rule 1; reproduced defect, §12 | §6; T3, T4 |
| Apply, publish and finalize read the same models preview read | evolve's own invariant; standing rule 4 | §6 one loader; T2 |
| Reference-free evolve behaviour is unchanged | IK-R3 | T6, the existing evolve suites |
| References are read without following links | the model loader's existing contract | §6 reuses `bind_references`; T4 |
| Standing rules 1–6 | IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | the existing synthetic `reference-corpus/dispatch` fixture |

## 4. Standing rules bound to this phase

| Rule | Application |
|---|---|
| 1 Totality | Every evolve model load maps a reference refusal to a named exit 3. Today `ReferenceInputError` escapes `_load_model_bytes` and `_validated_candidate`, which is exit 70 (§12). |
| 2 Input cap vs algorithm | No new work proportional to input. Binding reads each declared reference once per load, through the existing capped binder (`MAX_BYTES`, `MAX_ENTRIES`). Argued inapplicable beyond that. |
| 3 Validation order | Unchanged. The model loads where it loads today; binding happens inside the load. |
| 4 One walk | **One loader** for all seven loads (preview: before and candidate; apply: before and candidate; publish: staged; finalize: before and candidate). Not a fix at the one site that failed. |
| 5 One home | The binding semantics stay in `gnd.model.bind_references`, and evolve calls it. The evolve contract (`evolution-contract.md`) gains one sentence citing it. |
| 6 Measurement | The failure was reproduced (§12) before this spec, and T1–T4 decide the fix. |

## 5. Goal

For a model that declares `reference_populations` whose files resolve and match
their digests, `gnd evolve preview`, `apply` and `finalize` behave exactly as
for a reference-free model: exit 0 on a valid proposal.

When a declared reference cannot be bound (missing, a digest mismatch, a link,
an escape), the command exits 3 with the binder's named reason. It never exits
70. Every reference-free evolve outcome is unchanged.

## 6. Design

Home: `src/gnd/evolve/service.py`. About 30 lines.

```python
def _load_model_bytes(data: bytes, *, label: str, reference_root: Path) -> Any:
    """Load model bytes as if they sat at the workspace model's path: the
    two validation layers, then, when the model declares reference
    populations, binding through gnd.model.bind_references at reference_root.
    Any load or binding refusal is EvolutionError (exit 3)."""
```

- **`reference_root`** is the directory of the workspace model:
  `allowed_project_root / model_relative`'s parent, as the CLI resolved it.
  That is exactly where `gnd validate MODEL` and `gnd check` bind (IK4Q2-D2
  below).
- **The temp-directory write is replaced** by `load_model_bytes(data,
  source=<workspace model path>)`, which runs the same alias guard and both
  validation layers. If the model declares references,
  `bind_references(model, root=reference_root)` follows, and its context is
  attached as `load_model` attaches it.
- **`_validated_candidate`** calls the same loader, so the candidate binds
  exactly as the current model does.
- **All seven call sites** pass the same `reference_root`.
- **Caught errors:** `ModelLoadError`, `ModelValidationError`,
  `ReferenceInputError` and `OSError`, each mapped to `EvolutionError` with its
  label. The existing "validation failed" marker maps that to exit 3.
- **Contract:** `evolution-contract.md` gains one sentence: preview, apply and
  finalize bind declared reference populations from the model's own directory,
  as `gnd validate` does.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IK4Q2-D1 | Approval instrument | **This prose plus the §8 test list.** There is no new format or exit code: it is existing evolve exits on one more class of model. **Corpus-first:** a fixture directory with narrated outcomes, which costs a station-0 step for six cases. | prose |
| IK4Q2-D2 | Where references resolve from | **The workspace model's directory:** the same root `gnd validate` and `gnd check` use, so one model means one binding. **`allowed_project_root`:** differs whenever the model sits in a subfolder, so the same model would bind differently under evolve. | model's directory |
| IK4Q2-D3 | Also lift IK5's `references` export refusal now? | **No:** the export would also have to render the bound reference facts per example, which is a change to the neutral form. It goes to IK6 or later, with its own corpus case. **Yes:** a wider phase that touches IK5's approved export. | no |
| IK4Q2-D4 | Base and branch | `claude/ik4-q2-evolve-references` from B = `8f89af4` | as stated |

## 8. Tests

New file `tests/test_evolve_references.py`, over a scratch copy of
`tests/fixtures/reference-corpus/dispatch/`.

| ID | Case | Expected (now → after) |
|---|---|---|
| T1 | preview of a valid ADD proposal (a user-supplied mandatory constraint) on the reference-bearing model | 70 → 0 |
| T2 | the same proposal, then apply and finalize; the published model equals the candidate | 70 → 0 |
| T3 | preview when a declared reference file is missing, or its bytes no longer match the model's digest | 70 → 3, with the binder's reason |
| T4 | preview when the reference file is a symbolic link | 70 → 3, refused and not followed |
| T5 | a `gnd discover` proposal on a population of the reference-bearing model previews | not previewable → 0 |
| T6 | a reference-free proposal's preview payload is byte-identical to B's, on the IK4 corpus K08 proposal | equal |
| T7 | a reference file changed on disk between preview and apply | apply 3 |

**Branch walk:**
- the loader's two arms (no references; references bound): T6, T1;
- each caught error class (load, validation, reference, OS): T3 and T4 cover the
  reference arm, and the existing evolve suites cover the rest;
- every one of the seven call sites: T1 covers preview, T2 apply, publish and
  finalize, and T7 the apply-time rebinding.

**Verification selection:**
- **Direct:** `tests/test_evolve_references.py`.
- **Impact:**
  - every `tests/test_*evolve*.py`;
  - `tests/test_discover.py`, `tests/test_ilp_bridge.py` (both preview
    proposals) and `tests/test_measure_labels.py`;
  - the reference tests (`git grep -l reference_populations tests/`);
  - every `tests/test_rf*.py` and `test_gnd_arch.py`.
- **Selection rule:** the reduced v6.3 selection. The broad lane is `cadence`.

## 9. Out of scope for this phase

- IK4-Q3 (YAML-only values in evolve), which is at the milestone close;
- lifting IK5's `references` refusal (IK4Q2-D3);
- evolve operations that edit `reference_populations` (none exist, §12);
- linked-project conformance over reference-bearing models, beyond what apply
  already runs.

## 10. Size

About 30 source lines, 150 test lines and 5 doc lines.

## 11. Approval instrument

Proposed in IK4Q2-D1: this prose and the §8 test list. The tests are written red
first and committed before the fix.

## 12. Implementability sweep (author inspection, not review)

| Requirement | Finding |
|---|---|
| The failure as filed | Reproduced at B, and worse than IK4 F12 recorded. Preview of an ADD proposal on `reference-corpus/dispatch` exits **70**: `EVOLUTION PREVIEW REFUSED (70): safe reference descriptor traversal is unavailable or refused the model path`. `_load_model_bytes` writes the bytes into an empty temp directory, `load_model` cannot bind there, and `ReferenceInputError` is not among the caught errors. |
| One loader for seven sites | `_load_model_bytes` serves six (service.py lines 1216, 1544, 1659, 1839 and 1843, two of them pairs), and `_validated_candidate` the seventh. All can take one root. |
| Binding helper exists | `gnd.model.bind_references(model, root=)` uses a retained no-follow descriptor, and discover already calls it (`discover/service.py::_bind_references`). |
| Can a candidate change its references? | No evolve operation kind targets `reference_populations`, and preview refuses a candidate that differs from the replay of its operations. So a candidate's declarations equal the current model's. T3 still covers a reference that disappears. |
| Exit mapping | `EvolutionError` messages with "validation failed" already map to exit 3 (`evolve/cli_service.py:308`). |

## 13. Owner gate record (2026-10-26)

**Approval (o).** The owner was asked "Approve the IK4-Q2 spec r1 with its four
proposed rulings?" and replied "Approve IK4-Q2 spec r1 with all four proposed
rulings." on 2026-10-26. The approved bytes are spec r1 as committed in
`39ca1da`, before this section was added:

| Artifact | SHA-256 |
|---|---|
| `notes/phase-IK4-Q2-spec.md` (r1) | `3e5ce557539a76c18c888975bc8e17ee91adc3027753f7fa1e837b8305906301` |

**Rulings (o).**
- **D1:** this prose and the §8 test list are the instrument.
- **D2:** references resolve from the workspace model's directory.
- **D3:** IK5's `references` refusal stays.
- **D4:** branch `claude/ik4-q2-evolve-references` from B = `8f89af4`.

**Next.** The tests are committed red before the fix.
