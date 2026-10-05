"""Test-only materializers for the owner-gated v7.1 session corpus.

Expected outcomes are read only by assert_answer. Materialization and execution
never consume the answer key or implement patches, admission, rank or feedback.
"""

from __future__ import annotations

import copy
import hashlib
import importlib
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

from gnd import api
from gnd.artifacts import canonical_json_bytes
from gnd.cli import main
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_store import SessionStore
from gnd.model import load_model
from gnd.population import load_population
from gnd.references import bind_references
from tests import test_public_v71_full_judgments as closure

ROOT = closure.ROOT
CORPUS = ROOT / "tests/fixtures/v71/phase4"
INPUTS = json.loads((CORPUS / "inputs.json").read_text())
ANSWERS = {r["id"]: r for r in json.loads((CORPUS / "answers.json").read_text())["cases"]}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def require_lane() -> None:
    from gnd.exp import session_contract

    assert getattr(session_contract, "PATCH_SESSION_CONTRACT_VERSION", None) == 7, (
        "Phase 4 version-7 session lane is absent; this RED is not a branch outcome"
    )
    patch = importlib.import_module("gnd.exp.session_patch")
    validator = importlib.import_module("gnd.admission_validation")
    assert callable(patch.apply_candidate_patch)
    assert callable(validator.validate_admission_payload)


def bundle(domain: str, root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    source = CORPUS / domain
    shutil.copytree(source, root, dirs_exist_ok=True)
    return {
        "root": root,
        "ids": copy.deepcopy(INPUTS["domains"][domain]),
        "model": json.loads((source / "model.orm.yaml").read_text()),
        "population": json.loads((source / "candidate.pop.json").read_text()),
        "contract": json.loads((source / "contract-v7.json").read_text()),
    }


def patch_contract(b: dict) -> DataDrivenContract:
    doc = copy.deepcopy(b["contract"])
    doc["candidate_edits"] = {
        "patch_path": ".gnd-patch.json",
        "artifacts": b["ids"]["artifacts"],
    }
    return DataDrivenContract.model_validate(doc)


def base_files(b: dict) -> tuple[Path, str, dict[str, bytes]]:
    base = b["root"] / "base"
    base.mkdir(exist_ok=True)
    (base / "candidate.pop.json").write_bytes(canonical_json_bytes(b["population"]))
    write_json(base / "notes.json", {"note": "unchanged"})
    write_json(base / "kept.json", {"keep": True})
    store = SessionStore(b["root"] / "store", run_id="corpus")
    digest = store.inventory_candidate(base).tree_sha256
    return base, digest, {p.name: p.read_bytes() for p in base.iterdir()}


def proposal(b: dict, operations: list[dict], digest: str | None) -> dict:
    ops = copy.deepcopy(operations)
    for op in ops:
        if op["op"] != "replace-artifact":
            op.setdefault("artifact", "candidate.pop.json")
            op.setdefault("collection", ["facts", b["ids"]["fact"]])
    return {"schema_version": 1, "base_candidate_sha256": digest, "operations": ops}


def patch_case(row: dict, b: dict, monkeypatch=None) -> dict:
    module = importlib.import_module("gnd.exp.session_patch")
    base, digest, before = base_files(b)
    par = row["parameters"]
    variant = par.get("variant", "")
    ops = par.get("operations", [{"op": "delete", "key": ["A"]}])
    doc = proposal(b, ops, digest)
    if variant in {"first-complete", "retry-complete", "notes-object"}:
        doc = proposal(
            b,
            [
                {
                    "op": "replace-artifact",
                    "artifact": "candidate.pop.json",
                    "value": b["population"],
                },
                {"op": "replace-artifact", "artifact": "notes.json", "value": {"note": "replaced"}},
            ],
            None if variant == "first-complete" else digest,
        )
    if variant in {"wrong-digest", "stale-and-key-error"}:
        doc["base_candidate_sha256"] = "0" * 64
        if variant == "stale-and-key-error":
            doc["operations"][0]["key"] = [None]
    elif variant == "null-retry":
        doc["base_candidate_sha256"] = None
    if variant in {"absolute", "parent", "windows"}:
        doc["operations"][0]["artifact"] = {
            "absolute": "/outside.json",
            "parent": "../outside.json",
            "windows": "C:\\outside.json",
        }[variant]
    elif variant == "symlink":
        leaf = base / "candidate.pop.json"
        leaf.unlink()
        leaf.symlink_to(b["root"] / "candidate.pop.json")
    elif variant == "linked-ancestor":
        (base / "linked").symlink_to(b["root"], target_is_directory=True)
        b["ids"]["artifacts"][0]["path"] = "linked/candidate.pop.json"
        doc["operations"][0]["artifact"] = "linked/candidate.pop.json"
    exchanged = []
    if variant == "ancestor-exchange":
        assert monkeypatch is not None
        from gnd import artifacts

        original_open = artifacts.os.open

        def exchange(path, flags, *args, **kwargs):
            if isinstance(path, (str, Path)) and Path(path) == base and not exchanged:
                retained = base.with_name("base-before-exchange")
                base.rename(retained)
                shutil.copytree(retained, base)
                exchanged.append(retained)
            return original_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(artifacts.os, "open", exchange)
    keys = {
        "duplicate": ["A", "A"],
        "missing": ["A", "missing"],
        "null": [None, "B"],
        "opaque": [{"$opaque": "x"}, "B"],
        "container": [["A"], "B"],
        "numeric-collision": [1, 1.0],
        "bool-distinct": [True, 1],
        "number-string-distinct": [1, "1"],
        "negative-zero": [-0.0, 2],
    }
    if variant in keys:
        rows = b["population"]["facts"][b["ids"]["fact"]]
        for r, key in zip(rows, keys[variant], strict=True):
            if key == "missing":
                r.pop(b["ids"]["key"])
            else:
                r[b["ids"]["key"]] = key
        (base / "candidate.pop.json").write_bytes(canonical_json_bytes(b["population"]))
        digest = (
            SessionStore(b["root"] / "keys-store", run_id="corpus")
            .inventory_candidate(base)
            .tree_sha256
        )
        doc["base_candidate_sha256"] = digest
        doc["operations"] = [
            {
                "op": "delete",
                "artifact": "candidate.pop.json",
                "collection": ["facts", b["ids"]["fact"]],
                "key": [0 if variant == "negative-zero" else keys[variant][0]],
            }
        ]
        before = {p.name: p.read_bytes() for p in base.iterdir()}
    try:
        files = module.apply_candidate_patch(
            doc,
            contract=patch_contract(b),
            base_root=base,
            base_sha256=digest,
            allow_initial_seed=variant == "first-complete",
        )
    except module.PatchRefusal as error:
        if variant == "ancestor-exchange":
            assert exchanged, "ancestor exchange injection did not fire"
            assert all((exchanged[0] / name).read_bytes() == data for name, data in before.items())
        return {"status": "refused", "reason": error.reason}
    assert all((base / name).read_bytes() == data for name, data in before.items())
    assert files["kept.json"] == before["kept.json"]
    got = json.loads(files["candidate.pop.json"])
    from gnd.artifacts import tree_sha256_from_inventory
    from gnd.exp.session_store import CandidateFile

    inventory = [
        CandidateFile(
            path=name,
            media_type="application/json",
            encoding="utf-8",
            size_bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            executable=False,
        )
        for name, data in sorted(files.items())
    ]
    result = {
        "status": "ok",
        "rows": got["facts"][b["ids"]["fact"]],
        "same_tree": files == before,
        "files_sha256": {
            name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())
        },
        "tree_sha256": tree_sha256_from_inventory(inventory),
    }
    if variant in {"first-complete", "retry-complete", "notes-object"}:
        result["complete"] = got == b["population"] and json.loads(files["notes.json"]) == {
            "note": "replaced"
        }
    return result


