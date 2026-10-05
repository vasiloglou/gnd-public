"""RF1 instruments: golden manifest, inventory, mutation table, normalizer and the
rf1_pins.py tool (spec 6.2, 6.7, 6.9, 6.10 and 8.3)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from support.rf1_pins import (
    GOLDENS,
    MINORS,
    PINS_ROOT,
    NormalizationError,
    normalize_json_text,
    normalize_tree,
    sha256_hex,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PINS_ROOT / "goldens.sha256"
# The manifest's own digest: changing any golden edits this line too (SM1).
MANIFEST_SHA256 = "f9e5cd02a08a6b5d788791dad73a2d00e09414299f39a8a5efc93922d9fccf8a"

_SPEC = importlib.util.spec_from_file_location("rf1_pins_tool", ROOT / "tools" / "rf1_pins.py")
tool = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("rf1_pins_tool", tool)
_SPEC.loader.exec_module(tool)


# --- T-GOLD-MANIFEST ---------------------------------------------------------


def check_manifest(goldens: Path, manifest: Path) -> None:
    listed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, _, relative = line.partition("  ")
        assert re.fullmatch(r"[0-9a-f]{64}", digest) and relative, f"malformed manifest line {line!r}"
        listed[relative] = digest
    actual = {
        path.relative_to(goldens).as_posix(): sha256_hex(path.read_bytes())
        for path in sorted(goldens.rglob("*"))
        if path.is_file()
    }
    assert sorted(listed) == sorted(actual), "manifest and golden file set differ"
    changed = sorted(name for name in actual if actual[name] != listed[name])
    assert changed == [], f"goldens changed: {changed[:10]}"


def test_golden_manifest():
    check_manifest(GOLDENS, MANIFEST)
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256


@pytest.mark.parametrize("damage", ["changed-byte", "extra-file", "missing-file"])
def test_golden_manifest_negative(tmp_path, damage):
    goldens = tmp_path / "goldens"
    shutil.copytree(GOLDENS / "cli", goldens / "cli")
    manifest = tmp_path / "goldens.sha256"
    manifest.write_text(
        "".join(f"{sha256_hex(p.read_bytes())}  {p.relative_to(goldens).as_posix()}\n" for p in sorted(goldens.rglob("*.json")))
    )
    check_manifest(goldens, manifest)
    target = goldens / "cli" / "tree.json"
    if damage == "changed-byte":
        target.write_bytes(target.read_bytes().replace(b"gnd", b"gnD", 1))
    elif damage == "extra-file":
        (goldens / "cli" / "extra.json").write_text("{}\n")
    else:
        target.unlink()
    with pytest.raises(AssertionError):
        check_manifest(goldens, manifest)


def test_golden_versions():
    """T-GOLD-VERSIONS: every interpreter-keyed golden has exactly the three variants."""
    keyed: dict[str, set[str]] = {}
    for path in GOLDENS.rglob("*.json"):
        match = re.fullmatch(r"(.*)\.(py3\d+)\.json", path.relative_to(GOLDENS).as_posix())
        if match:
            keyed.setdefault(match.group(1), set()).add(match.group(2))
            assert not (GOLDENS / f"{match.group(1)}.json").exists(), f"{match.group(1)} is both plain and keyed"
    assert keyed, "the measured capture found interpreter-dependent goldens; their keys must exist"
    assert {key: variants for key, variants in keyed.items() if variants != set(MINORS)} == {}


# --- T-INV -------------------------------------------------------------------


def _collect(files: list[str]) -> set[str]:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *files],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 0, completed.stdout[-3000:]
    return {line.strip() for line in completed.stdout.splitlines() if "::" in line}


def _matches(reference: str, collected: set[str]) -> bool:
    return reference in collected or any(node.startswith(reference) for node in collected)


def test_inventory():
    inventory = json.loads((PINS_ROOT / "inventory.json").read_text())
    assert inventory["schema_version"] == 1
    rows = inventory["surfaces"]
    for row in rows:
        assert row["status"] in {"pinned", "existing", "owed"}
        assert row["phase"] in {"RF2", "RF3", "RF4", "RF5", "RF6", "RF8"}
        if row["status"] == "owed":
            assert row["owed_by"] in {"RF2", "RF3", "RF4", "RF5", "RF6", "RF8"} and not row["rf1_nodes"]
        elif row["status"] == "pinned":
            assert row["rf1_nodes"] and row["owed_by"] is None
        else:
            assert row["existing_nodes"] and not row["rf1_nodes"] and row["owed_by"] is None
    references = [ref for row in rows for ref in row["rf1_nodes"] + row["existing_nodes"]]
    files = sorted({ref.split("::", 1)[0] for ref in references} | set(tool.PIN_FILES) | {"tests/test_rf1_layering.py"})
    collected = _collect(files)
    assert [ref for ref in references if not _matches(ref, collected)] == []
    pins = {node for node in collected if node.split("::", 1)[0] in set(tool.PIN_FILES) | {"tests/test_rf1_layering.py"}}
    meta = {"tests/test_rf1_helper_pins.py::test_helper_coverage", "tests/test_rf1_helper_pins.py::test_case_manifest_builds",
            "tests/test_rf1_cli_pins.py::test_cli_coverage", "tests/test_rf1_layering.py::test_layer_scope",
            "tests/test_rf1_layering.py::test_layer_ratchet_detects_a_new_pair"}
    rf1_refs = [ref for row in rows for ref in row["rf1_nodes"]]
    unmapped = sorted(node for node in pins - meta if not any(node.startswith(ref) for ref in rf1_refs))
    assert unmapped == []


# --- mutation table (D3) -----------------------------------------------------


SOLE_PREFIXES = (
    "tests/test_rf1_helper_pins.py::test_helper[",
    "tests/test_rf1_semantic_pins.py::test_check[",
    "tests/test_rf1_session_pins.py::test_session_",
)


def test_mutation_table_rows_of_their_own():
    table = tool.load_table(ROOT / tool.DEFAULT_TABLE)
    tool.validate_rows(ROOT, tool.DEFAULT_SOURCE, table["rows"])
    named = {node for row in table["rows"] for node in row["expect_red"]}
    sole = {row["expect_red"][0] for row in table["rows"] if len(row["expect_red"]) == 1}
    required = sorted(node for node in named if node.startswith(SOLE_PREFIXES))
    assert required and [node for node in required if node not in sole] == []


# --- T-NORM ------------------------------------------------------------------


def test_norm_tokens_and_clock_placeholders():
    files = {"a.json": b'{"cwd":"/tmp/x/root/a","elapsed_seconds":1.25,"started_monotonic":3.5}'}
    out = normalize_tree(files, tokens={"/tmp/x/root": "<root>"}, clock_injected=False)
    assert out["a.json"]["text"] == '{"cwd":"<root>/a","elapsed_seconds":"<seconds>","started_monotonic":"<monotonic>"}'


def test_norm_digest_replaced_only_when_it_matches_a_file():
    leaf = b"leaf\n"
    files = {"leaf.txt": leaf, "index.json": json.dumps({"leaf": sha256_hex(leaf)}).encode()}
    out = normalize_tree(files, tokens={})
    assert out["index.json"]["text"] == '{"leaf": "<sha256:leaf.txt>"}'


def test_norm_digest_left_when_it_matches_nothing():
    stray = "a" * 64
    out = normalize_tree({"index.json": json.dumps({"x": stray}).encode()}, tokens={})
    assert stray in out["index.json"]["text"]


def test_norm_forbidden_token_fails():
    with pytest.raises(NormalizationError):
        normalize_tree({"a.json": b'{"dir":".staging-123"}'}, tokens={}, forbidden=[".staging-123"])


def test_norm_non_json_fails_with_a_named_assertion():
    with pytest.raises(NormalizationError, match="not a JSON document"):
        normalize_json_text("{not json", tokens={})


def test_norm_keyed_prompt_nonce_and_inputs():
    policy = b'{"policy":1}'
    text = json.dumps({"prompt_sha256": "b" * 64, "nonce": "c" * 64, "policy_sha256": sha256_hex(policy),
                       "argv": ["<prompt:sha256=" + "d" * 64 + ">"], "result_sha256": {"r.xml": "e" * 64}})
    out = normalize_tree({"a.json": text.encode()}, tokens={}, inputs={"policy": policy})
    assert json.loads(out["a.json"]["text"]) == {
        "prompt_sha256": "<prompt-sha256>", "nonce": "<nonce>", "policy_sha256": "<sha256:input:policy>",
        "argv": ["<prompt:sha256>"], "result_sha256": {"r.xml": "<junit-sha256>"},
    }


# --- T-TOOL ------------------------------------------------------------------


MINI_TEST = """
from minipkg.core import value


