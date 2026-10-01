"""RED contract for conservative, execution-free brownfield inventory (04-08).

The corpus is not illustrative prose.  Every selected entry is committed here as
base64 plus byte length and SHA-256, and every selected path has exactly one
census disposition.  A scanner that skips an input it cannot understand is more
dangerous than one that stops: the former silently turns a partial model into a
claim of complete recovery.
"""

from __future__ import annotations

import base64
import builtins
import hashlib
import importlib
import json
import os
import socket
import subprocess
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

import gnd.recovery.inventory as recovery_inventory
from gnd.recovery import (
    RecoveryInventory,
    RecoveryInventoryError,
    RootCategory,
    SelectedRoot,
    scan_recovery_scope,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "recovery.json"
CASE_IDS = (
    "recovery-mechanical-python-schema",
    "recovery-ambiguous-semantic-proposal",
    "recovery-unsupported-dynamic-mixed-frontier",
    "recovery-traversal-symlink-stale-digest",
)


def _corpus() -> dict[str, Any]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def _case(case_id: str) -> dict[str, Any]:
    return next(case for case in _corpus()["cases"] if case["case_id"] == case_id)


def _raw(blob: dict[str, Any]) -> bytes:
    return base64.b64decode(blob["bytes_base64"], validate=True)


def _materialize(case: dict[str, Any], root: Path) -> None:
    links: list[tuple[Path, str]] = []
    for blob in case["input_blobs"]:
        target = root / blob["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if blob["entry_kind"] == "symlink":
            links.append((target, blob["link_target"]))
        else:
            target.write_bytes(_raw(blob))
    for target, link_target in links:
        target.symlink_to(link_target)


def _roots(case: dict[str, Any]) -> tuple[SelectedRoot, ...]:
    return tuple(SelectedRoot.model_validate(item) for item in case["selected_roots"])


def _scan(case: dict[str, Any], root: Path, **limits: int) -> RecoveryInventory:
    _materialize(case, root)
    return scan_recovery_scope(root, _roots(case), **limits)


def _census(inventory: RecoveryInventory) -> dict[str, dict[str, Any]]:
    return {row["path"]: row for row in inventory.model_dump(mode="json")["census"]}


def _all_reference_ids(inventory: RecoveryInventory) -> set[str]:
    data = inventory.model_dump(mode="json")
    return {
        *(entry["evidence_id"] for entry in data["evidence"]),
        *(entry["proposal_id"] for entry in data["ambiguities"]),
        *(entry["frontier_id"] for entry in data["frontier"]),
        *(entry["exclusion_id"] for entry in data["scope"]["excluded_roots"]),
    }


def test_fixture_is_exactly_the_four_named_committed_byte_cases() -> None:
    corpus = _corpus()
    assert corpus["schema_version"] == 1
    assert tuple(case["case_id"] for case in corpus["cases"]) == CASE_IDS

    for case in corpus["cases"]:
        assert case["selected_paths"] == sorted(case["selected_paths"])
        assert len(case["selected_paths"]) == len(set(case["selected_paths"]))
        assert {blob["path"] for blob in case["input_blobs"]} == set(case["selected_paths"])
        for blob in case["input_blobs"]:
            raw = _raw(blob)
            assert len(raw) == blob["byte_length"], (case["case_id"], blob["path"])
            assert hashlib.sha256(raw).hexdigest() == blob["sha256"], (
                case["case_id"],
                blob["path"],
            )
            if blob["entry_kind"] == "symlink":
                assert raw.decode(blob["encoding"]) == blob["link_target"]


def test_fixture_selected_path_census_is_exactly_once_and_referentially_closed() -> None:
    for case in _corpus()["cases"]:
        expected = case["expected"]
        census_paths = [entry["path"] for entry in expected["census"]]
        assert census_paths == case["selected_paths"]
        assert len(census_paths) == len(set(census_paths))

        known_ids = {
            *(entry["evidence_id"] for entry in expected["evidence"]),
            *(entry["proposal_id"] for entry in expected["ambiguities"]),
            *(entry["frontier_id"] for entry in expected["frontier"]),
            *(entry["exclusion_id"] for entry in expected["exclusions"]),
        }
        for row in expected["census"]:
            assert row["disposition"] in {
                "parsed",
                "excluded",
                "ambiguous",
                "frontier",
            }
            assert row["reference_ids"], row
            assert set(row["reference_ids"]) <= known_ids

        evidence_ids = {entry["evidence_id"] for entry in expected["evidence"]}
        for evidence in expected["evidence"]:
            assert len(evidence["excerpt_sha256"]) == 64
            assert "excerpt" not in evidence
        for claim in [*expected["modeled_elements"], *expected["ambiguities"]]:
            assert claim["evidence_ids"], claim
            assert set(claim["evidence_ids"]) <= evidence_ids
        for claim in expected["modeled_elements"]:
            assert claim["model_pointer"].startswith("/")


def test_fixture_pins_supported_static_inputs_and_four_typed_locators() -> None:
    case = _case("recovery-mechanical-python-schema")
    assert [root["category"] for root in case["selected_roots"]] == [
        "source",
        "test",
        "docs",
        "config",
        "schema",
    ]
    assert {entry["locator"]["kind"] for entry in case["expected"]["evidence"]} == {
        "python-symbol",
        "line",
        "json-pointer",
        "yaml-path",
    }
    assert {entry["element_kind"] for entry in case["expected"]["modeled_elements"]} == {
        "object-type",
        "fact-type",
        "role",
        "constraint",
    }
    constraint = next(
        entry
        for entry in case["expected"]["modeled_elements"]
        if entry["element_kind"] == "constraint"
    )
    assert (constraint["source"], constraint["status"], constraint["modality"]) == (
        "explicit",
        "confirmed",
        "alethic",
    )


def test_fixture_ambiguity_is_one_inert_two_digest_proposal_not_an_asserted_fact() -> None:
    case = _case("recovery-ambiguous-semantic-proposal")
    marker = b"recovery-proposal: Request has Approver"
    assert all(marker in _raw(blob) for blob in case["input_blobs"])
    assert len(case["expected"]["ambiguities"]) == 1
    proposal = case["expected"]["ambiguities"][0]
    assert (proposal["source"], proposal["status"], proposal["modality"]) == (
        "llm-inferred",
        "proposed",
        "deontic",
    )
    assert len(proposal["evidence_ids"]) == 2
    assert proposal["element_id"] not in {
        entry["element_id"] for entry in case["expected"]["modeled_elements"]
    }


def test_fixture_third_row_is_the_exact_closed_false_negative_frontier() -> None:
    case = _case("recovery-unsupported-dynamic-mixed-frontier")
    assert case["selected_paths"] == [
        "src/dynamic.py",
        "src/mixed.py",
        "src/unresolved.py",
        "src/unsupported.rs",
    ]
    assert {(entry["path"], entry["reason"]) for entry in case["expected"]["frontier"]} == {
        ("src/dynamic.py", "dynamic-construct"),
        ("src/mixed.py", "mixed-language"),
        ("src/unresolved.py", "unresolved-import"),
        ("src/unsupported.rs", "unsupported-language"),
    }
    assert case["expected"]["evidence"] == []
    assert case["expected"]["modeled_elements"] == []
    assert case["expected"]["ambiguities"] == []


def test_fixture_fourth_row_combines_nested_exclusion_symlink_cycle_and_stale_bytes() -> None:
    case = _case("recovery-traversal-symlink-stale-digest")
    assert {(entry["path"], entry["reason"]) for entry in case["expected"]["frontier"]} == {
        ("src/alias.py", "symlink"),
        ("src/loop", "symlink-cycle"),
    }
    assert case["expected"]["exclusions"] == [
        {"exclusion_id": "exclusion:vendor", "path": "vendor/lib.py", "reason": "vendored"}
    ]
    mutation = case["mutations"][0]
    replacement = base64.b64decode(mutation["replacement_bytes_base64"], validate=True)
    assert len(replacement) == mutation["replacement_byte_length"]
    assert hashlib.sha256(replacement).hexdigest() == mutation["replacement_sha256"]
    assert mutation["expected_error"] == "stale-digest"


def test_every_case_names_exactly_three_canonical_outputs_without_a_self_hash() -> None:
    expected = [
        {"path": "model.orm.yaml", "digest_binding": "required"},
        {"path": "model.verbalization.txt", "digest_binding": "required"},
        {"path": "model.recovery.json", "digest_binding": "self-unbound"},
    ]
    for case in _corpus()["cases"]:
        assert case["expected"]["outputs"] == expected
        assert case["expected"]["verification_evidence"]


def test_root_categories_are_closed_and_paths_are_repository_relative() -> None:
    assert {member.value for member in RootCategory} == {
        "source",
        "test",
        "docs",
        "config",
        "schema",
    }
    with pytest.raises(ValidationError):
        SelectedRoot(category="source", path="../outside")
    with pytest.raises(ValidationError):
        SelectedRoot(category="source", path=str(REPO_ROOT.resolve()))
    with pytest.raises(ValidationError):
        SelectedRoot.model_validate({"category": "runtime", "path": "src"})


def test_mechanical_inventory_is_sorted_repeatable_and_census_closed(tmp_path: Path) -> None:
    case = _case("recovery-mechanical-python-schema")
    first = _scan(case, tmp_path / "first")
    second = _scan(case, tmp_path / "second")
    first_data = first.model_dump(mode="json")
    second_data = second.model_dump(mode="json")

    # The repository root is intentionally run-specific; all repository-relative
    # observations must otherwise be byte-identical and canonically ordered.
    first_data["scope"]["repository_root"] = "."
    second_data["scope"]["repository_root"] = "."
    assert first_data == second_data
    assert list(_census(first)) == case["selected_paths"]
    assert {row["disposition"] for row in _census(first).values()} == {"parsed"}
    assert [entry.path for entry in first.evidence] == sorted(
        entry.path for entry in first.evidence
    )
    assert {entry.locator.kind for entry in first.evidence} >= {
        "python-symbol",
        "line",
        "json-pointer",
        "yaml-path",
    }
    assert all(
        entry.sha256 in {blob["sha256"] for blob in case["input_blobs"]} for entry in first.evidence
    )
    assert all(
        set(row["reference_ids"]) <= _all_reference_ids(first) for row in _census(first).values()
    )


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_scanner_matches_every_committed_corpus_identity_and_locator(
    tmp_path: Path,
    case_id: str,
) -> None:
    case = _case(case_id)
    actual = _scan(case, tmp_path).model_dump(mode="json")
    expected = case["expected"]

    for field, identity in (
        ("evidence", "evidence_id"),
        ("ambiguities", "proposal_id"),
        ("frontier", "frontier_id"),
    ):
        actual_by_id = {entry[identity]: entry for entry in actual[field]}
        expected_by_id = {entry[identity]: entry for entry in expected[field]}
        assert set(actual_by_id) == set(expected_by_id)
        for record_id, expected_entry in expected_by_id.items():
            assert {key: actual_by_id[record_id][key] for key in expected_entry} == expected_entry

    actual_exclusions = {
        entry["exclusion_id"]: entry for entry in actual["scope"]["excluded_roots"]
    }
    expected_exclusions = {entry["exclusion_id"]: entry for entry in expected["exclusions"]}
    assert actual_exclusions == expected_exclusions
    assert actual["census"] == expected["census"]


def test_inert_marker_yields_one_evidence_backed_proposal_and_no_fact_assertion(
    tmp_path: Path,
) -> None:
    case = _case("recovery-ambiguous-semantic-proposal")
    inventory = _scan(case, tmp_path)
    assert len(inventory.ambiguities) == 1
    proposal = inventory.ambiguities[0]
    assert proposal.element_id == "fact:request-has-approver"
    assert (proposal.source, proposal.status, proposal.modality) == (
        "llm-inferred",
        "proposed",
        "deontic",
    )
    assert len(proposal.evidence_ids) == 2
    evidence_by_id = {entry.evidence_id: entry for entry in inventory.evidence}
    assert {evidence_by_id[item].sha256 for item in proposal.evidence_ids} == {
        blob["sha256"] for blob in case["input_blobs"]
    }
    assert {row["disposition"] for row in _census(inventory).values()} == {"ambiguous"}


def test_unsupported_dynamic_unresolved_and_mixed_inputs_do_not_disappear(
    tmp_path: Path,
) -> None:
    case = _case("recovery-unsupported-dynamic-mixed-frontier")
    inventory = _scan(case, tmp_path)
    assert {(item.path, item.reason) for item in inventory.frontier} == {
        (entry["path"], entry["reason"]) for entry in case["expected"]["frontier"]
    }
    assert list(_census(inventory)) == case["selected_paths"]
    assert {row["disposition"] for row in _census(inventory).values()} == {"frontier"}
    assert inventory.evidence == ()


def test_nested_file_is_parsed_but_vendor_and_symlinks_are_never_followed(
    tmp_path: Path,
) -> None:
    case = _case("recovery-traversal-symlink-stale-digest")
    inventory = _scan(case, tmp_path)
    census = _census(inventory)
    assert census["src/nested/domain.py"]["disposition"] == "parsed"
    assert census["vendor/lib.py"]["disposition"] == "excluded"
    assert census["src/alias.py"]["disposition"] == "frontier"
    assert census["src/loop"]["disposition"] == "frontier"
    assert {item.reason for item in inventory.frontier} == {"symlink", "symlink-cycle"}
    assert not any(entry.path == "src/alias.py" for entry in inventory.evidence)
    assert not any(entry.path == "vendor/lib.py" for entry in inventory.evidence)


def test_binary_parse_error_and_caps_are_frontier_not_silent_skips(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "binary.bin").write_bytes(b"\x00secret\xff")
    (source / "broken.py").write_text("class Broken(\n", encoding="utf-8")
    (source / "large.md").write_text("x" * 33, encoding="utf-8")

    inventory = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="source", path="src"),),
        max_file_bytes=32,
        max_total_bytes=128,
        max_files=8,
    )
    assert list(_census(inventory)) == [
        "src/binary.bin",
        "src/broken.py",
        "src/large.md",
    ]
    assert {(item.path, item.reason) for item in inventory.frontier} == {
        ("src/binary.bin", "binary"),
        ("src/broken.py", "parse-error"),
        ("src/large.md", "oversize"),
    }