def intake_case(row: dict, b: dict) -> dict:
    module = importlib.import_module("gnd.exp.session_patch")
    doc = proposal(b, [{"op": "delete", "key": ["A"]}], "0" * 64)
    variant = row["parameters"]["variant"]
    if variant == "root-list":
        doc = []
    elif variant == "unknown-field":
        doc["shell"] = "never execute"
    elif variant == "bool-version":
        doc["schema_version"] = True
    elif variant == "bad-op":
        doc["operations"][0]["op"] = "merge"
    if variant == "duplicate-json-key":
        raw = (
            b'{"schema_version":1,"schema_version":1,"base_candidate_sha256":null,"operations":[]}'
        )
    elif variant == "nan":
        raw = b'{"schema_version":NaN,"base_candidate_sha256":null,"operations":[]}'
    elif variant == "integer-too-long":
        raw = b'{"schema_version":' + b"9" * 5000 + b"}"
    elif variant == "deep-object":
        raw = b"[" * 1000 + b"0" + b"]" * 1000
    elif variant == "key-value-mismatch":
        changed = copy.deepcopy(row)
        changed["mode"] = "patch"
        changed["parameters"] = {
            "operations": [{"op": "upsert", "key": ["wrong"], "value": b["ids"]["row1"]}]
        }
        return patch_case(changed, b)
    else:
        raw = canonical_json_bytes(doc)
    try:
        module.read_patch_document(raw)
    except module.PatchRefusal as error:
        return {"status": "refused", "reason": error.reason}
    return {"status": "ok"}


def admission_case(row: dict, b: dict) -> dict:
    module = importlib.import_module("gnd.admission_validation")
    par = row["parameters"]
    mutation = par.get("mutation", "")
    refs = None
    if row["branch"] == "B26":
        b["model"] = json.loads((b["root"] / "reference-model.orm.yaml").read_text())
        if mutation in {"added-fixed", "duplicate-fixed"}:
            fixed = json.loads((b["root"] / "references/catalog.pop.json").read_text())
            fixed["facts"][b["ids"]["catalog"]].append(
                {b["ids"]["key"]: "C" if mutation == "added-fixed" else "A"}
            )
            (b["root"] / "references/catalog.pop.json").write_bytes(canonical_json_bytes(fixed))
            b["model"]["reference_populations"][0]["sha256"] = hashlib.sha256(
                (b["root"] / "references/catalog.pop.json").read_bytes()
            ).hexdigest()
        if mutation == "reference-only":
            b["population"]["facts"][b["ids"]["fact"]] = []
    rows = b["population"]["facts"][b["ids"]["fact"]]
    if par.get("partition") == "blocked":
        for r in rows:
            r[b["ids"]["quantity"]] = 0
    if mutation in {"duplicates", "candidate-duplicate"}:
        rows += copy.deepcopy(rows)
    elif mutation == "distinct":
        rows.append({b["ids"]["key"]: "C", b["ids"]["quantity"]: 3})
    elif mutation == "opaque":
        b["population"]["format_version"] = 2
        rows[0][b["ids"]["quantity"]] = {"$opaque": "pending"}
        if row["branch"] == "B17":
            # Isolate the opaque occurrence in an unconstrained fact type:
            # the guarded checker otherwise refuses the whole fact type.
            extra = copy.deepcopy(b["model"]["fact_types"][0])
            extra["id"] += "_opaque"
            b["model"]["fact_types"].append(extra)
            b["population"]["facts"][extra["id"]] = [rows.pop(0)]
    if mutation == "nonblocking-blocker":
        passing = copy.deepcopy(b["model"]["constraints"][0])
        passing["id"] += "_passing"
        passing["consequent"]["comparison"]["operator"] = "<="
        passing["consequent"]["comparison"]["right"] = 100
        b["model"]["constraints"].append(passing)
    write_json(b["root"] / "model.orm.yaml", b["model"])
    write_json(b["root"] / "candidate.pop.json", b["population"])
    model = load_model(b["root"] / "model.orm.yaml")
    population = load_population(b["root"] / "candidate.pop.json", model=model)
    if model.reference_populations:
        refs = bind_references(model, root=b["root"])
    payload = api.check(model, population, admission=True, references=refs)
    inner = payload.get("report", payload)
    side = par.get("partition", "admitted")
    entries = inner["admission"][side]
    other = inner["admission"]["blocked" if side == "admitted" else "admitted"]
    if mutation == "duplicate":
        entries.append(copy.deepcopy(entries[0]))
    elif mutation == "overlap":
        copied = copy.deepcopy(entries[0]["fact_ref"])
        other.append(
            {
                "fact_ref": copied,
                **(
                    {"opaque_deps": []} if side == "blocked" else {"blocked_by": ["constraints[0]"]}
                ),
            }
        )
    elif mutation == "missing":
        entries.pop()
    elif mutation in {"negative", "range", "bool-index", "unknown-fact"}:
        entries[0]["fact_ref"].update(
            {"index": {"negative": -1, "range": 2, "bool-index": True}.get(mutation, 0)}
        )
        if mutation == "unknown-fact":
            entries[0]["fact_ref"]["fact_type"] = "not-declared"
    elif mutation == "count":
        inner["counts"]["pass"] += 1
    elif mutation in {"bad-blocker", "nonblocking-blocker"}:
        if side == "admitted":
            bad = entries.pop(0)
            other.append(
                {
                    "fact_ref": bad["fact_ref"],
                    "blocked_by": ["absent" if mutation == "bad-blocker" else "constraints[1]"],
                }
            )
        else:
            entries[0]["blocked_by"] = (
                ["absent"] if mutation == "bad-blocker" else ["constraints[1]"]
            )
    elif mutation in {"bad-opaque-role", "duplicate-opaque"}:
        if side == "blocked":
            bad = entries.pop(0)
            other.append({"fact_ref": bad["fact_ref"], "opaque_deps": []})
            target = other[-1]
        else:
            target = entries[0]
        dep = {
            "fact_ref": {"fact_type": b["ids"]["fact"], "index": 0},
            "role": "absent" if mutation == "bad-opaque-role" else b["ids"]["quantity"],
        }
        target["opaque_deps"] = [dep] * (2 if mutation == "duplicate-opaque" else 1)
    elif mutation == "reference-origin-forged":
        next(r for r in payload["occurrence_origins"] if r["origin"]["kind"] == "candidate")[
            "origin"
        ]["kind"] = "reference"
    before_validation = copy.deepcopy(population.facts)
    try:
        metrics = module.validate_admission_payload(
            payload, model=model, candidate=population, references=refs
        )
    except module.AdmissionValidationError:
        return {
            "status": "refused",
            **(
                {"progress_invariant": population.facts == before_validation}
                if row["branch"] == "B26"
                else {}
            ),
        }
    result = {"status": "ok", **metrics}
    if row["branch"] == "B26":
        result["progress_invariant"] = metrics["candidate_admitted_unique"] == (
            0 if mutation == "reference-only" else 2
        )
    return result


