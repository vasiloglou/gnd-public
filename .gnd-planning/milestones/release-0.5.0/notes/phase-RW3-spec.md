# Phase RW3: publication hand-over

## 1. Status

**r1, draft. No ruling.** Written on 2026-11-25 against main `44d866df`,
after the owner merged the RW2 record (pull request 284). The
[plan](release-0.5.0-plan.md) is r5. No review has read this spec. The phase
prepares the owner's publication acts and performs none of them.

The three-file change of M1 to M3 was drafted in the working tree while this
spec was written, to measure what the helper reports. Nothing was committed
before the ruling of §7.

## 2. Provenance

This spec derives from plan §4 (RW3 and the publication stage), §9, §11
("RW3-C4 and RC-03", "Publication order") and the
[RW2 record](../004-phase-RW2.md), and from the predecessor phase
[RV3](../../release-0.4.0/010-phase-RV3.md) with
[its spec](../../release-0.4.0/notes/phase-RV3-spec.md) and
[dossier](../../release-0.4.0/evidence/RV3/dossier.md), whose shape it
repeats. Three carried items of the 0.4.0 close are discharged here
([sweep](../../release-0.4.0/notes/close-question-sweep.md)): RC-03, RC-06
and, as an owner act the dossier names, RC-07.

Measured before writing, on a disposable clone of main `44d866df`:
`tools/release_text.py publish` for 0.5.0 changes eight files and leaves
seven lines for a person, on five pages. They are listed in §6.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RW3-C1 | the dossier: candidate identity, results, what was not measured | plan §4 | M5 |
| RW3-C2 | each owner act with its evidence: the availability recheck, the route, the tag on the accepted `SOURCE_COMMIT`, the GitHub release with its attachments, RC-07's checks | plan §4, RW-D5, RW-D9, RW-D12 | M5 |
| RW3-C3 | the exact `release_text.py publish` invocation, rehearsed on a scratch tree; every prepared-state marker inventoried; the lines left for a person listed; a negative control for the receipts phrase | plan §4, RC-03 | M2, M3, M6, T1, T4 |
| RW3-C4 | `docs/releasing.md` names the releases published by token upload through 0.4.0 | plan §4, RC-06 | M1 to M3, T2 |
| RW3-C5 | a dated read-only remote snapshot, compared with W4 | plan §4 | M7 |
| publication order | upload; the served-file comparison and a fresh index install; the tag; the GitHub release; the pages pull request; the issue comments | plan §11 | M5 |
| RW2 open question | the dossier's "what was not measured" lists every "none" and "no probe" clause of the RW2 coverage table | RW2 record | M5 |
| RW2 boundary | the candidate is stale if main changes a shipped file after `85d076ba` | RW2 record | T6 |
| structure guards | RW3 changes a page and a tool | plan §11, `project.md` | T5 |
| component index | its check runs before a pull request | `project.md` | T5 |

## 4. The standing rules, bound to this phase

- Plan rule 1 and AGENTS.md: nothing is uploaded, tagged or released, and
  `release.yml` is not dispatched or edited. The dossier's commands are
  written for the owner and are not run.
- Plan rule 3: the install pins stay at 0.4.0 on main. The rehearsal changes
  them only in a disposable clone.
- `docs/releasing.md` is the one home of the procedure. The dossier cites it
  and adds no rule.
- AGENTS.md, "General solutions, not pattern-matched ones": M2 changes two
  patterns. Each is for a flat phrase or a flat sentence and states its whole
  grammar (§6). The helper reads pages line by line, and prose wraps, so M2
  also reads each paragraph as one line; T1 holds a wrapped case for each
  new phrase.
- `project.md` rules 1 to 4: the helper reads this repository's own pages.
  The phase adds no consumer of untrusted input.

## 5. Goal

On the RW3 tree:

- `uv run pytest -q tests/test_release_text.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py`
  exits 0;
- `uv run python tools/release_text.py check` exits 0;
- in a disposable clone of the RW3 commit, `release_text.py publish`
  followed by the supplemental patch leaves `release_text.py check` at exit
  0, the four release test files at exit 0, and the strict docs build and
  the site link check at exit 0;
- the dossier names every publication act with the exact command and the
  receipt it needs.

## 6. Design

Reuse: the helper `tools/release_text.py`, RV3's rehearsal script and
dossier shape. No new tool.

### What the helper leaves for a person (measured)

`publish --date 2026-11-25 --built 85d076ba --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10'`
on a clone of `44d866df` exits 1 and reports:

| Page | Line | Why it is reported | Proposed publication-day text |
|---|---|---|---|
| `docs/marketplace-plugins.md` | "version 0.5.0, which is prepared and not published. To use that plugin," | prepared wording RW1 wrote | the sentence 0.4.0's publication used: "When using a plugin from another commit, match its runtime as [Updates](#updates) describes." |
| `docs/bookrec/08-guarded-rules.md` | "GND 0.4.0 includes all commands in this chapter." | names an older version | "GND 0.4.0 and later include all commands in this chapter." |
| `docs/bookrec/09-suggested-rules.md` | "GND 0.4.0 includes guarded-join discovery and constants in mined rules." | the same | "GND 0.4.0 and later include ..." |
| `docs/bookrec/09-suggested-rules.md` | "GND 0.4.0 includes GR-D1 through GR-D12." | the same | "GND 0.4.0 and later include GR-D1 through GR-D12." |
| `docs/expense/05-receipts.md` | "GND 0.4.0 includes identity decisions, fixed reference lists, and separate" | the same | "GND 0.4.0 and later include ..." |
| `docs/literature/index.md` | "GND 0.4.0 lets you build one checked ontology over many papers." | the same | "GND 0.4.0 and later let you build ..." |
| `docs/literature/index.md` | "0.4.0, run for real." (of "the packaged literature example in GND 0.4.0, run for real") | the same | "the packaged literature example, run for real": the page now holds results 0.4.0 does not ship, and no test ties the sentence to a version (D3) |

Five of the seven are statements that a feature first shipped in 0.4.0,
written at the 0.4.0 publication. The helper already lets the form "GND
X.Y.Z and later" stand. The supplemental patch (M6) holds all seven edits;
they are applied at publication, not now, because the plan keeps the pages
in their prepared state until then.

### Prepared-state inventory

Searched in `README.md` and `docs/` outside the notes for wording that says
a feature is not published or needs a checkout:

- the three markers RW1 wrote: the compatibility sentence, the support row
  and the plugin sentence. `publish` rewrites the first two; the third is in
  the table above;
- the notes heading and opening paragraph, which `publish` rewrites;
- no page says a 0.5.0 feature is "on `main` after 0.4.0" or "not in a
  published package". The pages for the features of 0.5.0 describe them
  without a version;
- about a dozen lines say in general how to use unreleased work from a
  checkout (three how-to pages, three tutorials, `pyrel-apps.md`, the
  installation and plugin pages, and two example pages that run a script
  from a checkout). They stay true after any release and are not reported.

### Modules

| ID | Path | Change | Lines (estimate) |
|---|---|---|---|
| M1 | `docs/releasing.md` | the token-route sentence names 0.1.0 to 0.4.0 (RC-06) | 1 |
| M2 | `tools/release_text.py` | (a) the `STANDING` entry for that sentence accepts any list of releases of the form "through X (A, B and C)", so the next token release changes the page and not the tool; (b) `STALE` gains two phrases, "not in a published" or "not in any published", and "on `main` after" followed by a digit (RC-03); (c) each paragraph is also read as one line, so a phrase split over a line break is reported | about 20 |
| M3 | `tests/test_release_text.py` | the fixture's sentence; controls for (a), (b) and (c): the receipts note as it stood at the 0.4.0 preparation, each phrase alone and wrapped, the standing guidance that must not be reported, and five forms of the token-route sentence | about 50 |
| M4 | this spec's rulings, the record | planning | -- |
| M5 | `evidence/RW3/dossier.md`, `evidence/RW3/github-release-notes.md` | the hand-over | evidence |
| M6 | `evidence/RW3/rehearse-publication.sh`, `tool-only-preview.txt`, `post-publication-supplement.patch`, `scratch-verification.txt` | the rehearsal | evidence |
| M7 | `evidence/RW3/pre-publication-state.txt` | the remote snapshot | evidence |

**The two new `STALE` phrases, and what each covers.** "not in a published
package yet" is the receipts page's sentence; the pattern is the phrase up to
"published", with "a" or "any", in any case. "on `main` after 0.3.1" is the
other half of the same note; the pattern is "on main after" with or without
the code marks, followed by a digit, so "After 2 runs" in another sentence
and "on `main`" alone are not matched. Neither phrase occurs on main today
outside the notes.

**The paragraph pass.** For each paragraph, the helper counts the phrase
matches in the paragraph joined to one line and in its lines separately. If
the joined text has more and no line of the paragraph was already reported,
it reports the joined paragraph. A standing line is matched whole, as now.

