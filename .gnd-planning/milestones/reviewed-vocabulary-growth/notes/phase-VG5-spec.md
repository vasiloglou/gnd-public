# Phase VG5 · one example, the pages and the replies · spec r1

## 1. Status

**Approved by delegated ruling (auto=true), 2026-11-23; implemented, recorded in [006-phase-VG5.md](../006-phase-VG5.md)** `(d)`, under the
owner's `process-milestone reviewed-vocabulary-growth auto` of 2026-11-23;
the driving agent's ruling, not the owner's reading. Implementation needs
VG1–VG4 in the branch (plan §3), GO1 on `main` and the milestone
coordinator's clearance (VG5 changes `unattended-growth.md`). Before the
first edit this spec is re-read against VG2's and VG4's records, and any
criterion they make unmeetable returns to this gate as an amendment.

## 2. Provenance

- Derives from [plan r4](reviewed-vocabulary-growth-plan.md), approved by the
  owner on 2026-11-23 ([plan gate](../001-plan-gate.md)): Goal (VG5), §1
  (H24–H26), §2 (VG5), §3 (VG5 row; "Other writers"), §4 (VG5-C1 to
  VG5-C4), §5, §9.
- The packaged growth example it sits beside: `src/gnd/examples/growth/`,
  `tools/build_growth_example.py`, `tests/test_growth_example.py`.
- Written by `process-milestone` on 2026-11-23 at `59289af6`, while GO1 runs.
  No review has read this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H24 | `gnd coverage` and `gnd evolve` resolve an include root; the route list of "Model includes" omits both | §6 pages; T3 |
| plan H25; #222 "Workaround" | the imported, proposed, deontic packaging, now an alternative | §6 growth page |
| plan H26 | the growth example's proposals rebuild byte-identically | T1 pattern |
| VG5-C1 | the example's proposals rebuild byte-identically and its two rounds apply | T1 |
| VG5-C2 | the grown root passes `gnd validate --require-documents` with both documents, `gnd check` over the example population, and `gnd judgments check` | T2 |
| VG5-C3 | the route list names every route a test shows resolving an include root | T3 |
| VG5-C4 | the three replies are drafted and name what is on `main` and what is not released | T4 |
| plan §5 | the growth page cites "Unattended source" and the D-12 home; `docs/agents/model-from-text.md` and `docs/agents/evolve.md` cite them | §6; T5 |
| coordinator note (2026-11-23) | the packaged-example inventories the guards name may also change in literature-reading-reference LR3 | before the PR, fetch `main` and rebase over those inventories |

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** The builder reads only its own committed inputs.
- **A cap bounds the algorithm (rule 2).** Inapplicable: no new layer; the
  example is small.
- **Validation order (rule 3).** Inapplicable: no new refusal.
- **One walk for N kinds (rule 4).** Inapplicable.
- **One home (rule 5).** The growth page's new section and the agents pages
  cite "Unattended source" (VG3, VG4) and "Evolve admission (D-12)" (VG2);
  they restate no rule. T5 reads them.
- **Measurement (rule 6).** The route list is read against routes a test
  runs (T3), not against prose.

## 5. Goal

`src/gnd/examples/seeded_growth/` holds a reviewed seed, an unattended root
that includes it and declares no document, two documents and two proposals
built by `tools/build_seeded_growth_example.py`. Round 1 declares the first
document and adds root-owned elements; round 2 attaches a `sample`
constraint to an included fact type. Both rounds apply; the grown root
validates with both documents, checks and judges. The pages describe it and
the three replies are drafted. The VG5 lane, guards and lint exit 0.

## 6. Design

- **The example** (`src/gnd/examples/seeded_growth/`): `seed.orm.yaml`
  (version 4, `explicit`, `confirmed`, `alethic` with `reviewed_in`, as
  issue 222's seed), `root.orm.yaml` (version 5, `unattended`,
  `reviewer: none`, no `documents`, the include, nothing of its own),
  `round-1.document.txt`, `round-2.document.txt`, `round-1.proposal.json`,
  `round-2.proposal.json`, `population.json`, and the judgments `policy.json`
  and `receipts.json` the README's last step reads. A README walks the
  rounds with the exact commands.
- **The builder** (`tools/build_seeded_growth_example.py`): deterministic,
  fixed ids, actor and timestamp, as `build_growth_example.py`. Round 1:
  `source-document` add, a value type, a fact type with spans and sample
  rows, each with spans over round 1's document. Round 2 binds the model as
  round 1 publishes it: a second `source-document` add and a `sample`,
  `proposed`, `deontic` uniqueness constraint with a span, attached to the
  seed's fact type (`host: included_fact_type`).
