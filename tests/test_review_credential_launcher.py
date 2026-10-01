from __future__ import annotations

import importlib.util
import io
import os
import urllib.error
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).parents[1] / "tools" / "run_gnd_review_panel.py"
SPEC = importlib.util.spec_from_file_location("run_gnd_review_panel", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)
CredentialError = launcher.CredentialError
panel_environment = launcher.panel_environment


def _write(home: Path, text: str, *, mode: int = 0o600) -> Path:
    directory = home / ".codex"
    directory.mkdir()
    path = directory / ".env"
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)
    return path


def test_aliases_are_imported_from_the_owner_only_codex_env(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "QWEN_API_KEY_2='openrouter-secret'\nZ_API_KEY=glm-secret\n",
    )

    environment, provenance = panel_environment({}, home=tmp_path)

    assert environment["OPENROUTER_API_KEY"] == "openrouter-secret"
    assert environment["ZAI_API_KEY"] == "glm-secret"
    assert provenance == {
        "OPENROUTER_API_KEY": "QWEN_API_KEY_2",
        "ZAI_API_KEY": "Z_API_KEY",
    }


def test_parent_environment_wins_without_reading_the_file(tmp_path: Path) -> None:
    environment, provenance = panel_environment(
        {"OPENROUTER_API_KEY": "parent-qwen", "ZAI_API_KEY": "parent-glm"},
        home=tmp_path,
    )

    assert environment["OPENROUTER_API_KEY"] == "parent-qwen"
    assert environment["ZAI_API_KEY"] == "parent-glm"
    assert set(provenance.values()) == {"parent environment"}


def test_unrelated_names_and_shell_syntax_are_never_executed(tmp_path: Path) -> None:
    marker = tmp_path / "executed"
    _write(
        tmp_path,
        "QWEN_API_KEY_2=$(touch "
        + str(marker)
        + ")\nZ_API_KEY=z-secret\nANTHROPIC_API_KEY=do-not-import\n",
    )

    environment, _ = panel_environment({}, home=tmp_path)

    assert environment["OPENROUTER_API_KEY"].startswith("$(touch ")
    assert environment["ZAI_API_KEY"] == "z-secret"
    assert "ANTHROPIC_API_KEY" not in environment
    assert not marker.exists()


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("QWEN_API_KEY_2=q\n", "ZAI_API_KEY"),
        ("OPENROUTER_API_KEY=q\nOPENROUTER_API_KEY=q\nZAI_API_KEY=z\n", "repeats"),
    ],
)
def test_incomplete_or_ambiguous_files_fail_closed(tmp_path: Path, text: str, message: str) -> None:
    _write(tmp_path, text)
    with pytest.raises(CredentialError, match=message):
        panel_environment({}, home=tmp_path)


def test_exact_name_wins_over_legacy_alias(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "OPENROUTER_API_KEY=current\nQWEN_API_KEY_2=legacy\nZAI_API_KEY=z\n",
    )
    environment, provenance = panel_environment({}, home=tmp_path)
    assert environment["OPENROUTER_API_KEY"] == "current"
    assert provenance["OPENROUTER_API_KEY"] == "OPENROUTER_API_KEY"


def test_permissive_or_symlinked_file_is_refused(tmp_path: Path) -> None:
    path = _write(tmp_path, "OPENROUTER_API_KEY=q\nZAI_API_KEY=z\n", mode=0o644)
    with pytest.raises(CredentialError, match="mode 0600"):
        panel_environment({}, home=tmp_path)

    path.unlink()
    target = tmp_path / "target.env"
    target.write_text("OPENROUTER_API_KEY=q\nZAI_API_KEY=z\n", encoding="utf-8")
    target.chmod(0o600)
    os.symlink(target, path)
    with pytest.raises(CredentialError, match="unavailable"):
        panel_environment({}, home=tmp_path)


