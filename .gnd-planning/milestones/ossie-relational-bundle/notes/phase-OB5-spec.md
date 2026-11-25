# Phase OB5 spec: docs and skill

**Status: draft r1, awaiting owner review.** No docs, skill or test file is
edited before the owner gate.

## 1. Provenance

- **Plan:** [ossie-relational-bundle-plan.md](ossie-relational-bundle-plan.md)
  r2, §4 "OB5: docs and skill", completion predicate 6, §5 and §9.
- **Prior records:** [004 OB1](../004-phase-OB1.md),
  [008 OB2](../008-phase-OB2.md), [011 OB3](../011-phase-OB3.md),
  [012 OB3 departures](../012-OB3-departures-gate.md),
  [015 OB4](../015-phase-OB4.md),
  [016 OB4 departures](../016-OB4-departures-gate.md).
- **Base:** main at `6758d224` (PR 272 merged). OB1–OB4 are on main.
- **Reviews:** none has run over this spec.

## 2. Obligations (the harvest)

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | Plan §4 OB5, deliverable | The normative section, the explanation, the how-to (a worked relational export and a binding), the export skill guidance, a changelog entry. | §5.1–§5.6 |
| O2 | Plan §4 OB5, deliverable | The changelog states exit 11 and exit 64 by their constants. | §5.5, T5 |
| O3 | Plan §4 OB5, criteria | The docs build and the link check passes. | T1, T2 |
| O4 | Plan §4 OB5, criteria; predicate 6 | The normative section is the only home of every rule. The reviewer checks every cited rule. | §5.7, T4, §8 |
| O5 | Plan §3 | OB5 also documents OB1 (`--max-output-bytes`, `--max-input-bytes`). | §5.1, §5.2, §5.4, §5.5 |
| O6 | Plan §9, OB5 row | "The docs link check named in the OB5 spec"; affected consumer: the site. | T1, T2 |
| O7 | Plan §5 | The default change to five files and the exit 11 collision go in the changelog. | §5.5 |
| O8 | Plan §6 | A reader must not take the generated tables for delivered ones: the `source_kind: logical` marker is explained. | §5.1 |
| O9 | Records 011 and 015, boundary | The user docs, the how-to, the skill and the release note "still describe three files and no binding". | §5.1–§5.5 |
| O10 | Record 015, K13 | Tables linked only by surrogate keys cannot be bound. A reader has to be told. | §5.1, §5.3 |
| O11 | Records 012 and 016 | The accepted departures are behaviour a reader meets: a model with no table writes three files; `unmapped_links`; the 32-role limit; the 8-level identifier limit; an entity and a part of its identifier may share a column. | §5.1 (in plain words, linked to the rule) |
| O12 | Records 011 and 015 | The upstream validator has not run on the new files. Docs must not say it has. | H7, §5.1 |
| O13 | Records 004–015, OB1-Q1 | `guard_yaml`'s captured default: "OB5 or the close sweep". | H8 |
| O14 | Release session's message | Release-note bullets go under an `Unreleased:` heading in `docs/release-notes.md`. The repository has no `CHANGELOG.md`; that page is the changelog. | §5.5 |
| O15 | AGENTS.md; memory | Public text names no downstream project or customer. PyRel stays optional. Business pages show `/gnd` prompts beside results. | §5 (all), §8 brief |
| O16 | Plan §7 | Out of scope stays out: DDL, importing the relational files, metrics. | §6 |

## 3. Standing rules bound to this phase

| Rule | Binding here |
|---|---|
| 1 Totality | No new reader of untrusted input. The one new file (the example binding, H3) is read by the OB4 reader, already total. Inapplicable otherwise. |
| 2 Cap bounds the document | No algorithm changes. Inapplicable. |
| 3 Validation order | No new refusal. The docs state none; they link to the order in the normative section. |
| 4 One walk | Inapplicable: no walk is added. |
| 5 One home | The binding rule of this phase. The explanation, how-to and skill describe and link; they state no rule. T4 fails when a page uses a rule id, reason or flag the normative section lacks. |
| 6 Measure | Numbers on the pages (file counts, table counts in the example) come from a run in the test, not from memory (T3, T6). |
| General solutions | T4 and T6 read Markdown fences with the existing tutorial block parser and YAML with its loader. No regular expression over nested text. |