- **Pages.** `unattended-growth.md` gains "Starting from a reviewed
  vocabulary": include the seed, start with no document, what each round
  may add, what stays read-only, the `INCLUDE` line, and the imported
  packaging of issue 222 as the alternative when the seed cannot be
  included. The route list of "Model includes" names `gnd coverage` and
  `gnd evolve`. `docs/agents/model-from-text.md` and `docs/agents/evolve.md`
  link the section. One release-notes entry.
- **Replies.** `notes/issue-replies.md`: one reply each for #221, #222 and
  #218, naming the pull requests on `main` and that 0.4.0 does not carry
  them. The owner posts them (plan §5).

## 7. Decisions

Ruled by delegated approval (auto=true), 2026-11-23 `(d)`.

| ID | Question | Readings | Ruling |
|---|---|---|---|
| VG5-D1 | The example's folder name | `seeded_growth`, beside `growth` | as stated |
| VG5-D2 | Instrument | prose; the example itself is the corpus the README narrates | prose |

Budget: one diff review round (plan D7).

## 8. Tests

`tests/test_vg5_seeded_growth_example.py`, default lane.

| # | Criterion | Case | Expected |
|---|---|---|---|
| T1 | VG5-C1 | rebuild the two proposals into a copy; apply round 1 then round 2 with `gnd evolve preview`, `apply`, `finalize` | byte-identical proposals; every step exit 0 |
| T2 | VG5-C2 | the grown root: `gnd validate --document` (both) `--require-documents`; `gnd check` over `population.json`; `gnd judgments check` with the shipped policy and receipts | exit 0; the documented check exit; outcome 0 |
| T3 | VG5-C3 | every route the route list names, and `gnd coverage` and `gnd evolve preview`, run on the example root; every other route the list says refuses does refuse | each as the list says |
| T4 | VG5-C4 | `notes/issue-replies.md` holds one reply per issue, each naming its pull request(s) and "not released" | present |
| T5 | pages | the growth page section and the two agents pages link "Unattended source" and "Evolve admission (D-12)" | present |
| T6 | guards | every packaged-example inventory the guard block reads lists the new folder | the guard block exits 0 |

Ledger: the plan §9 VG5 lane
(`uv run pytest -q tests/test_vg5_seeded_growth_example.py tests/test_growth_example.py tests/test_unattended_growth_guidance.py tests/test_ir1_judgments_includes.py --tb=short`),
the guard block, `uv run ruff check src tests tools` and the component check,
all run; the packaged-example consumers (VG1's T1 over every loadable model,
the export tests that scan `src/gnd/examples/`) run as named at
implementation, since a new packaged model enters their scan.

## 9. Out of scope for this phase

- Posting the replies (the owner's).
- Any change to rules or routes; VG5 documents and exercises what VG1–VG4
  shipped.

## 10. Size

About 150 builder lines, 10 example files, 80 page lines, 200 test lines.

## 11. Approval instrument

This prose (VG5-D2).

## Implementation findings, recorded as they were found `(d)`

2026-11-23, at `b36b446d`. Re-read against VG2's and VG4's records before
the first edit: round 2's `sample`, `proposed`, `deontic` constraint is
what VG2 admits, and round 1's first-document add is what VG4 ships, so no
criterion changed.

1. **A receipt binds no reference identity for a model without references.**
   The first build bound `{"identity_version": 1, "references": []}` and
   `gnd judgments check` refused it as a stale subject: the check report
   carries no `reference_binding` for such a model, and the subject must
   equal it. The builder binds `null`.
2. **Two inventories name the new files.** `tests/test_mc1_guards.py`
   R30 lists every packaged include root (the new `root.orm.yaml` joins
   it), and `tests/test_packaged_skills.py` pins the skill link graph (the
   growth section's two citations join it as `VG5_GROWTH_EDGES`). These
   are the inventories literature-reading-reference LR3 rebases over.
3. **No cross-skill link from `gnd-orm-core` to `gnd-model-evolve`.** The
   new `gnd evolve` route row first linked the evolution contract; that
   edge is outside the pinned graph, so the row names the section in text.
4. **T3 is narrower than its row.** It runs `gnd coverage` and `gnd evolve
   preview` on the example root and shows `gnd codegen` refusing it; the
   routes the list already named are exercised on include roots by IR1–IR3
   and LX1–LX4, not again here.
5. **Paths through a symlink.** `gnd evolve` refuses a workspace whose path
   crosses a symlink (macOS `/var`); the tests copy the example under a
   resolved path. The README's commands run from a copy of the folder.
6. **Review r1 (Codex), F1, fixed at `0fc30381`.** The route list omitted
   `gnd discover`, which resolves an include root; the row is added.
7. **Review r1, F2, fixed at `0fc30381`.** T4 read a heading inside a fenced
   block as a reply boundary; it uses the fence-aware reader, now in
   `tests/support/markdown_sections.py`.