@pytest.mark.parametrize("code", [401, 403, 429, 500])
def test_provider_rejection_stops_before_launch_and_hides_response(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], code: int
) -> None:
    secret = "test-secret-never-print"
    monkeypatch.setattr(
        launcher,
        "panel_environment",
        lambda parent: (
            {"OPENROUTER_API_KEY": secret, "ZAI_API_KEY": "z"},
            {"OPENROUTER_API_KEY": "QWEN_API_KEY_2", "ZAI_API_KEY": "ZAI_API_KEY"},
        ),
    )
    calls = []

    def request(req, timeout):
        calls.append(req)
        assert req.full_url == "https://openrouter.ai/api/v1/key"
        assert req.get_header("Authorization") == "Bearer " + secret
        assert timeout == 10
        raise urllib.error.HTTPError(req.full_url, code, secret, {}, io.BytesIO(secret.encode()))

    monkeypatch.setattr(
        launcher.urllib.request,
        "build_opener",
        lambda *handlers: SimpleNamespace(open=request),
    )
    monkeypatch.setattr(launcher.os, "execve", lambda *args: pytest.fail("panel launched"))
    assert launcher.main(["request.json", "--out", "run"]) == 78
    output = capsys.readouterr()
    assert f"HTTP {code}" in output.err
    assert secret not in output.out + output.err
    assert len(calls) == 1  # No hidden retry.


def test_network_timeout_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    def request(*args, **kwargs):
        raise TimeoutError("sensitive transport details")

    monkeypatch.setattr(
        launcher.urllib.request,
        "build_opener",
        lambda *handlers: SimpleNamespace(open=request),
    )
    with pytest.raises(CredentialError, match=r"could not complete \(TimeoutError\)") as exc:
        launcher.check_openrouter_auth({"OPENROUTER_API_KEY": "fake"})
    assert "sensitive" not in str(exc.value)


def test_successful_provider_check_never_reads_private_key_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = SimpleNamespace(status=200)
    monkeypatch.setattr(
        launcher.urllib.request,
        "build_opener",
        lambda *handlers: SimpleNamespace(open=lambda *a, **kw: nullcontext(response)),
    )
    launcher.check_openrouter_auth({"OPENROUTER_API_KEY": "fake"})


def test_auth_redirect_is_not_followed() -> None:
    assert (
        launcher._NoRedirect().redirect_request(
            None, None, 302, "Found", {}, "https://unrelated.example/"
        )
        is None
    )


@pytest.mark.parametrize("light", [False, True])
def test_authenticated_launch_preserves_selected_effort_and_credentials(
    monkeypatch: pytest.MonkeyPatch, light: bool
) -> None:
    environment = {"OPENROUTER_API_KEY": "fake", "ZAI_API_KEY": "fake-z"}
    monkeypatch.setattr(
        launcher,
        "panel_environment",
        lambda parent: (environment, dict.fromkeys(environment, "parent environment")),
    )
    events = []
    monkeypatch.setattr(launcher, "check_openrouter_auth", lambda env: events.append("auth"))
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/usr/bin/uv")

    def execute(path, argv, env):
        assert events == ["auth"]
        assert argv == [path, "run", "gnd", "review", "panel-light" if light else "panel", *args]
        assert env is environment
        raise SystemExit(0)

    monkeypatch.setattr(launcher.os, "execve", execute)
    args = ["request.json", "--out", "run"]
    if light:
        args += ["--effort", "high"]
    with pytest.raises(SystemExit) as exc:
        launcher.main((["--light"] if light else []) + args)
    assert exc.value.code == 0


def test_missing_keys_refuse_without_network_or_repo_env(tmp_path, monkeypatch, capsys):
    repo = tmp_path / 'repo'
    repo.mkdir()
    marker = repo / 'executed'
    (repo / '.env').write_text('OPENROUTER_API_KEY=$(touch executed)\nZAI_API_KEY=private-test-value\n')
    monkeypatch.chdir(repo)
    monkeypatch.setattr(launcher.os, 'environ', {})
    monkeypatch.setattr(launcher.Path, 'home', lambda: tmp_path / 'unconfigured-home')
    monkeypatch.setattr(launcher, 'check_openrouter_auth', lambda env: pytest.fail('network before credential refusal'))
    assert launcher.main(['request.json', '--out', 'run']) == 78
    output = capsys.readouterr()
    assert 'private-test-value' not in output.out + output.err
    assert not marker.exists()


