from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files as resource_files
from pathlib import Path
from typing import Any

import pytest

from gnd import cli, install

EXPECTED_SKILL_FILES = frozenset(('gnd-adopt/SKILL.md', 'gnd-adopt/migration.schema.json', 'gnd-adopt/references/gsd-environment-cleanup.md', 'gnd-adopt/references/gsd-mapping.md', 'gnd-adopt/scripts/verify_migration.py', 'gnd-codegen/SKILL.md', 'gnd-codegen/references/architecture-contract.md', 'gnd-codegen/references/codegen-contract.md', 'gnd-conformance/SKILL.md', 'gnd-conformance/references/conformance-contract.md', 'gnd-dev-session/SKILL.md', 'gnd-dev-session/references/judgment-contract.md', 'gnd-dev-session/references/session-v7-contract.md', 'gnd-export/SKILL.md', 'gnd-export/references/export-contract.md', 'gnd-export/references/witness-contract.md', 'gnd-export/references/witness.schema.json', 'gnd-extract/SKILL.md', 'gnd-extract/references/extraction-contract.md', 'gnd-model-evolve/SKILL.md', 'gnd-model-evolve/references/evolution-contract.md', 'gnd-model-from-code/SKILL.md', 'gnd-model-from-code/references/recovery-contract.md', 'gnd-model-from-text/SKILL.md', 'gnd-model-from-text/USAGE.md', 'gnd-model-from-text/evals/README.md', 'gnd-model-from-text/evals/cases.json', 'gnd-model-from-text/evals/expected/synthetic_good_user.orm.yaml', 'gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md', 'gnd-model-from-text/evals/fixtures/synthetic_good_user/dialogue.md', 'gnd-model-from-text/evals/reviewability_checklist.md', 'gnd-model-from-text/examples/library_with_subtypes.dialogue.md', 'gnd-model-from-text/examples/library_with_subtypes.orm.yaml', 'gnd-model-from-text/examples/movie_catalog.dialogue.md', 'gnd-model-from-text/examples/movie_catalog.orm.yaml', 'gnd-model-from-text/examples/objectification_in_enrollment.dialogue.md', 'gnd-model-from-text/examples/objectification_in_enrollment.orm.yaml', 'gnd-model-from-text/examples/reference_scheme_elicitation.dialogue.md', 'gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml', 'gnd-model-from-text/references/csdp-workflow.md', 'gnd-model-from-text/references/dialogue-patterns.md', 'gnd-model-from-text/scripts/validate_model.py', 'gnd-new-project/SKILL.md', 'gnd-orm-core/SKILL.md', 'gnd-orm-core/references/constraint-inference.md', 'gnd-orm-core/references/constraint-reference.md', 'gnd-orm-core/references/coverage-and-element-addressing.md', 'gnd-orm-core/references/halpin-posture.md', 'gnd-orm-core/references/milestone-record-format.md', 'gnd-orm-core/references/orm-meta.schema.json', 'gnd-orm-core/references/population-format.md', 'gnd-orm-core/references/population.schema.json', 'gnd-orm-core/references/provenance-and-modality.md', 'gnd-orm-core/references/representation-format.md', 'gnd-orm-core/references/steps.schema.json', 'gnd-orm-core/references/verbalization-patterns.md', 'gnd-render-doc/SKILL.md', 'gnd-render-doc/references/rendering-contract.md', 'gnd-review-panel-light/SKILL.md', 'gnd-review-panel/SKILL.md', 'gnd-review-panel/references/review-contract.md', 'gnd-solve/SKILL.md', 'gnd-update-review-panel/SKILL.md', 'gnd-update-review-panel/agents/openai.yaml', 'gnd-update-review-panel/scripts/update_harnesses.py'))
EXPECTED_SKILL_FILE_COUNT = 65

def _target(root: Path, *, runtime: str='claude', scope: str='project') -> Any:
    return install.InstallTarget(runtime=runtime, scope=scope, root=root)

def _install(root: Path, *, mode: str='copy', force: bool=False) -> Any:
    skills = install.packaged_skills_root()
    target = _target(root)
    manifest = install.read_manifest(root)
    records = install.plan(skills, target, manifest, mode=mode)
    return install.apply(skills, target, records, mode=mode, force=force, manifest=manifest)

def _hand_place_the_packaged_tree(root: Path) -> int:
    count = 0
    index = install._packaged_index(install.packaged_skills_root())
    assert set(index) == EXPECTED_SKILL_FILES
    for relpath, resource in index.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(resource.read_bytes())
        count += 1
    return count

