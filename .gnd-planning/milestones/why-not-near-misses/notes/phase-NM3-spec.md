# Phase NM3: near-misses on the public why-not surface

**Status: r1, approved by the owner 2026-11-01 `(s3)`; implemented, record [003-phase-NM3.md](../003-phase-NM3.md).**

`(s3)` Owner approval, 2026-11-01, quoted: "Approve as proposed", in answer to
"Do you approve the NM3 spec with D1–D5 as proposed?" The answer was the offered
button whose stated meaning was approval with D1–D5 as proposed, no review panel
over the spec, and the go-ahead to implement. Approved bytes: SHA-256
`f836f123c1b5f6ce72ea5cb3ff82b44ee1c735b3b9305e150c32dda110c7e988` (before this tag). Rulings: D1 (a), D2 (a), D3 (a), D4 (a),
D5 (a); no spec review panel.

## Provenance

- Plan: [why-not-near-misses-plan.md](why-not-near-misses-plan.md) r3, approved
  `(a1)`: §0 (NM-R1..R8), §2.1 (payload, redacted view, enablement), §3 (homes),
  §4 NM3 (NM3-C1..C4), §5, §6, §9 NM3 row, and §10 rulings NM-D1, D5, D8, D15
  and D17.
- Prior phases: [001-phase-NM1.md](../001-phase-NM1.md) (kernel, flag off on
  every public path) and [002-phase-NM2.md](../002-phase-NM2.md) (disclosure
  mode), committed at `acfb9ae` and `23e4a99`.
- Checkpoint DC1b (2026-11-01, "Looks good") found that `DisclosureRefused` is
  not reachable from `gnd.api`. The owner asked for its export to be proposed
  here (D4).
- Harvest and measurements at `23e4a99`, by the author:
  - the why-not service, view, CLI and schema;
  - every site that pins `gnd-why-not/1` (`git grep`);
  - the docs pages that print why-not payloads;
  - a census of the 22 WN2 golden cases with the kernel flag forced on;
  - the kernel's output over the proposed spelling-gap population.

  No review has read this spec.

## Corrections to the plan, found at harvest

Recorded as refuted premises; the plan is repaired at milestone close.

| ID | Plan sentence | What the code shows | Repair here |
|---|---|---|---|
| H1 | NM3-C4: "the regenerated why-not outputs in that page and `python-api.md`" | `docs/reference/python-api.md:301-337` asserts two `samples` lists and prints one sentence. It prints no whole payload, so nothing in it changes with `/2`. Its sentence "The Python result carries raw values" is now mode-dependent, and the plan gives that edit to NM4. | `python-api.md` is not touched in NM3. Only `repair-a-missing-claim.md` prints whole payloads and is regenerated. |
| H2 | NM3-C2: regenerate `tests/fixtures/rf5-handlers/answers.json` | Its only why-not entry is the `refused`/`input-invalid` envelope (`answers.json:19`), which has no blocker. | One string changes there, `gnd-why-not/1` → `/2`. Nothing else. |
| H3 | NM3-C2: "`near_miss_count` ≥ the list length" | The kernel builds `min(5, g) × min(5, r)` pairs for a key with `g` binding groups and `r` row groups, which is at least `min(5, g·r)`, then keeps 5 (`why_not.py` `_near_misses`). So the list length is exactly `min(5, near_miss_count)`, truncated or not. | D2 proposes the exact tie. |

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| NM3-C1, O7 | the service enables the search; CLI and API emit the three fields in both views and honour the mode | `why_not_result`; `why_not_view`; T2–T5 |
| NM3-C2, NM-D8 | `gnd-why-not/2`: the three fields, required only on `atom`, `oneOf` list/`"redacted"`, the count tie, `"redacted"` in the redacted clause; five named negatives; regenerated goldens, RF5 answers and docs outputs | schema; T1, T6, T7; H2 |
| NM3-C3, O4 | the spelling-gap example and a repair test built only from payload fields, with a negative control | `examples/quoted_claims/spelling-gap.pop.json`; T8 |
| NM3-C4, O12 | the normative near-miss section in `docs/reference/why-not.md` (one home of `N` and the rule, including that the truncation flag is false at default limits); the how-to section "When the values are spelled differently"; regenerated outputs; a release-note entry with the `/2` migration line; docs gates exit 0 | Docs; T12 |
| NM-R1 | exact matching stays the meaning: status, blocker, counts, `work` and exit unchanged | T1 (census over every golden) |
| NM-R2 | one normalization, one home | the home moves to `why-not.md` (Docs); the NM1 spec's text yields |
| NM-R3 | bounded, deterministic | kernel unchanged; T1 checks byte-stable output |
| NM-R4, NM-R6 | disclosure decided once, after the verdict; `customer` withholds the pairs and refuses `--raw`; the count stays (NM-D17) | the NM2 projection, unchanged; T5 |
| NM-R5 | the unset mode changes only the `/2` payload, which is a released exception | T1; release note |
| NM-R7 | layering and query policy | T14 |
| NM-R8 | anonymity | T14 |
| NM1-Q1 | the representative is the first in canonical byte order, not the "smallest form" | the normative text (Docs) |
| NM1-Q2 | `samples` keep the first-seen value and `near_misses` the canonical minimum | D3 |
| NM1-Q3 | a flag-on census over the WN2 golden corpus | measured at harvest (below); T1 makes it a test |
| DC1b | `DisclosureRefused` from `gnd.api` | D4; T10 |
| §9 NM3 row | the gate command | Verification selection |
| H1–H3 | harvest corrections | Docs; T15; D2 |