@pytest.mark.parametrize(('args', 'exit_code'), [(['--check-credentials'], 0), ([], 64)])
def test_name_check_and_usage_do_not_call_provider(monkeypatch, capsys, args, exit_code):
    monkeypatch.setattr(launcher.os, 'environ', {'OPENROUTER_API_KEY': 'synthetic-q', 'ZAI_API_KEY': 'synthetic-z'})
    monkeypatch.setattr(launcher, 'check_openrouter_auth', lambda env: pytest.fail('unexpected network'))
    assert launcher.main(args) == exit_code
    output = capsys.readouterr()
    assert 'synthetic-q' not in output.out + output.err
    assert 'synthetic-z' not in output.out + output.err


@pytest.mark.parametrize('text', ['OPENROUTER_API_KEY="unfinished\n', 'not-an-assignment', '1BAD=q\n', 'OPENROUTER_API_KEY=123\nOPENROUTER_API_KEY=q\n'])
def test_malformed_trusted_text_refuses(tmp_path, text):
    _write(tmp_path, text)
    with pytest.raises(CredentialError):
        panel_environment({}, home=tmp_path)


def test_oversized_and_invalid_utf8_trusted_file_refuse(tmp_path):
    path = _write(tmp_path, 'x' * (launcher.MAX_CREDENTIAL_FILE_BYTES + 1))
    with pytest.raises(CredentialError, match='64 KiB'):
        panel_environment({}, home=tmp_path)
    path.write_bytes(b'\xff')
    with pytest.raises(CredentialError, match='UTF-8'):
        panel_environment({}, home=tmp_path)


def test_non_regular_trusted_file_refuses(tmp_path):
    directory = tmp_path / '.codex'
    directory.mkdir()
    (directory / '.env').mkdir(mode=0o700)
    with pytest.raises(CredentialError, match='regular file'):
        panel_environment({}, home=tmp_path)


def test_repository_env_is_never_opened(tmp_path, monkeypatch):
    import builtins
    repo = tmp_path / 'repo'
    repo.mkdir()
    blocked = repo / '.env'
    blocked.write_text('OPENROUTER_API_KEY=synthetic-q\nZAI_API_KEY=synthetic-z\n')
    home = tmp_path / 'home'
    home.mkdir()
    _write(home, 'OPENROUTER_API_KEY=synthetic-q\nZAI_API_KEY=synthetic-z\n')
    monkeypatch.chdir(repo)
    for module, name in [(builtins, 'open'), (io, 'open'), (launcher.os, 'open')]:
        original = getattr(module, name)
        def guarded(path, *args, _original=original, **kwargs):
            if not isinstance(path, int):
                assert Path(path).resolve() != blocked.resolve(), 'repository .env was opened'
            return _original(path, *args, **kwargs)
        monkeypatch.setattr(module, name, guarded)
    environment, _ = panel_environment({}, home=home)
    assert environment['OPENROUTER_API_KEY'] == 'synthetic-q'
    # Populated parent must also avoid a repository-file read.
    assert panel_environment(environment, home=home)[0] == environment


def test_production_opener_installs_the_no_redirect_handler(monkeypatch):
    build = launcher.urllib.request.build_opener
    def guarded_builder(*handlers):
        actual = build(*handlers)
        redirects = [h for h in actual.handlers if isinstance(h, urllib.request.HTTPRedirectHandler)]
        assert len(redirects) == 1
        assert isinstance(redirects[0], launcher._NoRedirect), 'default redirect handler could forward credentials'
        return SimpleNamespace(open=lambda request, timeout: nullcontext(SimpleNamespace(status=200)))
    monkeypatch.setattr(launcher.urllib.request, 'build_opener', guarded_builder)
    launcher.check_openrouter_auth({'OPENROUTER_API_KEY': 'synthetic-q'})


def test_foreign_owned_trusted_file_refuses(tmp_path, monkeypatch):
    _write(tmp_path, 'OPENROUTER_API_KEY=synthetic-q\nZAI_API_KEY=synthetic-z\n')
    real = launcher.os.fstat
    def foreign(descriptor):
        info = real(descriptor)
        return SimpleNamespace(st_mode=info.st_mode, st_uid=launcher.os.getuid() + 1, st_size=info.st_size)
    monkeypatch.setattr(launcher.os, 'fstat', foreign)
    with pytest.raises(CredentialError, match='owned by the current user'):
        panel_environment({}, home=tmp_path)