def test_proposal_markers_cannot_hide_unsupported_dynamic_or_invalid_source(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    marker = "# recovery-proposal: Hidden relation\n"
    (source / "unsupported.rs").write_text(marker + "struct Hidden;\n", encoding="utf-8")
    (source / "dynamic.py").write_text(marker + "exec('x = 1')\n", encoding="utf-8")
    (source / "broken.py").write_text(marker + "class Broken(\n", encoding="utf-8")

    inventory = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="source", path="src"),),
    )
    assert inventory.ambiguities == ()
    assert {(item.path, item.reason) for item in inventory.frontier} == {
        ("src/unsupported.rs", "unsupported-language"),
        ("src/dynamic.py", "dynamic-construct"),
        ("src/broken.py", "parse-error"),
    }


def test_nested_imports_and_common_metaprogramming_are_honest_frontier(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    files = {
        "type_factory.py": "Generated = type('Generated', (), {})\n",
        "globals_write.py": "globals()['Generated'] = object\n",
        "metaclass.py": "class Meta(type):\n    pass\nclass Dynamic(metaclass=Meta):\n    pass\n",
        "nested_import.py": "def load():\n    from private_domain import Customer\n",
        "namedtuple.py": "from collections import namedtuple\nCase = namedtuple('Case', 'id')\n",
        "make_dataclass.py": (
            "from dataclasses import make_dataclass\nCase = make_dataclass('Case', [('id', int)])\n"
        ),
        "import_module.py": "import importlib\nmodule = importlib.import_module('domain')\n",
        "namedtuple_alias.py": (
            "from collections import namedtuple as nt\nCase = nt('Case', 'id')\n"
        ),
        "make_dataclass_alias.py": (
            "from dataclasses import make_dataclass as md\nCase = md('Case', [('id', int)])\n"
        ),
        "import_module_alias.py": (
            "from importlib import import_module as im\nmodule = im('domain')\n"
        ),
        "new_class_alias.py": "from types import new_class as nc\nCase = nc('Case')\n",
        "type_alias.py": "factory = type\nCase = factory('Case', (), {})\n",
        "walrus_alias.py": "Case = (factory := type)('Case', (), {})\n",
        "nested_walrus_immediate.py": ("Case = (outer := (inner := type))('Case', (), {})\n"),
        "nested_walrus_later.py": (
            "from collections import namedtuple as nt\n"
            "(outer := (inner := nt))\n"
            "Case = outer('Case', 'id')\n"
        ),
    }
    for name, text in files.items():
        (source / name).write_text(text, encoding="utf-8")

    inventory = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="source", path="src"),),
    )
    assert {(item.path, item.reason) for item in inventory.frontier} == {
        ("src/type_factory.py", "dynamic-construct"),
        ("src/globals_write.py", "dynamic-construct"),
        ("src/metaclass.py", "dynamic-construct"),
        ("src/nested_import.py", "unresolved-import"),
        ("src/namedtuple.py", "dynamic-construct"),
        ("src/make_dataclass.py", "dynamic-construct"),
        ("src/import_module.py", "dynamic-construct"),
        ("src/namedtuple_alias.py", "dynamic-construct"),
        ("src/make_dataclass_alias.py", "dynamic-construct"),
        ("src/import_module_alias.py", "dynamic-construct"),
        ("src/new_class_alias.py", "dynamic-construct"),
        ("src/type_alias.py", "dynamic-construct"),
        ("src/walrus_alias.py", "dynamic-construct"),
        ("src/nested_walrus_immediate.py", "dynamic-construct"),
        ("src/nested_walrus_later.py", "dynamic-construct"),
    }