### Normative order

None is added. The order of the publication acts is plan §11's; the dossier
repeats it by reference to `docs/releasing.md` and the plan.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D1 | Are the seven page edits applied now or at publication? | (a) at publication, by the supplemental patch, as RV3 did and the plan says; (b) the six "0.4.0 and later" edits now, since they are true today, leaving one line for publication day. (b) shortens publication day and edits pages other phases wrote in a phase whose plan row names one page | open; proposed: (a) |
| D2 | The reviewer for the RW3 diff | one reviewer in a different tool through the review helper, one round, a second only over a repair | open; proposed: yes |
| D3 | The literature page's "in GND 0.4.0, run for real" | drop the version, or name 0.5.0. Naming 0.5.0 claims the page's every result comes from the 0.5.0 package, which this phase did not check | the owner's at publication; proposed: drop the version |
| D4 | The GitHub release body | a draft in M5, from the notes' headline and blocks, for the owner to edit | open; proposed: yes |
| D5 | Issue comments after publication (plan RW-D10) | the plan names issues 214 and 217. The 0.5.0 notes also link issues 193, 215, 216, 218, 221, 222, 226, 227 and 228, and the Ossie milestone says it filed 276 to 278 for its three requests | the owner's at publication; the dossier lists the issues and drafts no text |

Rulings are appended below this line, each with its date, source and the
SHA-256 of the spec bytes it covers.

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `tests/test_release_text.py::test_prepared_install_guidance_is_reported` (six texts) and `test_standing_install_guidance_is_not_reported` | the six are reported as stale lines of that page; the standing text reports nothing. Control, run before the ruling: with the helper as it is on main, all six fail (so do the tests whose fixture holds the new token-route sentence) |
| T2 | `test_the_token_route_sentence_stands_for_any_list_of_releases` (five forms) | three stand, two are reported |
| T3 | the rest of `tests/test_release_text.py`, and `tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py` | exit 0 |
| T4 | the rehearsal script on a disposable clone of the RW3 commit | the tool-only publish exits 1 with the seven lines; the patch applies; `check` exits 0; the four release test files, the strict docs build and the site link check exit 0 |
| T5 | the structure guards; `uv run ruff check`; the component-index check; the strict docs build and the site link check on the RW3 tree | exit 0, apart from the scaffold guard's known local failure |
| T6 | `git diff 85d076ba HEAD -- src PYPI.md pyproject.toml LICENSE NOTICE` on the RW3 tree | empty: the sdist holds exactly those paths, so the candidate is not stale |

### Verification selection

| Kind | Selection |
|---|---|
| Plan-mandated | plan §9's RW3 row: the four release test files and `release_text.py check`; plan §11: the structure guards |
| Direct | T1, T2, T4 |
| Impact closure | `tests/test_release_text.py` runs in the default lane; `docs/releasing.md` links are checked by the site link check |
| Broad lanes | none. The full default lane is the close's. No opt-in lane runs |

### Implementability

- T4 needs the RW3 commit, so the rehearsal runs after M1 to M3 are
  committed and its outputs go in a second commit.
- The rehearsal uses a date. The real publication date is an input of the
  publication stage; the dossier's command asks for it.
- RC-07 cannot be discharged by this phase: account ownership and a human
  review of repository content and history are the owner's. The dossier
  names them as the first act and says what record they need.

## 9. Out of scope for this phase

- Every publication act: the upload, the tag, the GitHub release, the pages
  pull request, the issue comments.
- The pins, `RELEASED`, and the seven page lines (D1).
- Any change under `src/`, and a new candidate.
- Trusted Publishing, TestPyPI and other platforms.

## 10. Size

About 20 tool lines, 50 test lines, 1 page line; one rehearsal; one review
round. Past 120 changed lines outside planning the phase pauses.

## 11. Approval instrument

This prose and the measured table of §6. Corpus-first is not used: the phase
changes no serialized format, exit code or validation predicate of the
product. The helper's exit codes do not change.

## Verification commands

```bash
uv run pytest -q tests/test_release_text.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py --tb=short
uv run python tools/release_text.py check
uv run ruff check
python3 scripts/components_index.py changed --base origin/main --strict
uv run --group docs zensical build --strict
uv run python tools/check_docs.py site
git diff 85d076ba HEAD -- src PYPI.md pyproject.toml LICENSE NOTICE
```

The structure-guard command is the one in `project.md`.