def public_case(row: dict, b: dict) -> dict:
    variant = row["parameters"]["variant"]
    if variant.startswith("temporal-reference"):
        b["model"] = json.loads((b["root"] / "reference-model.orm.yaml").read_text())
        if variant.endswith("blocked"):
            b["population"]["facts"][b["ids"]["fact"]][0][b["ids"]["key"]] = "unapproved"
    if variant == "reference-blocker":
        b["model"] = json.loads((b["root"] / "reference-model.orm.yaml").read_text())
        b["population"]["facts"][b["ids"]["fact"]][0][b["ids"]["key"]] = "unapproved"
    else:
        b["model"]["object_types"].append(
            {"id": "calendar_day", "name": "Day", "kind": "value", "primitive": "Date"}
        )
        b["model"]["fact_types"][0]["roles"] += [
            {"role_name": "start", "object_type": "calendar_day"},
            {"role_name": "deadline", "object_type": "calendar_day"},
        ]
        b["model"]["fact_types"][0]["reading"] += " at {Day} before {Day}"
        b["model"]["constraints"][0]["antecedent"][0]["bind"].update(start="$s", deadline="$d")
        b["model"]["constraints"][0]["consequent"]["comparison"] = {
            "left": {"fn": "date_add", "args": ["$s", {"duration_days": 2}]},
            "operator": "<=",
            "right": "$d",
        }
        if variant == "warning":
            b["model"]["constraints"][0]["modality"] = "deontic"
        for r in b["population"]["facts"][b["ids"]["fact"]]:
            r.update(
                start="2026-10-02",
                deadline="2026-10-03" if variant in {"late", "warning"} else "2026-10-04",
            )
            if variant == "overflow":
                r["start"] = "9999-12-31"
            if variant == "opaque":
                r["start"] = {"$opaque": "pending"}
        for rule in b["model"]["constraints"]:
            for atom in rule.get("antecedent", []):
                if atom["fact_type"] == b["ids"]["fact"]:
                    atom["bind"].update(start="$s", deadline="$d")
        if variant == "opaque":
            b["population"]["format_version"] = 2
        if variant == "empty":
            b["population"]["facts"][b["ids"]["fact"]] = []
    write_json(b["root"] / "model.orm.yaml", b["model"])
    write_json(b["root"] / "candidate.pop.json", b["population"])
    loaded = load_model(b["root"] / "model.orm.yaml")
    context = bind_references(loaded, root=b["root"]) if loaded.reference_populations else None
    payload = api.check(
        loaded, b["root"] / "candidate.pop.json", admission=True, references=context
    )
    wire = json.loads((CORPUS / "wire-fields.json").read_text())
    import io
    from contextlib import redirect_stdout

    stream = io.StringIO()
    with redirect_stdout(stream):
        cli_exit = main(
            [
                "check",
                str(b["root"] / "model.orm.yaml"),
                str(b["root"] / "candidate.pop.json"),
                "--admission",
                "--format",
                "json",
            ]
        )
    cli_payload = json.loads(stream.getvalue())
    assert (cli_exit, cli_payload["schema_version"]) == (
        payload["exit_code"],
        payload["schema_version"],
    )
    assert (
        cli_payload.get("report", cli_payload)["admission"]
        == payload.get("report", payload)["admission"]
    )
    if payload["schema_version"] == 14:
        assert sorted(payload) == wire["root_keys"]["temporal_reference_wrapper"]
        assert sorted(payload["report"]) == wire["root_keys"]["temporal_admission_report"]
        assert payload["report"]["schema_version"] == 13
    elif payload["schema_version"] == 13:
        assert sorted(payload) == wire["root_keys"]["temporal_admission_report"]
    return {"exit_code": payload["exit_code"], "schema_version": payload["schema_version"]}


def producer_source() -> str:
    # This script transports fixture proposals; it performs no feature computation.
    return """import base64,json,pathlib,sys
if sys.argv[1:] == ['--version']:
 print('v71-corpus-command 1');raise SystemExit(0)
plan=json.loads(pathlib.Path(sys.argv[1]).read_text())
log=pathlib.Path(sys.argv[2]);log.mkdir(exist_ok=True)
index=len(list(log.glob('stdin-*.bin')))
raw=sys.stdin.buffer.read();(log/f'stdin-{index:04d}.bin').write_bytes(raw)
frame=json.loads(raw) if raw else {}
feedback=json.loads(base64.b64decode(frame['feedback_base64'])) if frame.get('feedback_base64') else None
item=plan[min(index,len(plan)-1)]
if item.get('direct_edit'):
 pathlib.Path(item['direct_edit']).write_text('tampered')
if item.get('remove'):
 pathlib.Path(item['remove']).unlink()
if item.get('symlink'):
 p=pathlib.Path(item['symlink']);p.unlink(missing_ok=True);p.symlink_to(sys.argv[1])
for path,value in item.get('raw_files',{}).items():
 pathlib.Path(path).write_text(value)
for path,value in item.get('files',{}).items():
 p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\\n')
if 'proposal' in item:
 proposal=item['proposal']
 if proposal.get('base_candidate_sha256')=='CURRENT':
  proposal['base_candidate_sha256']=feedback['candidate_edit_context']['base_candidate_sha256']
 pathlib.Path('.gnd-patch.json').write_text(json.dumps(proposal,sort_keys=True,separators=(',',':'))+'\\n')
"""


