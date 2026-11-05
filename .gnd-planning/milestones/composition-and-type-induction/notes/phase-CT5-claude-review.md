# CT5 docs review (independent, read-only)

No blockers. Every shown output matches its gnd-run block (runner exit 0), and
the requested tests pass. The how-to says anchors bind values to ranges and
that nothing proves the contracts are true, so CT-R2/O5 is met. Nine findings
follow; I reproduced each one.

## Findings

**F1 (major): docs/how-to/compose-documents.md:114-117.** The page
overstates what the sidecar binds. It says: "The sidecar also carries three
digests: of the population's bytes, of the document's bytes, and of the
model's vocabulary. If any of the three files changes, the sidecar no longer
binds." The vocabulary digest leaves out `constraints`, `derivation_rule`,
`sample_population`, `depends_on` and descriptions (src/gnd/anchors.py:204-217).
- Reproduced: I deleted the uniqueness constraint from a copy of the model.
  `gnd compose` under the edited model still prints "Composed 6 fact(s) from
  2 source(s)." and exits 0, so every sidecar still binds. `gnd check
  --composition` then reports a clean BLOCKING section.
- Fix: say "if the population, the document, or the model's vocabulary (its
  object types, fact types and roles, not its constraints or rules) changes".
  Optionally add that the composition record binds the whole model file.

**F2 (major): compose-documents.md:89-94.** The page says each document was
extracted "the way the `gnd-extract` skill works: a population ... and beside
it an anchor sidecar". The gnd-extract skill writes an extraction sidecar
(`extracted.population.extraction.json`), not an anchor sidecar.
- The skill's own new sentence (src/gnd/skills/gnd-extract/SKILL.md:117)
  calls the anchor sidecar "optional" and sends the reader elsewhere.
- No CLI writes anchor sidecars (`gnd extract --help` lists none). The
  example's sidecars come from `tools/build_composition_example.py`, which is
  not shipped. The only writer is the Python `gnd.extract.anchors.write_anchor_sidecar`.
- So a reader cannot repeat the how-to on their own documents.
- Fix: say the populations follow gnd-extract and the anchor sidecars are
  written separately. Link anchors.md#the-file and name how to produce one, or
  state plainly that GND checks anchor sidecars but does not author them.

**F3 (minor): compose-documents.md:13.** "Every value is checked against the
document it came from" is too broad. Only `anchored` roles are checked: the
party in `contract_has_party` and the city in `party_is_based_in_city`. The
contract codes and the seat's party are never looked up in the text. Line 459
already says it correctly ("every anchored value").
- Fix: "Every anchored value is checked ...".

**F4 (minor): compose-documents.md:351-355.** The conflict explanation tells
half the story. The checker prints only the first missing derived row
(src/gnd/extensions.py:2487, `missing[0]`). "C-2 is in Lyon" is missing too.
- Reproduced: I added the C-1/Zurich claim to the composed conflict
  population and ran a plain `gnd check`. It then reports "missing
  {"contract":"C-2","city":"Lyon"}".
- The phrase "One wrong seat in the addendum" also assumes which document is
  wrong. That sits badly with the page's own "GND cannot [decide], and does
  not try" (l.347).
- Fix: say the rule now derives both cities for both contracts, so "C-1 is
  in Zurich" and "C-2 is in Lyon" are both unclaimed, and that the report
  shows the first. Rephrase the line as "one disagreeing seat".

**F5 (minor): compose-documents.md:469-470.** "So that the one decision a
person did make is the only thing they have to stand behind" contradicts
l.465-466. Those lines say an extraction can misread a document in ways the
anchors don't catch, and the documents themselves may be wrong. That is a
small truth overclaim against O5.
- Fix: "... so that what a person must still stand behind (the renamings,
  the extractions and the documents themselves) is named, not hidden".

**F6 (minor): docs/assets/applications/compose-composition.svg (record box) and
compose-trace.svg.** The figures don't match the record printed at
compose-documents.md:229.
- The record shows `party_is_based_in_city 0 ... renamings [1]`. The
  composition figure's record box gives that row as "from contract-a#0,
  contract-b#0" with no renaming. It shows renaming 0 only on
  `contract_has_party#1`.
- The manifest box says "rename ACME CORP. ... (party, in both fact types)"
  as if it were one entry, but the manifest has entries 0 and 1.
