"""Exact installed-distribution originals; three frozen-inventory siblings remain unresolved."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tomllib
from functools import cache
from pathlib import Path

import pytest

pytestmark = pytest.mark.distribution
REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / 'pyproject.toml'
FIXTURES = Path(__file__).resolve().parent / 'fixtures'
SKILLS_SRC = REPO_ROOT / 'src' / 'gnd' / 'skills'
PHASE_FOUR_RESOURCES = ('gnd-model-evolve/SKILL.md', 'gnd-model-evolve/references/evolution-contract.md', 'gnd-model-from-code/SKILL.md', 'gnd-model-from-code/references/recovery-contract.md', 'gnd-review-panel/SKILL.md', 'gnd-review-panel/references/review-contract.md')
EXPECTED_DISTRIBUTION = 'get-nick-done'
EXPECTED_SKILL_FILE_COUNT = 59
EXPECTED_RELATIVE_LINK_COUNT = 177
EXPECTED_INSTALL_ROOTS = 2
PACKAGED_EXAMPLE_MODEL = 'gnd-model-from-text/examples/movie_catalog.orm.yaml'
PACKAGED_FALLBACK_SCRIPT = 'gnd-model-from-text/scripts/validate_model.py'
PEP723_SIBLING_SCHEMA = 'gnd-orm-core/references/orm-meta.schema.json'
LAYER_TWO_DEFECT_FIXTURE = FIXTURES / 'models' / 'invalid' / 'bad_cross_ref.yaml'
CONFORMING_POPULATION = 'population:\n  model: movie_catalog.orm.yaml\n  source: fixture\n  label: conforming\n  covers:\n    - movie_has_title\n    - movie_directed_by_director\n    - movie_released_in_year\n    - movie_has_rating\nfacts:\n  movie_has_title:\n    - { movie: 1, title: "The Departed" }\n    - { movie: 2, title: "Inception" }\n  movie_directed_by_director:\n    - { movie: 1, director: "Martin Scorsese" }\n    - { movie: 2, director: "Christopher Nolan" }\n  movie_released_in_year:\n    - { movie: 1, year: 2006 }\n    - { movie: 2, year: 2010 }\n  movie_has_rating:\n    - { movie: 1, rating: "R" }\n    - { movie: 2, rating: "PG-13" }\n'
VIOLATING_POPULATION = CONFORMING_POPULATION.replace('rating: "R" }', 'rating: "X" }')
ISOLATION_PROBE = "import json, os, sys, sysconfig, gnd;print(json.dumps({'sys_path': sys.path,'resolved_sys_path': [os.path.realpath(p or os.getcwd()) for p in sys.path],'cwd': os.getcwd(),'gnd_file': gnd.__file__,'purelib': sysconfig.get_paths()['purelib']}))"
LINK_PROBE = '\nimport json, posixpath, re\nfrom importlib.resources import files\n\nRELATIVE_LINK_RE = re.compile(rb"\\]\\((\\.\\./[^)\\s]+)\\)")\n\n\ndef walk(root, prefix=""):\n    for entry in root.iterdir():\n        rel = prefix + entry.name\n        if entry.is_dir():\n            yield from walk(entry, rel + "/")\n        else:\n            yield rel, entry\n\n\nroot = files("gnd") / "skills"\nentries = {rel for rel, _ in walk(root)}\ndirectories = set()\nfor rel in entries:\n    parts = rel.split("/")\n    for depth in range(1, len(parts)):\n        directories.add("/".join(parts[:depth]))\n\nchecked = 0\nfragment_links = 0\nunresolved = []\nfor rel, resource in walk(root):\n    if not rel.endswith(".md"):\n        continue\n    parent = posixpath.dirname(rel)\n    for match in RELATIVE_LINK_RE.finditer(resource.read_bytes()):\n        target = match.group(1).decode("utf-8")\n        checked += 1\n        target_path, separator, fragment = target.partition("#")\n        if separator:\n            fragment_links += 1\n            if not fragment:\n                unresolved.append(rel + " -> " + target + " (empty fragment)")\n                continue\n        resolved = posixpath.normpath(posixpath.join(parent, target_path))\n        if resolved not in entries and resolved not in directories:\n            unresolved.append(rel + " -> " + target + " (resolved: " + resolved + ")")\n\nprint(json.dumps({\n    "files": len(entries),\n    "entries": sorted(entries),\n    "skills": sorted({rel.split("/")[0] for rel in entries}),\n    "checked": checked,\n    "fragment_links": fragment_links,\n    "unresolved": unresolved,\n    "pep723_sibling_ships": "gnd-orm-core/references/orm-meta.schema.json" in entries,\n}))\n'

@pytest.fixture(scope='session')
def built_wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Plain ``uv build`` — NOT ``uv build --wheel``. See the module docstring."""
    if shutil.which('uv') is None:
        pytest.skip('uv is not available on PATH; the build artifact cannot be produced')
    out = tmp_path_factory.mktemp('dist')
    subprocess.run(['uv', 'build', '--out-dir', str(out)], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    wheels = sorted(out.glob('*.whl'))
    assert len(wheels) == 1, f'expected exactly one wheel from `uv build`, got {[w.name for w in wheels]}. More than one means a stale artifact is in the output directory and the environment under test would be built from an unknown one.'
    return wheels[0]

@pytest.fixture(scope='session')
def clean_env(tmp_path_factory: pytest.TempPathFactory, built_wheel: Path) -> Path:
    """A fresh virtual environment with the built wheel installed into it.

    Never ``--editable``, never a path install of ``REPO_ROOT``: the artifact
    under test is the wheel, and installing the source tree would prove a
    strictly weaker claim while looking identical from the outside.
    """
    venv = tmp_path_factory.mktemp('cleanenv') / '.venv'
    subprocess.run(['uv', 'venv', str(venv)], check=True, capture_output=True, text=True)
    subprocess.run(['uv', 'pip', 'install', '--python', str(_bin(venv) / 'python'), str(built_wheel)], check=True, capture_output=True, text=True)
    return venv

def _bin(venv: Path) -> Path:
    """The environment's script directory. ``os.name`` is portability, not a
    platform support claim (D-24)."""
    return venv / ('Scripts' if os.name == 'nt' else 'bin')

def _scrubbed_environment(**overrides: str) -> dict[str, str]:
    """The inherited environment with every route back into a developer's tree
    removed. ``PYTHONPATH`` and ``PYTHONHOME`` prepend directories to the module
    search path; ``VIRTUAL_ENV`` is what ``uv run`` sets and what would point a
    child at this repository's own environment."""
    env = {key: value for key, value in os.environ.items() if key not in {'PYTHONPATH', 'VIRTUAL_ENV', 'PYTHONHOME'}}
    env['PYTHONNOUSERSITE'] = '1'
    env.update(overrides)
    return env

def _assert_outside_the_checkout(cwd: Path) -> None:
    """The working directory is load-bearing, so it is checked rather than
    assumed: a probe run from inside the repository would resolve the checkout's
    own files and every result in this module would mean nothing."""
    resolved = cwd.resolve()
    assert REPO_ROOT not in resolved.parents and resolved != REPO_ROOT, f'the working directory {resolved} lies inside the checkout {REPO_ROOT}. Every assertion in this module depends on running from a directory that has never seen this repository.'

def _run_gnd(venv: Path, *args: str, cwd: Path, env: dict[str, str] | None=None) -> subprocess.CompletedProcess[str]:
    """Invoke the environment's OWN ``gnd`` executable.

    The interpreter's isolation flag cannot be passed here — a console script is
    not ``python``. It is also unnecessary: the generated wrapper's shebang pins
    this environment's interpreter, and a script's ``sys.path[0]`` is the
    *script's* directory (``<venv>/bin``), never the working directory. The
    scrubbed environment closes the remaining routes.
    """
    _assert_outside_the_checkout(cwd)
    return subprocess.run([str(_bin(venv) / 'gnd'), *args], cwd=cwd, env=env if env is not None else _scrubbed_environment(), capture_output=True, text=True, check=False)

def _run_python(venv: Path, code: str, *, cwd: Path, isolated: bool) -> subprocess.CompletedProcess[str]:
    """Run the environment's interpreter. ``isolated`` selects ``-I``; see
    ``ISOLATION_PROBE`` for why the isolation test must NOT use it."""
    _assert_outside_the_checkout(cwd)
    argv = [str(_bin(venv) / 'python')]
    if isolated:
        argv.append('-I')
    argv += ['-c', code]
    return subprocess.run(argv, cwd=cwd, env=_scrubbed_environment(), capture_output=True, text=True, check=False)

@cache
def _site_packages(venv: str) -> Path:
    """The installed environment's ``purelib``, asked of the interpreter itself
    rather than assembled from an assumed ``lib/pythonX.Y`` layout."""
    result = subprocess.run([str(_bin(Path(venv)) / 'python'), '-I', '-c', "import sysconfig; print(sysconfig.get_paths()['purelib'])"], capture_output=True, text=True, check=True)
    return Path(result.stdout.strip())

def _installed_skills_root(venv: Path) -> Path:
    """The skill tree inside the installed distribution.

    A filesystem path is legitimate *here* because this harness installs an
    unpacked wheel into a virtual environment. The shipped package never relies
    on that (D-19) — ``src/gnd/install.py`` walks Traversables — and neither does
    the link probe above, which runs inside the environment.
    """
    return _site_packages(str(venv)) / 'gnd' / 'skills'

def _declared_version() -> str:
    return tomllib.loads(PYPROJECT.read_text(encoding='utf-8'))['project']['version']

def _entries_inside_the_checkout(probe: dict) -> list[str]:
    """Module search path entries that lie inside this repository.

    Reads ``resolved_sys_path`` — resolved by the probe against ITS OWN working
    directory — never the raw ``sys.path``. See ``ISOLATION_PROBE``.
    """
    return [entry for entry in probe['resolved_sys_path'] if Path(entry) == REPO_ROOT or REPO_ROOT in Path(entry).parents]

def _why(reason: str, result: subprocess.CompletedProcess[str]) -> str:
    return f'\nWhy this case exists: {reason}\ncommand: {result.args}\nexit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}'

def test_the_installed_distribution_identifies_itself_by_name_and_version(clean_env: Path, tmp_path: Path) -> None:
    """D-15: "some `gnd` command answers" is not the claim.

    A stale global install of an unrelated distribution answers to ``gnd`` and
    would satisfy every behavioural probe in this file. What must be true is that
    the environment under test carries THIS distribution at THIS version.
    """
    reason = 'a stale or unrelated install answering to `gnd` would pass every other probe in this module; only the distribution Name and version pin which artifact is actually under test (D-15)'
    result = _run_python(clean_env, f"import importlib.metadata as m, json;d = m.distribution({EXPECTED_DISTRIBUTION!r});print(json.dumps({{'name': d.metadata['Name'], 'version': m.version({EXPECTED_DISTRIBUTION!r})}}))", cwd=tmp_path, isolated=True)
    assert result.returncode == 0, f'reading installed metadata for {EXPECTED_DISTRIBUTION!r} failed.' + _why(reason, result)
    meta = json.loads(result.stdout)
    assert meta['name'] == EXPECTED_DISTRIBUTION, f"installed metadata reports Name {meta['name']!r}, expected {EXPECTED_DISTRIBUTION!r} (D-01: `gnd` is taken on PyPI; the import package and console script keep that name, the distribution does not)." + _why(reason, result)
    assert meta['version'] == _declared_version(), f"installed metadata reports version {meta['version']!r} but pyproject.toml declares {_declared_version()!r}. pyproject.toml is the only place a version number is written (D-02)." + _why(reason, result)

def test_nothing_in_the_installed_environment_resolves_into_this_checkout(clean_env: Path, tmp_path: Path) -> None:
    """T-01.2-21. If the checkout leaks in, every other test here is theatre.

    The test carries its own negative control. The positive assertion runs with
    the scrubbed environment; the control then re-runs the same probe with
    ``PYTHONPATH`` pointed at this repository's ``src/`` and requires BOTH halves
    of the assertion to flip. Without that, a scrubbing bug — or a future
    "cleanup" that adds ``-I`` here — would leave a guard that cannot fail, which
    is worse than no guard at all.
    """
    reason = 'the proof is that the wheel supplies the runtime; a checkout entry on sys.path, or a gnd imported from src/, would make every band, link and install result in this module a statement about the repository instead (T-01.2-21)'
    result = _run_python(clean_env, ISOLATION_PROBE, cwd=tmp_path, isolated=False)
    assert result.returncode == 0, 'the isolation probe did not run.' + _why(reason, result)
    probe = json.loads(result.stdout)
    leaked = _entries_inside_the_checkout(probe)
    assert not leaked, f'module search path entries lie inside the checkout {REPO_ROOT}: {leaked}.' + _why(reason, result)
    gnd_file = Path(probe['gnd_file']).resolve()
    purelib = Path(probe['purelib']).resolve()
    assert purelib == gnd_file.parent.parent or purelib in gnd_file.parents, f"the imported package resolves to {gnd_file}, which is not inside the environment's site directory {purelib}." + _why(reason, result)
    control_env = _scrubbed_environment()
    control_env['PYTHONPATH'] = str(REPO_ROOT / 'src')
    control = subprocess.run([str(_bin(clean_env) / 'python'), '-c', ISOLATION_PROBE], cwd=tmp_path, env=control_env, capture_output=True, text=True, check=False)
    assert control.returncode == 0, 'the negative control did not run.' + _why(reason, control)
    control_probe = json.loads(control.stdout)
    control_leaks = _entries_inside_the_checkout(control_probe)
    assert control_leaks, 'NEGATIVE CONTROL FAILED: pointing PYTHONPATH at this checkout did not put a checkout entry on the module search path, so the positive assertion above cannot fail and proves nothing.' + _why(reason, control)
    assert REPO_ROOT in Path(control_probe['gnd_file']).resolve().parents, 'NEGATIVE CONTROL FAILED: with PYTHONPATH pointed at src/, `import gnd` still resolved outside the checkout, so the site-directory assertion above cannot fail either.' + _why(reason, control)

def test_the_exit_bands_survive_distribution(clean_env: Path, tmp_path: Path) -> None:
    """D-17: the band contract is owned by CORE-03/CORE-05 and was verified in
    Phase 01.1. This proves distribution *preserves* it; it does not re-derive it.
    One probe per band packaging could plausibly disturb.
    """
    model = _installed_skills_root(clean_env) / PACKAGED_EXAMPLE_MODEL
    cases: list[tuple[list[str], int, str]] = [(['validate', str(model)], 0, 'a packaged example model must still validate through the console script the wheel installs — if the example did not ship, this is where that surfaces'), (['--nonsense'], 64, '_BandSafeParser routes argparse usage errors to EX_USAGE so they can never collide with the 0-4 verdict bands; a console-script wrapper that swallowed or remapped SystemExit would show up here'), (['validate', './definitely-not-here.orm.yaml'], 3, 'a missing input is ill-formed (band 3), not a pass and not an internal error; the path is relative so it resolves against the temporary working directory and cannot accidentally exist')]
    for argv, expected, reason in cases:
        result = _run_gnd(clean_env, *argv, cwd=tmp_path)
        assert result.returncode == expected, f"`gnd {' '.join(argv)}` exited {result.returncode}, expected {expected}." + _why(reason, result)

def test_two_layer_validation_and_a_real_population_check_run_end_to_end(clean_env: Path, tmp_path: Path) -> None:
    """The capability PKG-01 exists to deliver, asserted through the installed
    binary rather than in process.

    ``bad_cross_ref.yaml`` is the two-layer proof: the zero-install fallback
    calls it structurally valid (test 6 pins that), and the installed runtime
    rejects it on a layer-2 rule. A packaging change that shipped only the schema
    would pass layer 1 here and this case would go green for the wrong reason —
    which is why the pair is asserted, not just the rejection.
    """
    skills = _installed_skills_root(clean_env)
    model = skills / PACKAGED_EXAMPLE_MODEL
    (tmp_path / 'conforming.population.yaml').write_text(CONFORMING_POPULATION, encoding='utf-8')
    (tmp_path / 'violating.population.yaml').write_text(VIOLATING_POPULATION, encoding='utf-8')
    (tmp_path / 'layer_two_defect.orm.yaml').write_bytes(LAYER_TWO_DEFECT_FIXTURE.read_bytes())
    layer_two = _run_gnd(clean_env, 'validate', './layer_two_defect.orm.yaml', cwd=tmp_path)
    assert layer_two.returncode == 3, f'`gnd validate` on a layer-2 defect exited {layer_two.returncode}, expected 3.' + _why("this model is structurally valid and semantically broken; rejecting it is what distinguishes the installed runtime from the zero-install fallback, and it is item 1 on that fallback's own limitation list", layer_two)
    passing = _run_gnd(clean_env, 'check', str(model), './conforming.population.yaml', cwd=tmp_path)
    assert passing.returncode == 0, f'`gnd check` on a conforming population exited {passing.returncode}, expected 0.' + _why('a real population checked against a packaged model, end to end through the installed binary — the claim D-15 makes in full', passing)
    failing = _run_gnd(clean_env, 'check', str(model), './violating.population.yaml', cwd=tmp_path)
    assert failing.returncode == 1, f'`gnd check` on an alethic violation exited {failing.returncode}, expected 1.' + _why('the passing case alone would go green if the checker never ran; a value-constraint violation must reach band 1, which proves the checker executed rather than that the documents merely parsed', failing)
    assert 'fail=1' in failing.stdout, 'the violating population exited 1 without reporting a failed verdict — the exit code may be right for the wrong reason.' + _why('band 1 must be produced by a real verdict, not an error path', failing)

def _source_skill_files() -> set[str]:
    """The source tree read on its own terms, for the cross-surface comparison.

    This is the ONLY thing in this module that touches the checkout, and it is
    read in the parent process; the installed inventory it is compared against
    is read by the child, inside the throwaway environment. Two mechanisms, two
    processes, two trees — which is what makes their agreement a claim.
    """
    if not SKILLS_SRC.is_dir():
        return set()
    return {path.relative_to(SKILLS_SRC).as_posix() for path in SKILLS_SRC.rglob('*') if path.is_file()}

def test_the_installed_distribution_and_the_source_tree_agree_file_for_file(clean_env: Path, tmp_path: Path) -> None:
    """The parity claim across the build/install boundary.

    Both sides are read independently — the checkout by ``rglob`` in this
    process, the installed distribution by ``importlib.resources`` in a child
    interpreter running outside the checkout. Neither is recomputed from the
    other, and neither is recomputed from the pin.
    """
    reason = 'everything between these two surfaces is build and install machinery; a disagreement is a packaging defect, and it is invisible to any test that reads the repository twice (T-04-13-01, T-04-13-02)'
    result = _run_python(clean_env, LINK_PROBE, cwd=tmp_path, isolated=True)
    assert result.returncode == 0, 'the inventory probe did not run.' + _why(reason, result)
    installed = set(json.loads(result.stdout)['entries'])
    source = _source_skill_files()
    assert source, f'{SKILLS_SRC} yielded no files, so the comparison below would be vacuous on one side.'
    assert installed == source, f'the installed distribution and the source tree disagree about what ships.\n  in the source tree but not installed ({len(source - installed)}): ' + ', '.join(sorted(source - installed)) + f'\n  installed but not in the source tree ({len(installed - source)}): ' + ', '.join(sorted(installed - source)) + _why(reason, result)

@pytest.mark.parametrize('resource', PHASE_FOUR_RESOURCES)
def test_every_phase_four_resource_reads_from_the_installed_distribution(resource: str, clean_env: Path, tmp_path: Path) -> None:
    """Named individually, and *read* rather than merely listed.

    Listing proves the path exists in the tree; reading proves the bytes came
    with it. A resource entry that lists but cannot be read is the shape a
    packaging change producing empty or unreadable members leaves behind, and it
    satisfies every inventory assertion above.
    """
    reason = 'these six are the newest and least linked-to packaged files, so they are the ones a build change drops first; each is named rather than left to a set diff (T-04-13-01)'
    probe = f"import json;from importlib.resources import files;r = files('gnd') / 'skills' / {resource!r};print(json.dumps({{'is_file': r.is_file(), 'bytes': len(r.read_bytes()) if r.is_file() else 0}}))"
    result = _run_python(clean_env, probe, cwd=tmp_path, isolated=True)
    assert result.returncode == 0, f'reading {resource} from the installed distribution raised.' + _why(reason, result)
    read = json.loads(result.stdout)
    assert read['is_file'], f'{resource} is not a file in the installed distribution.' + _why(reason, result)
    assert read['bytes'] > 0, f'{resource} is present in the installed distribution but empty.' + _why(reason, result)

def test_the_zero_install_fallback_resolves_its_sibling_schema_once_installed(clean_env: Path, tmp_path: Path) -> None:
    """D-14. The fallback resolves its meta-schema as a *sibling skill* lookup,
    three directories up from ``scripts/``. That is a hard runtime dependency on
    co-location, not a documentation link — it must hold where the script is
    installed, not only where it was written.

    Run with the environment's own interpreter, which already carries both PEP 723
    dependencies because they are ``get-nick-done``'s own. Under ``uv run`` the
    inline metadata header supplies them instead; what is isolated here is the
    sibling resolution, which is the half packaging can break.
    """
    skills = _installed_skills_root(clean_env)
    script = skills / PACKAGED_FALLBACK_SCRIPT
    model = skills / PACKAGED_EXAMPLE_MODEL
    assert (skills / PEP723_SIBLING_SCHEMA).is_file(), f"{PEP723_SIBLING_SCHEMA} is not present at {skills}; the bundled validator's DEFAULT_SCHEMA points three levels up from scripts/ and would be broken for every installed user."
    _assert_outside_the_checkout(tmp_path)
    result = subprocess.run([str(_bin(clean_env) / 'python'), str(script), str(model)], cwd=tmp_path, env=_scrubbed_environment(), capture_output=True, text=True, check=False)
    assert result.returncode == 0, f'the bundled fallback exited {result.returncode}, expected 0.' + _why('a fallback that only resolves its schema from the repository it was authored in is broken in exactly the situation it exists for (D-14, D-22); exit 66 here means the sibling lookup missed', result)
_SAMPLE_POOL_PROBE = '\nimport json\nfrom importlib.resources import files\nfrom jsonschema import Draft202012Validator\n\nschema = json.loads((files("gnd") / "pool.schema.json").read_text(encoding="utf-8"))\nDraft202012Validator.check_schema(schema)\nsample = {\n    "object_types": {"employee": [1, 2]},\n    "value_types": {"employee_name": ["Ada", "Grace"]},\n    "provenance": {"source": "faker", "rng_seed": 7},\n}\nDraft202012Validator(schema).validate(sample)\n# A closed schema must also REJECT: an unknown top-level key proves the vendored\n# copy is the strict one, not some permissive stand-in.\nrejected = False\ntry:\n    Draft202012Validator(schema).validate({**sample, "surprise": 1})\nexcept Exception:\n    rejected = True\nprint(json.dumps({"validated": True, "rejects_extra_key": rejected}))\n'

def test_pool_schema_resolves_and_validates_from_the_installed_wheel(clean_env: Path, tmp_path: Path) -> None:
    """C12. pool.schema.json is a runtime contract this phase adds; a source-tree
    test can pass while the resource is missing from the built artifact. It ships
    because it lives under the module root at src/gnd/pool.schema.json (the
    report.schema.json precedent) — proven here from inside the installed
    distribution, resolved via importlib.resources, never a repo path.
    """
    reason = 'pool.schema.json is vendored alongside report.schema.json under the gnd module root; if packaging drops it, load_pool is broken for every installed user and only the wheel shows it (C12)'
    result = _run_python(clean_env, _SAMPLE_POOL_PROBE, cwd=tmp_path, isolated=True)
    assert result.returncode == 0, 'the pool-schema probe did not run.' + _why(reason, result)
    probe = json.loads(result.stdout)
    assert probe['validated'], 'a valid sample pool failed the packaged schema.' + _why(reason, result)
    assert probe['rejects_extra_key'], 'the packaged pool schema admitted an unknown top-level key — it is not the strict closed contract load_pool relies on.' + _why(reason, result)
_SYNTH_EXTRA_PROBE = '\nimport json, os, tempfile\nfrom importlib.resources import files\nimport faker  # proves the `synth` extra actually installed\nfrom gnd.model import load_model\nfrom gnd.synth.poolfile import build_faker_pool, load_pool, write_pool\n\n# Copy a packaged model out of the wheel to a temp path (load_model takes a path).\nmodel_text = (files("gnd") / "skills" / "gnd-model-from-text" / "examples"\n              / "movie_catalog.orm.yaml").read_text(encoding="utf-8")\nwork = tempfile.mkdtemp()\nmodel_path = os.path.join(work, "movie_catalog.orm.yaml")\nopen(model_path, "w", encoding="utf-8").write(model_text)\n\nmodel = load_model(model_path)\npool = build_faker_pool(model, 5)\npool_path = os.path.join(work, "movie_catalog.pool.json")\nwrite_pool(pool, pool_path)\nreloaded = load_pool(pool_path, model)\nprint(json.dumps({\n    "faker_version": faker.VERSION,\n    "sha_round_trips": reloaded.sha256 == pool.sha256,\n    "source": reloaded.provenance["source"],\n}))\n'

def test_the_synth_extra_installs_and_builds_a_pool_outside_the_checkout(built_wheel: Path, tmp_path: Path) -> None:
    """C12, the extra half. `get-nick-done[synth]` must pull faker and let
    build_faker_pool run against a PACKAGED model from a clean environment — the
    offline builder working end to end from the artifact a user installs, not
    only from the checkout where faker happens to be present."""
    if shutil.which('uv') is None:
        pytest.skip('uv is not available on PATH')
    venv = tmp_path / '.venv'
    subprocess.run(['uv', 'venv', str(venv)], check=True, capture_output=True, text=True)
    subprocess.run(['uv', 'pip', 'install', '--python', str(_bin(venv) / 'python'), f'get-nick-done[synth] @ {built_wheel.as_uri()}'], check=True, capture_output=True, text=True)
    result = _run_python(venv, _SYNTH_EXTRA_PROBE, cwd=tmp_path, isolated=True)
    assert result.returncode == 0, 'building a pool from the installed synth extra failed.' + _why('the offline builder must run from the artifact, C12', result)
    probe = json.loads(result.stdout)
    assert probe['faker_version'], 'faker did not install under the synth extra'
    assert probe['sha_round_trips'], 'a pool built from a packaged model did not survive its own gate when run from the installed distribution.'
    assert probe['source'] == 'faker'
_MEASUREMENT_SCHEMA_PROBE = '\nimport json\nfrom importlib.resources import files\nfrom jsonschema import Draft202012Validator\n\nschema = json.loads((files("gnd") / "measurement.schema.json").read_text(encoding="utf-8"))\nDraft202012Validator.check_schema(schema)\n# The schema must declare NO timestamp FIELD (its descriptive text may mention\n# the word; a field is what would break byte-for-byte reproduction) and REQUIRE\n# all six outcome counters and the evidence excerpt.\ntop_properties = set(schema["properties"])\nrow_properties = set(schema["$defs"]["constraint_row"]["properties"])\ncells = schema["$defs"]["cells"]["required"]\nrow_required = schema["$defs"]["constraint_row"]["required"]\ntimestamp_fields = {"generated_at", "timestamp", "created_at", "date"}\nprint(json.dumps({\n    "loads": True,\n    "no_timestamp": not (timestamp_fields & (top_properties | row_properties)),\n    "six_counters": sorted(cells) == sorted(\n        ["correct", "false_pass", "false_fail", "undecided", "masked_by_vacuity", "tool_defect"]\n    ),\n    "evidence_required": "evidence" in row_required,\n}))\n'

def test_measure_command_and_schema_resolve_from_the_installed_wheel(clean_env: Path, tmp_path: Path) -> None:
    """C12 (plan 04's half). `gnd measure` and measurement.schema.json are runtime
    surface this plan adds; a source-tree test passes while the resource is
    missing from the built artifact. The schema ships because it lives at
    src/gnd/measurement.schema.json (the report.schema.json precedent), and the
    command ships as a subparser of the installed console script — both proven
    here from inside the installed distribution.
    """
    reason = 'measurement.schema.json is vendored under the gnd module root and `gnd measure` is a console-script subcommand; if packaging drops either, the metrics lane is broken for every installed user and only the wheel shows it (C12)'
    helped = _run_gnd(clean_env, 'measure', '--help', cwd=tmp_path)
    assert helped.returncode == 0, '`gnd measure --help` did not run.' + _why(reason, helped)
    assert '--populations' in helped.stdout, 'the installed `gnd measure` does not expose --populations.' + _why(reason, helped)
    probe = _run_python(clean_env, _MEASUREMENT_SCHEMA_PROBE, cwd=tmp_path, isolated=True)
    assert probe.returncode == 0, 'the measurement-schema probe did not run.' + _why(reason, probe)
    result = json.loads(probe.stdout)
    assert result['loads'], 'measurement.schema.json failed to load.' + _why(reason, probe)
    assert result['no_timestamp'], 'the packaged measurement schema carries a timestamp field — the payload would not reproduce byte-for-byte.' + _why(reason, probe)
    assert result['six_counters'], 'the packaged schema does not require all six outcome counters.' + _why(reason, probe)
    assert result['evidence_required'], 'the packaged schema does not require the D-22 evidence excerpt.' + _why(reason, probe)
_CONFORMANCE_SCHEMA_PROBE = '\nimport json\nfrom importlib.resources import files\nfrom jsonschema import Draft202012Validator\n\nfrom gnd.conformance.report import load_conformance_schema\n\nschema = load_conformance_schema()\nDraft202012Validator.check_schema(schema)\nresource = json.loads(\n    (files("gnd") / "conformance.schema.json").read_text(encoding="utf-8")\n)\ntop = set(schema["properties"])\ntimestamp_fields = {"generated_at", "timestamp", "created_at", "date"}\nprint(json.dumps({\n    "loads": True,\n    "resolves_through_the_loader": schema == resource,\n    "unexamined_required": "unexamined" in schema["required"],\n    "unexamined_min_items_zero": schema["properties"]["unexamined"]["minItems"] == 0,\n    "limits_required": "limits" in schema["required"],\n    "no_timestamp": not (timestamp_fields & top),\n    "no_verdict_or_rate": not (\n        {"verdicts", "counts", "acceptance_ready", "band", "publishable"} & top\n    ),\n}))\n'

def test_conformance_command_and_schema_resolve_from_the_installed_wheel(clean_env: Path, tmp_path: Path) -> None:
    """Plan 03-05's half of the C12 obligation. `gnd conformance` and
    conformance.schema.json are new runtime surface; the schema ships because it
    lives at src/gnd/conformance.schema.json (the report/measurement/fidelity
    precedent), and the command ships as a subparser of the installed console
    script — both proven here from inside the installed distribution, because a
    source-tree test passes while the built artifact is missing the resource.
    """
    reason = "conformance.schema.json is vendored under the gnd module root and `gnd conformance` is a console-script subcommand; if packaging drops either, GEN-02's drift check is broken for every installed user and only the wheel shows it (C12)"
    helped = _run_gnd(clean_env, 'conformance', '--help', cwd=tmp_path)
    assert helped.returncode == 0, '`gnd conformance --help` did not run.' + _why(reason, helped)
    assert '--format' in helped.stdout, 'the installed `gnd conformance` does not expose --format.' + _why(reason, helped)
    probe = _run_python(clean_env, _CONFORMANCE_SCHEMA_PROBE, cwd=tmp_path, isolated=True)
    assert probe.returncode == 0, 'the conformance-schema probe did not run.' + _why(reason, probe)
    result = json.loads(probe.stdout)
    assert result['loads'], 'conformance.schema.json failed to load.' + _why(reason, probe)
    assert result['resolves_through_the_loader'], 'load_conformance_schema() and the packaged resource disagree.' + _why(reason, probe)
    assert result['unexamined_required'] and result['unexamined_min_items_zero'], "the packaged schema does not require `unexamined` with minItems 0 — G-08's present-and-empty rule is not shipped." + _why(reason, probe)
    assert result['limits_required'], "the packaged schema does not require the `limits` block (R-13')." + _why(reason, probe)
    assert result['no_timestamp'], 'the packaged conformance schema carries a timestamp field — the payload would not reproduce byte-for-byte.' + _why(reason, probe)
    assert result['no_verdict_or_rate'], 'the packaged conformance schema carries verdict- or rate-family fields (G-15).' + _why(reason, probe)

def test_no_proof_toolchain_artifact_ships_in_the_wheel(built_wheel: Path) -> None:
    """T51. No proof runtime ships; Phase 6 evidence remains inert package data."""
    import zipfile
    with zipfile.ZipFile(built_wheel) as archive:
        names = archive.namelist()
        evidence_root = 'gnd/_assurance_evidence/'
        product_names = [name for name in names if not name.startswith(evidence_root)]
        forbidden = [name for name in product_names if any(token in name.lower() for token in ('nagini', 'viper', '.jar', '/z3', 'proof/v6', 'toolchain'))]
        assert forbidden == []
        evidence_runtimes = [name for name in names if name.startswith(evidence_root) and (any(token in name.lower() for token in ('/.venv/', '/venv/', '/bin/')) or name.lower().endswith(('.jar', '.so', '.dylib', '.dll', '.exe')))]
        assert evidence_runtimes == []
        metadata_name = next(name for name in names if name.endswith('METADATA'))
        metadata = archive.read(metadata_name).decode('utf-8')
    requirements = [line.split(':', 1)[1].strip() for line in metadata.splitlines() if line.startswith('Requires-Dist:')]
    assert not any('nagini' in requirement.lower() for requirement in requirements)
    assert any(name.endswith('gnd/proof_kernel.py') for name in names)
    assert any(name.endswith('gnd/proof_bridge.py') for name in names)
    for module in ('semantic_registry', 'semantic_ir', 'semantic_adapter', 'semantic_spec'):
        assert any(name.endswith(f'gnd/{module}.py') for name in names)

def test_the_shipped_kernel_imports_without_any_proof_runtime(clean_env: Path) -> None:
    """T52's Phase 1 clause: `gnd.proof_kernel` and the bridge import and decide
    a slice in the clean environment, with no proof tool installed there."""
    probe = "from gnd.proof_kernel import SliceInput, phase1_decide\nvalue = SliceInput('constraints[0]', 'mandatory', 'alethic', True, True, ('a1',), ('a1',), (), None, None)\nverdict = phase1_decide(value)\nassert verdict is not None and verdict.verdict == 'pass'\nimport gnd.proof_bridge\nprint('kernel-ok')\n"
    completed = subprocess.run([str(_bin(clean_env) / 'python'), '-c', probe], capture_output=True, text=True, env=_scrubbed_environment(), check=False)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert 'kernel-ok' in completed.stdout

def test_semantic_adapter_imports_and_runs_off_checkout(clean_env: Path, tmp_path: Path) -> None:
    probe = "\nfrom importlib.util import find_spec\nfrom gnd.semantic_adapter import canonical_scalar\nfrom gnd.semantic_ir import Scalar\nfrom gnd.semantic_registry import REGISTRY\nassert find_spec('nagini_contracts') is None\nassert find_spec('nagini_translation') is None\nassert canonical_scalar(1, 'Integer') == canonical_scalar(1.0, 'Float')\nassert canonical_scalar(True, 'Integer') is None\nassert isinstance(canonical_scalar('2026-09-07', 'Date'), Scalar)\nassert any(row.family == 'adapter' for row in REGISTRY)\nprint('adapter-ok')\n"
    result = _run_python(clean_env, probe, cwd=tmp_path, isolated=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == 'adapter-ok'

def test_semantic_spec_imports_and_runs_off_checkout(clean_env: Path, tmp_path: Path) -> None:
    probe = "\nfrom importlib.util import find_spec\nfrom gnd.semantic_adapter import canonical_scalar\nfrom gnd.semantic_spec import missing_identities, pack_witness_row, scalar_ranges_state\nassert find_spec('nagini_contracts') is None\nassert find_spec('nagini_translation') is None\nzero = canonical_scalar(0, 'Integer')\ntext = canonical_scalar('unorderable', 'String')\nassert zero is not None and text is not None\nassert missing_identities((zero, zero), ()) == [zero]\nassert scalar_ranges_state(zero, ((text, None, True, True),\n                                (None, None, True, True))) == 1\nassert pack_witness_row([]) == [[]]\nprint('spec-ok')\n"
    result = _run_python(clean_env, probe, cwd=tmp_path, isolated=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == 'spec-ok'
