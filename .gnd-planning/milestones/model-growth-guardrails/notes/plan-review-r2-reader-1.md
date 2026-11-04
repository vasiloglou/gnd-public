# Confirmation reader 1 -- correctness against production semantics

Retained text of the reader's returned report, lightly edited for layout.
Confirmation round (round 2) over r2 of both milestones. Scratch paths read
`<scratch>`.

**Digest:** all four r2 SHA-256 match (MG plan `b0294807…`, MG1 spec
`553724f8…`, CT plan `506b285d…`, CT1 spec `0a31dad5…`). HEAD `1446f909`;
`notes/` copies byte-identical to the snapshots. Nothing written to the
repository. Probes: `<scratch>/plan-review-r2/reader1/` (`p1_corpus.py`,
`p2_fallbacks.py`, `p3_d6.py`, `p4_anchors.py`).

**Verdict:** approve-with-fixes. No theme unresolved; one small blocking
repair (C1-F2). All 9 findings attack text r2 created: this seat's
self-inflicted ratio is 9/9.

## Theme status

| Theme | Status | Evidence |
|---|---|---|
| A | resolved | p1: all 282 rendered rules over 118 models have `derived: `+text then one of the three successors; `text[:-1]` rejected every time; successors match `model_verbalization.py:569-574` |
| B | resolved | raw `model` reaches `_fact_type_cnl` at `:571`; 23 of 118 crash by path, 0 loaded; the fix touches only the aggregate branch |
| C | partly | every listed mutation refused by `load_model` (p2), so it holds for paths; table and "validated" claim wrong (F3, F4) |
| D | resolved | apply recomputes only validation, verbalization and blast radius (`service.py:1612-1647`), so a stripped-and-recomputed preview is caught only by the re-run, as MG2-C3 says; hardening F8 |
| E | resolved | optional field; `primitive(variant="strict")` exists (`model_index.py:276`) |
| F | partly | F1, F2 |
| G | partly | F5 |
| H | resolved, hardening | F7 |
| I | partly | F6 |
| J | resolved | CT §2.2, CT2-C4, predicate 2 consistent; note F9 |

## Findings

**C1-F1 (hardening; r2-introduced) -- MG §1 `service.py:634-637`, §2.2 Role/ADD
"already gated today".** That gate refuses a role ADD only when the fact type
is in an existing operation's reference set (`service.py:609,629-641`),
exiting 18; a role ADD on an ordinary existing fact type passes today.
Trusting the parenthetical, an implementer admits the cell. Code reading.
Repair: the policy itself refuses a role ADD on any existing fact type (3);
only operation-referenced fact types hit 18 first; both cases in MG2-C1.

**C1-F2 (blocking, small; r2-introduced) -- MG §2.2 matrix, strengthening.**
Not total: (a) ObjectType MODIFY lists only `reference`, `subtype_of`; the
schema also has `kind`, `name`, `primitive`, `precision`, `scale`,
`independent`, `inherits_reference`, `derivation`, `derivation_rule`,
`storage`; changing `primitive` or narrowing `scale` invalidates facts. (b)
FactType MODIFY omits `redact`, `depends_on`, `arity`, `inverse_reading`,
`objectification_independent`, `sample_population`, `provenance`; names
`objectification` (the key is `objectified_as`); admits `description`, which
`$defs.fact_type` lacks. (c) `ConstraintLocator.host == "model"`
(`models.py:254`) spans several fact types and has no row. (d) A constraint
MODIFY neither listed strengthening nor weakening (type change, other role
set) has no verdict. Schema dump. Repair: admitted only if listed as
admitted, all else refused; a model-hosted constraint is on a populated fact
type if any fact type it names is populated; fix key names.

**C1-F3 (hardening; r2-introduced) -- MG1 spec, fallback branches ("it is,
after `_coerce_model`").** `_coerce_model` returns any `Model` unchanged
(`model_verbalization.py:474-477`); `Model.model_validate(dict)` skips
semantic validation. Through an in-memory `Model`, p2 shows partial renders
(`book_rated_adult()`, `derive ()`, `{"x":1} = $b`) and raw
`AttributeError`/`ValueError` for `head:"x"`, a string `where` item, three
`date_add` args. That breaks #72 and rule 1. Repair: re-check `Model` inputs
with `validate_model_object` (`verbalize_population.py:28`), as
`_run_verbalize` does (`api.py:833-834`); map failures and any
`VerbalizationError` to `exit_code` 3; an in-memory invalid-`Model` case in
T5.

**C1-F4 (completeness; r2-introduced) -- MG1 fallback table.** `:168-172`
"non-dict binds" is dead (`atom_bind` always returns a dict, `atoms.py:30-43`);
the listed mutation never reaches it (refused for `$b` unbound); the real
partial render (`bind` missing, non-dict or `{}` → `ft()`) is unlisted. Lines:
`date_add` unpack `:158`, term fallthrough `:163`, head `:191-193`. A
non-dict `where` item and a missing `head` (→ `derive ()`) are absent; p2
shows both refused by `load_model`. Repair: replace the row with `bind: "x"`
/ missing `bind`, mark `:170` unreachable, add the two rows, fix lines.

**C1-F5 (hardening; r2-introduced; Owner) -- MG §2.5 U-matrix.** `source_kind`
has seven values including `imported` and `induced`; U3, U5, U8 cover five.
An unattended model can carry an `induced` or `imported` constraint with no
span (contradicts O13); an alethic `induced` constraint stays a warning
because U8 omits it. Repair (Owner, within `(p1)` G): spans for every source
except `common-sense`, or refuse `imported`/`induced` in this mode; extend U8
to `induced`.

**C1-F6 (hardening; r2-introduced) -- CT1 schema, P1–P3, T11.** JSON Schema
`integer`/`const: 1` accepts `1.0`; the parser requires `type(...) is int`
(`anchors.py:109,129,131`); p4 confirms. Duplicate keys (`_pairs`), the
18-digit cap and depth 32 are parser-only too. Repair: P4 integer-valued
floats, P5 duplicate keys, P6 integer length, P7 depth, one T11 case each.

**C1-F7 (hardening; r2-introduced) -- CT1 rule 1, T2 "961 KB".** Size depends
on the template: 958,077 B with the v70-phase5 anchor, 1,058,077 B (over the
cap) with the v70-phase1 anchor. Repair: pin the template and the compact
serialization (`write_anchor_sidecar`, `anchors.py:262`), or 3,500 anchors.

**C1-F8 (hardening; r2-introduced) -- MG §2.2 "omitted when unset".**
`_bindings_match` hashes `model_dump(mode="json")` (`models.py:817-818`),
which includes `None` fields; `_EvolutionPreviewV3` has `extra="forbid"`. If
omission is only at write time, every re-read v3 preview fails the digest
check. Unproved (design reading). Repair: the omission lives in
`_serialize_wire_version` (`models.py:786`) and the fields are declared on the
V3 reader.

**C1-F9 (completeness; r2-introduced) -- CT2-C4 exit 1.** A deontic uniqueness
yields `warning`, plausibly exit 0. Unproved. Repair: pin an alethic
constraint in the fixture, or state both exits.

Owner: F5. `(o1)`/`(p1)` rulings not contested.
