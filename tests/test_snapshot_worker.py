import json
import subprocess
import sys

from test_checked_extensions import fixture


def launch():
    return subprocess.Popen([sys.executable, "-m", "gnd.snapshot_worker"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def send(process, message):
    wire = message if isinstance(message, bytes) else json.dumps(message).encode()
    process.stdin.write(wire + b"\n")
    process.stdin.flush()
    return json.loads(process.stdout.readline())


def test_persistent_worker_isolation_and_model_replacement(tmp_path):
    from gnd import api
    path, pop = fixture(tmp_path)
    request = {"version": 1, "id": "first", "model": str(path), "population": json.loads(pop.read_text())}
    process = launch()
    try:
        first = send(process, request)
        assert first["status"] == "evaluated" and first["model_reused"] is False
        assert first["report"]["counts"] == api.check(path, pop)["counts"]
        repeat = send(process, {**request, "id": "second"})
        assert repeat["id"] == "second" and repeat["model_reused"]
        for msg, code in ((b"{", "invalid-input"), ({**request, "version": 3}, "unsupported-version"),
                          ({**request, "population": {"bad": "private-value"}}, "invalid-input"),
                          (b" " * (4 * 1024 * 1024 + 20), "request-too-large")):
            error = send(process, msg)
            assert error["error"] == code and "private-value" not in str(error)
        assert send(process, request)["report"] == first["report"]
        content = path.read_bytes()
        path.write_bytes(b"invalid: model")
        assert send(process, request)["status"] == "error"
        path.write_bytes(content + b"\n")
        after = send(process, request)
        assert not after["model_reused"] and after["model_sha256"] != first["model_sha256"]
        assert after["report"]["counts"] == api.check(path, pop)["counts"]
        process.kill()
    finally:
        process.kill()
        process.wait(timeout=10)
    with launch() as restarted:
        cold = send(restarted, request)
        assert not cold["model_reused"] and cold["model_sha256"] == after["model_sha256"]
        restarted.stdin.close()


def test_distinct_populations_in_one_worker(tmp_path):
    path, pop = fixture(tmp_path, claim=[])
    init = {"version": 1, "id": "request", "model": str(path)}
    with launch() as process:
        try:
            bad = send(process, {**init, "population": json.loads(pop.read_text())})
            fixture(tmp_path, claim=["a"])
            good = send(process, {**init, "population": json.loads(pop.read_text())})
            assert bad["report"]["exit_code"] == 1 and good["report"]["exit_code"] == 0
            assert good["model_reused"]
        finally:
            process.stdin.close()


def test_worker_path_errors_alias_and_external_dependencies(tmp_path):
    path, pop = fixture(tmp_path)
    request = {"version": 1, "id": "check", "model": str(path), "population": json.loads(pop.read_text())}
    alias = tmp_path / "alias.json"
    alias.symlink_to(path)
    with launch() as process:
        try:
            assert send(process, request)["status"] == "evaluated"
            for invalid in (tmp_path / "missing", tmp_path):
                assert send(process, {**request, "model": str(invalid)})["error"] == "invalid-input"
            assert send(process, {**request, "model": str(alias)})["model_reused"]
            model = json.loads(path.read_text())
            model["includes"] = ["dependency.json"]
            path.write_text(json.dumps(model))
            assert send(process, request)["error"] == "external-model-dependencies"
        finally:
            process.stdin.close()