def _gnd_argv() -> list[str]:
    executable = shutil.which('gnd')
    return [executable] if executable else [sys.executable, '-m', 'gnd']

def _run_gnd(args: list[str], cwd: Path, **env: str) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment.pop(install.CODEX_HOME_ENV, None)
    environment.update(env)
    return subprocess.run([*_gnd_argv(), *args], cwd=cwd, env=environment, capture_output=True, text=True, check=False)

def test_f01_a_run_that_placed_nothing_and_owns_nothing_writes_no_receipt(tmp_path: Path) -> None:
    root = tmp_path / '.claude' / 'skills'
    root.mkdir(parents=True)
    assert _hand_place_the_packaged_tree(root) == EXPECTED_SKILL_FILE_COUNT
    result = _install(root)
    assert result.writes == 0
    assert len(result.collisions) == EXPECTED_SKILL_FILE_COUNT, 'the premise of this test is that EVERY record collided; a partially collided root writes a legitimate receipt and evidences nothing'
    assert result.manifest_written is False
    assert result.manifest is None
    assert not (root / install.MANIFEST_NAME).exists(), 'a receipt is a claim of ownership. A run that placed nothing, pruned nothing, owns nothing and found no prior receipt established no state at all and must leave no document behind saying otherwise'

def test_f01_doctor_does_not_date_and_version_a_root_gnd_never_wrote(tmp_path: Path) -> None:
    root = tmp_path / '.claude' / 'skills'
    root.mkdir(parents=True)
    _hand_place_the_packaged_tree(root)
    _install(root)
    diagnosis = install.diagnose(install.packaged_skills_root(), [_target(root)]).targets[0]
    assert diagnosis.counts() == {'collided': EXPECTED_SKILL_FILE_COUNT}
    assert diagnosis.installed_at == '', 'a placement timestamp for a placement that never happened is the whole of the defect, and it is the one fact an operator reads doctor to learn'
    assert diagnosis.version == ''
    assert diagnosis.mode == ''

def test_f01_a_forced_run_over_the_same_root_still_writes_its_receipt(tmp_path: Path) -> None:
    root = tmp_path / '.claude' / 'skills'
    root.mkdir(parents=True)
    _hand_place_the_packaged_tree(root)
    result = _install(root, force=True)
    assert result.writes == EXPECTED_SKILL_FILE_COUNT
    assert result.manifest_written is True
    manifest = install.read_manifest(root)
    assert manifest is not None
    assert len(manifest.file_entries()) == EXPECTED_SKILL_FILE_COUNT

def _aliased_project(tmp_path: Path) -> Path:
    project = tmp_path / 'project'
    (project / '.claude' / 'skills').mkdir(parents=True)
    (project / '.codex').mkdir(parents=True)
    (project / '.codex' / 'skills').symlink_to(Path('..') / '.claude' / 'skills', target_is_directory=True)
    return project

def test_f01_two_targets_aliasing_one_directory_leave_a_receipt_owning_the_files(tmp_path: Path) -> None:
    project = _aliased_project(tmp_path)
    home = tmp_path / 'home'
    home.mkdir()
    result = _run_gnd(['install', '--project'], cwd=project, HOME=str(home))
    assert result.returncode == 0, f'expected 0; the aliased second target is not a collision, it is the same directory the first target just installed into.\n{result.returncode}\n{result.stdout}\n{result.stderr}'
    assert 'collided' not in result.stdout, f'GND placed these files in this same command.\n{result.stdout}'
    manifest = install.read_manifest(project / '.claude' / 'skills')
    assert manifest is not None
    assert len(manifest.file_entries()) == EXPECTED_SKILL_FILE_COUNT, 'the receipt must still own every file on disk; an empty one is what stranded 29 files beyond the reach of uninstall'

def test_f01_the_aliased_install_is_fully_removable_by_uninstall(tmp_path: Path) -> None:
    project = _aliased_project(tmp_path)
    home = tmp_path / 'home'
    home.mkdir()
    root = project / '.claude' / 'skills'
    assert _run_gnd(['install', '--project'], cwd=project, HOME=str(home)).returncode == 0
    placed = sorted(p for p in root.rglob('*') if p.is_file() and p.name != install.MANIFEST_NAME)
    assert len(placed) == EXPECTED_SKILL_FILE_COUNT
    removal = _run_gnd(['uninstall', '--claude', '--project'], cwd=project, HOME=str(home))
    assert removal.returncode == 0, f'{removal.returncode}\n{removal.stdout}\n{removal.stderr}'
    survivors = [p for p in placed if p.exists()]
    assert survivors == [], f'uninstall must remove the files install placed; these survived: {survivors}'
    assert not (root / install.MANIFEST_NAME).exists()

