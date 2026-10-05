"""RF1 lane L-SESSION: golden replays per contract version and path (spec 6.7).

Matrix: fresh v1-v8, resume v1-v8, reconstruct v7-v8, unknown versions 0 and 9.
Each version is built from the repository's existing session fixtures and
builders, which this file imports rather than restates. Normalization follows
rules N1-N6 in tests/support/rf1_pins.py; the clock is not injected (N1
fallback), so monotonic and seconds fields are placeholders.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import shutil
import stat
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from support.cli_runner import run_main
from support.rf1_pins import (
    assert_golden,
    encode,
    evidence_tree,
    normalize_text,
    normalize_tree,
    observe,
    tree_digests,
)

from gnd import cli
from gnd.exp.session import case_payload_versions
from gnd.exp.session_contract import read_session_contract
from gnd.exp.session_store import SessionStore

ROOT = Path(__file__).resolve().parents[1]
WALK = ROOT / "tests/fixtures/public-walk-floor/session"
STEPS = (WALK / "candidate/steps.json").read_bytes()


@dataclass
class Built:
    root: Path
    experiment_id: str
    argv: list[str]
    tokens: dict[str, str] = field(default_factory=dict)

    def inputs(self) -> dict[str, bytes]:
        """Declared inputs outside the run tree whose digests the evidence cites (N5).

        The adapter policy file, and the interpreter path string that a declared
        adapter's executable_sha256 hashes (declared_adapter.py).
        """
        found = {"python-path": sys.executable.encode(), "python-realpath": os.path.realpath(sys.executable).encode()}
        if "--adapter-policy" in self.argv:
            found["adapter-policy"] = Path(self.argv[self.argv.index("--adapter-policy") + 1]).read_bytes()
        return found


def _identities() -> dict[str, str]:
    """N9: digests over src/gnd bytes and the interpreter (RF-R8) change on every
    edit; each is replaced only where it equals the value computed in-process now."""
    from gnd.assurance_evidence import production_identity
    from gnd.assurance_transport import producer_identity

    return {production_identity(): "<production-identity>", producer_identity(): "<producer-identity>"}


def _tokens(tmp_path: Path) -> dict[str, str]:
    return {
        **_identities(),
        str(tmp_path.resolve()): "<root>",
        str(tmp_path): "<root>",
        sys.executable: "<python>",
        os.path.realpath(sys.executable): "<python>",
    }


def _bound(root: Path, relative: str, media_type: str) -> dict:
    data = (root / relative).read_bytes()
    return {"path": relative, "media_type": media_type, "encoding": "utf-8",
            "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}


def _init(tmp_path: Path, experiment_id: str) -> Path:
    assert cli.main(["exp", "init", experiment_id, "--out", str(tmp_path), "--kind", "data-driven",
                     "--question", "Q1=Does the RF1 pinned session replay?"]) == 0
    return tmp_path / experiment_id


TRANSITION_AGENT = """#!/usr/bin/env python3
import base64, pathlib, sys
if "--version" in sys.argv:
    print("rf1-transition-agent 1.0")
    raise SystemExit(0)
sys.stdin.buffer.read()
counter = pathlib.Path(__file__).with_name("attempts")
attempt = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(attempt))
if attempt >= 2:
    pathlib.Path("steps.json").write_bytes(base64.b64decode("STEPS_BASE64"))
