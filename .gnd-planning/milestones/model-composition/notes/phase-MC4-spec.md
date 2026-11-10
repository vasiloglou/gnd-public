# Phase MC4: documentation and skills

## Status

Owner-decided by delegated approval (auto=true), 2026-11-10; final implementation begins only after record 024 binds these bytes.

## Provenance

Canonical notes/model-composition-plan.md r3+a1, SHA256 775b5f16b81283cb5634124254c8ec6df8a53735192af946887db369dda1efe9; sections 0,4–10,12. Records 011/014/019/020 retain the checkpoint and correction; 023 completes MC3. Base is docs integration 30e91079, containing completed MC3 c6dad88d. No final-MC4 review has run. Prior checkpoint spec and rulings are preserved verbatim in phase-MC4-checkpoint-history.md.

The owner first requested a higher-level real example, then rejected the component/scanner story and explicitly selected Claude Fable to extend an existing demo. Fable (actual claude-fable-5-2) authored the expense story. The owner's latest actual reaction is **“Yes, this explains it”** to the rendered shared-expense-policies page. That satisfies the MD17 direction/reaction prerequisite; it is not byte or merge approval. Earlier rejections remain in the checkpoint history. Existing prompts are suggested reader requests, not executed agent transcripts.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| MC4-C1, §5 | One includes format home; three skills and CLI cite it | D2; T2 |
| MC4-C2, O8, MD12 | Tool produces standalone versioned vocabulary; project pins/re-pins; no runner implementation here | Technical expense page; T1/T2 |
| MC4-C3 | Doc-sync and skill structure with actual pin sites | T2 |
| MC4-C4, predicate8, a1 | Whole v1→v2 broken-own-rule→combined-repair story | D1; T1 |
| MC4-C5 | Shipped source data, all commands run with exact exits/key lines | Existing runner registration and tutorial parametrization; T1 |
| MC4-C6 | Before/after figure, source, full alt | T3 |
| MC4-C7 | Navigation, release notes, strict build, site checker | T3 |
| MC4-C8, MD17 | Fable business page and actual owner reaction | Provenance above; D1 |
| §9 | doc-sync/skill structure; uv run pytest -q tests/test_documentation_tutorials.py; uv run python tools/run_tutorials.py; zensical build --strict; uv run python tools/check_docs.py site | T1–T3, executed as written |
| §0, O10–13/O17/O25 | Standing rules, index, dependency homes, PR/merge, reduced lane | Rules below, T4, separate merge permission |
| §6 | Half-model, identity drift, duplicate resolvers, freshness, flattening, missing old vocabulary, ownership, mode/path/cap risks | Existing MC1–3 proof retained; no runtime changes; example tests actual authored publication and unchanged inputs |
| §7 | No generator in this repo, nested/remote/override, identity rewrite or multi-file atomicity | Out of scope |
| MC1 R30 carryover | Replace blanket example prohibition with exact rooted successor; keep other examples include-free | T4, exact three known roots with dirty-set control |
| 023 boundaries | Final skills/workflow docs; census/default and main close still owed | This phase T1–T4; close remains separate |
| 019/020 | Historical page manifest correction remains explicit | No evidence rewrites |

## Standing rules

Project rules: (1) totality and (2) bounded algorithm work add no runtime consumers here; existing loader/evolve tests remain authoritative. (3) Order: technical walkthrough previews invalid re-pin before valid combined update, then requires exact acceptance before publication. (4) Shared policy walk is unchanged; runner is reused. (5) Normative includes prose stays in representation-format.md; evolution grammar stays in evolution-contract.md; skills link instead of copying specifications. (6) Every stated example result is measured with the existing runner, including both failure and success branches.

Milestone rules 0.1/0.2: canonical loader only, unsupported generated-app/conformance routes remain explicitly unsupported. 0.3: no runtime/include-free serialization change; historical full/census not rerun per phase. 0.4: assert published Sales authored file retains only owned rules and shared inputs remain byte-identical. 0.5: publication uses actual MC3 live verification; describe captured checks without promising multi-file atomicity. 0.6: record measured exits, no planned result relabelled as observed before execution. 0.7: stop at declared size limits. No module, ModelIndex waiver, family hook, dependency allowance, discovery-link or delivered process-skill change.

## Goal

A reader sees why two teams share one definition while retaining different policies, then sees one team move to edition 2 through an analysis-only preview (3), a valid combined preview (0), exact accepted publication (0), and checks with/without a supporting document (0/1). Engineering remains on edition 1 and checks 0. Mandatory documentation gates exit 0; inherited unrelated known reds are recorded separately.

## Design

| Capability | Searches and source check | Decision |
|---|---|---|
| Execute tutorial blocks | components_index.py search 'tutorial execution'; search 'documentation checks'; both miss runner, rg 'def groups|def _run_pages' tools/run_tutorials.py locates existing executor | reuse runner unchanged except one group registry entry; one test parameter |
| Validate documentation/skills | earlier searches 'tutorial runner documentation skill' and 'documentation validation'; rg in tools/check_docs.py and tests/test_skill_prose_sync.py/tests/test_packaged_skills.py | reuse existing checks, no second validator |
| Render example figure | search documentation checks finds tools/figures/svgkit.py; existing expense-teams.svg inspected | adapt source SVG; no new renderer |
| Re-pin and publish | MC3 corpus/service and existing CLI tested in 023; index evolve.service is canonical | reuse existing public CLI, no new production helper |

Preserve Fable's high-level voice in docs/tutorials/shared-expense-policies.md. Supporting docs/how-to/shared-expense-policies-commands.md owns runnable blocks, expected outputs, versioned shipping advice and links. Remove planned labels only after measured success. Preserve old redirects. Register both pages in zensical.toml and announce unreleased checkout feature. Link final source files on main; no release publishing.

