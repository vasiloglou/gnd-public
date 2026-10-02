from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py"
)


@pytest.fixture
def updater() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gnd_update_harnesses_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    original = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = original
    return module


def _write_qwen_settings(
    path: Path,
    *,
    model: str = "qwen3.6-plus",
    base_url: str = "https://openrouter.ai/api/v1",
    env_key: str = "OPENROUTER_API_KEY",
    duplicate: bool = False,
) -> None:
    route = {
        "id": "qwen/qwen3.8-max",
        "baseUrl": base_url,
        "envKey": env_key,
    }
    document = {
        "env": {"preserved": "reference-only"},
        "model": {"name": model, "reasoningEffort": "xhigh"},
        "modelProviders": {"openai": [route, *([route] if duplicate else [])]},
    }
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def test_updater_roster_is_the_panel_roster(updater: ModuleType) -> None:
    assert [(item.reviewer, item.command, item.npm_package) for item in updater.HARNESSES] == [
        ("claude", "claude", "@anthropic-ai/claude-code"),
        ("codex", "codex", "@openai/codex"),
        ("qwen", "qwen", "@qwen-code/qwen-code"),
        ("gemini", "gemini", "@google/gemini-cli"),
        ("kimi", "kimi", "@moonshot-ai/kimi-code"),
    ]


def test_npm_source_requires_the_resolved_command_to_live_inside_its_package(
    updater: ModuleType,
    tmp_path: Path,
) -> None:
    npm_root = tmp_path / "node_modules"
    package_root = npm_root / "@vendor" / "tool"
    package_root.mkdir(parents=True)
    owned = package_root / "cli.js"
    owned.write_text("#!/bin/sh\n", encoding="utf-8")
    owned.chmod(0o755)
    link = tmp_path / "bin" / "tool"
    link.parent.mkdir()
    link.symlink_to(owned)
    shadow = tmp_path / "shadow" / "tool"
    shadow.parent.mkdir()
    shadow.write_text("#!/bin/sh\n", encoding="utf-8")
    shadow.chmod(0o755)

    assert updater._npm_owns_command(npm_root, "@vendor/tool", str(link)) is True
    assert updater._npm_owns_command(npm_root, "@vendor/tool", str(shadow)) is False


