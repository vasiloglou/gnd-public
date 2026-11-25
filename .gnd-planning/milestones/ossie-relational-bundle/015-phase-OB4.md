---
milestone: ossie-relational-bundle
station: "phase-OB4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-OB4
date: 2026-11-24
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB4-spec.md r1 sha256 f79b3979..., G1-G18 as proposed (013-OB4-spec-gate.md)"
    exit: "n/a -- ruling"
  - command: "ruling: owner approved the corpus, the schema file and amendment r1.1 (014-OB4-corpus-gate.md); corpus files sha256 d8377d48dbb9ba301ccf4938573463a8accea3b4615d092081a40e00ad7054ed"
    exit: "n/a -- ruling"
  - command: "ruling: owner directed the merge of PR 271 and the start of OB4 (Merge 271, start OB4), which met G16 and ruled OB3-Q4"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_physical_binding.py tests/test_ossie_relational.py tests/test_ossie_export.py tests/test_rmap.py tests/test_ossie_import.py tests/test_ossie_formulas.py tests/test_rf1_cli_pins.py tests/test_li0_witness_wire.py --tb=line"
    exit: 0
    output: "925 passed in 172.29s (0:02:52)"
    note: "plan §9 OB4 row (the first two files), plus the consumers this phase touched"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 122.00s (0:02:01)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, is the known red (see Gate)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (165fa7c): 81 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
    note: "cli.export_command, export.ossie, export.ossie_relational and model.relational_mapping were edited with the code; export.physical_binding is new"
  - command: "uv run python -m tests.support.physical_binding_corpus"
    exit: 0
    output: "V1: ok ... V7: ok; refusals: ok (50 rows, 19 rule ids)"
slow_cadence:
  command: "uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py"
  trigger: "explicit owner request, with GND_OSSIE_ORACLE_ROOT prepared from the OS0 receipt"
  reason: "T13 (and OB3's T11) are written and not run: the upstream validator is the opt-in oracle lane. The evidence and census lanes are outside this phase's impact closure."
evidence:
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB4-spec.md
    sha256: 8a43d9ae2c2e25cc41b1402b970064afae577fd71c9dce945db089fc6c8a8dba
  - path: "tests/fixtures/physical_binding (29 files: bindings, semantic models, mappings, extensions, each sorted by case, then refusals.json)"
    sha256: d8377d48dbb9ba301ccf4938573463a8accea3b4615d092081a40e00ad7054ed
    note: "identical to the digest approved at the corpus gate: no approved file or refusal row changed"
  - path: src/gnd/schema/physical-binding.schema.json
    sha256: 5640b691db86a4a197a0832de83207ab5f78f15053f35be6d225e1263eac9066
    note: "identical to the digest approved at the corpus gate"
  - path: src/gnd/export/physical_binding.py
    sha256: 80043d4e4ef5f8eb9dea830bcddf9c9d2fdc4c438180ceef32588e61ef935f8c
  - path: src/gnd/export/ossie.py
    sha256: 08ae0a6bd9673a2e2ec09d1243ccf5df87d64c12d14851f7579fa394e13ecdc3
  - path: src/gnd/export/ossie_relational.py
    sha256: 3764698dc7dbc2d3cbd13b29bc7fdb94647a15bb663ce00cb752fc8cf295a18b
  - path: src/gnd/commands/export.py
    sha256: 33aa22361392eb4bc354b2637bd6425ba2cd6c63d44d8065947ac1d34fa49590
  - path: src/gnd/rmap.py
    sha256: 35b5ed171bb1ad9bfe070c9ad7be3743b897cbb29a5093ad5fb7e8025d24a176
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: eb78735518913bb4ff7b05a096bbc1a6471964b7a824589d4e16bad3f0e57d17
  - path: tests/test_physical_binding.py
    sha256: 6bd6e5e6f937a4307b29addf79bef7dab30bd1b3bef552241118abfd3e76b8c6
  - path: tests/support/physical_binding_corpus.py
    sha256: e84ae331cfd338a0eb64e866477c0a0a08bf5193efabeb03fe4fd2a052f8eb13
  - path: tests/support/binding_large.py
    sha256: b3b686d744f5e85aa0a948f00533870605a6896200ccac7350d1e96412f7d4d6
  - path: tests/support/model_scan.py
    sha256: 6a5c0f1c3b5a3d8f838c370cda39adc8982165c86d95e63d9c4dc4d811b9b519
  - path: tests/fixtures/ossie_ob4_baseline.json
    sha256: bacd391dd026f56d3a2f4bb92d7903bc1e9951043c5a7a6aea5b46dc97912a70
    note: "captured from main at 165fa7c7 before any OB4 edit (commit ba192972)"
  - path: tests/test_ossie_external_oracle.py
    sha256: 47a482acdc2d734420d8434be41b81ca1e8dbf18c81073b6d77f8aa8f9309295
  - path: .gnd-planning/milestones/ossie-relational-bundle/evidence/OB4/dynamic-query-successor.json
    sha256: 693dbb047299d13bd06a4c300056ef705e9d6887170eb680ca7ddb91a98d1419
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB4-r1/review.md
    sha256: c9c596d718f6556b5a7fb269769bec7d01085201c4558555ed62e2c7c0cef6e1
    note: "sanitized; the reviewer's original bytes are 88049c0c6b2423365cdf0071ec5a4d8ce8357119258cfd7fc6987dae02f0560a, bound by run.json"
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB4-r1/SANITIZATION.md
    sha256: 6d338168fa68eaaa4fb7190251e8d344a53af001d1864926e2b78e14fd37975a
  - path: .gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB4-r1/FINDINGS.md
    sha256: 0c42265b26f7029ed4cd6d34fb479a6a74089cb6d6f2f3c48684fd8e76382e27