def test_f01_an_unmanaged_file_at_an_aliased_root_is_still_a_collision(tmp_path: Path) -> None:
    project = _aliased_project(tmp_path)
    home = tmp_path / 'home'
    home.mkdir()
    squatter = project / '.claude' / 'skills' / 'gnd-orm-core' / 'SKILL.md'
    squatter.parent.mkdir(parents=True)
    squatter.write_bytes(b"mine, not GND's\n")
    result = _run_gnd(['install', '--project'], cwd=project, HOME=str(home))
    assert result.returncode == cli.EXIT_COLLISION, f'expected {cli.EXIT_COLLISION}\n{result.returncode}\n{result.stdout}'
    assert squatter.read_bytes() == b"mine, not GND's\n", 'nothing may be destroyed'

def _shimmed(tmp_path: Path) -> Path:
    real = shutil.which('gnd')
    if real is None:
        pytest.skip('no `gnd` console script on PATH to shim')
    shim_dir = tmp_path / 'toolbin'
    shim_dir.mkdir()
    (shim_dir / 'gnd').symlink_to(Path(real))
    return shim_dir

def test_f02_doctor_says_on_path_when_invoked_through_a_uv_style_shim(tmp_path: Path) -> None:
    shim_dir = _shimmed(tmp_path)
    project = tmp_path / 'project'
    home = tmp_path / 'home'
    project.mkdir()
    home.mkdir()
    environment = dict(os.environ)
    environment.pop(install.CODEX_HOME_ENV, None)
    environment['HOME'] = str(home)
    environment['PATH'] = os.pathsep.join([str(shim_dir), '/usr/bin', '/bin'])
    result = subprocess.run([str(shim_dir / 'gnd'), 'doctor', '--project'], cwd=project, env=environment, capture_output=True, text=True, check=False)
    line = next(row for row in result.stdout.splitlines() if row.startswith('executable directory:'))
    assert str(shim_dir) in line, f'doctor must name the directory the shell resolved `gnd` in — the one PATH has to contain — not wherever that name happens to point.\n{line}'
    assert '(on PATH)' in line and 'NOT on PATH' not in line, f'`gnd` was invoked from a directory on PATH in this very process.\n{line}'

def test_f02_doctor_still_says_not_on_path_when_it_genuinely_is_not(tmp_path: Path) -> None:
    shim_dir = _shimmed(tmp_path)
    project = tmp_path / 'project'
    home = tmp_path / 'home'
    project.mkdir()
    home.mkdir()
    environment = dict(os.environ)
    environment.pop(install.CODEX_HOME_ENV, None)
    environment['HOME'] = str(home)
    environment['PATH'] = os.pathsep.join(['/usr/bin', '/bin'])
    result = subprocess.run([str(shim_dir / 'gnd'), 'doctor', '--project'], cwd=project, env=environment, capture_output=True, text=True, check=False)
    line = next(row for row in result.stdout.splitlines() if row.startswith('executable directory:'))
    assert str(shim_dir) in line
    assert '(NOT on PATH)' in line, f'this directory really is not on PATH.\n{line}'
    assert 'uv tool update-shell' in result.stdout, 'the remedy must accompany the verdict that calls for it'
REPO_ROOT = Path(__file__).resolve().parent.parent
SHIPPED_EXIT_REGISTRY: dict[str, int] = {'EXIT_GENERATOR': 5, 'EXIT_QUARANTINE': 6, 'EXIT_CHECKER_DEFECT': 6, 'EXIT_DRIFT': 10, 'EXIT_COLLISION': 11, 'EXIT_NO_INSTALL': 12, 'EXIT_MODEL_CODE_DRIFT': 13, 'EXIT_EXPERIMENT_OPEN': 14, 'EXIT_SESSION_NOT_ACCEPTED': 15, 'EXIT_REVIEW_INCONCLUSIVE': 16, 'EXIT_WALK_HALTED': 17, 'EXIT_EVOLUTION_OPERATIONS_GATED': 18, 'EXIT_USAGE': 64, 'EXIT_NO_INPUT': 66, 'EXIT_INTERNAL': 70, 'EXIT_IO': 74}
SANCTIONED_EXIT_ALIASES: frozenset[frozenset[str]] = frozenset({frozenset({'EXIT_QUARANTINE', 'EXIT_CHECKER_DEFECT'})})
VERDICT_BANDS = frozenset({0, 1, 2, 3, 4})
UNALLOCATED_HEADROOM = frozenset({7, 8, 9})

