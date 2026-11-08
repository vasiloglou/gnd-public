---
milestone: rule-check-followups
station: phase-FU3
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-FU3
date: 2026-11-07
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_fu3_*.py tests/test_rc2_acyclic_extent.py"
  exit: 0
  output: "46 passed"
  note: >-
    The plan section 9 FU3 row (V2), at a5e46e74. The mutant, the component
    index check (V6) and the sharded full default suite against the base
    failure list (V3) are in the body.
evidence:
  - path: tests/test_fu3_derived_ring.py
    sha256: 7f4fba87fe2de61bdbd17e8c5afa96c0b0414a1932d5e2c569b989d0188996ec
  - path: tests/fixtures/fu3-derived-ring/README.md
    sha256: 396fd482a99913c835a2bc54babf40f7734404c69f0bb2b85417e6f379a60163
  - path: tests/fixtures/fu3-derived-ring/models/ring.orm.yaml
    sha256: e503ab24917973184e26c5e32a635cd80320fbd9278f171191d3e4db6abf41f0
  - path: tests/fixtures/fu3-derived-ring/expected/exits.json
    sha256: 2087f703499cb28af4269468c1de9962465fb74be08e31484f1d24d961b87570
  - path: dev/components/COMPONENTS.md
    sha256: c84272f0183770a4783b86c0842d676348c524855c425229df803f08123e0c69
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU3-spec.md
    sha256: c3bf199fa3fb82e044d1593d0a20b9b5aff75f75d3bbe5cfd73d2010ac1a6ed0
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU3-codex-review.md
    sha256: 3ba1c2fc7f744a64938d20b332455c13d7465ae34a7dd76ea521d2b5646307cf
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU3/full-suite-fu3-528887ec.txt
    sha256: fabd81c26f4701a7a0d91b7751591bddbc415791b332c919c81595ecbb985a5b
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU3/full-suite-fu3-a5e46e74.txt
    sha256: ac385494f3f78deca9ed875f99c938a59dbd5a8b1f50e09fec2255ba3bba35cc
---

# Claim

At a5e46e74, under `gnd check --rule-ids`, a failing `acyclic` ring over a
fact type derived through an exact term lists exactly the in-group edges of
the stated facts of that fact type, which are the pairs the checker judges
(spec D2); a ring the checker passes or cannot check gets no listing, and
every version-7 report is unchanged. No source file changed: the checker
and `correspondence.acyclic_extents` already read the same view
(`extensions.constraint_view_legacy`), and the phase pins that with a
corpus (issue 119).

## What shipped

- **Corpus** `tests/fixtures/fu3-derived-ring/` (approved at 11aef429): a
  model deriving `leads` with a `mod` term and an `acyclic` rule on it;
  five cases (`agree`, `add-disjoint`, `asserted-only`, `derived-only`,
  `mod-zero`) and the successor case `self-loop` (review R2); version-15
  and version-7 answers recorded from reports, not from an implementation.
- **Tests** `tests/test_fu3_derived_ring.py`, T1-T6, 20 cases.
- **Component index**: `check.snapshot_decision` lists
  `tests/test_rc2_acyclic_extent.py` and the FU3 test.
- **Records**: the FU2 size ruling (FU2-O1, accepted by the owner's merge
  of PR 126).

## Gate output (verbatim)

V2, at a5e46e74:

    uv run pytest -q -p no:cacheprovider tests/test_fu3_*.py tests/test_rc2_acyclic_extent.py
    46 passed in 2.68s

FU3 tests at each stage (`uv run pytest -q tests/test_fu3_derived_ring.py`):

    11aef429 (corpus, approved):                        17 passed
    mutant, extent reads the derived extension:          2 failed, 15 passed (T1, T2 on asserted-only)
    self-loop case against the old T2 oracle:            1 failed, 19 passed
    528887ec (reachability oracle):                     20 passed
    a5e46e74 (ruamel.yaml, spec I4):                    20 passed
    mutant again, at 528887ec:                           2 failed, 18 passed