## 4. Goal

After OB5, a reader of the site and of the export skill learns that
`gnd export ossie` writes five files, how to get three, how to raise the size
bounds, and how to describe delivered tables with a binding. `uv run --group
docs zensical build --strict` exits 0, `uv run python tools/check_docs.py site`
exits 0, the how-to's commands run in the tutorial runner with exit 0, and the
focused docs tests exit 0.

## 5. Design

### Reuse

| Capability | Searched | Found | Decision |
|---|---|---|---|
| Build and link check | `components_index.py search "docs link check"`; `docs/development/documentation.md` | `zensical build --strict`, `tools/check_docs.py site` | reuse |
| Run a page's commands in tests | `git grep gnd-run`; `tools/run_tutorials.py` `groups()` | the `<!-- gnd-run expect=N -->` marker and the group table | reuse; add one group `ossie` |
| Exit constants | `src/gnd/exits.py` | `EXIT_COLLISION` 11, `EXIT_USAGE` 64 | reuse in T5 |
| Schema validation of the example output | `gnd.export.ossie_relational.validate_relational` | as used by the corpora | reuse in T6 |

Nothing new is built outside tests, pages and one example file.

### 5.1 `docs/explanation/ossie.md` (about 63 → 130 lines)

- **Scope paragraph.** Today it says semantic models and mappings are outside
  scope. New text: the export writes the ontology, a semantic model and a
  mapping. Import reads the ontology only. Metrics, dimensions and query
  interfaces stay outside.
- **New section "The tables an export describes".** In business terms: the
  semantic model lists one table per thing that has facts of its own, with
  its key and its links to other tables; the mapping says which column holds
  which concept. These tables are GND's reading of the model, not tables you
  have delivered, and each is marked `source_kind: logical` (O8).
- **New section "What is listed instead of mapped".** Every fact type and
  constraint is either carried or listed with a reason. The page gives the
  reasons a reader will meet, each in one plain sentence, and links to the
  normative list. It states the three limits as limits (O11): a model that
  yields no table writes three files and a note; a fact type with more than
  32 roles and an identifier nested more than 8 entities deep are listed.
- **New section "Describe the tables you delivered".** What a binding is, when
  to use one, that without it nothing changes, and the known limit: tables
  linked only by surrogate keys cannot be bound (O10).
- **New section "Large models".** The 10 MiB default per file,
  `--max-output-bytes`, `--max-input-bytes` on import, the 256 MiB ceiling,
  and that the model source itself stays capped at 10 MiB (O5).
- **Validation sentence (O12, H7).** "GND checks the semantic model and
  mapping against the pinned Ossie schemas." It does not say Ossie's own
  validator accepted them unless H7 runs that lane first.
- The PyRel section and its numbers are unchanged.

### 5.2 `docs/how-to/share-an-ossie-ontology.md` (revised in place)

- The file table grows from three export files to five, plus the two import
  files.
- A short "See the tables" step shows one dataset and one mapping entry from
  the real refunds export, and the list of fact types the export names
  instead of mapping.
- `--ontology-only` is shown as the way to keep the earlier three-file output,
  with one sentence on the exit 11 collision.
- The three existing commands get `<!-- gnd-run expect=0 -->` markers, and the
  page joins a new `ossie` group in `tools/run_tutorials.py`.
- The `/gnd` prompt stays beside the commands.

### 5.3 New page `docs/how-to/describe-delivered-tables-for-ossie.md` (H2)