def test_the_shipped_exit_registry_is_exactly_the_literal_allocation_set() -> None:
    named = {name: value for name, value in vars(cli).items() if name.startswith('EXIT_') and isinstance(value, int)}
    missing = sorted(set(SHIPPED_EXIT_REGISTRY) - set(named))
    extra = sorted(set(named) - set(SHIPPED_EXIT_REGISTRY))
    assert not missing, f'the CLI no longer defines: {missing}'
    assert not extra, f'undeclared exit constants: {extra}. A new band must be added to SHIPPED_EXIT_REGISTRY here AND proven disjoint in tests/test_exp_bands.py.'
    moved = {name: (SHIPPED_EXIT_REGISTRY[name], named[name]) for name in SHIPPED_EXIT_REGISTRY if named[name] != SHIPPED_EXIT_REGISTRY[name]}
    assert not moved, f'exit values moved (expected, actual): {moved}'
    by_value: dict[int, set[str]] = {}
    for name, value in named.items():
        by_value.setdefault(value, set()).add(name)
    aliases = {value: frozenset(names) for value, names in by_value.items() if len(names) > 1}
    unsanctioned = {value: sorted(names) for value, names in aliases.items() if names not in SANCTIONED_EXIT_ALIASES}
    assert not unsanctioned, f'unsanctioned exit aliases {unsanctioned}. Two names for one value are allowed only when they name ONE meaning; add the pair to SANCTIONED_EXIT_ALIASES with the meaning written down, or allocate a distinct value.'
    lifecycle = set(named.values())
    collisions = sorted(lifecycle & VERDICT_BANDS)
    assert not collisions, f'lifecycle codes {collisions} collide with the verifier verdict bands 0-4, which checker.band() owns'
    spent = sorted(lifecycle & UNALLOCATED_HEADROOM)
    assert not spent, f'{spent} was verdict-band headroom and has been spent'
CLAIM_FAMILY_KEYS: dict[str, frozenset[str]] = {'verdicts': frozenset({'acceptance_ready', 'verdicts', 'counts', 'coverage', 'outcome'}), 'rates': frozenset({'per_constraint', 'per_fact_type', 'checker_defects', 'coverage_summary', 'calibration', 'publishable', 'lanes'}), 'conformance': frozenset({'assertions', 'examined', 'unexamined', 'satisfied', 'findings'})}
CLAIM_FAMILY_SCHEMAS: dict[str, tuple[str, ...]] = {'verdicts': ('report.schema.json',), 'rates': ('measurement.schema.json', 'fidelity.schema.json'), 'conformance': ('conformance.schema.json',)}

def _schema_properties(*names: str) -> set[str]:
    keys: set[str] = set()
    for name in names:
        text = resource_files('gnd').joinpath(name).read_text(encoding='utf-8')
        document = json.loads(text)
        pending = [document]
        seen = set()
        while pending:
            node = pending.pop()
            if not isinstance(node, dict):
                continue
            reference = node.get('$ref')
            if reference is not None:
                assert isinstance(reference, str) and reference.startswith('#/$defs/')
                if reference in seen:
                    continue
                seen.add(reference)
                pending.append(document['$defs'][reference.removeprefix('#/$defs/')])
            properties = node.get('properties', {})
            keys.update(properties)
            # Current check envelopes preserve their own report claim family.
            if name == 'report.schema.json' and 'report' in properties:
                pending.append(properties['report'])
            for keyword in ('oneOf', 'anyOf', 'allOf'):
                pending.extend(node.get(keyword, []))
    return keys

def _blended_families(payload: dict[str, Any], family: str) -> dict[str, list[str]]:
    present = set(payload)
    return {other: sorted(present & keys) for other, keys in CLAIM_FAMILY_KEYS.items() if other != family and present & keys}

def _emitted_payloads() -> dict[str, dict[str, Any]]:
    from gnd.conformance.report import build_conformance_payload
    from gnd.fidelity.report import build_fidelity_payload
    from gnd.report import build_check_payload
    applicable = json.loads((REPO_ROOT / 'tests/fixtures/roundtrip/artifacts/setfam.applicable.json').read_text(encoding='utf-8'))
    return {'verdicts': build_check_payload(0, 'model.orm.yaml', 'population.yaml'), 'rates': build_fidelity_payload('model.orm.yaml', [], applicable, model_sha256='0' * 64, applicable_sha256='1' * 64, projection_sha256='2' * 64, gnd_version='test'), 'conformance': build_conformance_payload('model.orm.yaml', None, None, None, actual_model_sha256=None, gnd_version='test')}

