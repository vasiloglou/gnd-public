from __future__ import annotations

import re
from collections.abc import Mapping
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

import pytest

from gnd.review.adapters import reviewer_policies

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_MD = REPO_ROOT / 'AGENTS.md'
PROVENANCE_SOURCES = ('explicit', 'sample', 'common-sense', 'llm-inferred', 'user-supplied', 'imported', 'induced')
AUTHORING_ENTRY_POINTS = ('gnd-model-from-text/SKILL.md', 'gnd-model-from-code/SKILL.md')
PROVENANCE_REFERENCE = 'gnd-orm-core/references/provenance-and-modality.md'
PANEL_SKILL = 'gnd-review-panel/SKILL.md'
PANEL_CONTRACT = 'gnd-review-panel/references/review-contract.md'

def _skills_root() -> Traversable:
    return files('gnd') / 'skills'

def _packaged_text(rel: str) -> str:
    resource = _skills_root()
    for part in rel.split('/'):
        resource = resource / part
    return resource.read_text(encoding='utf-8')

def _present(text: str, token: str) -> bool:
    return re.search(f'(?<![\\w-]){re.escape(token)}(?![\\w-])', text) is not None

def test_agents_md_claims_no_fixed_skill_count() -> None:
    text = AGENTS_MD.read_text(encoding='utf-8').lower()
    for count_word in ('twelve', 'thirteen', 'fourteen', 'fifteen'):
        assert count_word not in text, f"AGENTS.md spells out the inventory count {count_word!r} again. The packaged tree is the count's one home; prose that repeats it drifts the moment a skill is added or removed."

def test_the_normative_reference_carries_all_seven_sources() -> None:
    text = _packaged_text(PROVENANCE_REFERENCE)
    absent = [token for token in PROVENANCE_SOURCES if not _present(text, token)]
    assert not absent, f'{PROVENANCE_REFERENCE} no longer names {absent} — it is the one normative home of the closed seven-source taxonomy, and a source it omits has no home at all.'

def test_each_authoring_entry_point_states_its_imported_policy() -> None:
    for rel in AUTHORING_ENTRY_POINTS:
        text = _packaged_text(rel)
        assert _present(text, 'imported'), f'{rel} no longer mentions the `imported` source. It emits five of six sources by design; the restriction must be stated, or the five-item list reads as the complete taxonomy again.'
        assert 'provenance-and-modality.md' in text, f'{rel} no longer links the normative provenance reference; its source list has nothing to be a restriction OF.'

def _policy_models() -> dict[str, str]:
    models: dict[str, str] = {}
    for policy in reviewer_policies():
        argv = list(policy.invocation_argv)
        assert '--model' in argv, f"reviewer {policy.reviewer_id} has no --model in its fixed argv; this suite's extraction rule no longer fits the policy shape"
        models[str(policy.reviewer_id)] = argv[argv.index('--model') + 1]
    return models

def test_both_prose_surfaces_name_every_reviewer_model() -> None:
    surfaces = {PANEL_SKILL: _packaged_text(PANEL_SKILL), PANEL_CONTRACT: _packaged_text(PANEL_CONTRACT)}
    for reviewer_id, model in _policy_models().items():
        for rel, text in surfaces.items():
            assert _present(text, model), f'{rel} does not name {model!r}, the code-owned model for reviewer {reviewer_id!r} (src/gnd/review/adapters.py). The prose copies are deliberate; being checked here is what makes them safe to keep.'

def test_the_contract_table_carries_every_fixed_invocation_flag() -> None:
    text = _packaged_text(PANEL_CONTRACT)
    for policy in reviewer_policies():
        flags = [token for token in policy.invocation_argv if re.fullmatch('--[\\w-]+', token)]
        missing = [flag for flag in flags if not _present(text, flag)]
        assert not missing, f"{PANEL_CONTRACT} is missing {missing} from reviewer {policy.reviewer_id!r}'s fixed invocation (src/gnd/review/adapters.py is the one code-owned source). Update the §3 policy table — and the entry point if the profile changed — rather than letting the copies diverge."

def test_the_effort_literal_and_kimi_transport_survive_in_prose() -> None:
    argv_text = ' '.join(token for policy in reviewer_policies() for token in policy.invocation_argv)
    skill = _packaged_text(PANEL_SKILL)
    contract = _packaged_text(PANEL_CONTRACT)
    if 'xhigh' in argv_text:
        assert 'xhigh' in skill and 'xhigh' in contract, 'the fixed argv requests the literal `xhigh` effort and at least one prose surface no longer says so — the profile summary is the half a reader of the entry point actually sees'
    kimi = next(p for p in reviewer_policies() if str(p.reviewer_id) == 'kimi')
    if kimi.prompt_transport == 'argv':
        assert 'argv element' in skill, 'gnd-review-panel/SKILL.md no longer states that Kimi receives the prompt as one argv element; that transport difference is a disclosed operational envelope, not an implementation detail'
        assert '| argv |' in contract, "review-contract.md's policy table no longer records Kimi's argv prompt transport"
