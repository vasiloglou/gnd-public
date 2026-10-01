"""Version-8 protected authority, retained opinions and replay composition."""

from gnd.artifacts import (
    canonical_json_bytes,
    publish_directory_once,
    read_regular_bounded,
    sha256_hex,
)
from gnd.exp.session_store import _collect_candidate, _evidence_entry
from gnd.judgments import (
    evaluate_judgments,
    read_judgment_policy,
    read_judgment_receipts,
    redact_policy,
)


def authority(contract, experiment):
    files, modes = {}, {}
    for case in contract.cases:
        gate = case.judgment_gate
        if gate is None:
            continue
        for bound in (case.verify.model, gate.policy):
            raw = read_regular_bounded(experiment, bound.path, max_bytes=10 * 1024 * 1024)[0]
            if sha256_hex(raw) != bound.sha256 or len(raw) != bound.size_bytes:
                raise ValueError("judgment authority differs from contract")
            files[bound.path] = raw
            modes[bound.path] = (experiment / bound.path).lstat().st_mode
        read_judgment_policy(files[gate.policy.path])
        trusted = experiment / gate.trusted_root
        _, leaves = _collect_candidate(trusted)
        for leaf in leaves:
            name = gate.trusted_root + "/" + leaf.entry.path
            files[name] = leaf.data
            modes[name] = (experiment / name).lstat().st_mode
        modes[gate.trusted_root] = trusted.lstat().st_mode
    return files, modes


def prepare(contract, experiment, run_root):
    files, modes = authority(contract, experiment)
    protected = run_root / "judgment-authority"
    manifest = canonical_json_bytes(
        {"files": {k: sha256_hex(v) for k, v in sorted(files.items())}, "modes": modes}
    )
    if not protected.exists():
        publish_directory_once(
            run_root,
            "judgment-authority",
            {**files, "authority.json": manifest},
            manifest_name="authority.json",
        )
    verify_authority(contract, experiment, run_root)


def verify_authority(contract, experiment, run_root):
    files, modes = authority(contract, experiment)
    protected = run_root / "judgment-authority"
    expected = canonical_json_bytes(
        {"files": {k: sha256_hex(v) for k, v in sorted(files.items())}, "modes": modes}
    )
    if read_regular_bounded(protected, "authority.json", max_bytes=1024 * 1024)[0] != expected:
        raise ValueError("protected judgment authority changed")
    for name, data in files.items():
        if read_regular_bounded(protected, name, max_bytes=10 * 1024 * 1024)[0] != data:
            raise ValueError("retained judgment authority changed")


def evaluate(case, result, mechanical, model, refs, snapshot, experiment, run_root):
    gate = case.judgment_gate
    if gate is None:
        return result
    from gnd.judgments import JudgmentInputError
    from gnd.population import load_population_bytes

    protected = run_root / "judgment-authority"
    policy_raw = read_regular_bounded(protected, gate.policy.path, max_bytes=1024 * 1024)[0]
    receipts_raw = read_regular_bounded(snapshot, gate.receipts_path, max_bytes=10 * 1024 * 1024)[0]
    model_raw = read_regular_bounded(
        experiment, case.verify.model.path, max_bytes=10 * 1024 * 1024
    )[0]
    pop_raw = read_regular_bounded(snapshot, case.verify.subject, max_bytes=10 * 1024 * 1024)[0]
    receipts = read_judgment_receipts(receipts_raw)
    report = {
        "schema_version": 15,
        "command": "judgments",
        "outcome": 3,
        "error": None,
        "mechanical_report": mechanical,
        "judgment_policy": None,
    }
    try:
        policy = evaluate_judgments(
            read_judgment_policy(policy_raw),
            receipts,
            model=model,
            candidate=load_population_bytes(pop_raw, source=case.verify.subject, model=model),
            mechanical_report=mechanical,
            model_bytes=model_raw,
            population_bytes=pop_raw,
            trusted_root=protected / gate.trusted_root,
            references=refs,
        )
        report.update(outcome=0 if policy["admission"] else 1, judgment_policy=policy)
    except JudgmentInputError as error:
        report.update(
            outcome=4 if error.reason in {"limit", "io"} else 3,
            error={"reason": error.reason, "message": str(error)},
        )
    prefix = "judgments/" + case.case_id + "/"
    files = {
        prefix + "policy.json": policy_raw,
        prefix + "receipts.json": receipts_raw,
        prefix + "report.json": canonical_json_bytes(report, exact_numbers=True),
    }
    sources = []
    for name in sorted({s["path"] for r in receipts for s in r.doc["sources"]}):
        raw = read_regular_bounded(protected / gate.trusted_root, name, max_bytes=1024 * 1024)[0]
        target = prefix + "sources/" + name
        files[target] = raw
        sources.append(entry(target, raw))
    evidence = {
        k: entry(prefix + k + ".json", files[prefix + k + ".json"])
        for k in ("policy", "receipts", "report")
    }
    evidence["sources"] = sources
    result._judgment_report = report
    result._judgment_files = (files, evidence)
    return result


def entry(path, raw):
    return _evidence_entry(path, raw)


def feedback(results, *, unredacted=False):
    rows = []
    for result in sorted(results, key=lambda r: r.case_id):
        report = result._judgment_report
        if report is None:
            continue
        policy = report["judgment_policy"]
        redacted = None if policy is None else redact_policy(policy)
        rows.append(
            {
                "case_id": result.case_id,
                "admission": False if policy is None else policy["admission"],
                "repair": False if policy is None else policy["repair"],
                "review_required": True if policy is None else policy["review_required"],
                "report": report
                if unredacted
                else {**report, "mechanical_report": None, "judgment_policy": redacted},
            }
        )
    return rows


def replay(record, rebuilt, directory):
    expected = {
        r.case_id: r._judgment_files[1] for r in rebuilt.results if r._judgment_files is not None
    }
    if {k: v.model_dump(mode="json") for k, v in record.judgment_evidence.items()} != expected:
        raise ValueError("retained judgment evidence map differs")
    for result in rebuilt.results:
        if result._judgment_files is not None:
            for name, raw in result._judgment_files[0].items():
                if read_regular_bounded(directory, name, max_bytes=10 * 1024 * 1024)[0] != raw:
                    raise ValueError("retained judgment evidence bytes differ")
