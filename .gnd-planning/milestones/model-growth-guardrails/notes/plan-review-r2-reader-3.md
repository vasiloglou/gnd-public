# Confirmation reader 3 -- protocol, authority, compatibility, privacy, docs plan

Retained text of the reader's returned report, lightly edited for layout.
Confirmation round (round 2) over r2 of both milestones.

**Digest:** all four r2 SHA-256 values match (`b0294807…`, `553724f8…`,
`506b285d…`, `0a31dad5…`); the live `notes/` files are byte-identical to the
snapshots. Nothing written to the repository; one probe in the reader3
scratch directory.

**Verdict: approve-with-fixes.** Eight blocking themes resolved; F and I
partly. Ten findings: 7 r2-introduced, 3 pre-existing. 7 of 10 exceeds one
half, so the declared stop rule fires: apply repairs, no further round. The
`(o1)` and `(p1)` records in both headers match the disposition, list the
eight questions correctly, and claim no approval of bytes; `auto=false` and
the PR rule are in both §8.

## Theme status

| Theme | Status | Evidence |
|---|---|---|
| A | resolved | `model_verbalization.py:569-574` puts a literal space after `_fact_type_cnl`, then the redaction sentence or `reading=`; `line_text` is a per-character `translate` (`verbalize.py:134`), so it composes over substrings; T3, T3b, T3c hold |
| B | resolved | Reproduced: 282 models load, 118 have rules, 23 crash by path; the disposition's "five" was stale; only aggregate rules read `model`, so the fix moves no digest |
| C | resolved (not reproduced) | fallback table, T4b mutations, T13 present |
| D | resolved | optional v3 fields omitted when unset; apply repeats both options and refuses a mismatch either way; re-run catches a stripped-and-recomputed preview (MG2-C3); refusing preview writes its document; follows `(p1)` D |
| E | resolved | `--shape-report`; MG3-C3 |
| F | **partly** | order case and confirm ruling in; matrix not total (C3-F3) |
| G | resolved | U1–U8 implement `(p1)` G; the ruling text claims more than was ruled (C3-F6) |
| H | resolved (size unproved) | 4,000 anchors, 961 KB |
| I | **partly** | parser-only rules incomplete (C3-F4) |
| J | resolved | §2.2 and CT2-C4 compose and let check report |

## Findings

**C3-F1 (medium, before the CT4 spec; r2-introduced) -- CT-R7, CT-R6, §2.4.**
"`gnd discover --show-values` is a `site` row … the rest keeps its every-mode
row" cannot be built: `SURFACES` has one row per CLI leaf, and
`disclosure.md` says each surface is "in exactly one row"; the CLI resolves
the mode only for site or spawning leaves (`cli.py:712`), so discover never
sees `--disclosure customer`, and T26 (`test_disclosure_mode.py:484-498`)
asserts such leaves see no mode; `disclosure.md` says every-mode outputs take
no value option. Site semantics also differ from `(p1)` U's "only with
`--show-values` under internal": under `internal` a site behaves "as if every
value option were passed" (`release-notes.md:13`), and under unset it would
emit with the flag. The change amends NM-D13 without saying so. Repair: make
`gnd discover` a site leaf with non-value output unchanged in every mode;
update T26's arithmetic, the `disclosure.md` table and its "same in every
mode" section; record that `(p1)` U supersedes NM-D13 for this option.
**Owner:** unset mode with `--show-values`: refused/ignored, or emitted under
normal site rules.

**C3-F2 (medium; r2-introduced) -- CT-R7.** `gnd compose` and `api:compose` as
`value-free` contradicts `disclosure.md` ("emits no population values"):
compose writes the composed population, including manifest `to` values. The
nearest precedent, `EvaluationSession.observe` ("the caller's own
population"), is `every-mode`. Repair: `every-mode`, noting the record is
value-free.

**C3-F3 (medium, before the MG2 spec; r2-introduced) -- MG §2.2 matrix.**
MODIFY cells list only some fields. Fact type: `arity`, `depends_on`,
`inverse_reading`, `objectified_as` (the plan's `objectification` is not a
schema property), `objectification_independent`, `redact`,
`sample_population`, and provenance keys other than `rationale` are
unclassified; fact types have no `description` in `orm-meta.schema.json`.
Object type: `primitive`, `kind`, `precision`, `scale`,
`inherits_reference`, `independent`, `derivation`, `storage`, `name`
unclassified. `redact: true→false` and a `primitive` change are both
unclassified. Model-hosted constraints (`ConstraintLocator.host == "model"`,
`models.py:251`) have no row. Repair: MODIFY as an allow-list (admitted only
when the diff is limited to description core keys and
`provenance.rationale`; all else refused); a model-hosted constraint row,
populated if any fact type it spans is populated.

**C3-F4 (low-medium; r2-introduced) -- CT1 schema section, T11.** `_parse` and
`parse_anchor_sidecar` (`anchors.py:56-89`) also refuse duplicate JSON keys,
NaN/Infinity, integers over 18 digits, nesting deeper than 32 and invalid
UTF-8; a schema cannot see the first two. T11 holds only because T2 lacks
these. Repair: list them as P4+, one T11 case each.

**C3-F5 (low; r2-introduced) -- CT §9 CT3 gate, §3.** `tests/test_schema_sync.py`
`SCHEMA_PAIRS` (`:27-34`) covers only orm-meta, population and steps; the
witness twin is identical today but unpinned. That test treats the skill copy
as canonical, while the MG plan calls `src/gnd/schema` primary. Repair: CT3
adds `witness.schema.json` to `SCHEMA_PAIRS`; MG5-C1 edits the canonical copy
first.

**C3-F6 (low, authority; r2-introduced) -- MG-D8, §2.5 U5.** MG-D8 is marked
"Ruled `(p1)` G" but includes two items not in the G proposal: spans on
`sample`/`llm-inferred` constraints (U5) and the `common-sense`
`library_entry` exemption, which narrows #74's "every constraint cites a
source span". Repair: mark both proposed; present the exemption at the plan
gate as a scoping of #74.

**C3-F7 (low; r2-introduced) -- MG §2.2, MG6-C3.** The additive guarantee
holds only if the `apply` caller repeats `--policy`; a stripped,
recomputed preview applied without the option publishes. Consistent with
(iii) but unstated. Repair: say so in the reference page and how-to.

**C3-F8 (low; pre-existing).** `PROJECT.md` says "Both plans are r1 drafts:
not reviewed"; the CT disposition pointer lists J and U as pending. Update.

**C3-F9 (low; pre-existing) -- MG §7, predicate 4.** #78 asks for value
constraints as text; MG-D6 (a) omits them but §7 does not scope them out.
Repair: a §7 line; raise at the plan gate.

**C3-F10 (low; pre-existing) -- MG §2.5.** The span's `start`/`end` unit and
the bytes `excerpt_sha256` covers are undefined (interchange-field rule).
Repair: define them, matching the anchors precedent (unit unproved by the
reader).

No population values, downstream names or credentials appear in the four
subjects.