def session_case(row: dict, b: dict) -> dict:
    p = row["parameters"]
    variant = p.get("variant", "")
    experiment = "EXP-714-corpus"
    parent = b["root"] / "experiment"
    assert (
        main(
            [
                "exp",
                "init",
                experiment,
                "--out",
                str(parent),
                "--kind",
                "data-driven",
                "--question",
                "Q1=Does the declared candidate meet the frozen relation?",
            ]
        )
        == 0
    )
    root = parent / experiment
    candidate = root / "candidate"
    candidate.mkdir()
    model = copy.deepcopy(b["model"])
    initial = copy.deepcopy(b["population"])
    if variant in {"reference-repair", "transition-reference", "annotation-mixed"}:
        model = json.loads((b["root"] / "reference-model.orm.yaml").read_text())
        shutil.copytree(b["root"] / "references", root / "references")
        fixed = json.loads((root / "references/catalog.pop.json").read_text())
        fixed["facts"][b["ids"]["catalog"]].append({b["ids"]["key"]: "C"})
        if variant == "annotation-mixed":
            model["constraints"][0]["owner"] = "reference"
            model["constraints"][0]["antecedent"].append(
                {"fact_type": b["ids"]["catalog"], "bind": {b["ids"]["key"]: "$k"}}
            )
            model["constraints"][0]["allowed_fixes"] = []
        write_json(root / "references/catalog.pop.json", fixed)
        model["reference_populations"][0]["sha256"] = hashlib.sha256(
            (root / "references/catalog.pop.json").read_bytes()
        ).hexdigest()
    if variant == "temporal-repair":
        model["object_types"].append(
            {"id": "calendar_day", "name": "Day", "kind": "value", "primitive": "Date"}
        )
        model["fact_types"][0]["roles"] += [
            {"role_name": "start", "object_type": "calendar_day"},
            {"role_name": "deadline", "object_type": "calendar_day"},
        ]
        model["fact_types"][0]["reading"] += " at {Day} before {Day}"
        model["constraints"][0]["antecedent"][0]["bind"].update(start="$s", deadline="$d")
        model["constraints"][0]["consequent"]["comparison"] = {
            "left": {"fn": "date_add", "args": ["$s", {"duration_days": 2}]},
            "operator": "<=",
            "right": "$d",
        }
    if variant == "transition-reference":
        model["operations"] = [
            {
                "id": "record_work",
                "reading": "Record {"
                + model["object_types"][0]["name"]
                + "} with {"
                + model["object_types"][1]["name"]
                + "}",
                "parameters": [
                    {"name": "key", "object_type": model["object_types"][0]["id"]},
                    {"name": "quantity", "object_type": model["object_types"][1]["id"]},
                ],
                "effects": [
                    {
                        "assert": {
                            "fact_type": b["ids"]["fact"],
                            "bind": {b["ids"]["key"]: "$key", b["ids"]["quantity"]: "$quantity"},
                        }
                    }
                ],
                "frame": {"modality": "alethic"},
                "source": "user-supplied",
                "status": "confirmed",
                "provenance": {"user_quote": "Record the additional approved work."},
            }
        ]
    write_json(root / "model.orm.yaml", model)
    write_json(candidate / "candidate.pop.json", initial)
    write_json(candidate / "notes.json", {"note": "unchanged"})
    write_json(candidate / "kept.json", {"keep": True})
    contract = copy.deepcopy(b["contract"])
    data = (root / "model.orm.yaml").read_bytes()
    contract["cases"][0]["verify"]["model"].update(
        sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data)
    )
    # Required floor keeps ranking demonstrations nonaccepted even with clean rows.
    contract["cases"][0]["acceptance"]["coverage"][0]["min_facts"] = 3
    if variant in {"reference-repair", "transition-reference", "annotation-mixed"}:
        contract["cases"][0]["reference_root"] = "."
    patch_mode = variant in {"patch-repair", "reference-repair", "protected", "patch-byte-noise"}
    if patch_mode:
        contract["candidate_edits"] = {
            "patch_path": ".gnd-patch.json",
            "artifacts": b["ids"]["artifacts"],
        }
    a = copy.deepcopy(initial)
    a["facts"][b["ids"]["fact"]] = (
        [] if b["ids"]["row1"] is None else [copy.deepcopy(b["ids"]["row1"])]
    )
    other = copy.deepcopy(a)
    if other["facts"][b["ids"]["fact"]]:
        other["facts"][b["ids"]["fact"]][0][b["ids"]["quantity"]] = 2
    better = copy.deepcopy(initial)
    third = copy.deepcopy(a)
    if third["facts"][b["ids"]["fact"]]:
        third["facts"][b["ids"]["fact"]][0][b["ids"]["quantity"]] = 3
    accepted = copy.deepcopy(initial)
    accepted["facts"][b["ids"]["fact"]].append({b["ids"]["key"]: "C", b["ids"]["quantity"]: 3})
    if variant == "temporal-repair":
        for pop in (a, other, better, third, accepted, initial):
            for r in pop["facts"][b["ids"]["fact"]]:
                r.update(
                    start="2026-10-02", deadline="2026-10-04" if pop is accepted else "2026-10-03"
                )
    sequence = [a, accepted]
    if variant in {"earlier-better", "rejected-high-score"}:
        sequence = [better, a]
    elif variant == "later-better":
        sequence = [a, better]
    elif variant in {"tie", "case-order", "resume", "tampered-score"}:
        sequence = [a, other]
    elif variant in {"same-candidate", "patch-byte-noise", "annotation-parse", "annotation-mixed"}:
        sequence = [a, a]
    elif variant == "a-b-a":
        sequence = [a, other, a]
    elif variant == "distinct-rejected":
        sequence = [a, other, third]
    elif variant == "accepted-repeated":
        contract["cases"][0]["acceptance"]["coverage"][0]["min_facts"] = 1
        sequence = [a, a]
    if row["branch"] in {"B16", "B18"}:
        contract["ranking"] = [{"metric": "candidate_admitted_unique", "direction": "max"}]
    if variant == "case-order":
        second = copy.deepcopy(contract["cases"][0])
        second["case_id"] = "z-last-in-canonical-order"
        contract["cases"].insert(0, second)
    contract["max_attempts"] = len(sequence)
    plan = []
    for index, pop in enumerate(sequence):
        if patch_mode:
            ops = [
                {"op": "replace-artifact", "artifact": "candidate.pop.json", "value": pop},
                {
                    "op": "replace-artifact",
                    "artifact": "notes.json",
                    "value": {"note": "unchanged"},
                },
            ]
            plan.append({"proposal": proposal(b, ops, None if index == 0 else "CURRENT")})
        else:
            plan.append({"files": {"candidate.pop.json": pop}})
    if variant == "annotation-parse":
        plan = [{"raw_files": {"candidate.pop.json": "{broken-json"}} for _ in sequence]
    if variant == "protected":
        target = p["target"]
        if target in {"direct-byte-edit", "extra-file", "missing-file"}:
            plan[-1]["remove" if target == "missing-file" else "direct_edit"] = (
                "kept.json" if target != "extra-file" else "extra.json"
            )
        else:
            plan[-1]["proposal"]["operations"].append(
                {
                    "op": "replace-artifact",
                    "artifact": f"{target}.json",
                    "value": {"tampered": True},
                }
            )
    if variant == "transition-reference":
        pre = canonical_json_bytes(initial)
        (root / "input").mkdir()
        (root / "input/pre.json").write_bytes(pre)
        case = contract["cases"][0]
        case["inputs"] = [
            {
                "path": "input/pre.json",
                "sha256": hashlib.sha256(pre).hexdigest(),
                "size_bytes": len(pre),
                "media_type": "application/json",
                "encoding": "utf-8",
            }
        ]
        case["acceptance"] = {
            "mode": "transition",
            "walk": {
                "required_ops": [{"op": "record_work", "bindings_subset": {"quantity": 1}}],
                "forbidden_ops": [],
            },
        }
        case["verify"] = {
            "command": "transition",
            "model": case["verify"]["model"],
            "pre": "input/pre.json",
            "steps": "steps.json",
            "post": None,
        }
        from gnd.transition import model_digest, operations_digest

        loaded_model = load_model(root / "model.orm.yaml")
        plan = [
            {
                "files": {
                    "steps.json": {
                        "steps_schema": 1,
                        "model": "model.orm.yaml",
                        "model_digest": model_digest(loaded_model),
                        "operations_digest": operations_digest(loaded_model.operations),
                        "steps": [{"op": "record_work", "bindings": {"key": "C", "quantity": q}}],
                    }
                }
            }
            for q in (0, 1)
        ]
    write_json(root / "session.contract.json", contract)
    log = b["root"] / "producer-log"
    write_json(b["root"] / "producer-plan.json", plan)
    agent = b["root"] / "producer.py"
    agent.write_text(producer_source())
    policy = b["root"] / "command.policy.json"
    write_json(
        policy,
        {
            "schema_version": 1,
            "policy_id": "local-command",
            "kind": "command",
            "executable": sys.executable,
            "argv": [str(agent), str(b["root"] / "producer-plan.json"), str(log)],
            "version_argv": [str(agent), "--version"],
            "prompt_transport": "stdin",
            "environment_allowlist": ["PATH", "TMPDIR", "LANG", "LC_ALL"],
        },
    )
    exit_code = main(
        ["exp", "run", str(root), "--adapter-policy", str(policy), "--wall-seconds", "60"]
    )
    run = root / "runs/run-0001"
    result = json.loads((run / "result.json").read_text())
    attempts = [
        json.loads(x.read_text()) for x in sorted((run / "attempts").glob("*/attempt.json"))
    ]
    wire = json.loads((CORPUS / "wire-fields.json").read_text())
    assert result["schema_version"] == wire["versions"]["result"]
    assert sorted(result) == wire["root_keys"]["result"]
    assert attempts, "a command session must retain an attempt"
    for directory, saved in zip(
        sorted((run / "attempts").glob("*/attempt.json")), attempts, strict=True
    ):
        assert saved["schema_version"] == wire["versions"]["attempt"]
        assert sorted(saved) == wire["root_keys"]["attempt"]
        if saved["candidate_edit"] is not None:
            assert sorted(saved["candidate_edit"]) == wire["candidate_edit_keys"]
        for leaf, audience in (("feedback", "candidate"), ("operator_feedback", "operator")):
            encoded = (directory.parent / saved[leaf]["path"]).read_bytes()
            decoded = json.loads(encoded)
            assert decoded["schema_version"] == wire["versions"]["feedback"]
            assert sorted(decoded) == wire["root_keys"]["feedback"]
            assert decoded["audience"] == audience
            assert hashlib.sha256(encoded).hexdigest() == saved[leaf]["sha256"]
    for leaf in sorted((run / "launches").glob("*.json")):
        launch = json.loads(leaf.read_text())
        assert launch["schema_version"] == wire["versions"]["launch"]
        assert sorted(launch) == wire["root_keys"]["launch"]
    result["exit_code"] = exit_code
    result["best_attempt_index"] = result["best_attempt"]
    result["_run_root"] = run
    result["_attempts"] = attempts
    result["_producer_log"] = log
    result["real_command"] = all(x["invocation"]["policy_id"] == "local-command" for x in attempts)
    result["no_partial_publish"] = all(
        x["candidate_edit"]["result_candidate_sha256"] is None
        for x in attempts
        if isinstance(x.get("candidate_edit"), dict)
        and x["candidate_edit"].get("refusal") is not None
    )
    if variant in {"resume", "tampered-score"}:
        from gnd.exp.session import case_payload_versions
        from gnd.exp.session_contract import read_session_contract

        loaded_contract = read_session_contract(
            root / "session.contract.json", experiment_root=root, experiment_id=experiment
        )
        # Exercise reconstruction of this exact run; the CLI always starts a new run.
        (run / "result.json").unlink()
        before = len(list(log.glob("stdin-*.bin")))
        if variant == "tampered-score":
            saved = run / "best.json"
            changed = json.loads(saved.read_text())
            changed["attempt_index"] = 2
            write_json(saved, changed)
        try:
            reconstructed = SessionStore(run, run_id=result["run_id"]).read_resume_state(
                loaded_contract,
                expected_payload_versions=case_payload_versions(loaded_contract, root),
            )
        except ValueError:
            result["resume_refused"] = True
        else:
            result["resume_refused"] = False
            assert reconstructed.best_attempt_identity is not None
            assert reconstructed.best_attempt_identity.attempt_index == result["best_attempt"]
        assert len(list(log.glob("stdin-*.bin"))) == before
    return result