### Census measured at harvest (NM1-Q3)

The kernel's `explain` was called with `near_misses=True` through
`api.why_not` for every case in `tests/fixtures/why_not/cases.json`. After the
three fields were removed, each of the 22 payloads was byte-equal to its
committed raw golden (minus `view`). Every atom blocker reported
`(near_miss_count, near_miss_truncated, len(near_misses)) = (0, false, 0)`:
one each in g1, g14 and g19, two in g2 and eight in g9. No non-atom blocker
carried a field. The existing corpus therefore cannot fail a non-empty report.
The new case g20 below is that case.

## Standing rules bound to this phase

1. **Totality.** No new input is read. `why_not_view` projects payloads that
   only the kernel produces. The three fields are copied only when they are
   present, so a non-atom blocker cannot gain them. Hostile model and
   population inputs reach the same intake ceilings as at `23e4a99`, and
   T1's refused cases (g10–g13) still refuse.
2. **The input cap bounds the algorithm.** The search's cost and its own cap
   are NM1's (NM-R3, NM1 T10–T12). NM3 adds only a projection that is linear
   in the payload. Nothing new scales with untrusted input, so no new
   time-bound test is needed.
3. **Validation order.** It is unchanged. Intake runs, then the kernel, then
   the projection. Disclosure refusals precede the handler (NM2 T9–T11).
4. **One walk.**
   - One switch: the service passes `near_misses=True`, and no flag or option
     is added.
   - One projection, `_why_not_clause`, serves every blocker at every descent
     depth.
   - One schema `$defs/blocker` rule covers every atom blocker.
5. **One home.**
   - `docs/reference/why-not.md` becomes the one home of `N`, eligibility and
     the pair rule. The NM1 spec's normative text yields to it. The spec is
     append-only, so a finding records the move.
   - The release note and the how-to cite the reference, not restate it.
6. **Measurement over argument.** The census above settles the inertness
   question, and T1 keeps it settled. H3 was confirmed against the kernel's
   pair-building code. D2's tie is also checked by T7 (a negative per side) and
   by the NM1 generated corpus (T13).

## Goal

- `uv run pytest -q tests/test_why_not_near_misses_public.py
  tests/test_public_why_not.py tests/test_why_not_repair_loop.py` exits 0.
