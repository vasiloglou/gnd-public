# Phase NM4: documentation

**Status: r1, approved by the owner 2026-11-02 `(s4)`; implemented, record [004-phase-NM4.md](../004-phase-NM4.md).**

`(s4)` Owner approval, 2026-11-02, quoted: "Approve as proposed", in answer to
"Do you approve the NM4 spec with D1–D4 as proposed?" The answer was the offered
button whose stated meaning was approval with D1–D4 as proposed and no review
panel over the spec. Approved bytes: SHA-256
`b973fbe0caa8c5dd4ff6bc576fbca04643766c4e6b99f708a889059f92b8ddb1` (before this tag). Rulings: D1 (a), D2 (a), D3 (a), D4 (a);
no spec review panel.

## Provenance

- Plan: [why-not-near-misses-plan.md](why-not-near-misses-plan.md) r3, approved
  `(a1)`: §0 (NM-R1..R8), §2.2 (the disclosure contract), §4 NM4 (the page
  table, NM4-C1..C5), §5, §6, §7, §9 NM4 row, and §10 rulings NM-D11, D12, D13,
  D16 and D17.
- Prior phases: [001-phase-NM1.md](../001-phase-NM1.md),
  [002-phase-NM2.md](../002-phase-NM2.md) and
  [003-phase-NM3.md](../003-phase-NM3.md), committed through `420114e`.
- Checkpoints, all shown to the owner on 2026-11-01:
  - DC1 (illustrative drafts), "Looks good";
  - DC1b (the how-to from real runs of `23e4a99`), "Looks good";
  - DC2 (every page from real runs of `420114e`), "Looks good".
    [checkpoints/DC2/](../checkpoints/DC2/) holds the drafts this phase ships.
    The two questions on the DC2 page were not ruled. They are D1 and D2 here.
- Harvest and measurements at `420114e`, by the author:
  - the plan inventory command, re-run at `33c260e` and at `420114e`;
  - `tools/run_tutorials.py` `groups()`, the parametrization in
    `tests/test_documentation_tutorials.py`, and the `zensical.toml` nav;
  - the packaged-skill pin suites;
  - the homes of `N` and of the mode table;
  - the real runner (`run_tutorials.run_pages`) over the two DC2 pages as one
    group: 16 blocks passed.

  No review has read this spec.

## Corrections to the plan, found at harvest

Recorded as refuted premises; the plan is repaired at milestone close.