def assert_answer(observed: dict, expected: dict) -> None:
    for key, value in expected.items():
        if key != "id":
            assert key in observed, f"missing observation {key}"
            assert observed[key] == value, f"{key}: got {observed[key]!r}, expected {value!r}"


def contract_case(row: dict, b: dict) -> dict:
    from gnd.exp.session_contract import SessionContractError, read_session_contract

    par = row["parameters"]
    doc = copy.deepcopy(b["contract"])
    variant = par["variant"]
    if variant == "unknown-version":
        doc["schema_version"] = 99
    elif variant == "unknown-rank":
        doc["ranking"] = [{"metric": "producer-score", "direction": "max"}]
    elif variant in {"path-overlap", "protected-target"}:
        doc["candidate_edits"] = {
            "patch_path": ".gnd-patch.json",
            "artifacts": copy.deepcopy(b["ids"]["artifacts"]),
        }
        if variant == "path-overlap":
            doc["candidate_edits"]["artifacts"].append(
                {"path": "candidate.pop.json/child", "collections": []}
            )
        else:
            doc["candidate_edits"]["artifacts"].append(
                {"path": "model.orm.yaml", "collections": []}
            )
    elif variant == "bool-attempts":
        doc["max_attempts"] = True
    elif variant == "bound-model-changed":
        (b["root"] / "model.orm.yaml").write_text("tampered")
    elif variant == "bound-reference-changed":
        doc["cases"][0]["reference_root"] = "."
        data = (b["root"] / "reference-model.orm.yaml").read_bytes()
        (b["root"] / "model.orm.yaml").write_bytes(data)
        doc["cases"][0]["verify"]["model"].update(
            sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data)
        )
        (b["root"] / "references/catalog.pop.json").write_text("tampered")
    elif variant == "missing-policy":
        # File-not-found is the existing public CLI 66, not malformed-contract 3.
        parent = b["root"] / "preflight"
        assert (
            main(
                [
                    "exp",
                    "init",
                    "EXP-714-corpus",
                    "--out",
                    str(parent),
                    "--kind",
                    "data-driven",
                    "--question",
                    "Q1=Preflight?",
                ]
            )
            == 0
        )
        experiment = parent / "EXP-714-corpus"
        (experiment / "model.orm.yaml").write_bytes((b["root"] / "model.orm.yaml").read_bytes())
        write_json(experiment / "session.contract.json", doc)
        code = main(
            ["exp", "run", str(experiment), "--adapter-policy", str(parent / "absent.json")]
        )
        assert not (experiment / "runs").exists() or not list(
            (experiment / "runs").glob("*/launches/*")
        )
        return {"exit_code": code, "invocations": 0}
    path = b["root"] / "session.contract.json"
    write_json(path, doc)
    try:
        read_session_contract(path, experiment_root=b["root"], experiment_id=doc["experiment_id"])
    except SessionContractError:
        return {"exit_code": 3, "invocations": 0}
    return {"exit_code": 0, "invocations": 0}


def annotation_case(row: dict, b: dict) -> dict:
    from gnd.model import ModelLoadError, ModelValidationError

    variant = row["parameters"]["variant"]
    doc = b["model"]
    rule = doc["constraints"][0]
    if variant == "unknown-owner":
        rule["owner"] = "producer"
    elif variant == "unknown-fix":
        rule["allowed_fixes"] = ["shell"]
    elif variant == "owner-type":
        rule["owner"] = ["candidate"]
    elif variant == "fix-container":
        rule["allowed_fixes"] = {"add-fact": True}
    elif variant == "too-many-fixes":
        rule["allowed_fixes"] = [
            "add-fact",
            "replace-fact",
            "delete-fact",
            "replace-artifact",
            "add-fact",
        ]
    elif variant == "duplicate-fixes":
        rule["allowed_fixes"] = ["add-fact", "add-fact"]
    elif variant == "wrong-site":
        doc["object_types"][0]["owner"] = "candidate"
    elif variant in {"parse-not-hidden", "floor-not-hidden", "mixed-origin"}:
        rule["owner"] = "host" if variant != "mixed-origin" else "reference"
        modified = copy.deepcopy(row)
        modified["parameters"] = {
            "variant": {
                "parse-not-hidden": "annotation-parse",
                "mixed-origin": "annotation-mixed",
            }.get(variant, "distinct-rejected")
        }
        if variant == "mixed-origin":
            b["ids"]["row1"][b["ids"]["quantity"]] = 0
        result = session_case(modified, b)
        assert result["exit_code"] == 15
        attempt = result["_attempts"][0]
        assert result["disposition"] != "accepted"
        if variant == "mixed-origin":
            assert any(
                v["verdict"] == "fail" for v in attempt["evaluation"]["results"][0]["verdicts"]
            )
        elif variant == "parse-not-hidden":
            assert not attempt["evaluation"]["results"][0]["verdicts"]
        return {"exit_code": 15}
    write_json(b["root"] / "model.orm.yaml", doc)
    try:
        load_model(b["root"] / "model.orm.yaml")
    except (ModelLoadError, ModelValidationError):
        return {"exit_code": 3}
    return {"exit_code": 0}


def feedback_case(row: dict, b: dict) -> dict:
    import base64

    par = row["parameters"]
    c = b["model"]["constraints"][0]
    c["owner"] = par.get("owner", "candidate")
    c["allowed_fixes"] = ["replace-fact"]
    c["modality"] = par.get("modality", "alethic")
    verdict = par.get("verdict", "fail")
    if verdict == "fail":
        b["ids"]["row1"][b["ids"]["quantity"]] = 0
    elif verdict == "unchecked":
        b["population"]["format_version"] = 2
        b["ids"]["row1"][b["ids"]["quantity"]] = {"$opaque": "awaiting"}
    elif verdict == "vacuous":
        b["population"]["facts"][b["ids"]["fact"]] = []
        # Empty first/retry snapshots, keeping a required coverage gap.
        b["ids"]["row1"] = None
    variant = par.get("variant", "")
    if variant:
        b["model"]["fact_types"][0]["roles"][0]["redact"] = True
        for r in b["population"]["facts"][b["ids"]["fact"]]:
            r[b["ids"]["key"]] = "P4_PRIVATE_CANARY"
        if b["ids"]["row1"]:
            b["ids"]["row1"][b["ids"]["key"]] = "P4_PRIVATE_CANARY"
        c["owner"] = {
            "candidate-secret": "candidate",
            "reference-secret": "reference",
            "host-secret": "host",
        }.get(variant, "candidate")
    modified = copy.deepcopy(row)
    modified["parameters"] = {"variant": "same-candidate"}
    result = session_case(modified, b)
    run = result["_run_root"]
    attempt = result["_attempts"][0]
    candidate_bytes = (run / "attempts/0001" / attempt["feedback"]["path"]).read_bytes()
    operator_bytes = (run / "attempts/0001" / attempt["operator_feedback"]["path"]).read_bytes()
    operator = json.loads(operator_bytes)
    projected = json.loads(candidate_bytes)
    retry_raw = (result["_producer_log"] / "stdin-0001.bin").read_bytes()
    retry = base64.b64decode(json.loads(retry_raw)["feedback_base64"])
    stdin_bound = (
        retry == candidate_bytes
        and hashlib.sha256(candidate_bytes).hexdigest()
        == result["_attempts"][1]["invocation"]["feedback_sha256"]
    )
    target = "constraints[0]"

    def refs(node: object) -> list[str]:
        if isinstance(node, dict):
            found = [node["constraint_ref"]] if "constraint_ref" in node else []
            return found + [item for value in node.values() for item in refs(value)]
        if isinstance(node, list):
            return [item for value in node for item in refs(value)]
        return []

    assert target in refs(operator), "operator feedback lost the full finding"
    # Mechanical evaluation is retained independently from projected feedback.
    retained = {x["constraint_ref"]: x for x in attempt["evaluation"]["results"][0]["verdicts"]}
    assert retained[target]["verdict"] == (
        "warning" if verdict == "fail" and c["modality"] == "deontic" else verdict
    )
    assert retained[target]["modality"] == c["modality"]
    return {
        "mechanical_invariant": operator["acceptance_ready"]
        == projected["acceptance_ready"]
        == False,
        "candidate_visible": target in refs(projected),
        "secret_visible": b"P4_PRIVATE_CANARY" in candidate_bytes,
        "stdin_bound": stdin_bound,
    }