- `gnd why-not` and `gnd.api.why_not` return `schema_version: "gnd-why-not/2"`
  on every path, including refusals. Every atom blocker carries
  `near_miss_count`, `near_miss_truncated` and `near_misses`. The redacted view
  shows the two counters and `near_misses: "redacted"`.
- The 22 existing goldens change by exactly the schema version and the three
  zero-valued fields per atom blocker.
- Under `customer`, `api.why_not` returns the redacted view and `--raw` exits 3.
- The NM3 gate in Verification selection exits 0.

## Design

### `src/gnd/witness/service.py` (about 3 lines)

- `_why_not_envelope`: `"schema_version": "gnd-why-not/2"`.
- `why_not_result`: `explain(model, candidate, fact_type, row=row,
  references=context, near_misses=True)`.

The public `why_not` is unchanged. Under `customer` it already returns
`{**why_not_view(raw), "view": "redacted"}`, so the pairs are withheld by the
projection below.

### `src/gnd/witness/view.py` (about 6 lines)

```python
_WHY_NOT_BLOCKER = (
    "kind", "index", "fact_type", "count", "derivation", "ground",
    "asserted_not_read", "sample_count", "near_miss_count", "near_miss_truncated",
)

def _why_not_clause(clause):
    ...
    blocker["samples"] = "redacted"
    if "near_misses" in clause["blocker"]:
        blocker["near_misses"] = "redacted"
```

Key order does not matter, because the CLI serializes with `sort_keys=True`.

### `src/gnd/why-not.schema.json` (about 90 JSON lines)

- `title` becomes "GND why-not explanation (gnd-why-not/2)". The description
  gains one sentence on near-misses. `properties.schema_version` becomes
  `{"const": "gnd-why-not/2"}`. `$id` is unchanged, and the file is replaced in
  place (D5).
- New `$defs/near_miss`:

```json
"near_miss": {
  "type": "object", "additionalProperties": false,
  "required": ["roles", "sample", "candidate"],
  "properties": {
    "roles": {"type": "array", "minItems": 1, "uniqueItems": true,
              "items": {"type": "string"}},
    "sample": {"type": "object", "minProperties": 1},
    "candidate": {"type": "object", "minProperties": 1}
  }
}
```

- `$defs/blocker.properties` gains:

```json
"near_miss_count": {"type": "integer", "minimum": 0},
"near_miss_truncated": {"type": "boolean"},
"near_misses": {"oneOf": [
  {"type": "array", "maxItems": 5, "items": {"$ref": "#/$defs/near_miss"}},
  {"const": "redacted"}
]}
```

- `$defs/blocker` gains an `allOf` with three parts.
  - **The atom rule:**

    ```json
    {"if": {"properties": {"kind": {"const": "atom"}}, "required": ["kind"]},
     "then": {"required": ["near_miss_count", "near_miss_truncated", "near_misses"]},
     "else": {"not": {"anyOf": [{"required": ["near_miss_count"]},
                                {"required": ["near_miss_truncated"]},
                                {"required": ["near_misses"]}]}}}
    ```

  - **The count tie (D2 (a)):** a list of length `k < 5` requires
    `near_miss_count == k`, and a list of 5 requires `near_miss_count ≥ 5`.
    These are six `if`/`then` clauses: for each `k` in 0..4,
    `if near_misses is an array with minItems k and maxItems k then
    near_miss_count const k`; and `if near_misses is an array with minItems 5
    then near_miss_count minimum 5`.
  - **The redacted side:** a `"redacted"` list carries no count tie, but the
    count is still an integer ≥ 0.
- `$defs/redacted_clause.properties.blocker.properties` gains
  `"near_misses": {"const": "redacted"}`. The existing top-level rule that
  applies `redacted_clause` when `view` is `redacted` therefore rejects a raw
  list in the redacted view, at any descent depth, through the recursive
  `descent.clauses` reference already in that `$def`.

The schema's spelling of the fields matches the kernel's
(`near_miss_count`, `near_miss_truncated`, `near_misses`, `roles`, `sample`,
`candidate`; `why_not.py` `_near_miss_pair` and `_atom_blocker`). T6 validates
real payloads against it, and T7 fails it on each negative.