def test_no_emitted_payload_blends_two_claim_families() -> None:
    for left, right in (('verdicts', 'rates'), ('verdicts', 'conformance'), ('rates', 'conformance')):
        shared = sorted(CLAIM_FAMILY_KEYS[left] & CLAIM_FAMILY_KEYS[right])
        assert not shared, f'{left} and {right} declare the same key(s): {shared}'
    for family, keys in CLAIM_FAMILY_KEYS.items():
        own = _schema_properties(*CLAIM_FAMILY_SCHEMAS[family])
        stale = sorted(keys - own)
        assert not stale, f'{family} declares {stale}, which no longer appears in {list(CLAIM_FAMILY_SCHEMAS[family])} — the literal has gone stale'
        for other, other_schemas in CLAIM_FAMILY_SCHEMAS.items():
            if other == family:
                continue
            crossed = sorted(keys & _schema_properties(*other_schemas))
            assert not crossed, f"{list(other_schemas)} now declares {crossed}, which is {family}'s distinguishing vocabulary — D-24 forbids one payload presenting unlike claims as one verdict"
    for family, payload in _emitted_payloads().items():
        blended = _blended_families(payload, family)
        assert not blended, f"an emitted {family} payload carries another family's fields: {blended}"

def test_the_claim_family_check_fires_on_a_blended_payload() -> None:
    payloads = _emitted_payloads()
    clean = payloads['conformance']
    assert not _blended_families(clean, 'conformance'), "the control's baseline is not clean"
    blended = dict(clean)
    blended['counts'] = {'pass': 3, 'fail': 0}
    blended['acceptance_ready'] = True
    detected = _blended_families(blended, 'conformance')
    assert detected == {'verdicts': ['acceptance_ready', 'counts']}, f'the blend detector reported {detected}; it must name the borrowed family and every borrowed key'
BANNED_IMPORT_ROOTS = frozenset({'anthropic', 'openai', 'cohere', 'mistralai', 'ollama', 'litellm', 'instructor', 'langchain', 'langchain_openai', 'langgraph', 'llama_index', 'boto3', 'botocore', 'vertexai', 'google', 'replicate', 'together', 'groq', 'requests', 'httpx', 'aiohttp', 'urllib', 'urllib3', 'http', 'socket', 'ssl', 'websockets', 'websocket', 'grpc', 'xmlrpc', 'ftplib', 'smtplib', 'poplib', 'imaplib', 'telnetlib'})

def _banned_imports_under(root: Path, *, allowed: dict[str, frozenset[str]] | None=None) -> list[str]:
    offenders: list[str] = []
    allowed = allowed or {}
    for path in sorted(root.rglob('*.py')):
        if '__pycache__' in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                candidates = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                candidates = [node.module] if node.level == 0 and node.module else []
            else:
                continue
            for dotted in candidates:
                relative = path.relative_to(root).as_posix()
                if dotted in allowed.get(relative, frozenset()):
                    continue
                first = dotted.split('.')[0]
                if first in BANNED_IMPORT_ROOTS:
                    offenders.append(f'{path.name}:{node.lineno}:{dotted}')
    return offenders

def test_no_module_under_src_gnd_imports_an_undeclared_http_client() -> None:
    offenders = _banned_imports_under(REPO_ROOT / 'src' / 'gnd', allowed={'declared_adapter.py': frozenset({'ssl', 'urllib.parse'}), 'exp/adapter_policy.py': frozenset({'urllib.parse'})})
    assert not offenders, f"src/gnd imports a provider SDK or an undeclared HTTP client: {offenders}. The sole approved live edge is v6.1's stdlib declared adapter."

def test_the_provider_sdk_scan_fires_on_a_planted_import(tmp_path: Path) -> None:
    package = tmp_path / 'planted'
    package.mkdir()
    (package / 'clean.py').write_text('from __future__ import annotations\nimport hashlib\nfrom . import sibling\n', encoding='utf-8')
    (package / 'reaches_out.py').write_text('import httpx\nimport http.client\nfrom anthropic import Anthropic\n', encoding='utf-8')
    offenders = _banned_imports_under(package)
    assert offenders == ['reaches_out.py:1:httpx', 'reaches_out.py:2:http.client', 'reaches_out.py:3:anthropic'], f'the scan reported {offenders}; it must name every planted import and no innocent'