---

# Phase OB4: the physical binding (`--physical-binding FILE`)

## Claim

- **The flag.** `gnd export ossie MODEL --out OUT --physical-binding FILE`
  writes the same five files. The semantic model describes the caller's
  delivered tables, and the mapping maps the ontology onto them. The
  built-in Rmap is not run (T6).
- **The approved corpus holds.** All seven valid cases equal their
  hand-written files byte for byte, and all 50 bad bindings are refused by
  their rule id with exit 3 and nothing published (T1, T4).
- **Every member is consumed** (OB4-C1): tables, columns, `sql_type`,
  `targets`, `references`, `primary_key`, `unique_keys` present and absent,
  `roles` and `extension_roles` each have a case.
- **One relationship per foreign key** (OB4-C7): a two-column foreign key is
  one relationship with ordered columns; a mismatched group is refused (T3).
- **One order** (OB4-C2, C3; plan §0 rule 3). Nineteen rule ids are checked
  in the order the source states them. 152 pairs of defects each report the
  earlier rule; binding syntax and schema come before the model, names and
  contradictions after it, and all before `--strict` and size (T5).
- **Unbound is not an error** (OB4-C4). An unbound fact type and its
  constraints are listed as `unbound`, with `binding_sha256` the digest of
  the binding file (T6).
- **Without the flag nothing changes** (OB4-C5). The 82 census exports equal
  a baseline captured from main before any OB4 edit, and the OB2 and OB3
  corpora still pass (T7). With the flag, the ontology, sidecar and loss
  report are the bytes of a run without it (T2).
- **Total over hostile input** (OB4-C6; plan §0 rule 1). 910 wrong values in
  a valid binding, 14 byte strings, lone surrogates and a 1,100-entity
  identifier chain give only named binding refusals or a valid run, never a
  traceback (T8, R1-F1, R1-F2). Role names match by the D8 rule, including
  compatibility forms; names that collide or vanish are refused (T9).
- **Time** (plan §0 rule 2). At 1,400 entities and 4,500 fact types (2,950
  tables) a binding run takes 4.1 s, against 3.4 s with the Rmap; the ratio
  to one fifth of that scale is 5.0. The binding file is 1.2 MB (T10).
- **One walk** (plan §0 rule 4). The binding path fills the Rmap's own
  records, and `gnd.rmap.dispositions` performs the walk for both paths.