- **Reader's goal:** "My warehouse already has a refunds table. I want the
  Ossie files to describe that table, not GND's."
- The page shows the example binding (H3), the command with
  `--physical-binding`, the resulting dataset, and the extension's list of
  what the binding left out.
- It shows one refused binding (a misspelled role name) with its rule id and
  exit 3, marked `<!-- gnd-run expect=3 -->`.
- It ends with the limits (O10) and a link to the normative section and the
  packaged schema.
- `zensical.toml` gains the nav entry. The page is in the `ossie` group.

### 5.4 `src/gnd/skills/gnd-export/SKILL.md`, "Ossie interchange" section

- Five files by default; `--ontology-only` for three.
- Before sharing, read the mapping's `GND` extension as well as the loss
  report: `dispositions` and, when present, `unmapped_links`.
- `--physical-binding FILE` when the user has delivered tables; a refusal
  names a `binding:` rule and exits 3; fix the binding, do not edit the model
  to fit.
- `--max-output-bytes` and `--max-input-bytes` for a named size refusal only;
  never raise a bound to pass a different refusal.
- The frontmatter `description` gains "semantic model and mapping".
- **Pin sites:** the generated discovery copies of the skill and any skill
  census or digest test. They are counted when the phase runs, not here.

### 5.5 `docs/release-notes.md`

One section, `## Unreleased: Ossie relational files`, with these bullets:

1. Five files by default. A file already at `OUT.semantic_model.<fmt>` or
   `OUT.mapping.<fmt>` exits 11 (`EXIT_COLLISION`) and publishes nothing.
   `--ontology-only` keeps the three-file run.
2. `--physical-binding FILE`, with its schema id and the exit 3 refusals.
   Combined with `--ontology-only` it exits 64 (`EXIT_USAGE`).
3. `--max-output-bytes N` on export and `--max-input-bytes N` on import;
   an out-of-range value exits 64 (`EXIT_USAGE`).
4. Known limits: surrogate-key tables cannot be bound; a model with no table
   writes three files.

The bullets name no downstream project (O15).

### 5.6 Smaller mentions

- `README.md` lines 22–28 and 149, and `docs/index.md` lines 25–32: "ontology
  files" becomes wording that includes the tables. One sentence each.
- `docs/reference/cli.md`: the command table gains rows for
  `gnd export ossie` and `gnd import ossie`, each with its flags and a link
  to the normative section. It has none today.
- `dev/components/`: no module changes, so the index needs no entry. The
  pre-PR check still runs.

### 5.7 The normative section (audit, not authorship)

OB1–OB4 already wrote "Ossie interchange" in `representation-format.md`. OB5
reads it against completion predicates 1–5 and the two departures records and
lists every gap. A gap is fixed there, in this phase, and named in the record.
One is known now: the section's opening paragraph on publication and exit
codes predates the five-file run and omits exit 64. No rule is restated
anywhere else.

## 6. Out of scope

- Any change to export or import behaviour, or to `--help` text beyond a
  wording error the audit finds.
- DDL, importing the relational files, metrics (plan §7).
- The reporter questions and the three GitHub issues (D10).
- The milestone close record and the close-bar panel.
- Videos, tours and the launch drafts.

## 7. Decisions for the owner