def rank_case(row: dict, b: dict) -> dict:
    from gnd.exp.session_eval import AttemptEvaluation, best_key, validate_verifier_payload

    par = row["parameters"]
    contract_doc = copy.deepcopy(b["contract"])
    contract_doc["ranking"] = [
        {"metric": "candidate_admitted_unique", "direction": par["direction"]}
    ]
    payload = api.check(
        b["root"] / "model.orm.yaml", b["root"] / "candidate.pop.json", admission=True
    )
    result = validate_verifier_payload(
        canonical_json_bytes(payload),
        case_id="work",
        role="required",
        process_exit=payload["exit_code"],
        expected_command="check",
        expected_model=str(b["root"] / "model.orm.yaml"),
        expected_subject=str(b["root"] / "candidate.pop.json"),
        candidate_sha256="a" * 64,
        contract_sha256="b" * 64,
        evidence_candidate_sha256="a" * 64,
        evidence_contract_sha256="b" * 64,
        expected_schema_version=10,
    )
    validator = importlib.import_module("gnd.admission_validation")
    model = load_model(b["root"] / "model.orm.yaml")
    pop = load_population(b["root"] / "candidate.pop.json", model=model)
    result.__pydantic_private__["_admission_metrics"] = validator.validate_admission_payload(
        payload, model=model, candidate=pop
    )
    variant = par["variant"]
    available = AttemptEvaluation(
        attempt_index=2, candidate_sha256="a" * 64, contract_sha256="b" * 64, results=(result,)
    )
    missing = available.model_copy(update={"attempt_index": 1, "results": ()})
    if variant == "missing-case":
        available = available.model_copy(update={"results": ()})
    elif variant == "exact-nonadmission":
        result.__pydantic_private__["_admission_metrics"] = None
    elif variant == "mixed-tests":
        second = copy.deepcopy(
            json.loads((CORPUS / "legacy-contracts.json").read_text())["3"]["input"]["cases"][0]
        )
        second["case_id"] = "missing-tests-observation"
        contract_doc["cases"].append(second)
    elif variant == "diagnostic-excluded":
        diagnostic = copy.deepcopy(contract_doc["cases"][0])
        diagnostic["case_id"] = "diagnostic"
        diagnostic["role"] = "diagnostic"
        contract_doc["cases"].append(diagnostic)
    contract = DataDrivenContract.model_validate(contract_doc)
    observed = best_key(contract, available)
    absent = best_key(contract, missing)
    # Availability is the first ascending element, independent of direction.
    return {
        "available": observed[0] == 0,
        "unavailable_last": absent[0] == 1 and (observed[0] == 1 or observed < absent),
    }


def publication_case(row: dict, b: dict, monkeypatch) -> dict:
    module = importlib.import_module("gnd.exp.session_patch")
    import gnd.exp.session_store as store_module
    from gnd.exp.session import case_payload_versions
    from gnd.exp.session_contract import read_session_contract

    variant = row["parameters"]["variant"]
    if variant.startswith("resume-tampered"):
        modified = copy.deepcopy(row)
        modified["parameters"] = {"variant": "patch-repair"}
        result = session_case(modified, b)
        run = result["_run_root"]
        root = run.parent.parent
        store = SessionStore(run, run_id=result["run_id"])
        (run / "result.json").unlink()
        contract = read_session_contract(
            root / "session.contract.json", experiment_root=root, experiment_id=root.name
        )
        versions = case_payload_versions(contract, root)
        assert (
            store.read_resume_state(contract, expected_payload_versions=versions).next_attempt_index
            == 3
        )
        retained = run / "attempts/0001"
        leaf = retained / (
            "patch.proposal.json"
            if variant.endswith("proposal")
            else "candidate/candidate.pop.json"
        )
        assert leaf.is_file(), "tamper control must address retained, digest-bound evidence"
        previous_attempts = {p: p.read_bytes() for p in (run / "attempts").glob("*/attempt.json")}
        previous_best = (run / "best.json").read_bytes()
        leaf.write_bytes(b"tampered\n")
        with __import__("pytest").raises(ValueError):
            store.read_resume_state(contract, expected_payload_versions=versions)
        return {
            "prior_bytes_intact": all(p.read_bytes() == raw for p, raw in previous_attempts.items())
            and (run / "best.json").read_bytes() == previous_best,
            "no_partial_publish": len(list((run / "attempts").glob("*/attempt.json"))) == 2,
        }
    base, digest, before = base_files(b)
    store = SessionStore(b["root"] / "publication-store", run_id="corpus")
    seeded = copy.deepcopy(b["population"])
    seeded["facts"][b["ids"]["fact"]].append(
        {b["ids"]["key"]: "C", b["ids"]["quantity"]: 3}
    )
    doc = proposal(
        b,
        [
            {"op": "replace-artifact", "artifact": "candidate.pop.json", "value": seeded},
            {"op": "replace-artifact", "artifact": "notes.json", "value": {"note": "unchanged"}},
        ],
        None,
    )
    kwargs = {
        "attempt_index": 1,
        "base_root": base,
        "base_sha256": digest,
        "proposal_raw": canonical_json_bytes(doc),
        "contract": patch_contract(b),
    }
    if variant == "crash-before-marker":
        staged = store.stage_patch_candidate(**kwargs)
        assert staged.snapshot_path.is_dir()
        assert (
            json.loads((staged.snapshot_path / "candidate.pop.json").read_bytes())["facts"][
                b["ids"]["fact"]
            ][-1][b["ids"]["key"]]
            == "C"
        )
        # Simulate process loss after staging and before the immutable marker.
        reopened = SessionStore(store.root, run_id="corpus")
        with __import__("pytest").raises(ValueError, match="staging|partial|unpublished"):
            reopened.read_resume_state(patch_contract(b))
    else:
        counter = {"calls": 0}
        point = {
            "write": "_write_new_file_at",
            "fsync": "fsync",
            "publish": "publish_directory_once",
        }[variant]
        from gnd import artifacts

        target = (
            artifacts.os
            if point == "fsync"
            else artifacts
            if point == "_write_new_file_at"
            else store_module
        )
        original = getattr(target, point)

        def inject(*args, **kwargs):
            counter["calls"] += 1
            if counter["calls"] == 2 or point == "publish_directory_once":
                raise OSError("phase4 fault injection")
            return original(*args, **kwargs)

        monkeypatch.setattr(target, point, inject)
        with __import__("pytest").raises((OSError, module.PatchRefusal)):
            store.stage_patch_candidate(**kwargs)
        assert counter["calls"] > 0, "injection did not fire"
        assert not store._staged, "a failed preparation exposed a verifier-ready handle"
    return {
        "prior_bytes_intact": all(
            (base / name).read_bytes() == data for name, data in before.items()
        ),
        "no_partial_publish": not list((store.root / "attempts").glob("*/attempt.json")),
    }


