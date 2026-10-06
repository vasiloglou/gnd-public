"""RED public-contract corpus for immutable v7.1 reference populations.

Expected outcomes are authored separately. Each feature case first requires a
working unmodified reference lane, so historical schema rejection cannot make a
negative case accidentally pass. There is no feature implementation here.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError
from ruamel.yaml import YAML

import gnd.checker._core as checker_core
from gnd import api, extensions
from gnd.model import load_model
from gnd.population import Population, load_population

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/reference-corpus"
INPUTS = json.loads((CORPUS / "inputs.json").read_text())
CASES = INPUTS["cases"]
ANSWERS = {row["id"]: row for row in json.loads((CORPUS / "answers.json").read_text())["cases"]}
MAX_BYTES = 10 * 1024 * 1024
MAX_SET_BYTES = 32 * 1024 * 1024
MAX_ROWS = 100_000


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bytes(doc: Any) -> bytes:
    return (json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_bytes(doc))


def _bundle(domain: str, root: Path) -> dict[str, Any]:
    shutil.copytree(CORPUS / domain, root)
    return {
        "root": root,
        "ids": INPUTS["domains"][domain],
        "model": YAML(typ="safe").load((root / "model.orm.yaml").read_text()),
        "candidate": json.loads((root / "candidate.pop.json").read_bytes()),
        "catalog": json.loads((root / "references/catalog.pop.json").read_bytes()),
    }


def _save(b: dict[str, Any], *, rehash: bool = True) -> None:
    root = b["root"]
    _write_json(root / "candidate.pop.json", b["candidate"])
    _write_json(root / "references/catalog.pop.json", b["catalog"])
    if rehash:
        for declaration in b["model"].get("reference_populations", []):
            path = root / declaration.get("path", "references/catalog.pop.json")
            if path.is_file() and not path.is_symlink():
                declaration["sha256"] = _digest(path.read_bytes())
    with (root / "model.orm.yaml").open("w") as stream:
        YAML().dump(b["model"], stream)


def _check(b: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    return api.check(b["root"] / "model.orm.yaml", b["root"] / "candidate.pop.json", **kwargs)


def _validate(b: dict[str, Any]) -> dict[str, Any]:
    return api.validate(b["root"] / "model.orm.yaml")


def _mechanical(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["report"] if payload.get("schema_version") == 12 else payload


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def _observe_wrapper(payload: dict[str, Any]) -> None:
    assert set(payload) == {
        "schema_version",
        "command",
        "outcome",
        "exit_code",
        "model_digest",
        "reference_binding",
        "report",
        "occurrence_origins",
    }
    assert payload["schema_version"] == 12
    for key in ("command", "outcome", "exit_code"):
        assert payload[key] == payload["report"][key]
    assert payload["reference_binding"]["identity_version"] == 1
    refs = payload["reference_binding"]["references"]
    assert len({r["id"] for r in refs}) == len(refs)
    origins = payload["occurrence_origins"]
    coordinates = []
    for row in origins:
        assert set(row) == {"origin", "fact_type", "index"}
        assert set(row["origin"]) == {"kind", "reference_id"}
        assert row["origin"]["kind"] in {"candidate", "reference"}
        assert (row["origin"]["reference_id"] is None) == (row["origin"]["kind"] == "candidate")
        assert type(row["index"]) is int and row["index"] >= 0
        coordinates.append(
            (row["origin"]["kind"], row["origin"]["reference_id"], row["fact_type"], row["index"])
        )
    assert len(coordinates) == len(set(coordinates))
    schema = json.loads((ROOT / "src/gnd/report.schema.json").read_text())
    Draft202012Validator(schema).validate(payload)


def _candidate_count(b: dict[str, Any]) -> int:
    from gnd.references import bind_population, bind_references, candidate_fact_count

    model = load_model(b["root"] / "model.orm.yaml")
    refs = bind_references(model, root=b["root"])
    population = load_population(b["root"] / "candidate.pop.json", model=model)
    view = bind_population(model, population, references=refs)
    return candidate_fact_count(view)


def _reference_raw(b: dict[str, Any], data: bytes, suffix: str = "json") -> None:
    path = b["root"] / f"references/catalog.pop.{suffix}"
    path.write_bytes(data)
    declaration = b["model"]["reference_populations"][0]
    declaration["path"] = path.relative_to(b["root"]).as_posix()
    declaration["sha256"] = _digest(data)
    with (b["root"] / "model.orm.yaml").open("w") as stream:
        YAML().dump(b["model"], stream)


def _fixed_nonvacuous(b: dict[str, Any]) -> None:
    b["model"]["constraints"] = []
    b["model"]["fact_types"][2]["constraints"] = [
        {
            "type": "uniqueness",
            "roles": [b["ids"]["left"], b["ids"]["right"]],
            "source": "explicit",
            "status": "confirmed",
            "modality": "alethic",
            "provenance": {"user_quote": "The fixed pair is unique."},
        }
    ]


def _add_reference(b: dict[str, Any]) -> None:
    i = b["ids"]
    path = b["root"] / "references/labels.pop.json"
    _write_json(
        path,
        {
            "population": deepcopy(b["catalog"]["population"]),
            "instances": {},
            "facts": {i["extra"]: [{i["left"]: i["left_value"]}]},
        },
    )
    b["model"]["reference_populations"].append(
        {
            "id": "labels",
            "path": "references/labels.pop.json",
            "sha256": _digest(path.read_bytes()),
            "fact_types": [i["extra"]],
        }
    )


def _operation(b: dict[str, Any], effect: str | None = None) -> dict[str, Any]:
    i = b["ids"]
    return {
        "id": "read_catalog",
        "reading": "{subject} requests {left} and {right}",
        "parameters": [
            {"name": "subject", "object_type": i["object_subject"]},
            {"name": "left", "object_type": i["object_left"]},
            {"name": "right", "object_type": i["object_right"]},
        ],
        "preconditions": [
            {
                "id": "fixed_pair",
                "require": [
                    {"fact_type": i["catalog"], "bind": {i["left"]: "$left", i["right"]: "$right"}}
                ],
                "modality": "alethic",
                "source": "explicit",
                "status": "confirmed",
                "provenance": {"user_quote": "Read the bound pair."},
            }
        ],
        "effects": [
            {
                "assert": {
                    "fact_type": i["a"],
                    "bind": {i["subject"]: "$subject", i["left"]: "$left"},
                }
            }
        ]
        if effect is None
        else [
            {
                effect: {
                    "fact_type": i["catalog"],
                    "bind": {i["left"]: "$left", i["right"]: "$right"},
                }
            }
        ],
        "frame": {"modality": "alethic"},
        "source": "explicit",
        "status": "confirmed",
        "provenance": {"user_quote": "Use the supplied catalog."},
    }


def _join_input(b: dict[str, Any], n: int, *, deontic: bool = False, fail: bool = False) -> None:
    i = b["ids"]
    b["candidate"]["facts"] = {
        i["a"]: [{i["subject"]: i["subject_value"], i["left"]: f"LEFT-{j}"} for j in range(n)],
        i["b"]: [{i["subject"]: i["subject_value"], i["right"]: f"RIGHT-{j}"} for j in range(n)],
    }
    rule = b["model"]["constraints"][0]
    rule["consequent"] = {"comparison": {"operator": "=", "left": "$l", "right": "$l"}}
    rule["modality"] = "deontic" if deontic else "alethic"
    if fail:
        contradiction = deepcopy(rule)
        contradiction["id"] = "independent_contradiction"
        contradiction["antecedent"] = [deepcopy(rule["antecedent"][0])]
        contradiction["consequent"] = {
            "comparison": {"operator": "!=", "left": "$l", "right": "$l"}
        }
        contradiction["modality"] = "alethic"
        b["model"]["constraints"].insert(0, contradiction)
    _save(b)


def _run(case: dict[str, Any], b: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> int:
    n, branch, i = case["scenario"], case["branch"], b["ids"]
    refs = b["model"]["reference_populations"]
    root = b["root"]
    if branch == "B01":
        result = _check(b)
        assert any(
            v["constraint_type"] == "guarded" and v["verdict"] == "pass"
            for v in _mechanical(result)["verdicts"]
        )
        return result["exit_code"]
    if branch == "B02":
        b["candidate"]["facts"][i["b"]][0][i["right"]] = "NOT-IN-CATALOG"
        if n.endswith("deontic"):
            b["model"]["constraints"][0]["modality"] = "deontic"
        _save(b)
        result = _check(b)
        assert _mechanical(result)["counts"]["warning" if n.endswith("deontic") else "fail"] > 0
        return result["exit_code"]
    if branch == "B03":
        if n in {"candidate-owned", "candidate-owned-empty"}:
            b["candidate"]["facts"][i["catalog"]] = (
                [] if n.endswith("empty") else deepcopy(b["catalog"]["facts"][i["catalog"]])
            )
            _save(b)
            return _check(b)["exit_code"]
        model = load_model(root / "model.orm.yaml")
        pop = load_population(root / "candidate.pop.json", model=model)
        if n.endswith("constructed"):
            pop = Population.model_validate(
                {
                    **pop.model_dump(),
                    "facts": {
                        **pop.facts,
                        i["catalog"]: deepcopy(b["catalog"]["facts"][i["catalog"]]),
                    },
                }
            )
        else:
            pop.facts[i["catalog"]] = deepcopy(b["catalog"]["facts"][i["catalog"]])
        return api.check(model, pop)["exit_code"]
    if branch == "B04":
        effect = None if n == "operation-read" else n.split("-")[1]
        b["model"]["operations"] = [_operation(b, effect)]
        _save(b)
        return _validate(b)["exit_code"]
    if branch == "B05":
        d = refs[0]
        if n == "duplicate-id":
            refs.append(deepcopy(d))
        elif n == "duplicate-owner":
            d["fact_types"].append(i["catalog"])
        elif n == "overlapping-owners":
            refs.append({**deepcopy(d), "id": "second"})
        elif n == "unknown-owner":
            d["fact_types"] = ["not_a_type"]
        elif n in {"derived-owner", "semiderived-owner"}:
            b["model"]["fact_types"][2].update(
                {
                    "derivation": n.split("-")[0],
                    "derivation_rule": "A supplied legacy derived extension.",
                }
            )
        elif n.startswith("missing-"):
            del d[n.removeprefix("missing-")]
        elif n == "extra-field":
            d["authority"] = "candidate"
        elif n == "old-version":
            b["model"]["version"] = 3
        elif n == "hash-short":
            d["sha256"] = "a" * 63
        elif n == "hash-uppercase":
            d["sha256"] = "A" * 64
        elif n == "hash-nonhex":
            d["sha256"] = "g" * 64
        elif n == "empty-owner":
            d["fact_types"] = []
        elif n == "id-over-limit":
            d["id"] = "x" * 129
        else:
            raise AssertionError(n)
        _save(b, rehash=False)
        return _validate(b)["exit_code"]
    if branch == "B06":
        if n == "missing-file":
            (root / refs[0]["path"]).unlink()
        elif n == "stale-hash":
            (root / refs[0]["path"]).write_bytes(b"{}\n")
        elif n in {
            "malformed-json",
            "malformed-yaml",
            "duplicate-key",
            "nan",
            "giant-integer",
            "alias-cycle",
        }:
            raw, suffix = {
                "malformed-json": (b'{"population":', "json"),
                "malformed-yaml": (b"population: [broken\n", "yaml"),
                "duplicate-key": (b'{"population":{},"population":{}}', "json"),
                "nan": (b'{"population":{},"facts":{"x":[{"v":NaN}]}}', "json"),
                "giant-integer": (
                    b'{"population":{},"facts":{"x":[{"v":' + b"1" * 10000 + b"}]}}",
                    "json",
                ),
                "alias-cycle": (
                    b"population: &a {model: model.orm.yaml, source: fixture}\nfacts: &b {loop: [*b]}\n",
                    "yaml",
                ),
            }[n]
            _reference_raw(b, raw, suffix)
        else:
            row = b["catalog"]["facts"][i["catalog"]][0]
            if n == "wrong-role":
                del row[i["right"]]
            elif n == "wrong-type":
                row[i["right"]] = ["wrong scalar shape"]
            elif n == "wrong-header":
                b["catalog"]["population"]["model_id"] = "urn:other"
            elif n in {"undeclared-type", "undeclared-empty-type"}:
                b["catalog"]["facts"][i["extra"]] = (
                    [] if "empty" in n else [{i["left"]: i["left_value"]}]
                )
            elif n == "transitive-include":
                b["catalog"]["reference_populations"] = deepcopy(refs)
            else:
                raise AssertionError(n)
            _save(b)
        return _validate(b)["exit_code"]
    if branch == "B07":
        paths = {
            "path-absolute": str(root / "references/catalog.pop.json"),
            "path-unc": "//host/catalog.json",
            "path-drive": "C:/catalog.json",
            "path-backslash": "references\\catalog.pop.json",
            "path-dot": "references/./catalog.pop.json",
            "path-parent": "references/../catalog.pop.json",
            "path-empty-component": "references//catalog.pop.json",
            "path-nul": "references/\x00.json",
            "path-depth-over": "/".join(["r"] * 32 + ["catalog.json"]),
            "path-length-over": "r" * 4097,
        }
        if n in paths:
            refs[0]["path"] = paths[n]
            _save(b, rehash=False)
        elif n == "symlink-leaf":
            leaf = root / refs[0]["path"]
            target = leaf.with_name("target.json")
            leaf.rename(target)
            leaf.symlink_to(target.name)
        elif n == "symlink-ancestor":
            original = root / "references"
            target = root / "real-references"
            original.rename(target)
            original.symlink_to(target.name, target_is_directory=True)
        elif n == "symlink-root":
            real = root.with_name(root.name + "-real")
            root.rename(real)
            root.symlink_to(real.name, target_is_directory=True)
        elif n == "nested-path":
            target = root / "one/two/catalog.pop.json"
            target.parent.mkdir(parents=True)
            shutil.copyfile(root / refs[0]["path"], target)
            refs[0]["path"] = "one/two/catalog.pop.json"
            _save(b)
        else:
            raise AssertionError(n)
        return _validate(b)["exit_code"]
    if branch == "B08":
        from gnd import artifacts, checker

        if n == "refusal-before-evaluation":
            b["candidate"]["facts"][i["catalog"]] = deepcopy(b["catalog"]["facts"][i["catalog"]])
            b["candidate"]["facts"][i["b"]][0][i["right"]] = "MISSING"
            _save(b)

            def forbidden(*args: Any, **kwargs: Any) -> Any:
                pytest.fail("domain evaluator invoked before ownership refusal")

            monkeypatch.setattr(extensions, "evaluate_derivations", forbidden)
            return _check(b)["exit_code"]
        if n == "declaration-before-file":
            refs.append({**deepcopy(refs[0]), "id": "second"})
            _save(b)
            (root / refs[0]["path"]).unlink()
            read = artifacts.read_regular_bounded_at

            def no_reference_read(fd: int, relative: str, **kwargs: Any) -> Any:
                assert not relative.endswith("catalog.pop.json"), (
                    "overlap checked after reference read"
                )
                return read(fd, relative, **kwargs)

            monkeypatch.setattr(artifacts, "read_regular_bounded_at", no_reference_read)
            return _validate(b)["exit_code"]
        b["candidate"]["facts"][i["catalog"]] = []
        _save(b)
        (root / refs[0]["path"]).write_bytes(b"{}\n")
        result = _check(b)
        assert (
            "hash" in json.dumps(_mechanical(result)).lower()
            or "digest" in json.dumps(_mechanical(result)).lower()
        )
        return result["exit_code"]
    if branch in {"B09", "B10"}:
        before_count = _candidate_count(b)
        before_admission = _mechanical(_check(b, admission=True))["admission"]
        if n in {"empty-candidate", "reference-nonvacuous", "zero-candidate-floor"}:
            b["candidate"]["facts"] = {}
        if n in {"reference-nonvacuous", "zero-candidate-floor"}:
            _fixed_nonvacuous(b)
        if n == "empty-catalog":
            b["catalog"]["facts"][i["catalog"]] = []
        if n == "reference-inflation":
            b["catalog"]["facts"][i["catalog"]].extend(
                [
                    {i["left"]: "NEW-FIXED", i["right"]: "NEW-ITEM"},
                    deepcopy(b["catalog"]["facts"][i["catalog"]][0]),
                ]
            )
            b["catalog"]["instances"][i["object_left"]] = ["NEW-FIXED"]
        _save(b)
        result = _check(b, admission=True)
        count = _candidate_count(b)
        if n in {"empty-candidate", "reference-nonvacuous", "zero-candidate-floor"}:
            assert count == 0 and not count >= 1
        if n == "reference-inflation":
            assert count == before_count == 2
            assert _mechanical(result)["admission"] == before_admission
        return result["exit_code"]
    if branch == "B11":
        import gnd.model as model_module

        read = model_module.load_model_bytes
        old_hash = refs[0]["sha256"]
        fired = []

        def replace_after_read(data: bytes, *, source: Any) -> Any:
            if not fired:
                fired.append(True)
                if n == "model-parent-swap":
                    old = root.with_name(root.name + "-old")
                    root.rename(old)
                    root.mkdir()
                    (root / "model.orm.yaml").write_text(
                        "version: 1\nobject_types: []\nfact_types: []\n"
                    )
                else:
                    other = root / "other.yaml"
                    other.write_text("version: 1\nobject_types: []\nfact_types: []\n")
                    other.replace(root / "model.orm.yaml")
            return read(data, source=source)

        monkeypatch.setattr(model_module, "load_model_bytes", replace_after_read)
        result = _validate(b)
        assert fired
        assert result["exit_code"] in {0, 3}
        if result["exit_code"] == 0:
            assert result["reference_binding"]["references"][0]["sha256"] == old_hash
        return result["exit_code"]
    if branch == "B12":
        from gnd import artifacts

        if n == "fd-cleanup":
            opened: set[int] = set()
            original_open, original_close = os.open, os.close

            def tracked_open(*args: Any, **kwargs: Any) -> int:
                fd = original_open(*args, **kwargs)
                opened.add(fd)
                return fd

            def tracked_close(fd: int) -> None:
                original_close(fd)
                opened.discard(fd)

            monkeypatch.setattr(os, "open", tracked_open)
            monkeypatch.setattr(os, "close", tracked_close)
            for _ in range(3):
                assert _validate(b)["exit_code"] == 0
                (root / refs[0]["path"]).write_bytes(b"{}\n")
                assert _validate(b)["exit_code"] == 3
                _save(b)
            assert not opened
            return 0
        read = artifacts.read_regular_bounded_at
        expected = refs[0]["sha256"]
        fired = []

        def replace_after_read(fd: int, relative: str, **kwargs: Any) -> Any:
            result = read(fd, relative, **kwargs)
            if relative.endswith("catalog.pop.json") and not fired:
                fired.append(True)
                if n == "reference-root-swap":
                    old = root.with_name(root.name + "-old")
                    root.rename(old)
                    shutil.copytree(old, root)
                elif n == "reference-parent-swap":
                    old = root / "old-references"
                    (root / "references").rename(old)
                    shutil.copytree(old, root / "references")
                target = root / "references/catalog.pop.json"
                if n == "reference-inplace-write":
                    target.write_bytes(b"{}\n")
                else:
                    other = target.with_name("replacement.json")
                    other.write_bytes(b"{}\n")
                    other.replace(target)
            return result

        monkeypatch.setattr(artifacts, "read_regular_bounded_at", replace_after_read)
        result = _validate(b)
        assert fired
        if result["exit_code"] == 0:
            assert result["reference_binding"]["references"][0]["sha256"] == expected
        monkeypatch.setattr(artifacts, "read_regular_bounded_at", read)
        assert _validate(b)["exit_code"] == 3
        return result["exit_code"]
    if branch == "B13":
        from gnd.references import reference_model_digest
        from gnd.transition import model_digest

        first = reference_model_digest(load_model(root / "model.orm.yaml"))
        if n == "identity-order":
            _add_reference(b)
            _save(b)
            first = reference_model_digest(load_model(root / "model.orm.yaml"))
            refs.reverse()
            _save(b)
            assert reference_model_digest(load_model(root / "model.orm.yaml")) == first
        elif n == "legacy-digest":
            del b["model"]["reference_populations"]
            b["model"]["version"] = 3
            _save(b)
            model = load_model(root / "model.orm.yaml")
            assert reference_model_digest(model) == model_digest(model)
            assert model_digest(model) == ANSWERS[case["id"]]["legacy_model_digest"]
        else:
            if n == "identity-updated-bytes":
                b["catalog"]["facts"][i["catalog"]].append(
                    {i["left"]: "NEW-FIXED", i["right"]: "NEW-ITEM"}
                )
            elif n == "identity-path":
                shutil.copyfile(root / refs[0]["path"], root / "renamed.json")
                refs[0]["path"] = "renamed.json"
            elif n == "identity-id":
                refs[0]["id"] = "renamed"
            elif n == "identity-owner":
                refs[0]["fact_types"].append(i["extra"])
            else:
                raise AssertionError(n)
            _save(b)
            assert reference_model_digest(load_model(root / "model.orm.yaml")) != first
        return 0
    if branch == "B14":
        if n in {"api-check", "api-validate"}:
            command = "check" if n == "api-check" else "validate"
            args = [command, str(root / "model.orm.yaml")]
            if command == "check":
                args.append(str(root / "candidate.pop.json"))
            result = _cli(*args, "--format", "json")
            public = _check(b) if command == "check" else _validate(b)
            assert result.returncode == public["exit_code"] == 0
            assert json.loads(result.stdout) == public
        elif n == "api-cwd":
            monkeypatch.chdir(root.parent)
            assert _check(b)["exit_code"] == 0
        elif n in {"api-bound-context", "api-missing-context"}:
            from gnd.model import load_model_bytes
            from gnd.references import bind_references

            model = load_model_bytes(
                (root / "model.orm.yaml").read_bytes(), source="model.orm.yaml"
            )
            population = load_population(root / "candidate.pop.json", model=model)
            if n == "api-missing-context":
                return api.check(model, population)["exit_code"]
            context = bind_references(model, root=root)
            assert api.check(model, population, references=context)["exit_code"] == 0
        elif n == "batch":
            from gnd.batch import check_population_directory

            folder = root / "candidates"
            folder.mkdir()
            shutil.copyfile(root / "candidate.pop.json", folder / "one.json")
            batch = check_population_directory(root / "model.orm.yaml", folder)
            assert batch.aggregate_exit == 0 and len(batch.rows) == 1
        elif n == "diff":
            other = root.with_name(root.name + "-second")
            shutil.copytree(root, other)
            public = api.diff(root / "model.orm.yaml", other / "model.orm.yaml", populations=None)
            assert public["exit_code"] == 0
        elif n == "transition":
            from gnd.transition import model_digest, operations_digest

            b["model"]["operations"] = [_operation(b)]
            _save(b)
            model = load_model(root / "model.orm.yaml")
            steps = {
                "steps_schema": 1,
                "model": "model.orm.yaml",
                "model_digest": model_digest(model),
                "operations_digest": operations_digest(model.operations),
                "steps": [
                    {
                        "op": "read_catalog",
                        "bindings": {
                            "subject": i["subject_value"],
                            "left": i["left_value"],
                            "right": i["right_value"],
                        },
                    }
                ],
            }
            reference_before = (root / "references/catalog.pop.json").read_bytes()
            public = api.transition(model, root / "candidate.pop.json", steps)
            assert public["exit_code"] == 0, public
            assert all(
                row["origin"]["kind"] != "reference"
                for row in public.get("post_candidate_origins", [])
            )
            assert (root / "references/catalog.pop.json").read_bytes() == reference_before
        else:
            raise AssertionError(n)
        return 0
    if branch == "B15":
        from gnd.references import bind_references

        model = load_model(root / "model.orm.yaml")
        pop = load_population(root / "candidate.pop.json", model=model)
        context = bind_references(model, root=root)
        if n == "context-forged":
            context = object()
        elif n == "context-wrong-model":
            other = root.with_name(root.name + "-other")
            shutil.copytree(root, other)
            doc = deepcopy(b["model"])
            doc["model_id"] = "urn:other"
            with (other / "model.orm.yaml").open("w") as stream:
                YAML().dump(doc, stream)
            # Byte loading avoids the different model_id in the old catalog header.
            from gnd.model import load_model_bytes

            alien = load_model_bytes(
                (other / "model.orm.yaml").read_bytes(), source="model.orm.yaml"
            )
            assert alien.model_id != model.model_id
            return api.check(alien, pop, references=context)["exit_code"]
        elif n == "context-model-mutation":
            model.constraints[0]["id"] = "mutated-after-binding"
        elif n == "context-snapshot-immutable":
            (root / "references/catalog.pop.json").write_bytes(b"{}\n")
            assert api.check(model, pop, references=context)["exit_code"] == 0
            assert _validate(b)["exit_code"] == 3
            return 0
        else:
            raise AssertionError(n)
        return api.check(model, pop, references=context)["exit_code"]
    if branch == "B16":
        if n == "legacy-wire":
            del b["model"]["reference_populations"]
            b["model"]["version"] = 3
            b["candidate"]["facts"][i["catalog"]] = deepcopy(b["catalog"]["facts"][i["catalog"]])
            _save(b)
            b["candidate"]["population"]["covers"] += b["catalog"]["population"]["covers"]
            _save(b)
            old = _check(b)
            assert sorted(old) == ANSWERS[case["id"]]["legacy_keyset"]
            assert {key: old[key] for key in ANSWERS[case["id"]]["legacy_projection"]} == ANSWERS[
                case["id"]
            ]["legacy_projection"]
            b["model"]["version"] = 4
            _save(b)
            new = _check(b)
            for key in ("schema_version", "counts", "verdicts", "outcome", "exit_code"):
                assert new[key] == old[key]
            assert new["schema_version"] != 12
        else:
            payload = _check(b)
            _observe_wrapper(payload)
            if n == "report-dirty-control":
                for mutation in ("extra", "exit", "origin"):
                    dirty = deepcopy(payload)
                    if mutation == "extra":
                        dirty["extra"] = True
                    elif mutation == "exit":
                        dirty["exit_code"] = 1
                    else:
                        dirty["occurrence_origins"].append(deepcopy(dirty["occurrence_origins"][0]))
                    with pytest.raises((AssertionError, ValidationError)) as caught:
                        _observe_wrapper(dirty)
                    assert caught.value is not None
        return 0
    if branch == "B17":
        if n == "derivation-origins":
            derived = deepcopy(b["model"]["fact_types"][2])
            derived["id"] = i["catalog"] + "_derived"
            derived["derivation"] = "derived"
            derived["derivation_rule"] = {
                "body": [{"fact_type": i["catalog"], "bind": {i["left"]: "$l", i["right"]: "$r"}}],
                "head": {i["left"]: "$l", i["right"]: "$r"},
            }
            b["model"]["fact_types"].append(derived)
            b["candidate"]["facts"][derived["id"]] = deepcopy(b["catalog"]["facts"][i["catalog"]])
            b["candidate"]["population"]["covers"].append(derived["id"])
            _save(b)
            result = _check(b, admission=True)
            _observe_wrapper(result)
            assert len(result["occurrence_origins"]) == 4
            assert _mechanical(result)["derivations"]
            assert _candidate_count(b) == 3
            return result["exit_code"]
        if n == "anchored-origins":
            b["model"]["fact_types"][0]["constraints"] = [
                {
                    "type": "anchored",
                    "role": i["left"],
                    "source": "explicit",
                    "status": "confirmed",
                    "modality": "alethic",
                    "provenance": {"user_quote": "Candidate locations require a source anchor."},
                }
            ]
            _save(b)
            result = _check(b, admission=True)
            _observe_wrapper(result)
            assert len(result["occurrence_origins"]) == 3
            assert any(
                v["constraint_type"] == "anchored" and v["verdict"] == "unchecked"
                for v in _mechanical(result)["verdicts"]
            )
            return result["exit_code"]
        if n == "multiple-origins":
            _add_reference(b)
        if n == "duplicate-origins":
            b["catalog"]["facts"][i["catalog"]].append(
                deepcopy(b["catalog"]["facts"][i["catalog"]][0])
            )
        _save(b)
        result = _check(b, admission=True)
        _observe_wrapper(result)
        origins = result["occurrence_origins"]
        expected_count = 4 if n in {"multiple-origins", "duplicate-origins"} else 3
        assert len(origins) == expected_count
        if n == "multiple-origins":
            assert {row["origin"]["reference_id"] for row in origins} == {None, "catalog", "labels"}
        if n == "duplicate-origins":
            assert {row["index"] for row in origins if row["origin"]["kind"] == "reference"} == {
                0,
                1,
            }
        admission = _mechanical(result)["admission"]
        assert set(admission) == {"admitted", "blocked"}
        actual = [row["fact_ref"] for rows in admission.values() for row in rows]
        assert {tuple(sorted(row.items())) for row in actual} == {
            tuple(sorted({"fact_type": i["a"], "index": 0}.items())),
            tuple(sorted({"fact_type": i["b"], "index": 0}.items())),
        }
        assert len(actual) == 2
        if n == "candidate-admission":
            b["candidate"]["facts"][i["b"]][0][i["right"]] = "NOT-IN-CATALOG"
            _save(b)
            blocked = _mechanical(_check(b, admission=True))["admission"]["blocked"]
            assert blocked and all(row["blocked_by"] for row in blocked)
        return result["exit_code"]
    if branch == "B18":
        target = case["parameters"]["target"]
        path = (
            root
            / {
                "model": "model.orm.yaml",
                "reference": "references/catalog.pop.json",
                "candidate": "candidate.pop.json",
            }[target]
        )
        data = path.read_bytes()
        limit = MAX_BYTES + (1 if n.endswith("over") else 0)
        data += b" " * (limit - len(data))
        path.write_bytes(data)
        if target == "reference":
            refs[0]["sha256"] = _digest(data)
            with (root / "model.orm.yaml").open("w") as stream:
                YAML().dump(b["model"], stream)
        start = time.monotonic()
        result = _check(b)
        assert time.monotonic() - start <= 10
        assert path.stat().st_size == limit
        return result["exit_code"]
    if branch == "B19":
        over = n.endswith("over")
        if n.startswith("file-count"):
            count = 33 if over else 32
            b["catalog"]["facts"] = {}
            refs.clear()
            for idx in range(count):
                ft = deepcopy(b["model"]["fact_types"][3])
                ft["id"] = f"fixed_{idx}"
                b["model"]["fact_types"].append(ft)
                path = root / f"references/r{idx}.json"
                _write_json(
                    path,
                    {
                        "population": deepcopy(b["catalog"]["population"]),
                        "instances": {},
                        "facts": {ft["id"]: []},
                    },
                )
                refs.append(
                    {
                        "id": f"r{idx}",
                        "path": path.relative_to(root).as_posix(),
                        "sha256": _digest(path.read_bytes()),
                        "fact_types": [ft["id"]],
                    }
                )
            # Preserve the actual membership catalog as one of the counted files.
            refs[0]["fact_types"] = [i["catalog"]]
            doc = deepcopy(b["catalog"])
            doc["facts"] = {
                i["catalog"]: [{i["left"]: i["left_value"], i["right"]: i["right_value"]}]
            }
            _write_json(root / refs[0]["path"], doc)
            _save(b)
        elif n.startswith("set-bytes"):
            _add_reference(b)
            _save(b)
            while len(refs) < 4:
                idx = len(refs)
                ft = deepcopy(b["model"]["fact_types"][3])
                ft["id"] = f"fixed_{idx}"
                b["model"]["fact_types"].append(ft)
                path = root / f"references/r{idx}.json"
                _write_json(
                    path,
                    {
                        "population": deepcopy(b["catalog"]["population"]),
                        "instances": {},
                        "facts": {ft["id"]: []},
                    },
                )
                refs.append(
                    {
                        "id": f"r{idx}",
                        "path": path.relative_to(root).as_posix(),
                        "sha256": _digest(path.read_bytes()),
                        "fact_types": [ft["id"]],
                    }
                )
            total = MAX_SET_BYTES + int(over)
            for idx, ref in enumerate(refs):
                path = root / ref["path"]
                data = path.read_bytes()
                size = total // 4 + (total % 4 if idx == 3 else 0)
                path.write_bytes(data + b" " * (size - len(data)))
                ref["sha256"] = _digest(path.read_bytes())
            with (root / "model.orm.yaml").open("w") as stream:
                YAML().dump(b["model"], stream)
        elif n.startswith("row-count"):
            b["catalog"]["facts"][i["catalog"]] = [
                deepcopy(b["catalog"]["facts"][i["catalog"]][0])
                for _ in range(MAX_ROWS - 2 + int(over))
            ]
            _save(b)
        elif n.startswith("instance-count"):
            b["catalog"]["instances"][i["object_left"]] = [
                f"FIXED-{idx}" for idx in range(MAX_ROWS + int(over))
            ]
            _save(b)
        elif n.startswith("container-depth"):
            # The guard is the discriminating layer; typed schema cannot reach
            # this depth. The corpus addendum fixes the depth definition.
            from gnd.references import validate_reference_structure

            doc: Any = 0
            for _ in range(65 if over else 64):
                doc = [doc]
            if over:
                from gnd.references import ReferenceInputError

                with pytest.raises(ReferenceInputError):
                    validate_reference_structure(doc)
                return 3
            assert validate_reference_structure(doc) is None
            return 0
        elif n == "id-near":
            refs[0]["id"] = "x" * 128
            _save(b)
        elif n == "path-depth-near":
            relative = "/".join(["r"] * 31 + ["catalog.json"])
            path = root / relative
            path.parent.mkdir(parents=True)
            shutil.copyfile(root / refs[0]["path"], path)
            refs[0]["path"] = relative
            _save(b)
        else:
            raise AssertionError(n)
        start = time.monotonic()
        result = _check(b)
        assert time.monotonic() - start <= 10
        return result["exit_code"]
    if branch == "B20":
        _join_input(
            b,
            300 if n == "join-near" else 317,
            deontic=n.endswith("deontic"),
            fail=n.endswith("failure"),
        )
        start = time.monotonic()
        result = _check(b)
        assert time.monotonic() - start <= 10
        if "over" in n:
            assert _mechanical(result)["counts"]["unchecked"] > 0
        return result["exit_code"]
    if branch == "B21":
        monkeypatch.delattr(os, "O_NOFOLLOW")
        result = _validate(b)
        plain = ROOT / "tests/fixtures/reference-legacy" / case["domain"] / "model.orm.yaml"
        assert api.validate(plain)["exit_code"] == 0
        return result["exit_code"]
    if branch == "B22":
        if n == "reader-counter-control":
            reads = []
            original = os.read

            def watched(fd: int, length: int) -> bytes:
                assert 0 <= length <= MAX_BYTES + 1, "unbounded or over-budget read"
                reads.append(length)
                return original(fd, length)

            monkeypatch.setattr(os, "read", watched)
            assert _validate(b)["exit_code"] == 0
            assert reads, "no observed descriptor read"
            with pytest.raises(AssertionError, match="unbounded"):
                watched(-1, MAX_BYTES + 2)
        else:
            from gnd import checker

            # A budget-bypassing binding producer is a known dirty control.
            original = checker._guarded_bindings

            def dirty_bindings(*args: Any, **kwargs: Any) -> Any:
                bindings = original(*args, **kwargs)
                return list(bindings) * 100_001

            _join_input(b, 1)
            monkeypatch.setattr(checker_core, "_guarded_bindings", dirty_bindings)
            assert _check(b)["exit_code"] == 4, "uncharged binding expansion escaped the work limit"
        return 0
    if branch == "B23":
        if n in {"synth-refusal", "codegen-refusal"}:
            out = root / "output"
            args = (
                [
                    "synth",
                    str(root / "model.orm.yaml"),
                    "--out",
                    str(out),
                    "--class",
                    "conforming",
                    "--seed",
                    "1",
                ]
                if n.startswith("synth")
                else ["codegen", str(root / "model.orm.yaml"), "--out", str(out)]
            )
            result = _cli(*args)
            assert not out.exists() or not any(out.iterdir())
            assert "reference" in (result.stdout + result.stderr).lower()
            return result.returncode
        if n == "session-refusal":
            from gnd.exp.session_contract import SessionContractError, read_session_contract

            raw = (root / "model.orm.yaml").read_bytes()
            bound = {
                "path": "model.orm.yaml",
                "media_type": "application/yaml",
                "encoding": "utf-8",
                "sha256": _digest(raw),
                "size_bytes": len(raw),
            }
            doc = {
                "schema_version": 2,
                "experiment_id": "EXP-v71-reference",
                "max_attempts": 1,
                "wall_seconds": 30.0,
                "cases": [
                    {
                        "case_id": "fixed",
                        "role": "required",
                        "inputs": [bound],
                        "acceptance": {
                            "mode": "constraint-satisfaction",
                            "coverage": [{"fact_type": i["a"], "min_facts": 1}],
                        },
                        "verify": {
                            "command": "check",
                            "model": bound,
                            "subject": "candidate.pop.json",
                        },
                    }
                ],
            }
            _write_json(root / "contract.json", doc)
            with pytest.raises(SessionContractError, match="(?i)reference"):
                read_session_contract(
                    root / "contract.json", experiment_root=root, experiment_id=doc["experiment_id"]
                )
            return 3
        if n == "conformance-drift":
            model_path = root / "model.orm.yaml"
            original = model_path.read_bytes()
            original_reference = (root / "references/catalog.pop.json").read_bytes()
            del b["model"]["reference_populations"]
            b["model"]["version"] = 3
            _save(b)
            out = root / "generated"
            control = _cli("codegen", str(model_path), "--out", str(out))
            assert control.returncode == 0
            model_path.write_bytes(original)
            (root / "references/catalog.pop.json").write_bytes(original_reference)
            result = _cli("conformance", str(model_path), str(out), "--format", "json")
            payload = json.loads(result.stdout)
            assert result.returncode != 0
            assert (
                "model" in json.dumps(payload).lower() and "digest" in json.dumps(payload).lower()
            )
            return 0
        if n == "extract-owned-projection":
            from gnd.extract.projection import project

            projection = project(load_model(root / "model.orm.yaml"))
            assert i["catalog"] not in projection["properties"]["facts"]["properties"]
            assert i["a"] in projection["properties"]["facts"]["properties"]
        elif n == "verbalize-ownership":
            from gnd.model_verbalization import render_model_verbalization

            text = render_model_verbalization(root / "model.orm.yaml")
            assert "reference" in text.lower() and i["catalog"] in text
        elif n == "diagnostic-redaction":
            b["catalog"]["facts"][i["catalog"]][0][i["right"]] = {
                "secret": "PRIVATE-REFERENCE-ROLE"
            }
            _save(b)
            result = _validate(b)
            assert result["exit_code"] == 3
            assert "PRIVATE-REFERENCE-ROLE" not in json.dumps(result)
        else:
            raise AssertionError(n)
        return 0
    if branch == "B24":
        from support.census_scope import verify_v71_registration

        canonical = ROOT / "src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json"
        assert canonical.read_bytes() == (ROOT / "src/gnd/schema/orm-meta.schema.json").read_bytes()
        Draft202012Validator(json.loads(canonical.read_bytes())).validate(b["model"])
        prose = (canonical.parent / "representation-format.md").read_text()
        assert "reference_populations" in prose and "fact_types" in prose
        verify_v71_registration()
        return 0
    raise AssertionError(f"unhandled case {case['id']}")


def _audit_corpus(root: Path = CORPUS) -> None:
    manifest = json.loads((root / "manifest.json").read_text())
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }
    assert set(manifest["files"]) == actual
    for name, expected in manifest["files"].items():
        data = (root / name).read_bytes()
        assert len(data) == expected["bytes"] and _digest(data) == expected["sha256"]
    inputs = json.loads((root / "inputs.json").read_text())["cases"]
    answers = json.loads((root / "answers.json").read_text())["cases"]
    ids = [row["id"] for row in inputs]
    assert len(ids) == len(set(ids))
    assert set(ids) == {row["id"] for row in answers}
    assert len(answers) == len(ids)
    for domain in ("dispatch", "release"):
        assert {r["branch"] for r in inputs if r["domain"] == domain} == {
            f"B{x:02d}" for x in range(1, 25)
        }
    assert all(r["scenario"] and r["story"] for r in inputs)


def test_phase2_corpus_manifest() -> None:
    _audit_corpus()


@pytest.mark.parametrize("mutation", ["input", "answer", "inventory"])
def test_phase2_corpus_dirty_control(tmp_path: Path, mutation: str) -> None:
    copied = tmp_path / "copied"
    shutil.copytree(CORPUS, copied)
    if mutation == "input":
        (copied / "inputs.json").write_text("{}\n")
    elif mutation == "answer":
        doc = json.loads((copied / "answers.json").read_text())
        doc["cases"][0]["exit_code"] = 3
        _write_json(copied / "answers.json", doc)
    else:
        (copied / "unregistered.json").write_text("{}\n")
    with pytest.raises(AssertionError):
        _audit_corpus(copied)


# B24 verifies the old repository-wide census registration, not reference behavior.
@pytest.mark.parametrize("case", [
    pytest.param(case, id=case["id"], marks=pytest.mark.evidence)
    if case["branch"] == "B24" else pytest.param(case, id=case["id"])
    for case in CASES
])
def test_phase2_corpus(
    case: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    b = _bundle(case["domain"], tmp_path / "subject")
    assert _validate(b)["exit_code"] == 0, "reference feature control is unavailable"
    assert _check(b)["exit_code"] == 0, "reference join control is unavailable"
    observed = _run(case, b, monkeypatch)
    answer = ANSWERS[case["id"]]
    if answer["exit_code"] is None:
        assert observed in case["parameters"]["allowed_exits"]
    else:
        assert observed == answer["exit_code"]


def test_phase2_public_context_signatures() -> None:
    for name in ("validate", "check", "transition", "diff"):
        parameter = inspect.signature(getattr(api, name)).parameters["references"]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is None
    assert (
        inspect.signature(api.diff).parameters["references_b"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )


@pytest.mark.evidence
def test_phase2_registration_dirty_control(tmp_path: Path) -> None:
    from support.census_scope import verify_v71_registration

    copied = tmp_path / "repository"
    destination = copied / "tests/fixtures/v71"
    shutil.copytree(ROOT / "tests/fixtures/v71", destination)
    verify_v71_registration(copied, require_tracked=False)
    (destination / "phase2/unlisted.json").write_text("{}\n")
    with pytest.raises(ValueError, match="unlisted"):
        verify_v71_registration(copied, require_tracked=False)