Data in src/gnd/examples/expense/teams/: existing v1/v2 shared vocabularies; new sales-v2.orm.json (same six caps and identity), sales-repin.proposal.json (invalid repin-only candidate embedded as committed text, not a standalone invalid ORM file), sales-update.proposal.json (repin plus delete receipt_required and add document_required on new shared fact host), sales-v2-seed.population.json and sales-v2-missing-document.population.json. Proposals use the already shipped schema3, existing IncludeLocator and owned inline locators, existing canonical digest producer. No new schema/signature/enum. New fact uses existing v2 spelling, measured before authoring. Existing v1 remains on disk. Commands copy shipped files, inspect analysis radius, preview valid update, accept its exact report SHA and publish/finalize. Generic shell runner already supports variables/stdin; no special runner branch.

Three skill pin sites: src/gnd/skills/gnd-orm-core/SKILL.md reference table; gnd-model-evolve/SKILL.md operation/workflow guidance and existing evolution-contract link; gnd-model-from-text/SKILL.md vocabulary authoring guidance. Add links to the one includes home, not a second grammar. Reference CLI documents previous-include and model verbalization; formats page links canonical section. No unnecessary API expansion.

## Decisions

| ID | Question, alternatives and cost | Ruling |
|---|---|---|
| D1 | Component literal versus owner-selected expense story | (o delegated 2026-11-10) use accepted Fable expense; preserve component MC3 corpus; record plan repair at close |
| D2 | Duplicate specification versus canonical citations | (o delegated) citations; practical workflow/example only |
| D3 | Corpus-first new runtime contract versus prose for documentation-only integration | (o delegated) prose; schemas/exits/predicates already approved MC1–3, this adds example instances, not semantics; narrated 3/0/0/1 outcomes above and exact runner enforce them |
| D4 | Optional spec review versus implementation | (o delegated) omit optional spec review; one independent Codex CLI diff review plus at most one repair confirmation, max2 invocations; existing auth only, no env reads, panel or reviewer subagent |
| D5 | MD17 and feedback | (o delegated) selected business page with actual Fable authorship and latest positive owner reaction; no further reaction gate invented |
| D6 | R30 exact successor versus blanket exemption | (o delegated) exact three rooted expense models only; all other examples retain no-includes assertion; dirty missing/unexpected-set controls |
| D7 | Broad historical suites | (o delegated) not phase gates; explicitly authorized beast-3 final default/census remain close obligations |

## Tests and verification selection

T1 (C2/C4/C5): uv run pytest -q tests/test_documentation_tutorials.py and uv run python tools/run_tutorials.py, expected0. New group shared-expenses executes every marked block, matches stdout/stderr keys and exact exits. Cases: v1 validate/check0; dinner and receipt failure1 versus other-team success0; tampered vocab3; repin-only analysis3 names receipt_required and excludes six caps; valid combined preview0 breaking; accepted apply/finalize0; v2 seed0 and missing document1; Engineering still0; authored/no copied definitions and shared bytes unchanged. Existing runner wrong-exit/output/marker controls retain falsifiability. Optional native lanes are labelled skipped, not completed.

T2 (C1/C3): uv run pytest -q tests/test_skill_prose_sync.py tests/test_packaged_skills.py tests/test_plan_app_docs.py --tb=short, expected0 except independently reproduced inherited grow-a-model prose known red. New page/citation checks and pin inventories updated only where measured changes require exact successors; no blanket link exemption.

T3 (C6/C7): zensical build --strict and uv run python tools/check_docs.py site, expected0. Inspect rendered accepted-story and update figure; figure source/alt/navigation/release checked. Installed help confirms --strict supported. Source links may target eventual main files; no claim those merge bytes already live.

T4 (carryover/rules): focused tests/test_mc1_guards.py and direct MC4 tests, expected0; exact example set positive and unexpected/missing control. Existing MC3 re-pin-only conservative-breaking behavior may receive one small byte/path-only integration case if within budget. uv run python scripts/components_index.py --check --strict and changed --base 30e91079 --strict expected0, disposition each reread. uv run ruff check src tests --output-format json expected exact13 inherited baseline findings, no new finding; git diff --check expected0. No runtime source changed, so no replay of entire evolution/export suite. Default/census and close reviewer remain separate and current-byte claims unavailable until run.

## Out of scope

Runtime/schema/exit semantics, dev-tools fact generator, generated expense app/codegen/conformance includes support, remote/nested includes, identity redesign, multi-file atomicity, installed-link editing, certification, release publication, merges without explicit authorization. No unrelated baseline cleanup.

## Size

Plan heading estimate0 production/450 doc/80 test lines; MD17(a) explicitly adds about250 doc lines, selected here, effective doc estimate700, stop1050. Python test/support estimate80, stop120 including checkpoint5 test lines and36 retained wrapper lines. Production estimate0; no production Python changes permitted. Count conservatively added prose/SVG and moved text; shipped JSON and retained execution output are separate data/evidence axes, report actual counts without hiding them as Python. Stop before exceeding test/source/doc limits; MC1/MC3 raises do not transfer.

## Approval instrument

Delegated approval (auto=true), 2026-11-10, authority user process-milestone model-composition auto; exact spec digest recorded separately in 024 before implementation. Prose instrument; D1–D7 ruled as above after implementability sweep: existing schema/CLI/runner can satisfy every narrated case, strict option exists, update prerequisites met at MC3 source, and positive feedback present. One reviewer is one reviewer; independent diff budget max2 Codex CLI invocations, optional spec review omitted. This is agent approval under delegation, not personal owner reading. All historical checkpoint rulings remain retained in phase-MC4-checkpoint-history.md. No merge authority supplied.
