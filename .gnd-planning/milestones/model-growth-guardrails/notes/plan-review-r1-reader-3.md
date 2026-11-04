# Reader 3 -- protocol, authority, compatibility, privacy, docs plan

Retained text of the reader's returned report, lightly edited for layout.
One review round covered both milestones.

**Digest check:** all four snapshots match their stated SHA-256 (MG plan
`32a851f0…`, MG1 spec `d44bf94e…`, CT plan `48430d1a…`, CT1 spec
`51dd6948…`); the working copies in `notes/` match their snapshots.

**Verdict:** request-changes. Every repair is a text change; F1 is the only
blocking one.

**Scope.** All four snapshots against issues #72–#78, start-milestone,
spec-note-contract, standing-rules, review-convergence, AGENTS.md,
compatibility.md, IK close 012, follow-up 014, NM close 005, the disclosure
table, the meta-schema and the packaged-skill pins. No tests run.

**What holds.** Both plans have the goal/predicates block and sections 0–10;
each obligation cites its issue and maps to a gate; `auto=false`, the
branch/PR/owner-merge rule and "plan authorship is not approval" are stated;
`(o1)` is dated, scoped to the instrument and approves no bytes, and the
four-reader precedent is real (IK D7, NM `(o2)`); no downstream application
or host path appears; both specs follow the 11-section contract; MG1 T6 names
all four `__all__` pins; the 2026-10-25 ruling and NM-D13 are cited
correctly.

**Findings.**

**R3-F1 (blocking) -- MG plan §2.3, predicate 2, MG-D2, §5.** `shape_matches`
has no flag: every preview with a fact-type ADD changes, contradicting MG-R1,
predicate 2 and MG-D2 (a)'s premise. Repair: an option, or the **Owner**
accepts a new preview version for all previews with a release-note migration
entry (compatibility.md).

**R3-F2 (hardening) -- CT plan §2.2, CT2-C4.** Both refuse a cross-source
functional conflict with exit 3, while CT-D4 proposes (b). Repair: make them
conditional on CT-D4 (**Owner**).

**R3-F3 (hardening) -- CT-D9 vs CT4-C3, CT-R6.** CT-D9 (b) puts the value
"only in the migration report", but CT4-C3 says the report holds "no raw
values (IK-R11)". Reading (a) writes a population value into a model id; CT-R6
covers only redacted roles, and discover's every-mode row (NM-D13) emits it
even under `customer`. Repair: a digest of the value in the report plus an
explicit opt-in for the raw value; state behaviour under `customer`
(**Owner**).

**R3-F4 (hardening) -- MG §2.5 item 2, MG-D8, O13.** `$defs.object_type` and
`$defs.fact_type` have no `source`, so the span rule selects only
constraints; "every elementary fact cites a span" and CSDP
`sample_population` rows are ungated. Repair: spans on every fact type and
object type unconditionally; decide `sample_population` (**Owner**).

**R3-F5 (completeness) -- schema mirrors, skill surfaces.** The meta-schema is
at `src/gnd/schema/orm-meta.schema.json`; its vendored copy
`gnd-orm-core/references/orm-meta.schema.json` is pinned
(`tests/test_public_aggregate_surface_corpus_controls.py:87`,
`test_public_float_corpus_guards.py:30`, others) and MG5 never names it. CT3's
`schema/witness.schema.json` mirror `gnd-export/references/witness.schema.json`
and `gnd-export/references/witness-contract.md` are missing from CT §5. "SKILL.md
twins" is wrong: skill directories are installer symlinks; the real twins are
the schema mirrors. `gnd-extract/SKILL.md:41` restricts reads to the bundle
files and `:63` says "three files"; MG4 must amend both. The standalone
`gnd-model-from-text/scripts/validate_model.py` is schema-only; route the
skill to `gnd validate`. A new skill file changes `EXPECTED_SKILL_FILES`.

**R3-F6 (hardening) -- MG1 T7, MG plan §9 for MG2.** `tests/test_evolve*.py`
matches 2 of 8 evolve-consumer files; it misses `test_model_evolution.py`,
`test_evolution_conformance.py` and four `test_public_*evolution*` files.
Record 014 refuted this same premise. Repair: list files explicitly.

**R3-F7 (completeness) -- MG1 docs and T6.** `docs/reference/api.md` does not
exist; the page is `docs/reference/python-api.md`, whose `:9` says "nine
functions, the one count other pages refer to"; MG1 and CT2 change it. T6
calls `docs/release-notes.md:56` "the list", but it is prose in the why-not
entry. Repair: a new Unreleased entry; a count sweep in MG6 and CT5.

**R3-F8 (completeness) -- MG §10, inherited questions.** Carried rows that
bear on these phases: IK1-Q4 (a description or reading can forge a role line)
for MG4, which repeats descriptions into markdown, so escaping and a
structure test; IK close "Reader four" (apply rewrites the model as one-line
JSON, dropping comments) for the MG6 how-to; NM2-Q3 (RF1 goldens do not
reproduce from a fresh capture) for MG2, MG4, MG5, CT2; IKE-Q3 (discover lets
a raw `ArtifactError` escape) for CT4. Repair: add these rows with
dispositions.

**R3-F9 (completeness) -- rule binding.** MG1 never mentions MG-R8; CT1 never
mentions CT-R3..R7. CT-R7 needs a sentence because `gnd check --anchors` is a
declared disclosure site.

**R3-F10 (hardening, privacy) -- CT2 record.** The record stores renamings per
fact, and manifest renamings carry raw values; CT-R7 says it "follows the
mode", but a byte-re-verified record cannot be redacted per mode; no
disclosure row kind for `gnd compose`/`api:compose`. Repair: renamings by
manifest index so the record is value-free; assign the row kind (`gnd synth`,
`gnd extract` are value-free precedents); refusal messages never quote values
(**Owner** on the row kind).

**R3-F11 (completeness) -- CT public API.** `gnd.api` accepts `AnchorSidecar`
objects (`api.py:801`, `validate_anchor_sidecar`), so v2 reaches the public
API; not in CT §5 or `python-api.md`. `gnd replay --composition` has no
`api.replay` keyword in §5. CT2-C6 should name the four `__all__` pin sites.
`src/gnd/extract/anchors.py` is a re-export; the writer is
`write_anchor_sidecar` in `gnd/anchors.py`.

**R3-F12 (completeness) -- issue coverage.** #77 asks for "new object or fact
types" from an "attribute or relation name"; CT4 covers fact types from
attribute names only, and §7 does not scope the rest out. #76 asks for
"compatible reference modes"; MG-D7 reads it as exact identity without
saying so. Repair: scope-outs or decisions (**Owner**).

**R3-F13 (completeness) -- protocol.** CT §8 says the stop rule is "declared
here" but points to the predecessor; review-convergence.md:57 wants it in the
artifact's own bytes. MG §8 omits the same-seat trend. MG-D5 (b) and MG-D7 (a)
state no real cost. The MG README still says the owner picks MG-D1. The
`(o1)` quotation cannot be checked against the repository (unproved).