def limit_case(row: dict, b: dict, monkeypatch) -> dict:
    from gnd.exp.session_contract import SessionContractError, read_session_contract
    from gnd.exp.session_eval import VerifierPayloadError, validate_verifier_payload
    from gnd.model import ModelLoadError, ModelValidationError

    patch = importlib.import_module("gnd.exp.session_patch")
    validation = importlib.import_module("gnd.admission_validation")
    name = row["parameters"]["limit"]
    n = row["parameters"]["value"]
    doc = proposal(
        b, [{"op": "replace-artifact", "artifact": "notes.json", "value": {"n": 1}}], "a" * 64
    )
    contract = copy.deepcopy(b["contract"])
    contract["candidate_edits"] = {
        "patch_path": ".gnd-patch.json",
        "artifacts": copy.deepcopy(b["ids"]["artifacts"]),
    }
    try:
        if name in {"patch-bytes", "json-depth", "numeric-digits"}:
            if name == "patch-bytes":
                raw = canonical_json_bytes(doc)
                raw += b" " * (n - len(raw))
                assert len(raw) == n
            else:
                value = 10 ** (n - 1) if name == "numeric-digits" else 0
                if name == "json-depth":
                    for _ in range(n - 3):
                        value = [value]
                doc["operations"][0]["value"] = value
                raw = canonical_json_bytes(doc)
            patch.read_patch_document(raw)
        elif name in {"contract-bytes", "bound-input-bytes"}:
            if name == "bound-input-bytes":
                model_size = (b["root"] / "model.orm.yaml").stat().st_size
                remaining = n - model_size
                while remaining:
                    size = min(remaining, 10 * 1024 * 1024)
                    relative = f"inputs/{len(contract['cases'][0]['inputs'])}.txt"
                    path = b["root"] / relative
                    path.parent.mkdir(exist_ok=True)
                    data = b"a" * size
                    path.write_bytes(data)
                    contract["cases"][0]["inputs"].append(
                        {
                            "path": relative,
                            "sha256": hashlib.sha256(data).hexdigest(),
                            "size_bytes": size,
                            "media_type": "text/plain",
                            "encoding": "utf-8",
                        }
                    )
                    remaining -= size
            raw = canonical_json_bytes(contract)
            if name == "contract-bytes":
                raw += b" " * (n - len(raw))
                assert len(raw) == n
            path = b["root"] / "session.contract.json"
            path.write_bytes(raw)
            read_session_contract(
                path, experiment_root=b["root"], experiment_id=contract["experiment_id"]
            )
        elif name in {"rank-metrics", "artifacts", "collections", "attempts", "path-bytes"}:
            if name == "rank-metrics":
                names = [
                    "accepted_required_cases",
                    "candidate_admitted_unique",
                    "alethic_failures",
                    "alethic_indeterminate",
                    "coverage_shortfall",
                ]
                contract["ranking"] = [
                    {"metric": names[i % 5], "direction": "min"} for i in range(n)
                ]
            elif name == "artifacts":
                contract["candidate_edits"]["artifacts"] = [
                    {"path": f"item-{i}.json", "collections": []} for i in range(n)
                ]
            elif name == "collections":
                contract["candidate_edits"]["artifacts"] = [
                    {
                        "path": "items.json",
                        "collections": [{"path": [f"rows-{i}"], "key": ["key"]} for i in range(n)],
                    }
                ]
            elif name == "attempts":
                contract["max_attempts"] = n
            else:
                segments = ["p" * 127 for _ in range(31)]
                prefix = "/".join(segments) + "/"
                contract["candidate_edits"]["artifacts"][0]["path"] = prefix + "x" * (
                    n - len(prefix)
                )
            DataDrivenContract.model_validate(contract)
        elif name == "allowed-fixes":
            fixes = ["add-fact", "replace-fact", "delete-fact", "replace-artifact"]
            b["model"]["constraints"][0]["allowed_fixes"] = [fixes[i % 4] for i in range(n)]
            write_json(b["root"] / "model.orm.yaml", b["model"])
            load_model(b["root"] / "model.orm.yaml")
        elif name in {
            "selector-segments",
            "key-fields",
            "scalar-bytes",
            "operations",
            "collection-rows",
        }:
            base, digest, _ = base_files(b)
            population = b["population"]
            key = b["ids"]["key"]
            quantity = b["ids"]["quantity"]
            ft = b["ids"]["fact"]
            collection = contract["candidate_edits"]["artifacts"][0]["collections"][0]
            operation = {
                "op": "delete",
                "artifact": "candidate.pop.json",
                "collection": ["facts", ft],
                "key": ["A"],
            }
            operations = [operation]
            if name in {"operations", "collection-rows"}:
                population["facts"][ft] = [{key: f"A{i}", quantity: 1} for i in range(n)]
                operations = [
                    {**operation, "key": [f"A{i}"]} for i in range(n if name == "operations" else 1)
                ]
            elif name == "scalar-bytes":
                population["facts"][ft][0][key] = "a" * n
                operation["key"] = ["a" * n]
            elif name == "key-fields":
                collection["key"] = [f"k{i}" for i in range(n)]
                for index, r in enumerate(population["facts"][ft]):
                    r.update({f"k{i}": index for i in range(n)})
                operation["key"] = [0] * n
            else:
                path = [f"p{i}" for i in range(n)]
                nested: object = population["facts"][ft]
                for segment in reversed(path):
                    nested = {segment: nested}
                population = nested
                collection["path"] = path
                operation["collection"] = path
            (base / "candidate.pop.json").write_bytes(canonical_json_bytes(population))
            digest = (
                SessionStore(b["root"] / "limit-store", run_id="corpus")
                .inventory_candidate(base)
                .tree_sha256
            )
            parsed = DataDrivenContract.model_validate(contract)
            patch.apply_candidate_patch(
                proposal(b, operations, digest), contract=parsed, base_root=base, base_sha256=digest
            )
        elif name.startswith("candidate-"):
            base = b["root"] / "physical-candidate"
            base.mkdir()
            if name == "candidate-files":
                for i in range(n):
                    (base / f"{i}.json").write_bytes(b"{}")
            elif name in {"candidate-file-bytes", "candidate-total-bytes"}:
                remaining = n
                limit = n if name == "candidate-file-bytes" else 10 * 1024 * 1024
                index = 0
                while remaining:
                    size = min(remaining, limit)
                    (base / f"{index}.txt").write_bytes(b"x" * size)
                    remaining -= size
                    index += 1
            else:
                leaf = base
                for _ in range(n):
                    leaf /= "p"
                leaf.mkdir(parents=True)
                (leaf / "file.txt").write_bytes(b"x")
            SessionStore(b["root"] / "physical-store", run_id="corpus").inventory_candidate(base)
        elif name == "report-bytes":
            payload = api.check(
                b["root"] / "model.orm.yaml", b["root"] / "candidate.pop.json", admission=True
            )
            raw = canonical_json_bytes(payload)
            raw += b" " * (n - len(raw))
            validate_verifier_payload(
                raw,
                case_id="work",
                role="required",
                process_exit=0,
                expected_command="check",
                expected_model=str(b["root"] / "model.orm.yaml"),
                expected_subject=str(b["root"] / "candidate.pop.json"),
                candidate_sha256="a" * 64,
                contract_sha256="b" * 64,
                evidence_candidate_sha256="a" * 64,
                evidence_contract_sha256="b" * 64,
                expected_schema_version=10,
            )
        elif name == "propagation-cells":
            # A compact many-blocker graph reaches the real propagation ceiling.
            count = 50000
            template = b["model"]["constraints"][0]
            b["model"]["constraints"] = []
            for i in range(20):
                rule = copy.deepcopy(template)
                rule["id"] = f"f{i}"
                b["model"]["constraints"].append(rule)
            if n > 1000000:
                rule = copy.deepcopy(template)
                rule["id"] = "f20"
                rule["antecedent"][0]["bind"][b["ids"]["key"]] = "A0"
                b["model"]["constraints"].append(rule)
            b["population"]["facts"][b["ids"]["fact"]] = [
                {b["ids"]["key"]: f"A{i}", b["ids"]["quantity"]: 0} for i in range(count)
            ]
            write_json(b["root"] / "model.orm.yaml", b["model"])
            write_json(b["root"] / "candidate.pop.json", b["population"])
            model = load_model(b["root"] / "model.orm.yaml")
            pop = load_population(b["root"] / "candidate.pop.json", model=model)
            # Exercise the semantic propagation bound directly: a million
            # blocker cells exceeds the separately tested report byte cap.
            from types import SimpleNamespace

            from gnd.admission import build_admission

            nodes = [(b["ids"]["fact"], i) for i in range(count)]
            verdicts = [
                SimpleNamespace(
                    constraint_ref=f"constraints[{i}]",
                    constraint_type="rule",
                    verdict="fail",
                    modality="alethic",
                )
                for i in range(len(model.constraints))
            ]
            findings = [
                SimpleNamespace(fact_refs=nodes if i < 20 else nodes[:1])
                for i in range(len(verdicts))
            ]
            report = SimpleNamespace(
                verdicts=verdicts, snapshot_projection=SimpleNamespace(findings=findings)
            )
            partition = build_admission(model, pop, report, max_cells=1000000)
            assert sum(len(r["blocked_by"]) for r in partition["blocked"]) == 1000000
        else:
            raise AssertionError(f"unmaterialized limit {name}")
    except (
        patch.PatchRefusal,
        validation.AdmissionValidationError,
        SessionContractError,
        VerifierPayloadError,
        ModelLoadError,
        ModelValidationError,
        ValueError,
    ):
        return {"accepted_limit": False}
    return {"accepted_limit": True}


