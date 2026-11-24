# Phase LR2 · where a quote may lie · spec r1

## 1. Status

r1, 2026-11-23, written by `process-phase` under `auto=true`. The spec gate
is §12. Started on the coordinator's "GO LR2" (2026-11-23), built on the LR1
branch (PR 243), with these conditions: keep the `docs/literature/commands.md`
edit away from PR 241's "Drive it from your host" passage, and keep the
example README edit outside its admission section.

## 2. Provenance

[Plan r4](literature-reading-reference-plan.md): Goal (LR2), §0 (R0.1,
R0.4, R0.6), §1 (H7–H11, H19, H21), §2 LR2, §3 (LR2 homes), §4 (LR2-C1 to
LR2-C5), §5 (issue reply), §6 (the "any text is evidence" risk), §9 (LR2
lane), D2 (b) and D5. [#226](https://github.com/vasiloglou/gnd-public/issues/226)
request 2. Code read at `70632449`: `src/gnd/anchors.py:238-271`,
`docs/reference/anchors.md`, `src/gnd/examples/literature/reading.py:258-286`
and `:390-395`, `docs/literature/index.md:11`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| H7; #226 request 2 | say whether a quote must lie inside the shown section | §6 anchors.md section; T1, T2 |
| H8, §7 | no quote concept is added to the example | §6 "What does not change" |
| H9 | the example verifies the joined attempted sections, or `conflict.txt`, with an extraction sidecar and no anchor sidecar | §6 README paragraph; T5 |
| H10 | a span binds to the document `document_sha256` names; `block_id` and `unit_id` are free labels | §6; T1–T3 |
| H11 | sections are byte ranges of a source | §6 host paragraph |
| H19, R0.1 | no anchor or verify format change | §6; no code change |
| H21 | `index.md:11` ("tied to its passage") cites the rule | §6; T4 |
| R0.4, LR2-C4 | the packaged reading run is byte-identical | no example code changes; `tests/test_ld3_reading_workflow.py` in the lane |
| R0.6, LR2-C1 | the rule has one home, `anchors.md`; the literature pages cite it | §6; T4 |
| LR2-C2 | a quote from the second section binds when the sidecar names the whole source | T1 |
| LR2-C3 | the same quote is refused `anchor:binding-mismatch: source span or excerpt differs` when the sidecar's document is the first section alone | T2 |
| LR2-C5 | README and `index.md:11` | T4, T5 |
| §5, D5 | the interim reply draft to #226 | `notes/issue-reply.md` |
| §6 risk | "anywhere in the document" is not "any text is evidence" | §6: the section cites the page's opening, which says an anchor proves no entailment |

## 4. The standing rules, bound to this phase

- **Totality (1), cap (2), order (3), N kinds (4):** inapplicable. No code
  that reads input is added; the phase adds pages and a test.
- **One home (5):** the rule is one sentence in `anchors.md`; T4 holds that
  no other page under `docs/` or `src/gnd/skills/` states it and the
  literature pages link it.
- **Measurement (6):** T1–T3 run the real `gnd check --anchors --document`.
- **General solutions (`AGENTS.md`):** no new matcher. The test builds
  sidecars with `gnd.anchors.vocabulary_digest` and the JSON loader; pages
  are checked for one fixed sentence and one fixed link target, not parsed.

## 5. Goal

A host reading the anchor reference learns that a span may lie anywhere in
the document the sidecar's digest names, and the literature pages tell it
what that means when it shows a model one section at a time. A test holds
both sides of the rule, and the branch that refuses.

## 6. Design

### Reuse

| Capability | Search | Found | Decision |
|---|---|---|---|
| bind a span to a document | `git grep -n bind_anchors src` | `src/gnd/anchors.py:238` | reuse; unchanged |
| a minimal anchored model | `git grep -n "type: anchored" tests` | `tests/test_anchor_sidecar_v2.py:191` (`_synthetic`) | the same model text, written in the test |
| vocabulary digest | `gnd.anchors.vocabulary_digest` | | reuse |

### `docs/reference/anchors.md`: "Where a span may lie" (about +12 lines)

After "The file": a span may lie anywhere in the document whose SHA-256 is
`document_sha256`; GND has no notion of a section or of what a model was
shown. `block_id` and `unit_id` may record that, and GND does not check
them. The opening paragraph's limit stands: a bound span shows where a
value occurs, not that the text supports the fact.

### `docs/literature/commands.md` (about +8 lines)

After the anchor check's output block in Act 2 (the time-step example), far
from PR 241's Act 3 passage: a host that shows its model one section at a
time and wants quotes from anywhere in a paper names the whole source
version as the anchor document and records the shown section in
`block_id`; naming the shown section alone refuses a quote from another
section with `anchor:binding-mismatch`. One link to the rule.

### `docs/literature/index.md:11`

"GND keeps each claim tied to its passage" becomes "GND keeps each claim
tied to its passage in the document version it was read from", linking the
rule.

### `src/gnd/examples/literature/README.md`, "Replayable reading"

One paragraph (outside the admission section): the reading example
verifies the attempted sections of each pass joined with newlines, and
`conflict.txt` for the reported conflict; each verify binds its document by
digest in an extraction sidecar, and the example writes no anchor sidecar,
so it is not a model for anchoring quotes. Absolute URL to the rule.

### `docs/release-notes.md`, `notes/issue-reply.md`

One release-notes bullet. The interim reply draft covers requests 3 (LR1)
and 2 (LR2) and says request 1 waits for LR3.

### What does not change

`src/gnd/anchors.py`, the sidecar schema, `gnd verify`, `gnd check`; the
reading example's code, fixtures and outputs.

## 7. Decisions, ruled under `auto=true`

| ID | Question | Ruling |
|---|---|---|
| LR2-D1 | plan open question: is `block_id` the recommended place for the shown section | yes; it is the existing free label, and no new convention is added |
| LR2-D2 | where the host guidance goes | `docs/literature/commands.md`, after the Act 2 anchor check, the page where a host first meets an anchor in the literature story |

## 8. Tests

New `tests/test_lr2_quote_scope.py`, default lane. A two-section document
(section A, then section B holding the quoted value), a one-fact
population, and the anchored model of `test_anchor_sidecar_v2._synthetic`.

| # | Case | Expected |
|---|---|---|
| T1 | sidecar names the whole document; span on the value in section B; `block_id` names section A (the shown section) | `gnd check` exit 0; the anchored verdict passes |
| T2 | document is section A alone; sidecar `document_sha256` is section A's; same span and excerpt | exit 3; stderr or issues carry `anchor:binding-mismatch: source span or excerpt differs` |
| T3 | document is section A alone; sidecar names the whole document | exit 3, `anchor:binding-mismatch: digest differs`. T2 and T3 tell the span rule from the digest check |
| T4 | the rule's sentence | once in `docs/reference/anchors.md`, on no other page under `docs/` or `src/gnd/skills/`; `docs/literature/index.md` and `docs/literature/commands.md` link `../reference/anchors.md#where-a-span-may-lie` |
| T5 | the example README | names `conflict.txt`, "no anchor sidecar" and the absolute link to the rule |

Branch table: the binding has three outcomes the rule speaks to (bound,
span refused, digest refused); T1–T3 reach each. `block_id` naming another
section than the span's is in T1, so a check that tied spans to `block_id`
would fail it.

Gate:

```bash
uv run pytest -q tests/test_lr2_quote_scope.py tests/test_anchor_sidecar_v2.py tests/test_ld3_reading_workflow.py tests/test_documentation_tutorials.py --tb=short
```

`tests/test_documentation_tutorials.py` joins the plan's lane because
`commands.md` and `index.md` are tutorial and link-checked pages. Plus the
guard block, `uv run ruff check` and the component-index check.

## 9. Out of scope

A quote or claim concept in the reading example; a section concept in GND;
the 38 claims #226 dropped for a participant or predicate not in the quote
(the reporter's host rule); LR3.

## 10. Size

About 30 page lines, about 120 test lines, 0 source lines.

## 11. Approval instrument

This prose and §8's expected exits and messages.

## 12. Spec gate

Delegated approval (`auto=true`), 2026-11-23, under the milestone delegation
in [001-plan-gate.md](../001-plan-gate.md). Instrument: this prose. No spec
review. No paid call. Compatibility: no format or code change. The SHA-256 of
these bytes is in the phase record; implementation findings are appended as
§13.

## 13. Implementation findings

- **F1, population label.** The first T1–T3 run exited 3 because the test
  population's `label` was not one of `conforming`, `boundary`, `violating`;
  the fixture now uses `conforming`.
- **F2, review round 1.** T5 checked only two of the README's four claims;
  it now checks all four over whitespace-normalized text.