- The trace figure marks only "C-2 has party" as "renamed by the manifest".
  The contract-b source of "Acme Corp. is based in Lyon" was renamed too.
- Fix: add ", renaming 1" to the `party_is_based_in_city#0` line, and say
  "two entries (0, 1)" in the manifest box.

**F7 (minor): .gnd-planning/milestones/composition-and-type-induction/notes/CT5-dispositions.md:8,10.**
The counts are wrong. The text says "47 files" and "Totals: 11 updated, 36
unchanged", but the table has 48 rows (11 updated, 37 unchanged). The spec
itself says 48.
- One packaged-skill file the grep matches has no row:
  `src/gnd/skills/gnd-export/references/witness.schema.json`. It already
  enumerates versions [1, 2], so no edit is needed, but it is the file the
  updated gnd-export SKILL.md sentence describes.
- I found no stale "unchanged" row:
  - guides/documents.md already links version 2 (l.82-83).
  - disclosure.md has the compose row (l.125).
  - The witness contract covers version 2.
- Fix: correct the counts, and add the schema row or say why `.json` files
  are left out.

**F8 (nit): compose-documents.md:356.** The page says the `lineage` lines in
the JSON report sit "under `composition.lineage`, keyed by fact type and
index". In fact `composition.lineage` is a list of `{fact_type, index,
sources}` objects, confirmed with `gnd check ... --format json`.
- Fix: "one entry per offending fact, with its fact type and index".

**F9 (nit): pedagogy for a business reader.** Several terms go unexplained.
- l.436: `gnd replay` prints `"replayable": false` right after a successful
  replay, with no word of explanation. The flag means the printed view is
  not itself a certificate.
- "digest" (l.114, 233) is never glossed; "a fingerprint of the file's
  bytes" would do.
- "base node" (l.364) and "derived extension" (l.333) are used without
  definition.
- l.491-494: "Next steps" implies `gnd discover --families fact-type` works
  on any "item has attribute with value" fact type. It only groups a fact
  type whose provenance declares `generic: {entity, attribute, value}`
  (discover.md:116-123). Add "declared generic".

## Verified as correct (no finding)

- Every behaviour claim below matches the code:
  - Renaming is the only way a value changes, and a renaming that matches no
    row is refused (composition.py:286-288).
  - The check compares the model and population digests, then re-derives
    and compares manifest, sources, scope tags, lineage and bytes
    (composition.py:325-339).
  - Replay checks the binding digests, then each base node's sources
    against the record, then the proof (witness/kernel.py:307-326). Replay
    without the record gives `composition-required`, exit 3.
  - A role passes only when every anchor on it binds.
- The edits to cli.md, discover.md (synopsis and flags match `gnd discover
  --help`), formats.md (all three schema files exist), python-api.md
  (signatures match `inspect.signature`), agents/index.md (eleven public
  functions in `gnd.api.__all__`), disclosure-mode.md, and the skill edits
  are accurate.
- Every in-page anchor link resolves: anchors.md#versions-1-and-2,
  composition.md#trace-a-derived-fact-back-to-its-sources,
  discover.md#proposing-fact-types-from-generic-rows.
- The DC2 checkpoint copy is byte-identical to the page (SHA-256 `47705a00...`).
  The figures are not retained, which matches the earlier growth DC2 pattern.

## Commands run

| Command | Result |
|---|---|
| `uv run python tools/run_tutorials.py --group compose` | "18 tutorial blocks passed", exit 0 |
| `uv run pytest -q tests/test_composition_example.py tests/test_development_scaffold.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py` | 124 passed, 1 deselected, exit 0 |
| In the scratch `w/` copy: `gnd compose` / `gnd check --composition ... --format json` on composition-conflict | exit 1; the lineage list and only the first missing row appear (F4, F8) |
| Compose and check under a model with the uniqueness removed | exit 0 and a clean check, so the sidecars still bind (F1) |
| Plain `gnd check` on the conflict population plus the C-1/Zurich claim | reports the C-2/Lyon row as missing (F4) |
| `gnd discover --help`, `gnd extract --help`, `inspect.signature` of `gnd.api` | used for F2 and the edit checks |
| `grep -rlE "<CT5-C1 terms>" docs src/gnd/skills README.md` against the table | 55 matches; table rows reconciled (F7) |

Not run: `zensical build --strict` and `tools/check_docs.py site` (T2). The
build writes `site/` inside the repo, which this read-only review must not
touch.