def test_large_destructuring_alias_graph_is_linear_and_explicitly_capped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    targets = ", ".join(f"target_{index}" for index in range(600))
    values = ", ".join(f"source_{index}" for index in range(600))
    (source / "aliases.py").write_text(f"{targets} = {values}\n", encoding="utf-8")

    monkeypatch.setattr(recovery_inventory, "MAX_ALIAS_EDGES", 500)
    inventory = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="source", path="src"),),
    )
    assert {(item.path, item.reason) for item in inventory.frontier} == {
        ("src/aliases.py", "dynamic-construct")
    }


def test_structured_alias_dates_nan_and_resource_caps_fail_closed_as_frontier(
    tmp_path: Path,
) -> None:
    config = tmp_path / "config"
    config.mkdir()
    (config / "alias.yaml").write_text("a: &shared [1]\nb: *shared\n", encoding="utf-8")
    (config / "date.yaml").write_text("created: 2026-08-14\n", encoding="utf-8")
    (config / "nan.json").write_text('{"value": NaN}\n', encoding="utf-8")
    (config / "scalar.yaml").write_text("plain\n", encoding="utf-8")

    inventory = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="config", path="config"),),
    )
    assert {(item.path, item.reason) for item in inventory.frontier} == {
        ("config/alias.yaml", "parse-error"),
        ("config/date.yaml", "parse-error"),
        ("config/nan.json", "parse-error"),
    }
    assert _census(inventory)["config/scalar.yaml"]["disposition"] == "parsed"

    capped = tmp_path / "capped"
    capped.mkdir()
    (capped / "a.txt").write_text("aaaaa", encoding="utf-8")
    (capped / "b.txt").write_text("bbbbb", encoding="utf-8")
    aggregate = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="docs", path="capped"),),
        max_file_bytes=8,
        max_total_bytes=8,
        max_files=8,
    )
    assert {(item.path, item.reason) for item in aggregate.frontier} == {
        ("capped/b.txt", "aggregate-limit")
    }

    file_limited = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="docs", path="capped"),),
        max_file_bytes=8,
        max_total_bytes=16,
        max_files=1,
    )
    assert {(item.path, item.reason) for item in file_limited.frontier} == {
        ("capped/b.txt", "file-limit")
    }