| ID | Plan sentence | What the code shows | Repair here |
|---|---|---|---|
| H1 | NM4 page table: "`docs/reference/python-api.md` Lines 273-275, 336, 345-346" | At `420114e` the passages are lines 271-276 (witness), 330-337 (why-not) and 345-346 (redaction bullet). | Edits are placed by passage text (Design), not by line. |
| H2 | NM4-C3: register new pages "in `tests/test_documentation_tutorials.py` parametrization" | That parametrization omits the `why-not` and `learners` groups that `groups()` defines. They run only through `tools/run_tutorials.py` and `check_installed_docs.py`. | D3. |
| H3 | NM4 page table: `disclosure.md` "the disclosure table (generated from NM2-C2, not hand-listed)" | Nothing generates pages at build time. The site build is `zensical build`, with no macro or hook in use. | D2: the table is pasted from a generator, and a test fails on drift. |
| H4 | The plan names no source edit in NM4 | `src/gnd/disclosure.py:6` says "The normative text is the NM2 spec until docs/reference/disclosure.md holds it." Standing rule 5 makes the page the one home once it ships. | One docstring line points at the page (Design). |
| H5 | NM4 page table: `docs/bookrec/*` "expected unchanged" | `docs/bookrec/02-facts.md:63-64` says "choose disclosure deliberately when checking real user data", with no link. | That phrase links to `disclosure.md`. Nothing else in the tutorial changes. |

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| §4 NM4 page table | each listed page changes as stated | Design, page by page |
| NM4-C1 | the disposition table is complete and committed in the NM4 record | Disposition table below; T9 |
| NM4-C2 | DC1, DC1b and DC2 shown, with reactions recorded | done (Provenance); the record repeats the quotes |
| NM4-C3 | new pages registered in `groups()` and in the test parametrization; `run_tutorials.py`, `zensical build --strict`, `check_docs.py site`, `test_documentation_tutorials.py`, `test_plan_app_docs.py`, `check_installed_docs.py` exit 0 | Design (registration); T1–T4 |
| NM4-C4 | one home: `N` and the near-miss rule only in `why-not.md`; the mode table only in `disclosure.md`; a grep test enforces both | T5 |
| NM4-C5 | an independent docs review (one local reader) against shipped behaviour | T8 |
| §9 NM4 row | "NM4-C3 commands plus the one-home grep test" | Verification selection |
| §2.2 reporting | the release note lists the customer-mode contract changes | Design, `release-notes.md` |
| NM-D13, NM-D16, NM-D17 | `disclosure.md` lists the every-mode outputs, the child-process rule and the membership signal | Design, `disclosure.md` |
| NM-R6 | the docs state the threat model: guard, not lock, in process | Design, `disclosure.md` "Who customer mode protects" |
| §6 "docs describe the plan rather than the code" | every output from a real run | T1; every block is `gnd-run` |
| §6 "docs drift into two homes" | one home per rule | T5 |
| §5 skill surfaces | packaged-skill edits with their pins | Design, packaged skills; T6 |
| NM2-Q1 (owner, before NM4 publishes `disclosure.md`) | `doccheck` stays every-mode? | D1 |
| NM2 record boundary: every-mode rows "nothing documents that yet (NM4)" | documented | `disclosure.md` every-mode table |
| NM3 H1 and review R5 | "The Python API returns raw values" in `why-not.md` is mode-dependent | Design, `why-not.md` |
| DC1b finding | `gnd check` text format prints a banner then JSON | out of scope (pre-existing on main); pages use `--format json` |

### Inventory and dispositions (NM4-C1)

