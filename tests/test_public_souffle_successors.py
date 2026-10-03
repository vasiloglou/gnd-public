"""Local fake-tool output, work and publication controls; no native run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gnd.export import souffle_runtime as runtime
from gnd.export.souffle_io import export_souffle
from tests.support.v71_souffle_cases import fake_tool, load, source, write


def test_exec_format_is_native_failure(tmp_path):
    tool = tmp_path / "foreign"
    tool.write_bytes(b"invalid executable")
    tool.chmod(0o700)
    bundle = Path("tests/fixtures/v71/phase6/dispatch/golden")
    result = runtime.run_souffle(bundle, executable=tool)
    assert (result["exit_code"], result["reason"]) == (4, "tool-error")


def test_non_utf8_output_is_native_failure(tmp_path):
    tool = fake_tool(tmp_path, "dispatch")
    text = tool.read_text()
    text = text.replace("(out/name).write_text(data)", "(out/name).write_bytes(b'\\xff')")
    tool.write_text(text)
    result = runtime.run_souffle(Path("tests/fixtures/v71/phase6/dispatch/golden"), executable=tool)
    assert (result["exit_code"], result["reason"]) == (4, "output-invalid")
    tool = fake_tool(tmp_path, "dispatch")
    tool.write_text(
        tool.read_text().replace("print(VERSION,end='')", "sys.stdout.buffer.write(b'\\xff')")
    )
    result = runtime.run_souffle(Path("tests/fixtures/v71/phase6/dispatch/golden"), executable=tool)
    assert (result["exit_code"], result["reason"]) == (4, "tool-version-unsupported")


def test_count_cannot_authorize_unrelated_invented_integer(tmp_path):
    src = source("dispatch", "count", tmp_path)
    model = load(src / "model.orm.json")
    role = {"object_type": "dispatch_integer", "role_name": "value"}
    model["fact_types"] += [
        {"id": "independent_int", "reading": "{Count} is given", "roles": [role]},
        {
            "id": "copied_int",
            "reading": "{Count} is copied",
            "roles": [role],
            "derivation": "derived",
            "derivation_rule": {
                "body": [{"fact_type": "independent_int", "bind": {"value": "$v"}}],
                "head": {"value": "$v"},
            },
        },
    ]
    pop = load(src / "candidate.pop.json")
    pop["population"]["covers"].append("independent_int")
    pop["facts"]["independent_int"] = [{"value": 0}]
    write(src / "model.orm.json", model)
    write(src / "candidate.pop.json", pop)
    bundle = tmp_path / "bundle"
    assert (
        export_souffle(
            src / "model.orm.json",
            src / "candidate.pop.json",
            reference_root=src,
            out=bundle,
            raw=True,
        ).exit_code
        == 0
    )
    tool = fake_tool(tmp_path, "dispatch", "count")
    text = tool.read_text()
    text = text.replace("VERSION=", "FILES['r5.csv']='n:2:1\\n'\nVERSION=", 1)
    tool.write_text(text)
    result = runtime.run_souffle(bundle, executable=tool)
    assert (result["exit_code"], result["reason"]) == (4, "output-invalid")


def test_large_distinct_join_count_is_exact(tmp_path):
    import hashlib

    from gnd.export.souffle_types import DEFAULT_LIMITS

    src = source("dispatch", "count-join", tmp_path)
    model = load(src / "model.orm.json")
    ref = load(src / "references/links.pop.json")
    ref["facts"]["dispatch_leg"] = [{"source": f"S{i}", "target": f"T{i}"} for i in range(320)]
    write(src / "references/links.pop.json", ref)
    model["reference_populations"][0]["sha256"] = hashlib.sha256(
        (src / "references/links.pop.json").read_bytes()
    ).hexdigest()
    c = next(f for f in model["fact_types"] if f["id"] == "dispatch_count")["derivation_rule"]
    c["body"] = [
        {"fact_type": "dispatch_request", "bind": {"source": "$x", "target": "$y"}},
        {"fact_type": "dispatch_leg", "bind": {"source": "$a", "target": "$b"}},
        {"fact_type": "dispatch_leg", "bind": {"source": "$c", "target": "$d"}},
    ]
    c["aggregate"].update(over=["$a", "$b", "$c"], of="$d")
    write(src / "model.orm.json", model)
    rendered = export_souffle(
        src / "model.orm.json", src / "candidate.pop.json", reference_root=src
    )
    assert rendered.exit_code == 0
    outputs = {"r2.csv": b"", "r3.csv": b"s:57482d41\tn:102400:1\n", "r4.csv": b""}
    assert runtime.extensions(rendered, outputs, DEFAULT_LIMITS)["dispatch_count"][0][1] == {
        "primitive": "Integer",
        "value": 102400,
    }


def test_nested_foreign_output_is_bounded(tmp_path):
    from dataclasses import replace

    from gnd.export.souffle_types import DEFAULT_LIMITS

    tool = fake_tool(tmp_path, "dispatch")
    text = tool.read_text().replace(
        "for name,data in FILES.items():",
        "(out/'nested').mkdir()\n(out/'nested'/'payload').write_bytes(b'x'*2048)\ntime.sleep(.5)\nfor name,data in FILES.items():",
    )
    tool.write_text(text)
    result = runtime.run_souffle(
        Path("tests/fixtures/v71/phase6/dispatch/golden"),
        executable=tool,
        limits=replace(DEFAULT_LIMITS, native_output_bytes=512),
    )
    assert (result["exit_code"], result["reason"]) == (4, "output-limit")


def test_verifier_honors_lower_shape_limits():
    from dataclasses import replace

    from gnd.export.souffle_io import verify_souffle_bundle
    from gnd.export.souffle_types import DEFAULT_LIMITS

    for key, value in [
        ("fact_types", 1),
        ("input_rows", 1),
        ("roles", 1),
        ("clauses", 1),
        ("atom_sites", 2),
        ("encoded_cells", 1),
        ("scalar_bytes", 1),
        ("container_depth", 1),
    ]:
        result = verify_souffle_bundle(
            Path("tests/fixtures/v71/phase6/dispatch/golden"),
            limits=replace(DEFAULT_LIMITS, **{key: value}),
        )
        assert (result.exit_code, result.reason) == (3, "input-invalid"), key


def test_every_native_proof_document_is_depth_checked(tmp_path, monkeypatch):
    import copy
    import json

    bundle = Path("tests/fixtures/v71/phase6/dispatch/golden")
    document = load(Path("tests/fixtures/v71/phase6/dispatch/native-proof.json"))
    nested = []
    for _ in range(70):
        nested = [nested]
    document["rules"] = nested
    stdout = (json.dumps(document) + json.dumps(document)).encode()
    monkeypatch.setattr(runtime, "invoke", lambda *a, **k: ({}, stdout, {}, 0))
    targets = load(Path("tests/fixtures/v71/phase6/dispatch/targets.json"))
    targets["targets"] += copy.deepcopy(targets["targets"])
    result = runtime.native_witness(bundle, targets, executable=fake_tool(tmp_path, "dispatch"))
    assert (result.exit_code, result.reason) == (3, "input-invalid")


def test_combined_native_certificate_replays_under_one_graph_budget(tmp_path, monkeypatch):
    import copy
    import json
    from dataclasses import replace

    from gnd.witness.kernel import replay_witness
    from gnd.witness.types import DEFAULT_LIMITS

    targets = load(Path("tests/fixtures/v71/phase6/dispatch/targets.json"))
    targets["targets"] += copy.deepcopy(targets["targets"])
    proof = load(Path("tests/fixtures/v71/phase6/dispatch/native-proof.json"))
    tool = fake_tool(tmp_path, "dispatch", proof=json.dumps(proof) + json.dumps(proof))

    def bounded(*args, **kwargs):
        return replay_witness(*args, **kwargs, limits=replace(DEFAULT_LIMITS, nodes=10))

    monkeypatch.setattr(runtime, "replay_witness", bounded)
    result = runtime.native_witness(
        Path("tests/fixtures/v71/phase6/dispatch/golden"), targets, executable=tool
    )
    assert (result.exit_code, result.reason, result.certificate) == (4, "work-limit", None)


def test_tool_cannot_replace_itself_with_a_fifo_during_version_query(tmp_path):
    import subprocess
    import sys

    tool = fake_tool(tmp_path, "dispatch")
    text = tool.read_text().replace(
        "print(VERSION,end='');sys.exit(0)",
        "__import__('os').unlink(__file__);__import__('os').mkfifo(__file__);print(VERSION,end='');sys.exit(0)",
    )
    tool.write_text(text)
    argv = [
        sys.executable,
        "-m",
        "gnd",
        "export",
        "souffle-run",
        "tests/fixtures/v71/phase6/dispatch/golden",
        "--executable",
        str(tool),
        "--json",
    ]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=3, check=False)
    import json

    assert (result.returncode, json.loads(result.stdout)["reason"]) == (4, "tool-error")


def test_exited_group_cleanup_cannot_replace_output_refusal(tmp_path, monkeypatch):
    from dataclasses import replace

    from gnd.export.souffle_types import DEFAULT_LIMITS
    from tests.support.v71_souffle_cases import csv_files

    tool = fake_tool(tmp_path, "dispatch")

    def gone(*args):
        raise PermissionError("exited process group cleanup race")

    monkeypatch.setattr(runtime.os, "killpg", gone)
    cap = (
        sum(len(v.encode()) for v in csv_files("dispatch", "base").values())
        + len(b"Version: 2.5\nWord size: 64 bits\n")
        - 1
    )
    result = runtime.run_souffle(
        Path("tests/fixtures/v71/phase6/dispatch/golden"),
        executable=tool,
        limits=replace(DEFAULT_LIMITS, native_output_bytes=cap),
    )
    assert (result["exit_code"], result["reason"]) == (4, "output-limit")
    tool.chmod(0o4700)
    result = runtime.run_souffle(Path("tests/fixtures/v71/phase6/dispatch/golden"), executable=tool)
    assert (result["exit_code"], result["reason"]) == (4, "tool-error")