def test_value():
    assert value() == 1
"""


def _mini(tmp_path: Path, rows: list[dict] | None = None, exempt: list[dict] | None = None, raw: bytes | None = None) -> Path:
    root = tmp_path / "mini"
    (root / "src" / "minipkg").mkdir(parents=True)
    (root / "src" / "minipkg" / "__init__.py").write_text("")
    (root / "src" / "minipkg" / "core.py").write_text("def value():\n    return 1\n")
    (root / "tests").mkdir()
    (root / "tests" / "test_mini.py").write_text(MINI_TEST)
    table = root / "mutations.json"
    if raw is not None:
        table.write_bytes(raw)
    else:
        if rows is None:
            rows = [{"id": "kill", "file": "src/minipkg/core.py", "old": "return 1", "new": "return 2",
                     "expect_red": ["tests/test_mini.py::test_value"]}]
        table.write_text(json.dumps({"schema_version": 1, "rows": rows, "exempt": exempt or []}))
    return root


def _mutate(root: Path, out: Path, *extra: str) -> int:
    return tool.main(["mutate", "--root", str(root), "--table", "mutations.json", "--source", "src/minipkg",
                      "--tests", "tests/test_mini.py", "--out", str(out), "--jobs", "1", *extra])


def test_tool_kills_a_row(tmp_path):
    root = _mini(tmp_path)
    assert _mutate(root, tmp_path / "out") == 0
    report = json.loads((tmp_path / "out" / "mutation-report.json").read_text())
    assert report["rows"]["kill"]["status"] == "killed" and report["killed"] == 1


def test_tool_existing_out_wins_over_invalid_table(tmp_path):
    root = _mini(tmp_path, raw=b"not json")
    (tmp_path / "out").mkdir()
    assert _mutate(root, tmp_path / "out") == 11


@pytest.mark.parametrize(
    "raw",
    [
        b"[]",
        b'{"schema_version":1,"schema_version":1,"rows":[],"exempt":[]}',
        b'{"schema_version":NaN,"rows":[],"exempt":[]}',
        b" " * (1024 * 1024 + 1),
        json.dumps({"schema_version": 1, "exempt": [], "rows": [{"id": "x", "file": "src/minipkg/core.py", "old": "absent", "new": "y",
                                                                  "expect_red": ["tests/test_mini.py::test_value"]}]}).encode(),
        json.dumps({"schema_version": 1, "exempt": [], "rows": [{"id": "x", "file": "src/minipkg/core.py", "old": "e", "new": "y",
                                                                  "expect_red": ["tests/test_mini.py::test_value"]}]}).encode(),
        json.dumps({"schema_version": 1, "exempt": [], "rows": [{"id": "x", "file": "src/minipkg/core.py", "old": "return 1", "new": "return 2",
                                                                  "expect_red": ["tests/test_mini.py::test_absent"]}]}).encode(),
    ],
    ids=["non-object", "duplicate-key", "nan", "over-cap", "absent-snippet", "non-unique-snippet", "unknown-node"],
)
def test_tool_hostile_tables_exit_3(tmp_path, raw, capsys):
    root = _mini(tmp_path, raw=raw)
    assert _mutate(root, tmp_path / "out") == 3
    assert "Traceback" not in capsys.readouterr().err


def test_tool_uncovered_node_exits_3(tmp_path):
    root = _mini(tmp_path)
    (root / "tests" / "test_mini.py").write_text(MINI_TEST + "\n\ndef test_other():\n    assert True\n")
    assert _mutate(root, tmp_path / "out") == 3


def test_tool_red_control_exits_1(tmp_path):
    root = _mini(tmp_path)
    (root / "src" / "minipkg" / "core.py").write_text("def value():\n    return 1  # control\n")
    (root / "tests" / "test_mini.py").write_text(MINI_TEST.replace("== 1", "== 3"))
    assert _mutate(root, tmp_path / "out") == 1
    assert "not passing: 1" in (tmp_path / "out" / "control.txt").read_text()


def test_tool_surviving_row_exits_1(tmp_path):
    rows = [{"id": "noop", "file": "src/minipkg/core.py", "old": "    return 1\n", "new": "    return 1  # rf1\n",
             "expect_red": ["tests/test_mini.py::test_value"]}]
    root = _mini(tmp_path, rows=rows)
    assert _mutate(root, tmp_path / "out") == 1
    report = json.loads((tmp_path / "out" / "mutation-report.json").read_text())
    assert report["rows"]["noop"]["status"] == "survived"


def test_tool_timed_out_row_exits_1(tmp_path):
    rows = [{"id": "hang", "file": "src/minipkg/core.py", "old": "    return 1\n", "new": "    while True:\n        pass\n",
             "expect_red": ["tests/test_mini.py::test_value"]}]
    root = _mini(tmp_path, rows=rows)
    assert _mutate(root, tmp_path / "out", "--timeout", "3") == 1
    report = json.loads((tmp_path / "out" / "mutation-report.json").read_text())
    assert report["rows"]["hang"]["status"] == "timed-out"


def test_tool_capture_refuses_existing_out(tmp_path):
    (tmp_path / "cap").mkdir()
    assert tool.main(["capture", "--out", str(tmp_path / "cap")]) == 11
    assert list((tmp_path / "cap").iterdir()) == []


def test_tool_merge_keys_by_interpreter(tmp_path):
    for tag, text in zip(MINORS, ("a", "a", "b"), strict=True):
        (tmp_path / tag / "lane").mkdir(parents=True)
        (tmp_path / tag / "lane" / "same.json").write_text("{}\n")
        (tmp_path / tag / "lane" / "diff.json").write_text(json.dumps(text) + "\n")
    out = tmp_path / "merged" / "goldens"
    assert tool.main(["merge", "--out", str(out), *(str(tmp_path / tag) for tag in MINORS)]) == 0
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob("*.json")) == [
        "lane/diff.py311.json", "lane/diff.py313.json", "lane/diff.py314.json", "lane/same.json"]
    check_manifest(out, out.parent / "goldens.sha256")