_SKILLS_ROOT = REPO_ROOT / 'src' / 'gnd' / 'skills'
PHASE4_ONE_HOME_SENTENCES: tuple[tuple[str, str], ...] = (('the case carries **no `inputs` and no `verify`**', 'gnd-dev-session/SKILL.md'), ('the exact test node ids the run must report passed', 'gnd-dev-session/SKILL.md'), ('Seal the thing that decides, not just the thing that is decided', 'gnd-dev-session/SKILL.md'), ('Extension bytes are not integrity-digest-gated.', 'gnd-conformance/SKILL.md'), ('**Assertion 4 is static only.**', 'gnd-conformance/SKILL.md'), ('Three lines that hand every smoke row in your contract to `gnd.archsmoke`', 'gnd-codegen/SKILL.md'), ('a smoke id contains `[`, `]`, or whitespace', 'gnd-codegen/references/architecture-contract.md'))
PHASE4_ID_BRIDGE = "taken verbatim from the\narchitecture contract's `smoke[].id`"

def _packaged_documents() -> dict[str, str]:
    return {str(path.relative_to(_SKILLS_ROOT)): path.read_text(encoding='utf-8') for path in sorted(_SKILLS_ROOT.rglob('*.md'))}

@pytest.mark.parametrize(('sentence', 'home'), PHASE4_ONE_HOME_SENTENCES, ids=[home.split('/')[0] + ':' + sentence[:28] for sentence, home in PHASE4_ONE_HOME_SENTENCES])
def test_phase4_skill_sentences_have_exactly_one_home(sentence: str, home: str) -> None:
    documents = _packaged_documents()
    holders = sorted((name for name, text in documents.items() if sentence in text))
    assert holders == [home], {'sentence': sentence, 'found_in': holders}
    assert documents[home].count(sentence) == 1, sentence

def test_id_bridge_sentence_is_stated_once() -> None:
    documents = _packaged_documents()
    holders = sorted((name for name, text in documents.items() if PHASE4_ID_BRIDGE in text))
    assert holders == ['gnd-dev-session/SKILL.md'], holders

def test_no_fifteenth_skill_directory_was_created() -> None:
    directories = {path.name for path in _SKILLS_ROOT.iterdir() if path.is_dir()}
    assert 'gnd-architecture' not in directories
    assert not [name for name in directories if 'architecture' in name]
V61_PHASE3_ONE_HOME = {'`acceptance.mode: transition`': 'gnd-dev-session/SKILL.md', 'digest-bound pre': 'gnd-dev-session/SKILL.md', 'candidate steps and optional candidate post': 'gnd-dev-session/SKILL.md', 'never bindings or witnesses': 'gnd-dev-session/SKILL.md'}
V61_PHASE5_ONE_HOME = {'`acceptance.walk`': 'gnd-dev-session/SKILL.md', '`required_ops`': 'gnd-dev-session/SKILL.md', '`forbidden_ops`': 'gnd-dev-session/SKILL.md', '`unmet_walk_floors`': 'gnd-dev-session/SKILL.md'}
V61_PHASE6_ONE_HOME = {'`adapter.policy_id`': 'gnd-dev-session/SKILL.md', '`--adapter-policy`': 'gnd-dev-session/SKILL.md', 'one closed base64 file bundle': 'gnd-dev-session/SKILL.md', 'Resume requires the same policy bytes': 'gnd-dev-session/SKILL.md'}

def test_panel_workflow_refuses_a_disposable_tree_that_omits_pending_fixes() -> None:
    documents = _packaged_documents()
    skill = documents[PANEL_SKILL]
    contract = documents[PANEL_CONTRACT]
    for text in (skill, contract):
        assert 'git diff --quiet -- src/gnd/review' in text
        assert 'run the required verification ladder' in text.casefold()
        assert 'never use a clean checkout' in text.casefold()
        assert 'git rev-parse HEAD' in text
        assert 'resolves inside that tree' in text
        assert 'OPENROUTER_API_KEY' in text
        assert 'ZAI_API_KEY' in text
        assert 'stop before invoking reviewers' in text
        assert 'Never read or source a repository `.env`' in text