def test_directory_and_global_selected_path_observations_are_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    for index in range(4):
        (docs / f"{index}.txt").write_text(f"document {index}\n", encoding="utf-8")

    monkeypatch.setattr("gnd.recovery.inventory.MAX_OBSERVATIONS", 3)
    with pytest.raises(RecoveryInventoryError, match="observation cap"):
        scan_recovery_scope(
            tmp_path,
            (SelectedRoot(category="docs", path="docs"),),
            max_files=10,
        )


def test_preopen_growth_cannot_escape_the_aggregate_byte_cap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.txt").write_bytes(b"aaaaa")
    raced = docs / "b.txt"
    raced.write_bytes(b"b")
    real_open = recovery_inventory.os.open
    did_race = False

    def open_with_growth(
        path: str | bytes | int,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal did_race
        if path == "b.txt" and dir_fd is not None and not did_race:
            did_race = True
            raced.write_bytes(b"b" * 10)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(recovery_inventory.os, "open", open_with_growth)
    with pytest.raises(RecoveryInventoryError, match="changed before it opened|byte cap"):
        scan_recovery_scope(
            tmp_path,
            (SelectedRoot(category="docs", path="docs"),),
            max_file_bytes=10,
            max_total_bytes=10,
            max_files=10,
        )


def test_repeated_symbols_and_colliding_proposal_slugs_get_stable_unique_ids(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "repeated.py").write_text(
        "class A:\n    pass\nclass A:\n    pass\nclass A:\n    pass\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "claims.md").write_text(
        "recovery-proposal: A+B\nrecovery-proposal: A B\n",
        encoding="utf-8",
    )
    roots = (
        SelectedRoot(category="source", path="src"),
        SelectedRoot(category="docs", path="docs"),
    )

    first = scan_recovery_scope(tmp_path, roots)
    second = scan_recovery_scope(tmp_path, roots)
    assert first == second
    repeated = [item for item in first.evidence if item.path == "src/repeated.py"]
    assert len(repeated) == 3
    assert len({item.evidence_id for item in repeated}) == 3
    assert {item.locator.kind for item in repeated} == {"line"}
    assert len({item.proposal_id for item in first.ambiguities}) == 2


def test_whole_repository_dot_root_is_supported_safely(tmp_path: Path) -> None:
    (tmp_path / "domain.py").write_text("class Domain:\n    pass\n", encoding="utf-8")
    inventory = scan_recovery_scope(
        tmp_path,
        (SelectedRoot(category="source", path="."),),
    )
    assert tuple(row.path for row in inventory.census) == ("domain.py",)


def test_scanner_does_not_import_execute_spawn_install_probe_or_open_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _case("recovery-mechanical-python-schema")
    _materialize(case, tmp_path)

    def forbidden(*_args: object, **_kwargs: object) -> Any:
        pytest.fail("static recovery inventory crossed an execution/provider boundary")

    # Imports needed to define the scanner have already happened.  Repository
    # modules must be parsed as bytes/AST and never imported during the scan.
    monkeypatch.setattr(importlib, "import_module", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(subprocess, "check_call", forbidden)
    monkeypatch.setattr(subprocess, "check_output", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    # Patch the interpreter import hook last: MonkeyPatch itself lazily imports
    # ``inspect`` while installing its first attribute replacement.
    monkeypatch.setattr(builtins, "__import__", forbidden)

    inventory = scan_recovery_scope(tmp_path, _roots(case))
    # Serialization is outside the repository scan and may legitimately use
    # Pydantic's own lazy imports; restore the process hooks before asserting.
    monkeypatch.undo()
    assert list(_census(inventory)) == case["selected_paths"]


def _python_calls(path: Path) -> Iterator[str]:
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Name):
                yield target.id
            elif isinstance(target, ast.Attribute):
                yield target.attr


def test_scanner_source_has_no_execution_or_live_probe_escape_hatch() -> None:
    source = REPO_ROOT / "src" / "gnd" / "recovery" / "inventory.py"
    text = source.read_text(encoding="utf-8")
    assert not ({"exec", "eval", "compile", "system", "Popen"} & set(_python_calls(source)))
    assert "INFORMATION_SCHEMA" not in text
    assert "rai-pyrel-coding" not in text
    assert "Step 10" not in text
    assert "NULL-rate" not in text