- **One home.** The rules are in `representation-format.md` § "Ossie
  interchange", "Physical binding"; the member list is the packaged schema.

## Gate

The front matter gives each command and its exit verbatim.

**Known red.** `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap`
fails because `.agents/skills/review-pr/SKILL.md` cannot resolve
`../process-phase/references/review-tool.md`, a discovery-link layout this
worktree has not adopted. It failed on the phase base: main at `165fa7c7`
has the tree `5718e427`, which is the tree OB3's gate ran on
(`1 failed, 865 passed`, that test being the failure). OB4 touches no part
of that layout.

## Review

There was one reviewer, Codex, run through `review_tool.py` with a read-only
sandbox and effort high, over base `ba192972` to head `a8a41130`. **One
reviewer is one reviewer.**

| Item | Value |
|---|---|
| Review | [review.md](notes/reviews/phase-OB4-r1/review.md), sha256 `88049c0c…560a` as written, `c9c596d7…f6e1` after sanitization ([SANITIZATION.md](notes/reviews/phase-OB4-r1/SANITIZATION.md)) |
| Verdict | CHANGES_REQUESTED, with six findings |
| Ledger | [FINDINGS.md](notes/reviews/phase-OB4-r1/FINDINGS.md) |

| Id | Class | Reproduced | Disposition |
|---|---|---|---|
| F1 | blocking | yes (exit 70) | fixed: a string that is not Unicode text is `binding:syntax` |
| F2 | blocking | yes (`RecursionError`) | fixed: explicit stack, and an identifier nested more than 8 deep is not followed |
| F3 | blocking | yes | fixed: an external uniqueness is placed by the roles it names |
| F4 | hardening | yes | fixed: foreign-key groups are checked in sorted order |
| F5 | hardening | yes | fixed: a word after the type's list needs a space |
| F6 | hardening | yes | fixed: schema refusals name an escaped pointer |

Eleven regression tests were shown failing on the pre-repair bytes before
any fix. The repairs are commit `527cf956`.

The reviewer also confirmed: 149 tests over the approved outputs, schemas
and baseline; all 50 refusal rows; all 910 wrong-shape probes; all five
artifact digests equal to `ba192972` across the 82 baseline runs; the
generated binding runs listing every fact type and constraint without
invoking the Rmap; and its matcher probes of dotted, quoted, Unicode and
newline-containing identifiers, role-name normalization and SQL parameter
boundaries, where the only failure was F5.

**The repaired bytes are not reviewed.** No second round ran.

## Refactoring review

**Refactors EXECUTED**, behind the same gates and with no OB2 or OB3 corpus
byte changed:
- **The foreign-key naming rule has one home.** It was inline in the Rmap's
  build. It is now `gnd.rmap.name_foreign_keys`, used by the Rmap and the
  binding.
- **The unary flag is a field, not a convention.** The mapping read a unary
  fact type's flag column out of the position of a name in `carried_as`.
  `RolePlacement.flag` now carries it, and the binding path leaves it unset.
- **Absorption is a field.** The mapping inferred an absorbed subtype from a
  table name that differed from the object type id, which a binding breaks.
  `Identification.absorbed` states it.
- **One fixture-model scan** (OB3-Q6): `tests/support/model_scan.py`.

**Seen and deferred.**
- An RFC 6901 pointer is now built by four private helpers
  (`export/ossie.py`, `ossie_import.py`, `transition.py` in its own style,
  and the binding). Row OB4-Q4.
- OB3's `MAX_LINK_ARITY` and OB4's `MAX_IDENTIFIER_DEPTH` are two bounds on
  one concern, the depth of a mapping document. Row OB4-Q5.

## Refuted premises and findings

The spec's §12 (IF1–IF14), §13 (K1–K13) and §14 (RR1–RR6) list them all. The
ones that change an earlier document:

- **Plan §2.4** says a foreign key's columns are "ordered by each column's
  position in `references.columns`". Every column of a group carries the
  same block, so no column has a position there. They pair by table column
  order (K1).
- **Plan §10 D8** names four contradiction classes without definitions. Two
  needed one before they could be tested (K4, K5), and K5 as first written
  refused the approved case V3 (IF1).