| ID | Question | Proposal | Cost of the alternative |
|---|---|---|---|
| H1 | Approval instrument. | Prose: this spec. Then one **viewable checkpoint**: the built pages, shown before the review, as for earlier docs work. | Corpus-first does not fit; a docs phase has no format, exit contract or predicate of its own. |
| H2 | One how-to page or two. | Two: the existing page for sharing, a new page for the binding. | One page mixes two readers' goals and doubles its length; the plan's "the how-to" reads as one page. |
| H3 | Where the example binding lives. | A packaged file, `src/gnd/examples/refunds/physical-binding.json`, so the page's command runs from an installed GND. | Inline in the page: the reader pastes about 30 lines of JSON before the first command. |
| H4 | Run the how-to commands in tests. | Yes: `gnd-run` markers and an `ossie` tutorial group. | Without them a page can show a command that no longer works. |
| H5 | The release-note section title and its four bullets (§5.5). | As written. | — |
| H6 | Update README, the index page and the CLI reference (§5.6). | Yes, minimal wording. | They keep saying "ontology files" only. |
| H7 | **Run Ossie's own validator now** (OB3-Q3, the opt-in oracle lane: OB3 T11 and OB4 T13). Predicate 4 needs it before the milestone can close. | Yes, in this phase, before the pages are final. If it finds a defect, that is repaired first and the pages describe what is true. | Deferring to the close leaves the docs worded around an unrun check, and a late finding reopens pages already merged. |
| H8 | OB1-Q1, `guard_yaml`'s captured default. | Leave to the close sweep. It is a code change with its own tests, not docs. | Folding it in widens a docs phase into the input policy. |
| H9 | Review. | One Codex round over the diff. Its brief: check every rule id, reason and flag on a page against the normative section; find a rule stated twice; run each page command; look for a downstream name. | — |
| H10 | OB4's review fixes are not re-reviewed (OB4-Q2). | No second round; the close-bar panel reads the merged code. | A second round costs one more reviewer run now. |

## 8. Tests

New file `tests/test_ossie_docs.py` unless noted.

| ID | Case | Expected |
|---|---|---|
| T1 | `uv run --group docs zensical build --strict` | exit 0 |
| T2 | `uv run python tools/check_docs.py site` | exit 0 |
| T3 | `tests/test_documentation_tutorials.py::test_documented_learning_path[ossie]`: both how-to pages run block by block. The binding page's refused run expects exit 3. | exit 0; more than 0 blocks run |
| T4a | **Cited ids exist.** Every `binding:…` rule id, every unmapped reason and every `ossie:…` id written on the explanation, the two how-tos and the skill section appears in the normative section. | pass; fails on a planted unknown id |
| T4b | **Flags are covered.** Every option in the `gnd export ossie` and `gnd import ossie` parsers appears in the skill section and in the CLI reference. Read from the parsers, not from help text. | pass; fails when a flag is added and not documented |
| T5 | The release notes have the `Unreleased: Ossie relational files` section, and the numbers beside `EXIT_COLLISION` and `EXIT_USAGE` equal `gnd.exits`. | pass |
| T6 | **Shown output is real.** Each YAML or JSON excerpt marked on the how-to pages is contained in the file the test's own run wrote. The example binding exports with exit 0 and `validate_relational` accepts the result. | pass; fails on an edited excerpt |
| T7 | Existing guards: `tests/test_disclosure_docs.py`, `tests/test_release_docs.py`, `tests/test_packaged_skills.py`, `tests/test_skill_prose_sync.py`, the skill census tests, and the project guard block. | exit 0, except the one known red `test_reference_closure_and_declared_bootstrap` |
| T8 | `uv run ruff check`; `python3 scripts/components_index.py changed --base origin/main --strict` | exit 0; 0 to fix |
| T9 | Only if H7 is approved: `uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py` with the oracle root prepared from the OS0 receipt. | recorded as run, with its result |

**Verification selection.** Direct: T1–T6. Impact closure: T7 (the skill and
docs guards). Not selected: the export, Rmap and binding suites, because no
source under `src/gnd` changes except the skill text and one example file;
they are selected again if the audit (§5.7) or H7 leads to a code change.

## 9. Coverage argument

- A page that shows a dead command fails T3.
- A page that invents or misspells a rule id fails T4a.
- A flag added later without docs fails T4b.
- A release note with a wrong exit number fails T5.
- An excerpt that drifts from real output fails T6.
- A broken link or anchor fails T1 or T2.
- A rule stated a second time in different words is not caught by a test. It
  is the reviewer's task (H9) and is named in the record's boundary.