def compat_case(row: dict, b: dict) -> dict:
    par = row["parameters"]
    version = par.get("version")
    if version is not None:
        observations = json.loads((CORPUS / "legacy-contracts.json").read_text())
        entry = observations[str(version)]
        parsed = DataDrivenContract.model_validate(entry["input"])
        by_bytes = DataDrivenContract.model_validate_json(canonical_json_bytes(entry["input"]))
        return {
            "legacy_identity": parsed.model_dump(mode="json")
            == by_bytes.model_dump(mode="json")
            == entry["normalized"]
        }
    variant = par["variant"]
    if variant in {"v10-wire", "no-request-wire"}:
        payload = api.check(
            b["root"] / "model.orm.yaml",
            b["root"] / "candidate.pop.json",
            admission=variant == "v10-wire",
        )
        expected = json.loads((CORPUS / row["domain"] / f"legacy-{variant}.json").read_text())

        # Only caller-selected path coordinates vary in this legacy observation.
        def normalize(value):
            if isinstance(value, str):
                return value.replace(str(b["root"]), "<ROOT>")
            if isinstance(value, dict):
                return {k: normalize(v) for k, v in value.items()}
            if isinstance(value, list):
                return [normalize(v) for v in value]
            return value

        return {"legacy_identity": normalize(payload) == expected}
    if variant == "witness-separate":
        payload = api.check(b["root"] / "model.orm.yaml", b["root"] / "candidate.pop.json")
        return {"legacy_identity": not ({"certificate", "replay", "judgments"} & payload.keys())}
    from gnd.exp.session_contract import SessionContractError, read_session_contract

    ref = (b["root"] / "reference-model.orm.yaml").read_bytes()
    (b["root"] / "model.orm.yaml").write_bytes(ref)
    doc = copy.deepcopy(b["contract"])
    doc["schema_version"] = 6
    doc["cases"][0]["verify"]["model"].update(
        sha256=hashlib.sha256(ref).hexdigest(), size_bytes=len(ref)
    )
    write_json(b["root"] / "session.contract.json", doc)
    try:
        read_session_contract(
            b["root"] / "session.contract.json",
            experiment_root=b["root"],
            experiment_id=doc["experiment_id"],
        )
    except SessionContractError:
        return {"legacy_identity": True}
    return {"legacy_identity": False}


def work_case(row: dict, b: dict, monkeypatch) -> dict:
    variant = row["parameters"]["variant"]
    module = importlib.import_module(
        "gnd.exp.session_patch" if variant != "linear-partition" else "gnd.admission_validation"
    )
    called = 0
    filename = module.__file__

    def profile(frame, event, arg):
        nonlocal called
        if event == "call" and frame.f_code.co_filename == filename:
            called += 1

    if variant != "linear-partition":
        b["population"]["facts"][b["ids"]["fact"]] = [
            {b["ids"]["key"]: f"A{i}", b["ids"]["quantity"]: 1} for i in range(100000)
        ]
        base, digest, _ = base_files(b)
        contract = patch_contract(b)
        doc = proposal(b, [], digest)
    if variant == "linear-partition":
        b["population"]["facts"][b["ids"]["fact"]] *= 5000
        write_json(b["root"] / "candidate.pop.json", b["population"])
        model = load_model(b["root"] / "model.orm.yaml")
        pop = load_population(b["root"] / "candidate.pop.json", model=model)
        payload = api.check(model, pop, admission=True)
        started = time.monotonic()
        sys.setprofile(profile)
        try:
            result = module.validate_admission_payload(payload, model=model, candidate=pop)
            assert result["candidate_admitted_unique"] == 2
        finally:
            sys.setprofile(None)
    else:
        started = time.monotonic()
        sys.setprofile(profile)
        try:
            assert module.apply_candidate_patch(
                doc, contract=contract, base_root=base, base_sha256=digest
            )
        finally:
            sys.setprofile(None)
    elapsed = time.monotonic() - started
    assert called > 0, "work instrumentation did not observe the selected layer"
    return {"bounded": called <= 1600000 and (elapsed <= 10 if variant == "layer-time" else True)}


def instrument_case(row: dict, b: dict, monkeypatch) -> dict:
    import pytest

    variant = row["parameters"]["variant"]
    if variant in {"dirty-answer", "missing-input", "unlisted-input"}:
        from tests.test_v71_phase4_sessions import validate_corpus

        copied = b["root"] / "dirty-corpus"
        shutil.copytree(CORPUS, copied)
        if variant == "dirty-answer":
            path = copied / "answers.json"
            doc = json.loads(path.read_text())
            doc["cases"][0]["status"] = "dirty"
            write_json(path, doc)
        elif variant == "missing-input":
            (copied / "dispatch/candidate.pop.json").unlink()
        else:
            write_json(copied / "unlisted.json", {})
        with pytest.raises(AssertionError):
            validate_corpus(copied)
    else:
        # Observe the real layer, then mutate exactly the observed assertion.
        sibling = {
            "wrong-rank": ("B16", "session", {"variant": "earlier-better"}),
            "missing-delete": ("B03", "patch", {"operations": [{"op": "delete", "key": ["A"]}]}),
            "hidden-canary": ("B21", "feedback", {"variant": "host-secret"}),
            "dirty-partition": (
                "B14",
                "admission",
                {"partition": "admitted", "mutation": "overlap"},
            ),
        }[variant]
        branch, mode, parameters = sibling
        changed = {**row, "branch": branch, "mode": mode, "parameters": parameters}
        observed = execute(changed, b["root"] / "control", monkeypatch)
        expected = {
            "wrong-rank": {"best_attempt_index": 1},
            "missing-delete": {"rows": [b["ids"]["row2"]]},
            "hidden-canary": {"secret_visible": False},
            "dirty-partition": {"status": "refused"},
        }[variant]
        assert_answer(observed, expected)
        dirty = copy.deepcopy(observed)
        for key in expected:
            dirty[key] = {
                "wrong-rank": 2,
                "missing-delete": [b["ids"]["row1"], b["ids"]["row2"]],
                "hidden-canary": True,
                "dirty-partition": "ok",
            }[variant]
        with pytest.raises(AssertionError):
            assert_answer(dirty, expected)
    return {"control_fails": True}


def execute(row: dict, root: Path, monkeypatch) -> dict:
    require_lane()
    b = bundle(row["domain"], root)
    mode = row["mode"]
    if mode == "patch":
        return patch_case(row, b, monkeypatch)
    simple = {
        "patch-intake": intake_case,
        "admission": admission_case,
        "public-report": public_case,
        "session": session_case,
        "contract": contract_case,
        "annotation": annotation_case,
        "feedback": feedback_case,
        "rank": rank_case,
        "compat": compat_case,
    }
    if mode in simple:
        return simple[mode](row, b)
    with_patch = {
        "publication": publication_case,
        "limit": limit_case,
        "work": work_case,
        "instrument": instrument_case,
    }
    assert mode in with_patch, f"unmaterialized mode {mode}"
    return with_patch[mode](row, b, monkeypatch)