raise SystemExit(0)
""".replace("STEPS_BASE64", base64.b64encode(STEPS).decode())


def _agent(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _legacy_path(tmp_path: Path, monkeypatch, name: str, text: str) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    _agent(bin_dir / name, text)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")


def _transition_experiment(tmp_path: Path, version: int) -> Path:
    experiment = f"EXP-910-rf1-v{version}"
    root = _init(tmp_path, experiment)
    (root / "input").mkdir()
    (root / "candidate").mkdir()
    shutil.copyfile(WALK / "model.orm.yaml", root / "model.orm.yaml")
    shutil.copyfile(WALK / "input/pre.pop.yaml", root / "input/pre.pop.yaml")
    if version == 5:
        contract = json.loads((WALK / "contract-v5.json").read_text())
        contract["experiment_id"] = experiment
    else:
        case = {
            "case_id": "walk", "role": "required",
            "inputs": [_bound(root, "input/pre.pop.yaml", "application/yaml")],
            "acceptance": {"mode": "transition", **({"walk": None} if version == 6 else {})},
            "verify": {"command": "transition", "model": _bound(root, "model.orm.yaml", "application/yaml"),
                       "pre": "input/pre.pop.yaml", "steps": "steps.json", "post": None},
        }
        contract = {"schema_version": version, "experiment_id": experiment, "max_attempts": 2,
                    "wall_seconds": 120.0, "cases": [case]}
        if version == 6:
            contract["adapter"] = {"policy_id": "rf1-agent", "parameters": {"model": None}}
    (root / "session.contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True))
    return root


def build_v1(tmp_path: Path, monkeypatch) -> Built:
    import test_exp_session_e2e as e2e

    accepted = e2e._accepted_population()
    root = e2e._make_experiment(tmp_path, monkeypatch, subject_fixture=e2e.SKELETON / "population.bad.yaml",
                                max_attempts=2, wall_seconds=60.0, expected_bytes=accepted)
    e2e._write_exact_feedback_retry_agent(tmp_path / "bin" / "codex", accepted_population=accepted)
    return Built(root, root.name, ["exp", "run", str(root), "--adapter", "codex"])


def build_v2(tmp_path: Path, monkeypatch) -> Built:
    import test_public_constraint_sessions as constraint

    root = constraint._make_experiment(tmp_path, monkeypatch, initial=constraint.VIOLATED,
                                       produced=constraint.SATISFYING_A, adapter="codex", max_attempts=2,
                                       retry_branch="violations")
    return Built(root, root.name, ["exp", "run", str(root), "--adapter", "codex"])


def build_v3(tmp_path: Path, monkeypatch) -> Built:
    import test_public_tests_mode_corpus as tests_mode

    fixture = tests_mode._materialize("happy", tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    shutil.copyfile(tests_mode.BASE / "adapter.py", bin_dir / "codex")
    (bin_dir / "codex").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    argv = ["exp", "run", str(fixture.root), "--adapter", "codex", *(f"--test-argv={w}" for w in fixture.argv)]
    tokens = {str(tests_mode.CORPUS.resolve()): "<tests-mode-corpus>", str(tests_mode.CORPUS): "<tests-mode-corpus>"}
    return Built(fixture.root, tests_mode.EXPERIMENT_ID, argv, tokens)


def build_v4(tmp_path: Path, monkeypatch) -> Built:
    root = _transition_experiment(tmp_path, 4)
    _legacy_path(tmp_path, monkeypatch, "claude", TRANSITION_AGENT)
    return Built(root, root.name, ["exp", "run", str(root), "--adapter", "claude"])


def build_v5(tmp_path: Path, monkeypatch) -> Built:
    root = _transition_experiment(tmp_path, 5)
    _legacy_path(tmp_path, monkeypatch, "claude", TRANSITION_AGENT)
    return Built(root, root.name, ["exp", "run", str(root), "--adapter", "claude"])


def build_v6(tmp_path: Path, monkeypatch) -> Built:
    root = _transition_experiment(tmp_path, 6)
    agent = tmp_path / "agent" / "rf1_agent.py"
    agent.parent.mkdir()
    _agent(agent, TRANSITION_AGENT)
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({
        "schema_version": 1, "policy_id": "rf1-agent", "kind": "command", "executable": sys.executable,
        "argv": [str(agent)], "version_argv": [str(agent), "--version"], "prompt_transport": "stdin",
        "environment_allowlist": ["PATH", "HOME"]}))
    return Built(root, root.name, ["exp", "run", str(root), "--adapter-policy", str(policy)])


def build_v7(tmp_path: Path, monkeypatch) -> Built:
    from support import v71_session_cases as v71

    holder: dict = {}
    real_main = v71.main
    b = v71.bundle("dispatch", tmp_path / "v7")
    monkeypatch.setattr(v71, "main", lambda argv: real_main(argv) if argv[:2] == ["exp", "init"] else _stop(holder, argv))
    with pytest.raises(_Stop):
        v71.session_case({"parameters": {}, "branch": "B00"}, b)
    monkeypatch.setattr(v71, "main", real_main)
    root = Path(holder["argv"][2])
    return Built(root, root.name, holder["argv"])


def build_v8(tmp_path: Path, monkeypatch) -> Built:
    import test_public_v71_full_judgments as judgments

    module = judgments._JUDGMENTS
    holder: dict = {}
    domain = min(module.INPUTS["domains"])
    b = module.bundle(domain, tmp_path / "v8")
    real_main = module.main
    monkeypatch.setattr(module, "main", lambda argv: real_main(argv) if argv[:2] == ["exp", "init"] else _stop(holder, argv))
    with monkeypatch.context() as scoped:
        scoped.setitem(sys.modules, "tests.support.v71_session_cases", judgments._SESSIONS)
        with pytest.raises(_Stop):
            module.session_case({"parameters": {"variant": "default"}, "mode": "session", "domain": domain}, b)
    monkeypatch.setattr(module, "main", real_main)
    root = Path(holder["argv"][2])
    tokens = {str(judgments.ROOT): "<judgment-corpus>"}
    return Built(root, root.name, holder["argv"], tokens)


class _Stop(Exception):
    pass


def _stop(holder: dict, argv) -> int:
    holder["argv"] = list(argv)
    raise _Stop


BUILDERS: dict[int, Callable[[Path, pytest.MonkeyPatch], Built]] = {
    1: build_v1, 2: build_v2, 3: build_v3, 4: build_v4, 5: build_v5, 6: build_v6, 7: build_v7, 8: build_v8,
}


def _forbidden(run: Path) -> list[str]:
    # N4: staging directory names never appear in published files.
    return [entry.name for entry in run.rglob(".staging*")]


def _normalized_run(built: Built, run: Path, tmp_path: Path) -> dict:
    tokens = {**_tokens(tmp_path), **built.tokens}
    return normalize_tree(evidence_tree(run), tokens=tokens, forbidden=_forbidden(run), clock_injected=False,
                          inputs=built.inputs())


def _norm(value, built: Built, tmp_path: Path, run: Path | None) -> object:
    """Normalize a stream or state observation with the evidence tree's rules (N3, N7, N5, N1/N2)."""
    files = evidence_tree(run) if run is not None and run.is_dir() else {}
    by_digest = tree_digests(files, built.inputs())
    text = normalize_text(json.dumps(value, ensure_ascii=False), own=None, by_digest=by_digest,
                          tokens={**_tokens(tmp_path), **built.tokens}, clock_injected=False)
    return json.loads(text)


