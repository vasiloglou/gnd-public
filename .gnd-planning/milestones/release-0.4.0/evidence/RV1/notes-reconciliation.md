# RV1 release notes reconciliation

Source for both ranges is the public commit history and Markdown at
`cc4c8bf05ae8720b1ec5814b3709bfadb8643b16`. Compare the two peeled tags to
that commit with first-parent logs and the changed files under `src`,
`docs` and the packaging inputs. Phase records disambiguate product changes
from fixture, review and planning commits.

## Changes after v0.3.1

| Change | Source | 0.4.0 coverage |
|---|---|---|
| Typed literal lists in guarded and derivation comparisons | GC1, `62c45016` | Guarded-rule clauses |
| Guarded antecedent filters and coverage-aware verdicts | GC2, `b4e84af4` | Guarded-rule clauses |
| Disjunctive consequents and their failure diagnostics | GC3, `20172ace` | Guarded-rule clauses |
| Lower supported guarded clauses for exporters, with retail controls | GC4, `f446f350`, `6cd2e5df` | Guarded-rule clauses |
| Witness and why-not accept legacy version-1 and identity-free models | LI0, `dc4ce588` | Literature identity |
| Packaged staged assurance corpus and report | LI1, `4c261d29`, `a5168dac` | Literature identity |
| Bind reviewed resolution decisions to composition | LI2, `4735730d` | Literature identity |
| Report unresolved name candidates without merging them | LI3, `e76c3c59` | Literature identity |
| Project contextual assertions through saved judgments | LI4, `0fffbba5` | Literature identity |
| Qualify lineage by context and verify paths | LI5, `3463cdd1`, `4f20f7a7` | Literature identity |
| Extract and check against flattened includes, including split reading/checking roots | LX1 and LX4, `e2ce2ade`, `8e98afc1`, `a3463627` | Literature interoperability |
| Authenticate witness origin and replay over a flattened root | LX2, `12747764`, `706b9345` | Literature interoperability |
| Bind fixed catalogs across composition, checking, witness and replay | LX3, `28dc21b7`, `9e1c1d29` | Literature interoperability |
| Source-scoped examples for scientific and algorithm questions | LD1, `da41bc07` | Literature depth |
| Time dimensions and exact decimal replay | LD2, `07a2bb06`, `55ffa8ea` | Literature depth |
| Multipass reading with explicit covered and missing inputs | LD3, `3a0b2bb1`, `92086a00`, `a589b5b3` | Literature depth |
| Digest-bound semantic migration and prior snapshot replay | LD4, `c9373078`, `238e8ce8` | Literature depth |
| Support-scoped verdicts on claims across revisions | LD5, `2e34530a`, `729111ba` | Literature depth |
| Guarded-rule BookRec guides | PR 191 | Other changes |
| Expense receipts and BookRec review walkthroughs | PRs 205 and 206 | Other changes |
| Rule identifiers documented and historical candidate/assurance boundaries restored | PR 207 | Other changes. Internal refactoring and fixture pin updates need no separate user-facing note |
| Development helper sync and milestone close records | PRs 198, 200 and 201 | Development and review infrastructure. Runtime work is listed in its phase rows |

## v0.3.0 to v0.3.1

| Change | Source | Coverage |
|---|---|---|
| Guarded diagnostics, edition comparison, guarded synthesis and guarded joins | PRs 184 and 190 | Existing 0.3.1 guarded-rules block |
| Typed AMIE constants and bounded recount | `24851fbb` | Existing 0.3.1 guarded-rules block |
| Guarded-case synthesis reports a missing optional dependency | `618141de` | 0.4.0 carryover if not already clear from the 0.3.1 linked synthesis guide |
| Ossie disclosure and import rule identifiers | `37df747e` | Existing 0.3.1 other changes |
| Package long description and publication-day text tool | `4ca709e2` | Existing 0.3.1 other changes |
| Unattended reply shape for derived fact types | `d8c0b2a3` | Existing 0.3.1 other changes |
| Query-budget relocation, version-normalized recorded tests and publication records | PRs 186, 187 and 189 | Development and historical records |
| Tag-only version and installation route | PR 192 | Existing 0.3.1 heading and install command |