### `src/gnd/api.py` and `src/gnd/disclosure.py` (D4 (a), about 3 lines)

- `api.py`: `from gnd.disclosure import DisclosureRefused`, and
  `"DisclosureRefused"` is appended to `__all__` after `"why_not"`, keeping the
  approved stable order.
- `disclosure.SURFACES` moves `"api:DisclosureRefused"` into the value-free
  class list beside `ReceiptRefused`. The NM2 totality test (T13 there) would
  otherwise fail on the new public name, so the row is required.

### Example: `src/gnd/examples/quoted_claims/spelling-gap.pop.json` (NM3-C3)

This is `gap.pop.json` with three `authored` rows:

```json
"authored": [
  {"work": "FIELD NOTES", "person": "Ada Byrne"},
  {"work": "Field notes", "person": "Bo Lin"},
  {"work": "Letters Home", "person": "Ada Byrne"}
]
```

Each row has a different role in the story:

| Row | What it is | What it shows |
|---|---|---|
| `FIELD NOTES` / `Ada Byrne` | the near-miss | `work` is spelled differently, `person` matches exactly |
| `Field notes` / `Bo Lin` | the negative control | `work` near-matches, but the other bound role, `person`, differs |
| `Letters Home` / `Ada Byrne` | a distractor | `person` matches, but `work` names another work |

The claimed row is `certified(q-17, Ada Byrne)` (`claim.json`, unchanged). The
measured row-mode blocker, raw, with only the near-miss fields shown (the rest
is as in the gap case, with `sample_count: 1`):

```json
{"kind": "atom", "index": 1, "fact_type": "authored",
 "near_miss_count": 1, "near_miss_truncated": false,
 "near_misses": [{"roles": ["work"],
                  "sample": {"person": "Ada Byrne", "work": "Field Notes"},
                  "candidate": {"person": "Ada Byrne", "work": "FIELD NOTES"}}]}
```

`work` was `{"pre_joins": 3, "joins": 1, "probes": 7, "binding_cells": 3}`.
In rule mode (no `--row`), `Letters Home` joins, and the blocker is
`reviewed`, with no rows and `(0, false, [])`.

The example's `README.md` gains one line naming the file.

### Docs (NM3-C4)

- **`docs/reference/why-not.md`**, a new section "Values spelled differently"
  after "The blocker". It is the normative home. Its outline follows DC1, with
  real payloads:
  - what a near-miss is, and that matching stays exact;
  - `N`, in four steps, with the Unicode-database sentence and the three
    consequences (`ACME-CORP`/`ACMECORP`, `Acme . Corp`, `℅`);
  - the eligible rows and the one stated relaxation;
  - the pair rule and `roles`;
  - counting, and the representative, described as **the first in canonical
    byte order** (NM1-Q1);
  - `near_miss_count`, `near_miss_truncated` and the five shown pairs;
  - that the flag is false at default limits;
  - that an empty list with count 0 means "searched, none";
  - the redacted view.
- **The same page's "Limits" section** gains the near-miss inspection cap
  (200,000, its own counter, not part of `work`).
- **The same page's "Values in the answer" section** gains one sentence on the
  three fields in the redacted view. How the disclosure mode applies is NM4's
  (plan NM4 table).
- **`docs/how-to/repair-a-missing-claim.md`**:
  - The whole-payload outputs are regenerated (three fields on each atom
    blocker, `/2`).
  - A new section, "When the values are spelled differently", is added before
    "What the answer does not tell you". It runs `gnd why-not` with `--raw` over
    `spelling-gap.pop.json`, shows the pair, fixes the spelling, and asks
    again. Every block is `gnd-run`.
- **`docs/release-notes.md`**: a new top entry, "Unreleased: near-miss values
  in why-not". It describes the three fields, that matching is unchanged, the
  redacted view and the cap. Its migration line reads: "`gnd-why-not/1`
  consumers: the schema is closed, so read `schema_version` and accept `/2`.
  Atom blockers carry three new required fields; nothing else changes." The
  disclosure-mode note is NM4's.