def _streams(result, built: Built, tmp_path: Path, run: Path | None) -> object:
    observed = {"exit": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
    return _norm(observed, built, tmp_path, run)


def _fresh(version: int, tmp_path: Path, monkeypatch) -> tuple[Built, Path, dict]:
    built = BUILDERS[version](tmp_path, monkeypatch)
    result = run_main(built.argv, cwd=tmp_path)
    run = built.root / "runs" / "run-0001"
    observed = {"streams": _streams(result, built, tmp_path, run),
                "evidence": _normalized_run(built, run, tmp_path) if run.is_dir() else None}
    return built, run, observed


def _contract(built: Built):
    return read_session_contract(built.root / "session.contract.json", experiment_root=built.root,
                                 experiment_id=built.experiment_id)


def _resume_state(built: Built, run: Path, tmp_path: Path) -> dict:
    def read():
        contract = _contract(built)
        store = SessionStore(run, run_id=run.name)
        return store.read_resume_state(contract, expected_payload_versions=case_payload_versions(contract, built.root))

    return _norm(observe(read), built, tmp_path, run)


VERSIONS = sorted(BUILDERS)


@pytest.mark.parametrize("version", VERSIONS)
def test_session_fresh(version, tmp_path, monkeypatch):
    _built, _run, observed = _fresh(version, tmp_path, monkeypatch)
    assert_golden("session", f"v{version}-fresh", observed)


@pytest.mark.parametrize("version", VERSIONS)
def test_session_resume(version, tmp_path, monkeypatch):
    built, run, _observed = _fresh(version, tmp_path, monkeypatch)
    (run / "result.json").unlink()
    before = sorted(path.relative_to(run).as_posix() for path in run.rglob("*"))
    state = _resume_state(built, run, tmp_path)
    monkeypatch.setattr(cli, "_next_session_run_root", lambda _root: run)
    result = run_main(built.argv, cwd=tmp_path)
    after = sorted(path.relative_to(run).as_posix() for path in run.rglob("*"))
    observed = {
        "resume_state": state,
        "resumed_streams": _streams(result, built, tmp_path, run),
        "new_paths": sorted(set(after) - set(before)),
        "evidence_after": _normalized_run(built, run, tmp_path),
    }
    assert_golden("session", f"v{version}-resume", observed)


@pytest.mark.parametrize("version", [7, 8])
def test_session_reconstruct(version, tmp_path, monkeypatch):
    from gnd.exp import session_v7

    built, run, _observed = _fresh(version, tmp_path, monkeypatch)
    contract = _contract(built)

    def terminal():
        store = SessionStore(run, run_id=run.name)
        state = session_v7.reconstruct(store, contract, allow_terminal=True)
        best = getattr(store, "_v7_best", None)
        return {"state": state, "best": None if best is None else encode(best[0])}

    observed = {"terminal": _norm(observe(terminal), built, tmp_path, run)}
    (run / "result.json").unlink()

    def resumable():
        store = SessionStore(run, run_id=run.name)
        return session_v7.reconstruct(store, contract)

    observed["without_result"] = _norm(observe(resumable), built, tmp_path, run)
    assert_golden("session", f"v{version}-reconstruct", observed)


@pytest.mark.parametrize("version", [0, 9])
def test_session_unknown_version(version, tmp_path, monkeypatch):
    built = build_v2(tmp_path, monkeypatch)
    path = built.root / "session.contract.json"
    document = json.loads(path.read_text())
    document["schema_version"] = version
    path.write_text(json.dumps(document, sort_keys=True))
    observed = {
        "reader": _norm(observe(_contract, built), built, tmp_path, None),
        "cli": _streams(run_main(built.argv, cwd=tmp_path), built, tmp_path, None),
    }
    assert_golden("session", f"unknown-v{version}", observed)


@pytest.mark.parametrize("version", VERSIONS)
def test_session_determinism(version, tmp_path, monkeypatch):
    """T-SESSION-DET (N6): two fresh runs of one case normalize to the same bytes."""
    first_dir, second_dir = tmp_path / "one", tmp_path / "two"
    first_dir.mkdir()
    second_dir.mkdir()
    with monkeypatch.context() as scoped:
        _b, _r, first = _fresh(version, first_dir, scoped)
    with monkeypatch.context() as scoped:
        _b, _r, second = _fresh(version, second_dir, scoped)
    assert copy.deepcopy(first) == copy.deepcopy(second)