- **Plan §2.4** treats `targets` as how a column gets its meaning. `roles`
  alone binds a role; `identifier` targets mark home tables, and the other
  two kinds are only checked (K12).
- **Spec §6.7** put `binding:role-name` after the unknown-role lookup. It
  has to come before (K2).
- **Spec §6.5** expanded an entity's identifier "in turn" without a bound.
  A chain the model admits can be over a thousand deep (RR2).
- **The issue** asks that the datasets equal a delivered DDL. A schema that
  links tables by surrogate keys can be described, but the fact types held
  only through those keys cannot be bound (K13).

The plan is not edited here; these go to the milestone-close amendment.

## Open questions

| Id | Question | Target |
|---|---|---|
| OB4-Q1 | Accept the two rules implementation and review added: K5's refinement (an entity and a part of its own identifier may share a column, IF1) and the 8-level identifier depth limit (RR2)? | owner, before OB5 |
| OB4-Q2 | Should the review repairs (`527cf956`) get a second round, or is the close review the next instrument? | owner |
| OB4-Q3 | **Surrogate keys (K13).** Does the reporter's schema use them? If so, most of their fact types may be unbindable as specified. | D10 |
| OB4-Q4 | One shared RFC 6901 pointer helper for the four private ones? | close sweep |
| OB4-Q5 | One depth bound for mapping documents instead of two (OB3's 32 roles, OB4's 8 identifier levels)? | close sweep |
| OB4-Q6 | OB2's `test_r2_f8_external_unique_keys_are_not_quadratic` failed once in a long run and passed three times alone (IF14). Loosen its ratio, or leave it? | close sweep |
| OB3-Q3 | Carried: the opt-in oracle lane (OB3 T11, OB4 T13) has not run, so upstream acceptance of these files is unconfirmed. | owner |
| OB3-Q5 | Carried: identifiers the ontology does not declare (unit-based, multi-supertype). | close sweep |
| OB1-Q1, OB1-Q2 | Carried: `guard_yaml`'s captured default; D11, the source cap. | OB5 or the close sweep; after D10 |
| OB2-Q1, OB2-Q2 | Carried: the duplicated predicate; `refscheme`'s selection. | close sweep |

## Boundary

- **Residuals.**
  - **Surrogate keys (K13)**, accepted at the corpus gate as a known limit.
  - **The reporter's format is unconfirmed (G1).** The document is GND's
    own, defined from the issue's prose. D10 has not been asked.
  - **`extension_roles` has no confirmed meaning (G7).** It is checked and
    listed, and nothing is mapped from it.
  - **Lowercase-folding databases (G11).** Names are quoted and uppercased in
    expressions, by Ossie's comparison rule.
  - **No nullability.** A binding carries none, so `mandatory` is always
    `not-relational` on a binding run.
- **Size** (spec §10 estimated about 450 reader, 120 schema, 60 wiring, 110
  normative and 500 test lines):
  - `physical_binding.py`: 722 lines, about 1.6× the estimate, from the
    declared-home and object-mapping distinction (IF2), the stack-based
    identifier shape (RR2) and the per-rule sorted passes.
  - The schema file: 194 lines.
  - `rmap.py`, `ossie.py`, `ossie_relational.py`, `commands/export.py`: 117
    lines added and 36 removed, about 2× the estimate, from the shared-record
    generalization (IF7).
  - Normative text: 115 lines.
  - Tests: `test_physical_binding.py` 787 lines, the corpus checker 250 and
    the binding generator 35, about 2× the estimate.
  - Corpus: 7 valid cases and 50 refusal rows.
- **Not done:** the explanation, how-to, export skill and release-note entry
  (OB5): **they still describe three files and no binding.** No binding from
  DDL, no DDL from a binding, no YAML binding, no size parameter.
- **Not run:** the opt-in oracle lane (T13), and the evidence and census
  lanes.
- **Not pushed.** Branch `claude/ossie-ob4-binding-spec`, cut from main at
  `165fa7c7`, has no pull request; opening one is the owner's call.
- **Approval:** this record approves nothing beyond OB4. Merge is the
  owner's.