### Regenerated fixtures

- `tests/fixtures/why_not/goldens/*.json`: all 45 files (22 cases × 2 views,
  plus `refused-input.json`). They are regenerated by the WN2 builder's method
  (`evidence/WN2/build_goldens.py`, run against the new code, writing into a
  scratch directory). T1 then checks the diff mechanically, so it does not
  need reading.
- New case `g20-spelling-gap`, exit 0, and its two goldens. Its argv is
  `why-not <fx>/spelling/model.orm.json <fx>/spelling/spelling-gap.pop.json
  --fact-type certified --row <fx>/spelling/claim.json`.
  - `tests/fixtures/why_not/spelling/` holds byte copies of the example's
    `model.orm.json`, `spelling-gap.pop.json` and `claim.json`. The WN2 fixture
    model in `claims/` is a different model, so the copies are needed.
  - The existing `<fx>` substitution then suffices.
  - T2 asserts that the three copies equal the packaged example's bytes, so
    the two cannot drift apart.
- `tests/fixtures/rf5-handlers/answers.json`: one string (H2).

### Successor evidence

The RF4 identity and body pins do not cover `why_not_result` or the view
(measured: neither name appears in the source-successor file). The RF6
dynamic-query census may count the changed lines. If it does, a successor row
is added in `evidence/NM3/`, as in NM1 and NM2, and recorded as a finding.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 `(s3)` | Approval instrument (plan NM3: corpus-first, "as WN2") | (a) This spec is the corpus's narration: g20's measured blocker (Design), the census rule (T1) and the eleven schema negatives (T7) are the expected answers. The harness and the g20 goldens are committed red as the first implementation commit, before any source file changes, as NM2 did. (b) A separate committed corpus directory with a README and a split answer key, authored before this gate: it restates the same items and allows a blind reader, which this phase does not plan. | **(a)** |
| D2 `(s3)` | The count tie (H3) | (a) Exact: length `k < 5` ⇒ count `== k`; length 5 ⇒ count ≥ 5. Rejects payloads the kernel cannot produce, such as count 7 with 3 pairs or count 1 with none. Six `if`/`then` clauses. (b) The plan's floor, count ≥ length: five clauses; accepts both of those payloads. Either way an exit code never changes; the difference is which malformed payloads a consumer's validator catches. | **(a)** |
| D3 `(s3)` | NM1-Q2: in one blocker, `samples` show the first-seen value of an identity group, and `near_misses` show the canonical minimum, so `1` and `1.0` can both appear for one group | (a) Keep both and document the difference in the normative section: no existing `samples` byte changes (T1 holds). (b) Make `samples` use the canonical minimum too: changes `samples` for mixed-identity groups, a WN2 contract change outside this milestone's plan. | **(a)** |
| D4 `(s3)` | `DisclosureRefused` from `gnd.api` (DC1b) | (a) Append to `__all__`, with a value-free `SURFACES` row: one public name, and the public-API pin (`test_public_api.py:16`) changes. (b) Bind it on `gnd.api` outside `__all__`, like `judgments`: reachable but not declared stable. (c) Leave it in `gnd.disclosure`, and document catching `ValueError`. | **(a)** |
| D5 `(s3)` | The schema file under `/2` | (a) Replace `why-not.schema.json` in place: same path and `$id`, `title` and `schema_version` const name `/2`, and a release-note migration line. (b) Ship `/1` and `/2` side by side: two homes for one contract, and no `/1` producer remains. | **(a)** |

## Tests

New tests are in `tests/test_why_not_near_misses_public.py` unless stated.
Every expected exit is literal.