V5_PHASE4_SKILL_CONSEQUENCES: dict[str, tuple[str, ...]] = {'gnd-orm-core/references/coverage-and-element-addressing.md': ('operation | fact_type | constraint | derivation', 'one claim says the\nexperiment covers the computed extension'), 'gnd-model-from-text/SKILL.md': ('A derivation computes the expected **extension of one fact type**', 'A constraint judges a population; it does not manufacture the facts it', 'legacy/opaque/unchecked'), 'gnd-model-evolve/SKILL.md': ("every fact type named by the rule's positive and negative atoms", 'bump `version` and `model_id`\ntogether with one `ModelIdentityLocator` operation', 'unchanged fact-type provenance block remains byte-identical under D-12'), 'gnd-codegen/SKILL.md': ('no constructor for a structured-derived fact type', 'claims the derived rows and `gnd check`/`gnd verify` verifies that claim', 'legacy string `derivation_rule` keeps its constructor'), 'gnd-conformance/SKILL.md': ('structured-derived fact type is `derived-fact-type-constructed` drift', 'This is structural agreement only. It establishes neither that a structured', 'semantically correct; those claims are outside conformance')}
V5_STRUCTURED_DERIVATION_NORMATIVE_SENTENCE = '**This section is the one normative home for structured derivation rules.**'
V5_STRUCTURED_DERIVATION_NORMATIVE_HOME = 'gnd-orm-core/references/representation-format.md'
V5_PHASE4_WORKFLOW_CORE_ROUTES = frozenset({'gnd-model-from-text/SKILL.md', 'gnd-model-evolve/SKILL.md', 'gnd-codegen/SKILL.md', 'gnd-conformance/SKILL.md'})
V5_PHASE4_CORE_ROUTE = '../gnd-orm-core/SKILL.md'

def _v5_consequence_failures(documents: Mapping[str, str]) -> dict[str, list[str]]:
    failures: dict[str, list[str]] = {}
    for home, fragments in V5_PHASE4_SKILL_CONSEQUENCES.items():
        for fragment in fragments:
            holders = sorted((path for path, text in documents.items() if fragment in text))
            if holders != [home] or documents.get(home, '').count(fragment) != 1:
                failures.setdefault(home, []).append(fragment)
    return failures

def _normative_derivation_homes(documents: Mapping[str, str]) -> list[str]:
    return sorted((path for path, text in documents.items() if V5_STRUCTURED_DERIVATION_NORMATIVE_SENTENCE in text))

def _missing_v5_core_routes(documents: Mapping[str, str]) -> set[str]:
    return {home for home in V5_PHASE4_WORKFLOW_CORE_ROUTES if V5_PHASE4_CORE_ROUTE not in documents.get(home, '')}

def test_v5_phase4_each_named_skill_carries_one_routed_consequence() -> None:
    documents = _packaged_documents()
    assert {home.split('/', 1)[0] for home in V5_PHASE4_SKILL_CONSEQUENCES} == {'gnd-orm-core', 'gnd-model-from-text', 'gnd-model-evolve', 'gnd-codegen', 'gnd-conformance'}
    assert not _v5_consequence_failures(documents)
    assert not _missing_v5_core_routes(documents)
    for home, fragments in V5_PHASE4_SKILL_CONSEQUENCES.items():
        for fragment in fragments:
            removed = dict(documents)
            removed[home] = removed[home].replace(fragment, '', 1)
            assert fragment in _v5_consequence_failures(removed)[home]
            duplicated = dict(documents)
            duplicated['gnd-extract/SKILL.md'] += f'\n{fragment}\n'
            assert fragment in _v5_consequence_failures(duplicated)[home]
    for home in V5_PHASE4_WORKFLOW_CORE_ROUTES:
        unrouted = dict(documents)
        unrouted[home] = unrouted[home].replace(V5_PHASE4_CORE_ROUTE, '')
        assert home in _missing_v5_core_routes(unrouted)

def test_v5_structured_derivation_semantics_has_one_normative_home() -> None:
    documents = _packaged_documents()
    assert _normative_derivation_homes(documents) == [V5_STRUCTURED_DERIVATION_NORMATIVE_HOME]
    removed = dict(documents)
    removed[V5_STRUCTURED_DERIVATION_NORMATIVE_HOME] = removed[V5_STRUCTURED_DERIVATION_NORMATIVE_HOME].replace(V5_STRUCTURED_DERIVATION_NORMATIVE_SENTENCE, '', 1)
    assert not _normative_derivation_homes(removed)
    duplicated = dict(documents)
    duplicated['gnd-extract/SKILL.md'] += f'\n{V5_STRUCTURED_DERIVATION_NORMATIVE_SENTENCE}\n'
    assert _normative_derivation_homes(duplicated) == ['gnd-extract/SKILL.md', V5_STRUCTURED_DERIVATION_NORMATIVE_HOME]

def test_v61_phase5_walk_floor_fragments_have_one_home() -> None:
    documents = _packaged_documents()
    for fragment, home in V61_PHASE5_ONE_HOME.items():
        holders = sorted((path for path, text in documents.items() if fragment in text))
        assert holders == [home], (fragment, holders)

def test_v61_phase6_declared_adapter_fragments_have_one_home() -> None:
    documents = _packaged_documents()
    for fragment, home in V61_PHASE6_ONE_HOME.items():
        holders = sorted((path for path, text in documents.items() if fragment in text))
        assert holders == [home], (fragment, holders)

def test_v61_phase3_dev_session_fragments_have_one_home() -> None:
    documents = _packaged_documents()
    for fragment, home in V61_PHASE3_ONE_HOME.items():
        holders = sorted((path for path, text in documents.items() if fragment in text))
        assert holders == [home], (fragment, holders)