V6, component index:

    python3 scripts/components_index.py changed --base 1e63aeb5 --strict
    changed against 1e63aeb5 (1e63aeb): 29 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    exit=0

V3, full default lane, six round-robin shards on beast-3 (run although no
source changed, because a new fixture directory is visible to
repository-wide fixture scans):

    fu3  528887ec: 14202 passed, 2 failed, 3 errors; shards exit 1,1,0,0,2,0
    fu3b a5e46e74: 17852 passed, 2 errors; shards exit 1,0,0,0,0,0
    failing list at a5e46e74: sha256 8261732b98e252d1e17e491a8480080bafd2434fbd17f8a503aad8390ea9c20a (equal to main 6651e5a4's and FU2's)

The first run's failures came from FU3 itself (spec I4): the module
imported PyYAML, absent from the locked environment, so it did not
collect (shard 4 stopped at collection, exit 2), which also failed
`test_public_collection`; and the milestone README linked this record
before it was committed (`test_development_scaffold`). Both repaired in
a5e46e74. The 2 errors are the `tests/test_public_optional.py`
uv-version pins. Evidence: `evidence/FU3/full-suite-*.txt`.

## Criteria

| Criterion | Result |
|---|---|
| FU3-C1 | T1: each case's version-15 bytes and exit equal the answer key and validate; T2: on `agree`, `add-disjoint`, `asserted-only` and `self-loop` the rows equal the stated edges inside a loop by an oracle independent of `gnd.graphs`, and contain the version-7 cycle; T3: a loop only in the derived set passes with no listing; T5: an unavailable term leaves the rule unchecked with no listing |
| FU3-C2 | T4: `add-disjoint` keeps `agree`'s rows in order and adds `[20, 21]`, `[21, 20]` |
| plan §0 rule 1 | T6: every case's version-7 bytes equal the answer key recorded at 1e63aeb5; V3 |
| plan §2 FU3 | no disagreement was found (spec P1, C1), so the conditional M1 is empty |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 1e63aeb5 9662812e`, disposition `revise`, five findings, all
reproduced: [phase-FU3-codex-review.md](notes/phase-FU3-codex-review.md).
R2 (hardening): T2's oracle missed self-loops and reused production's
graph function; fixed with a reachability oracle and the `self-loop`
successor case, red against the old oracle first. R1 is recorded as a
boundary; R3-R5 corrected wording and records. The reviewer reported its
own probes over derived, uncovered, semiderived, deontic and
unavailable-term rings agreeing. The repair commits 528887ec and a5e46e74
carry no review opinion.

## Refactoring review

None needed. The phase changed no source. What it read: the checker and
the extent both build their view through `constraint_view_legacy`, which is
the one home for "which facts a constraint sees"; the extent still
re-evaluates derivations and re-adapts the snapshot rather than reading the
checker's (RC2's boundary). Sharing the checker's snapshot would remove a
second evaluation, but the checker does not expose it, and with the two
views now pinned equal for this route the cost is time only. Not proposed.

## Boundary: what this phase does NOT establish

- `acyclic-intransitive` and the other combined variants over a derived
  fact type: their listing appends intransitivity witnesses after the
  in-group edges (`correspondence.py:1298-1312`); FU3 has no case for them
  (spec I1, review R1).
- Derivations over derivations, clause or fixpoint rules, and `semiderived`
  rings have no corpus case; the reviewer's probes are its report, not
  retained evidence.
- `--baseline` with a structured-derivation model is refused (RC-D11) and
  untouched.
- One reviewer read 9662812e; the repairs in 528887ec and a5e46e74 were
  checked by the gates above, not re-reviewed.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| FU3-O1 (spec P2) | Refuted premise: plan §3 says FU3 reuses FU1's exact-term fixtures; they hold no fact type that can carry a ring, so FU3 has its own model. Repair the plan's §3 sentence. | milestone close |