def test_apply_refuses_every_change_when_preflight_has_an_unknown_source(
    updater: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot = {
        item.reviewer: {"source": "npm", "current": True}
        for item in updater.HARNESSES
    }
    snapshot["qwen"] = {"source": "unsupported", "error": "shadow executable"}

    monkeypatch.setattr(updater.shutil, "which", lambda command: "/bin/npm")
    monkeypatch.setattr(updater, "_text", lambda *_args, **_kwargs: str(tmp_path))
    monkeypatch.setattr(updater, "_npm_inventory", lambda _npm: {})
    monkeypatch.setattr(updater, "_snapshot", lambda *_args: snapshot)

    def forbidden_apply(*_args: Any) -> None:
        pytest.fail("an update ran after preflight refusal")

    monkeypatch.setattr(updater, "_apply", forbidden_apply)

    assert updater.main(["--apply"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert "preflight refused before making changes" in payload["error"]
    assert "qwen: shadow executable" in payload["error"]


def test_apply_updates_npm_once_and_preserves_native_kimi(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = {
        item.reviewer: {"source": "native" if item.reviewer == "kimi" else "npm"}
        for item in updater.HARNESSES
    }
    calls: list[tuple[tuple[str, ...], bytes | None]] = []
    selected: list[bool] = []

    def fake_run(
        argv: tuple[str, ...],
        *,
        timeout: float,
        input_bytes: bytes | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        assert timeout == 600.0
        calls.append((tuple(argv), input_bytes))
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr(updater, "_run", fake_run)
    monkeypatch.setattr(updater, "_https_bytes", lambda _url: b"verified-by-vendor-installer")
    monkeypatch.setattr(updater.shutil, "which", lambda command: "/bin/bash" if command == "bash" else None)
    monkeypatch.setattr(
        updater,
        "_select_qwen_openrouter",
        lambda: selected.append(True),
    )

    updater._apply(
        "/bin/npm",
        before,
        expected_installer_sha256=hashlib.sha256(b"verified-by-vendor-installer").hexdigest(),
    )

    assert calls == [
        (
            (
                "/bin/npm",
                "install",
                "-g",
                "@anthropic-ai/claude-code@latest",
                "@openai/codex@latest",
                "@qwen-code/qwen-code@latest",
                "@google/gemini-cli@latest",
            ),
            None,
        ),
        (("/bin/bash",), b"verified-by-vendor-installer"),
    ]
    assert selected == [True]


def _installer_spy(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    payload: bytes = b"vendor-installer-body",
) -> list[tuple[tuple[str, ...], bytes | None]]:





    executed: list[tuple[tuple[str, ...], bytes | None]] = []

    def fake_run(
        argv: tuple[str, ...],
        *,
        timeout: float,
        input_bytes: bytes | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        executed.append((tuple(argv), input_bytes))
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr(updater, "_run", fake_run)
    monkeypatch.setattr(updater, "_https_bytes", lambda _url: payload)
    monkeypatch.setattr(
        updater.shutil, "which", lambda command: "/bin/bash" if command == "bash" else None
    )
    return executed


def test_an_unpinned_installer_is_refused_and_never_reaches_bash(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:





    executed = _installer_spy(updater, monkeypatch)
    monkeypatch.setattr(updater, "NATIVE_KIMI_INSTALLER_SHA256", None)

    with pytest.raises(updater.UpdateError, match="no reviewed sha256 is pinned"):
        updater._install_native_kimi(expected_sha256=None)

    assert executed == [], "an unpinned installer must never be executed"


def test_a_mismatched_installer_digest_is_refused_and_never_reaches_bash(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    executed = _installer_spy(updater, monkeypatch, payload=b"upstream-changed-this")
    reviewed = hashlib.sha256(b"the-body-that-was-reviewed").hexdigest()
    monkeypatch.setattr(updater, "NATIVE_KIMI_INSTALLER_SHA256", reviewed)

    with pytest.raises(updater.UpdateError, match="digest mismatch"):
        updater._install_native_kimi(expected_sha256=None)

    assert executed == [], "a digest mismatch must never be executed"


def test_the_reviewed_digest_is_what_permits_execution(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:






    payload = b"vendor-installer-body"
    executed = _installer_spy(updater, monkeypatch, payload=payload)
    monkeypatch.setattr(
        updater, "NATIVE_KIMI_INSTALLER_SHA256", hashlib.sha256(payload).hexdigest()
    )

    updater._install_native_kimi(expected_sha256=None)

    assert executed == [(("/bin/bash",), payload)]


def test_a_per_run_digest_is_accepted_in_any_case_and_a_malformed_one_is_refused(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"vendor-installer-body"
    executed = _installer_spy(updater, monkeypatch, payload=payload)
    monkeypatch.setattr(updater, "NATIVE_KIMI_INSTALLER_SHA256", None)

                                                                                
    updater._install_native_kimi(expected_sha256=hashlib.sha256(payload).hexdigest().upper())
    assert executed == [(("/bin/bash",), payload)]

                                                                          
    executed.clear()
    for malformed in ("", "deadbeef", "z" * 64, hashlib.sha256(payload).hexdigest() + "0"):
        with pytest.raises(updater.UpdateError, match="64-character hex sha256"):
            updater._install_native_kimi(expected_sha256=malformed)
    assert executed == [], "a malformed digest must never be executed"


def test_an_unpinned_installer_aborts_apply_before_npm_touches_anything(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:







    executed = _installer_spy(updater, monkeypatch)
    monkeypatch.setattr(updater, "NATIVE_KIMI_INSTALLER_SHA256", None)
    selected: list[bool] = []
    monkeypatch.setattr(updater, "_select_qwen_openrouter", lambda: selected.append(True))

    before = {
        item.reviewer: {"source": "native" if item.reviewer == "kimi" else "npm"}
        for item in updater.HARNESSES
    }

    with pytest.raises(updater.UpdateError, match="no reviewed sha256 is pinned"):
        updater._apply("/bin/npm", before)

    assert executed == [], "npm must not run when the installer digest is unreviewed"
    assert selected == [], "the qwen route must not be touched either"


def test_check_mode_reports_the_installer_digest_without_executing_it(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    payload = b"vendor-installer-body"
    executed = _installer_spy(updater, monkeypatch, payload=payload)
    monkeypatch.setattr(updater, "NATIVE_KIMI_INSTALLER_SHA256", None)

    status = updater._installer_pin_status()

    assert status["observed_sha256"] == hashlib.sha256(payload).hexdigest()
    assert status["pinned"] is False
    assert status["apply_would_execute"] is False
    assert executed == [], "--check must never execute the installer"


def test_qwen_route_must_be_unique_and_exactly_openrouter(
    updater: ModuleType,
    tmp_path: Path,
) -> None:
    settings = tmp_path / "settings.json"
    _write_qwen_settings(settings, base_url="https://dashscope.aliyuncs.com/v1")
    with pytest.raises(updater.UpdateError, match="must use https://openrouter.ai/api/v1"):
        updater._qwen_openrouter_status(settings)

    _write_qwen_settings(settings, env_key="DASHSCOPE_API_KEY")
    with pytest.raises(updater.UpdateError, match="OPENROUTER_API_KEY"):
        updater._qwen_openrouter_status(settings)

    _write_qwen_settings(settings, duplicate=True)
    with pytest.raises(updater.UpdateError, match="exactly one"):
        updater._qwen_openrouter_status(settings)


def test_qwen_openrouter_selection_is_atomic_and_preserves_other_settings(
    updater: ModuleType,
    tmp_path: Path,
) -> None:
    settings = tmp_path / "settings.json"
    _write_qwen_settings(settings)
    settings.chmod(0o640)

    assert updater._select_qwen_openrouter(settings) is True

    document = json.loads(settings.read_text(encoding="utf-8"))
    assert document["model"] == {
        "name": "qwen/qwen3.8-max",
        "reasoningEffort": "xhigh",
        "baseUrl": "https://openrouter.ai/api/v1",
    }
    assert document["env"] == {"preserved": "reference-only"}
    assert settings.stat().st_mode & 0o777 == 0o640
    assert updater._qwen_openrouter_status(settings) == {
        "active": True,
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "model": "qwen/qwen3.8-max",
        "provider": "openrouter",
        "settings_path": str(settings),
    }
    assert updater._select_qwen_openrouter(settings) is False


def test_https_fetch_uses_curl_and_rejects_an_off_domain_redirect(
    updater: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(updater.shutil, "which", lambda command: "/usr/bin/curl")

    def fake_run(
        argv: tuple[str, ...],
        *,
        timeout: float,
        input_bytes: bytes | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        assert timeout == 45.0
        assert input_bytes is None
        calls.append(tuple(argv))
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout=b"0.36.1\n",
            stderr=b"https://cdn.kimi.com/kimi-code/latest",
        )

    monkeypatch.setattr(updater, "_run", fake_run)

    assert updater._https_bytes(updater.NATIVE_KIMI_LATEST) == b"0.36.1\n"
    assert calls[0][0:2] == ("/usr/bin/curl", "-q")
    assert "=https" in calls[0]
    assert calls[0][-1] == updater.NATIVE_KIMI_LATEST

    monkeypatch.setattr(
        updater,
        "_run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            (), 0, stdout=b"malicious", stderr=b"https://example.com/payload"
        ),
    )
    with pytest.raises(updater.UpdateError, match="outside its official hosts"):
        updater._https_bytes(updater.NATIVE_KIMI_INSTALLER)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2.1.233 (Claude Code)", "2.1.233"),
        ("codex-cli 0.147.0", "0.147.0"),
        ("no semantic version", None),
    ],
)
def test_command_versions_are_normalized_without_vendor_specific_parsing(
    updater: ModuleType,
    raw: str,
    expected: str | None,
) -> None:
    assert updater._normalized_version(raw) == expected