| ID | Case | Expected |
|---|---|---|
| T1 | Census (NM-R1, NM1-Q3), for each of the 22 WN2 cases: take the new raw and redacted goldens; remove `near_miss_count`, `near_miss_truncated` and `near_misses` from every atom blocker at every depth; set `schema_version` to `/1` | equal to the golden at `23e4a99` (read with `git show 23e4a99:<path>`); every atom blocker carried all three fields with `(0, false, [])` raw and `(0, false, "redacted")` redacted; no other blocker carried any; status, exit and `work` equal |
| T2 | `tests/test_public_why_not.py` T1 over the regenerated goldens plus g20, both views, CLI and API; the `spelling/` copies equal the example's bytes | exit and bytes equal; copies equal |
| T3 | g20 raw: the atom blocker of clause 0 | exactly the Design block: count 1, truncated false, one pair with `roles: ["work"]` |
| T4 | g20 redacted view | count 1, truncated false, `near_misses: "redacted"`; none of `FIELD NOTES`, `Field notes`, `Field Notes`, `Ada Byrne`, `Bo Lin`, `Letters Home` occurs in stdout |
| T5 | Mode over g20: `api.why_not` under customer, internal and unset; `gnd --disclosure internal why-not …`; `GND_DISCLOSURE=customer gnd why-not … --raw` | customer equals the redacted golden payload with `view`; internal and unset equal the raw golden payload minus `view`; the CLI with `internal` equals the `--raw` golden; the customer `--raw` call exits 3 with empty stdout |
| T6 | Schema positives: every golden, g20 in both views, and the T5 API payloads | valid under `/2` |
| T7 | Schema negatives, each a one-edit mutation of a g20 or g1 golden: N1 a raw list under `view: redacted`; N2 a nested descent clause with a raw list under `view: redacted` (from g2); N3–N5 each of the three fields removed from an atom blocker; N6 `near_miss_count` added to the g15 `negated` blocker; N7 count 0 with one pair; N8 six pairs with count 6; N9 count 3 with one pair (D2); N10 a pair with `roles: []`; N11 a pair with an extra key; N12 `schema_version: "gnd-why-not/1"` | each invalid; a control asserts the unmutated payload is valid |
| T8 | `tests/test_why_not_repair_loop.py`, new test: from `spelling-gap.pop.json`, using only payload fields | `api.why_not` blocks at `authored` with one pair. The loop rewrites the population row equal to the pair's `candidate` to the pair's `sample` values (it finds the row by `candidate` alone). Asked again, the blocker is `reviewed` with `(0, false, [])`. The loop then adds the `reviewed` row from `extracted.json`, as the existing loop does. Asked again, the status is `derived`, and `api.witness` over the claim exits 0. Negative control: no pair names `Bo Lin` or `Letters Home`, and those rows are untouched. |
| T9 | `why_not_view` over a synthetic kernel payload with `near_miss_truncated: true`, count 9 and five pairs, plus a `negated` blocker | the atom blocker keeps true, 9 and `"redacted"`; the negated blocker gains no field |
| T10 | D4: `api.DisclosureRefused is gnd.disclosure.DisclosureRefused`; `api.__all__[-1] == "DisclosureRefused"`; `SURFACES["api:DisclosureRefused"].kind == "value-free"`; `tests/test_public_api.py` with its updated pin | true; exit 0 |
| T11 | g20 rule mode (no `--row`), raw, through `api.why_not` | blocker `reviewed`, `(0, false, [])`; status `blocked`, exit 0 |
| T12 | Docs: `uv run python tools/run_tutorials.py`, `uv run zensical build --strict`, `uv run python tools/check_docs.py site`, `uv run pytest -q tests/test_documentation_tutorials.py tests/test_plan_app_docs.py` | each exits 0; the new how-to section's blocks are among those executed |
| T13 | NM1's generated corpus (`tests/test_why_not_oracle.py`): every kernel report validated as a blocker fragment against the `/2` `$defs/blocker` | valid; T18's floor of 46 non-empty reports still holds, so D2's tie is checked on real non-empty reports |
| T14 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py`, `tests/test_why_not_anonymity.py`, `tests/test_disclosure_mode.py` | exit 0, zero new allowances |
| T15 | `tests/test_rf5_handler_pins.py`, `tests/test_rf5_commands.py` with the one-string `answers.json` change | exit 0 |

Every branch has a case that can fail it:

| Branch | Case |
|---|---|
| atom blocker with fields | T3, N3–N5 |
| non-atom blocker without fields | T1, T9, N6 |
| a non-empty raw list | T3 |
| an empty raw list | T1 |
| redacted top level | T4, N1 |
| redacted inside a descent | T1 (g2), N2 |
| count tie, `k < 5` | N7, N9 |
| count tie, `k = 5` | N8, T13 |
| truncated true in the view | T9 |
| a refused envelope at `/2` | T1 (g10–g13), T15 |
| customer, internal and unset | T5 |

### Verification selection

| Obligation | Disposition | Command | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Plan §9 NM3 row (mandated) | run | the NM2 gate (`uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_disclosure_mode.py tests/test_public_api.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py`) plus `tests/test_why_not_near_misses_public.py tests/test_why_not_repair_loop.py tests/test_documentation_tutorials.py tests/test_plan_app_docs.py`, then `tools/run_tutorials.py`, `zensical build --strict`, `tools/check_docs.py site`; each exits 0 | service, view, schema, `api.py`, `disclosure.py`, the example, goldens, docs | the plan's row | any of those files |
| Schema inventories | run | `uv run pytest -q tests/test_public_built_inventory.py` plus every test that imports `tests/support/runtime_schema_inventory.py` or that `git grep why-not.schema` finds at implementation; exit 0 | `why-not.schema.json` | they list or digest packaged schemas | a schema change |
| Installed docs | run | `uv run python tools/check_installed_docs.py`, exit 0 | the example directory and docs | the example gains a file | an example change |
| Broad default suite | cadence | milestone close, on explicit owner selection | whole repository | every changed path is covered above | an owner selection |

### Implementability sweep (before the gate)

Each requirement was checked against `23e4a99`:

- **Enablement is one keyword.** `explain(..., near_misses=True)` exists
  (NM1), and the census ran it through `api.why_not` unchanged.
- **The census rule holds today.** Measured: 22 of 22 equal after removing the
  fields.
- **g20 produces exactly one pair, with the negative control silent.**
  Measured (Design).
- **The count tie can be expressed.** Draft 2020-12 supports `if`/`then` with
  `minItems`/`maxItems` on an array branch. A non-array value fails the `if`,
  so the redacted string is not constrained. jsonschema 4 is already used by
  T2 in `test_public_why_not.py`.
- **The redacted rule reaches nested clauses.** `redacted_clause` already
  recurses through `descent.clauses` (schema at `23e4a99`).
- **D4 can be applied.** The NM2 totality test enumerates `gnd.api`'s public
  names (`dir` minus private), so the new name must get a row. The RF1 CLI
  goldens do not list API names.
- **The docs runner can run the new section.** The how-to already copies
  `examples/quoted_claims` and runs `gnd why-not --raw` blocks.

No requirement was found that no implementation can satisfy.

## Out of scope for this phase

- How the disclosure mode applies on any docs page, `disclosure.md`, the
  disclosure how-to, and the disclosure release note (NM4).
- Any other page in the NM4 inventory, including `python-api.md` (H1).
- A CLI or API switch to turn the search off.
- Near-misses on negated atoms, comparisons and heads (NM-D6).
- Changing `samples` to canonical minima (D3 (b)).
- Fuzzy, edit-distance or locale-aware matching.

## Size

About 15 source lines (service, view, `api.py`, `disclosure.py`), about 90
schema lines, one example file. About 300 test lines. 47 regenerated golden
files and one RF5 string. Docs: one new reference section of about 80 lines,
one how-to section of about 60 lines, regenerated how-to outputs, and one
release-note entry.

## Approval instrument

This prose, as the narration of the corpus (D1 (a)). No review panel is
planned over the spec. One local reviewer will read the phase diff.