The plan's command, `git grep -li 'redact\|--raw\|unredacted\|why-not' <rev> --
docs src/gnd/skills`, returns the same 28 files at `33c260e` and at `420114e`.
Adding `disclos` returns 8 more hits (one already listed). Seven of them use
"disclosure" in another sense. Every file has a disposition:

| File | Disposition | Reason |
|---|---|---|
| `docs/reference/why-not.md` | change | "Values in the answer" depends on the mode |
| `docs/reference/cli.md` | change | root option, the check-family sentence, witness and why-not rows, refusal exits |
| `docs/reference/python-api.md` | change | witness, why-not and redaction passages; new section "Under a disclosure mode" |
| `docs/reference/capabilities.md` | change | why-not row; new disclosure row |
| `docs/reference/discover.md` | change | one sentence: same in every mode |
| `docs/reference/ilp-bridge.md` | change | one sentence: same in every mode |
| `docs/guides/exports.md` | change | one sentence: `--raw` refused under `customer` |
| `docs/agents/export-and-review.md` | change | the same sentence |
| `docs/release-notes.md` | change | disclosure-mode entry |
| `docs/bookrec/02-facts.md` | change | one link (H5) |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | change | the `redact` entry says how the modes use it |
| `src/gnd/skills/gnd-export/SKILL.md` | change | near-miss counters in the why-not step; `--raw` refused under `customer` |
| `src/gnd/skills/gnd-export/references/export-contract.md` | change | `--raw` refused under `customer` |
| `src/gnd/skills/gnd-dev-session/references/judgment-contract.md` | change | `--unredacted` refused under `customer` |
| `src/gnd/skills/gnd-dev-session/references/session-v7-contract.md` | change | feedback redaction is the same in every mode |
| `docs/how-to/repair-a-missing-claim.md` | unchanged | changed in NM3; runs with the mode unset and links the reference |
| `docs/runtimes/lean.md`, `docs/runtimes/souffle.md` | unchanged | the runner drops `GND_DISCLOSURE`; their `--raw` is the unset behaviour |
| `docs/bookrec/04-application.md`, `05-repair.md`, `06-evolution.md` | unchanged | `unredacted=True` / `--unredacted` under the unset default, as the tutorial explains |
| `docs/expense/01-model.md`, `02-application.md`, `03-evolution.md` | unchanged | the same |
| `docs/development/architecture-audit.md` | unchanged | "redaction" names a module in a historical inventory |
| `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json` | unchanged | `redact` has no description stating behaviour |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | unchanged | "redact" refers to user-authored prose in records |
| `src/gnd/skills/gnd-dev-session/SKILL.md` | unchanged | its "redaction" is of adapter credentials |
| `src/gnd/skills/gnd-conformance/references/conformance-contract.md`, `gnd-review-panel/references/review-contract.md` | unchanged | "progressive disclosure" of skill files |
| `src/gnd/skills/gnd-extract/SKILL.md`, `gnd-orm-core/references/coverage-and-element-addressing.md` | unchanged | "disclosed" means a stated outcome or identity |
| `src/gnd/skills/gnd-review-panel/SKILL.md`, `gnd-review-panel-light/SKILL.md`, `gnd-update-review-panel/SKILL.md` | unchanged | disclosure of reviewer-tool limits |

New files: `docs/reference/disclosure.md`, `docs/how-to/disclosure-mode.md`,
`tests/test_disclosure_docs.py`.

## Standing rules bound to this phase

1. **Totality.** No new input is read by GND. The new test reads repository
   files only.
2. **The input cap bounds the algorithm.** Not applicable: no algorithm
   changes.
3. **Validation order.** Unchanged. The pages state the shipped order (the
   malformed variable first, then loosening, then raw requests), which NM2
   T9–T11 pin.
4. **One walk.** The disclosure table on the page is produced by one function
   over `gnd.disclosure.SURFACES`, the same table NM2's totality test walks.
   No page lists surfaces by hand.
5. **One home.**
   - `disclosure.md` becomes the home of the mode's rules and table.
     `gnd.disclosure`'s docstring yields to it (H4). Other pages cite it.
   - `why-not.md` stays the home of `N` and the near-miss rule. The how-to,
     the release note and `disclosure.md` link to it.
   - T5 enforces both.
6. **Measurement over argument.** Every output on the new pages comes from a
   `gnd-run` block, and the table comes from the code. Nothing is asserted
   from the plan.

NM-R1..R8: R1–R3 are unchanged (no kernel change). R4: the docs describe the
one resolver. R5: unset behaviour is described as unchanged, and the tutorials
run unset. R6: the threat model section. R7: no new module (the test lives in
`tests/`). R8: `auto=false`; `tests/test_why_not_anonymity.py` covers the new
files.

## Goal

Every page in the plan's NM4 table says what `420114e` does, as the DC2
drafts do. The two new pages are in the nav and run in a new `disclosure`
tutorial group. `tools/run_tutorials.py`, `zensical build --strict`,
`tools/check_docs.py site`, `tests/test_documentation_tutorials.py`,
`tests/test_plan_app_docs.py`, `tools/check_installed_docs.py --out <new dir>`,
the new `tests/test_disclosure_docs.py` and the packaged-skill suites each
exit 0.

## Design

The shipped text is the DC2 text, minus the DC2 header comments, with these
differences:

- links resolve inside the site (`../reference/disclosure.md` and so on), as
  the drafts already write them;
- in `python-api.md` the new section reuses the `targets.json` the witness
  block already writes, so it has no setup block of its own.

### `docs/reference/disclosure.md` (new, about 230 lines)

Exactly [checkpoints/DC2/docs/reference/disclosure.md](../checkpoints/DC2/docs/reference/disclosure.md):

- the three states;
- setting the mode, with the resolution order and a run of the two exit-64
  usage errors;
- what customer mode refuses;
- the outputs that are the same in every mode (six rows: sessions, `observe`,
  `discover`, ILP export, `fidelity`, `doccheck`, per D1);
- child processes;
- who customer mode protects, with a run of the near-miss count under
  `customer`;
- declaring sensitive roles;
- every command and function.

The last section's table is the output of `disclosure_table()` (D2), pasted
between two marker comments:

```
<!-- disclosure-table:start -->
| Surfaces | What they disclose |
...
<!-- disclosure-table:end -->
```

### `docs/how-to/disclosure-mode.md` (new, about 230 lines)

Exactly [checkpoints/DC2/docs/how-to/disclosure-mode.md](../checkpoints/DC2/docs/how-to/disclosure-mode.md):
13 `gnd-run` blocks over the packaged `disclosure` example and the
`quoted_claims` spelling gap.

### Registration

- `tools/run_tutorials.py` `groups()`: `'disclosure': [root /
  'docs/how-to/disclosure-mode.md', root / 'docs/reference/disclosure.md']`.
- `tests/test_documentation_tutorials.py`: `'disclosure'` added to the
  `test_documented_learning_path` parametrization, plus `'why-not'` if D3 (a).
- `zensical.toml` nav:
  - under How-to guides, after "Repair a claim that does not derive":
    `{ "Run GND for internal or customer readers" = "how-to/disclosure-mode.md" }`;
  - under Reference, after "Why a derived fact is missing":
    `{ "Disclosure mode" = "reference/disclosure.md" }`.

### Edits to existing pages

Exactly the new text in [checkpoints/DC2/changes.md](../checkpoints/DC2/changes.md),
each placed at the passage it names: `why-not.md`, `cli.md`, `python-api.md`,
`capabilities.md`, `formats.md`, `discover.md`, `ilp-bridge.md`,
`guides/exports.md`, `agents/export-and-review.md`, `release-notes.md` (new
entry above the near-miss entry, dated 2026-11-01). In addition there is the
H5 link in `bookrec/02-facts.md`.

### Packaged skills

The five edits in `changes.md` "Packaged skills". They add no relative link,
so `EXPECTED_RELATIVE_LINKS` and `EXPECTED_SKILL_FILES` in
`tests/test_packaged_skills.py` are unchanged. Any phrase or digest pin that
changes is measured at implementation and listed in the record.

### `src/gnd/disclosure.py` (one line, H4)

```python
The normative text is docs/reference/disclosure.md.
```

replaces "The normative text is the NM2 spec until
docs/reference/disclosure.md holds it."

### `tests/test_disclosure_docs.py` (new, about 90 lines)

```python
def disclosure_table() -> str: ...          # moved from checkpoints/DC2/disclosure_table.py
def table_on_page(text: str) -> str: ...    # the text between the two markers
def homes(needle: str, roots=("docs", "src/gnd/skills", "README.md")) -> set[str]: ...
```

Its tests are T5 (a)–(e).

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | `gnd doccheck` in every mode (NM2-Q1, NM2 F10) | (a) Keep it every-mode and list it on the page with its reason: its input is the operator's own rendering case. No exit code changes. (b) Make it a site that follows the mode. That is a code change and a new refusal path, outside a docs phase; it would need its own spec. | **(a)** |
| D2 | How the page's table stays equal to the code (H3) | (a) The table is pasted between markers from `disclosure_table()`, and T5 (a) fails when they differ. A table change means re-pasting, and the failure message prints the expected table. (b) A build-time generator (a zensical hook or macro): a new build dependency, and the page source no longer shows the table. | **(a)** |
| D3 | Which groups join the test parametrization (H2) | (a) `disclosure` and `why-not`: both belong to this milestone, and the second closes a gap NM3 inherited. Costs about 2 seconds of test time. (b) `disclosure` only, as NM4-C3 says literally. `learners` is another milestone's in either reading. | **(a)** |
| D4 | Approval instrument | (a) The DC2 drafts (the owner reacted to their real output) plus this spec's stated differences: the shipped bytes are checked against the drafts in T7. (b) This prose alone. | **(a)** |

## Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `uv run python tools/run_tutorials.py` | exit 0; the `disclosure` group's 16 blocks among those passed |
| T2 | `uv run zensical build --strict`; `uv run python tools/check_docs.py site` | each exits 0; the anchors the new pages link to resolve |
| T3 | `uv run pytest -q tests/test_documentation_tutorials.py tests/test_plan_app_docs.py` | exit 0, including `test_documented_learning_path[disclosure]` (and `[why-not]` under D3 (a)) |
| T4 | `uv run python tools/check_installed_docs.py --out <new dir>` | exit 0 (both wheel origins) |
| T5 | `tests/test_disclosure_docs.py`: (a) the table on `disclosure.md` equals `disclosure_table()`; (b) a page string with one row removed fails (a)'s comparison; (c) `homes("NFKC") == {"docs/reference/why-not.md"}`; (d) the three-state header `\| Mode \| Declared sensitive roles` and the marker `disclosure-table:start` appear only in `docs/reference/disclosure.md`; (e) a copy of either into another page's text is caught by `homes` (negative control over strings) | exit 0 |
| T6 | Packaged-skill suites: `tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_ik6_skill_census.py tests/test_il6_skill_census.py tests/test_public_binding_prose.py tests/test_public_workflow_claim_routes.py tests/test_marketplace_plugins.py` | exit 0 |
| T7 | The shipped new pages equal the DC2 drafts apart from the header comment and the table markers; `changes.md`'s new text appears verbatim on each target page (a scripted check in `evidence/NM4/`) | exit 0 |
| T8 | NM4-C5: one local reader checks every changed page against `420114e` behaviour (running commands), with findings reproduced before they count | findings recorded and dispositioned in the record |
| T9 | NM4-C1: the plan's inventory command at the implementation commit, each file matched to a row of the disposition table (scripted in `evidence/NM4/`) | exit 0, no file without a row |
| T10 | `tests/test_why_not_anonymity.py tests/test_disclosure_mode.py tests/test_rf1_layering.py` | exit 0 (new files scanned; the docstring edit changes no behaviour) |

Every branch has a case that can fail it:

| Branch | Case |
|---|---|
| the page table drifts from `SURFACES` | T5 (a), (b) |
| `N` restated outside `why-not.md` | T5 (c), (e) |
| the mode table restated outside `disclosure.md` | T5 (d), (e) |
| a shown output differs from a real run | T1, T3, T4 |
| a broken link or anchor | T2 |
| a packaged-skill pin | T6 |
| shipped text differs from what the owner saw | T7 |
| an inventory file without a disposition | T9 |

### Verification selection

| Obligation | Disposition | Command | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Plan §9 NM4 row (mandated) | run | T1–T5 | docs, nav, runner groups, the new test | the plan's row | any docs page or the runner |
| Packaged skills | run | T6 | the five skill files | they pin phrases, links and file sets | a skill edit |
| Disclosure module and anonymity | run | T10 | `disclosure.py` docstring; new files | the docstring is in a pinned module; new files are scanned | a source or new-file change |
| Broad default suite | cadence | milestone close, on explicit owner selection | whole repository | every changed path is covered above | an owner selection |

### Implementability sweep (before the gate)

Each requirement was checked against `420114e`:

- **The new pages run under the real runner.** `run_tutorials.run_pages` over
  the two DC2 pages as one group: 16 blocks passed. Every shown output was also
  re-compared byte for byte (`checkpoints/DC2/check_outputs.py`, 13 of 13).
- **The table can be generated deterministically.** `SURFACES` is a dict
  literal, so iteration order is fixed. The DC2 generator produced the page's
  table.
- **The one-home needles are unique today.** `NFKC` appears only in
  `docs/reference/why-not.md` across `docs/`, `src/gnd/skills/` and
  `README.md`. `constraint-reference.md`'s lexical matching says
  "NFC-normalizes", which the needle does not match.
- **Registration is two literal lines and two nav entries.** `groups()` and
  the parametrization are literal lists; the nav is a TOML array.
- **The skill edits add no link**, so the link and file pins hold.
- **The anchors the pages use exist** in the rendered DC2 page (5 of 5); the
  site build's strict mode checks them again.

No requirement was found that no implementation can satisfy.

## Out of scope for this phase

- Any behaviour change, including making `doccheck` follow the mode (D1 (b)).
- The `gnd check` text-format banner (DC1b finding; pre-existing on main).
- The `learners` group's test registration.
- NM2-Q2 (`fidelity` in three modes) and NM3-Q1 (the plan's installed-docs
  command), both for milestone close; NM2-Q3 (RF1 golden recapture), later.
- A business tutorial page.
- Publication, release, certification.

## Size

About 460 new page lines, about 80 lines of edits across 11 pages, about 15
lines across five skill files, one source line, three registration lines, and
about 90 test lines. Scripted checks in `evidence/NM4/`, about 60 lines.

## Approval instrument

D4. No review panel is planned over the spec. One local reader reviews the
shipped docs (T8).

## Implementation findings, recorded as they were found

| ID | Finding | Effect |
|---|---|---|
| F1 | `tests/test_ik6_skill_census.py::test_t4_the_changed_cells_agree_with_git` diffs the induced-knowledge milestone base against the working tree, with no end commit. Its census marks `gnd-export/references/export-contract.md`, `gnd-dev-session/references/judgment-contract.md` and `gnd-dev-session/references/session-v7-contract.md` as `no`. Any later edit to those three files fails it permanently. The other census failures (both IK and IL tests credit an uncommitted skill edit to their own scope) clear once the edit is committed under another scope, as WN3's did. `representation-format.md` and `gnd-export/SKILL.md` are already marked changed in both censuses, so their edits are unaffected. | The approved Design's three edits to those files cannot ship without either dropping them or changing a closed milestone's test. Put to the owner as D5. |
| F2 | `judgment-contract.md` writes flags without backticks; the drafted sentence followed the file's style, not the DC2 text. | Moot: D5 dropped the edit. |
| F3 | `tests/test_disclosure_docs.py` has one test beyond T5: every every-mode CLI leaf in `SURFACES` is named in the page's every-mode section. | Extra coverage; no design change. |
| F4 | `tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes` covers every how-to page: no exit code and no banned term (`production`) in prose. Three DC2 sentences in the how-to broke it. The spec's T3 named the file but no reading noticed the rule. | The sentences drop "with exit 1" / "with exit 3" (each block's `expect=` still checks the exit, and `disclosure.md` states the codes) and say "a real deployment". `check_against_dc2.py` lists the three as stated differences. |

## Decisions added during implementation

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D5 | F1: three approved skill edits fail a closed milestone's census test permanently | (a) Drop the edits to `export-contract.md`, `judgment-contract.md` and `session-v7-contract.md`; keep the `gnd-export/SKILL.md` and `representation-format.md` edits. Agents still learn the `customer` refusal from `gnd-export/SKILL.md` and `disclosure.md`. (b) Bound the IK census test at that milestone's last commit and keep all five: edits a closed milestone's test and chooses its end commit. | **(a)** `(s5)` |

`(s5)` Owner ruling, 2026-11-02, quoted: "Drop the three edits", in answer to
"How should I handle the three blocked skill edits?" The three files keep
their `420114e` bytes; in the disposition table they read as unchanged, for
this reason.
