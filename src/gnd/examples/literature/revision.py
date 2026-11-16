"""Publish and replay the literature semantic revision example offline."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from gnd.artifacts import ArtifactError, canonical_json_bytes, sha256_hex
from gnd.errors import ModelLoadError, ModelValidationError
from gnd.model import load_model

from . import reading
from .depth import _command, _decode, _read, _success, _write
from .revision_manifest import MARKER, POLICY, POLICY_SHA256, Policy, publish, require, status

FIXTURE = Path(__file__).with_name("revision_fixture")
RESOLUTION = Path(__file__).with_name("resolution")
MODEL = "model.orm.yaml"
FACT = "method_builds_on_method"
ANCESTOR = "method_has_ancestor_method"
CANDIDATES = ("whale-a", "whale-b")
SUPPORTS = ("whale-a", "corroboration")
SOURCE_FILES = ("document.txt", "population.json", "population.json.anchors.json")
READING_FILES = ("run.json", *reading.FILES)
READING_INPUTS = (*reading.INPUTS, "annex.txt", "control.txt", "study.txt", "vocabulary.orm.json")
READING_INPUTS_SHA256 = "e49c1448bbb2856db377d407b932ce06cd65612e4855869b832dfa7448e70a76"
REVIEW_INPUTS_SHA256 = "860de5eaab0da246bec9871ae0b8094ef8d1507ee487724f0d7d1e0b925b1a47"
APPROVED_PREVIEW_SHA256 = "efb39fd26996186729d444ca697cc54038b086a8569bbffee11997fbc4f48adf"
REVIEWED_RESOLUTION_SHA256 = "8804cfeedffb014c792018ada339c1acf4067b8dda79ccf91494a6cf1eb7db60"
RELEASE = "release.json"


def _copy(root: Path, files: dict[str, bytes]) -> None:
    for name, raw in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def _input_names(snapshot: str) -> list[str]:
    names = [MODEL, "targets.json", "interpretation.json", "review-inputs.json", "sources/manifest.json"]
    names.extend(f"reading-inputs/{name}" for name in READING_INPUTS)
    sources = (*CANDIDATES, "corroboration") if snapshot == "after" else CANDIDATES
    names.extend(f"sources/{source}/{name}" for source in sources for name in SOURCE_FILES)
    names.extend(f"reading/{name}" for name in READING_FILES)
    if snapshot == "after":
        names.extend(("sources/resolution.json", "evolution/proposal.json",
                      "comparison/base.orm.json", "comparison/head.orm.json", "comparison/population.json",
                      *(f"supports/{source}/targets.json" for source in SUPPORTS)))
    return names


def _fixture_inputs(snapshot: str, retained: dict[str, bytes]) -> dict[str, bytes]:
    case = RESOLUTION / "cases" / ("W-flat" if snapshot == "before" else "W-resolved")
    files = {
        MODEL: _read(RESOLUTION, MODEL),
        "targets.json": _read(FIXTURE, "targets.json"),
        "interpretation.json": _read(FIXTURE, "interpretation.json"),
        "review-inputs.json": _read(FIXTURE, "review-inputs.json"),
        **{f"reading-inputs/{name}": _read(reading.FIXTURE, name)
           for name in READING_INPUTS if name != "vocabulary.orm.json"},
        "reading-inputs/vocabulary.orm.json": _read(reading.DEPTH_FIXTURE, "vocabulary.orm.json"),
        **retained,
    }
    for name in _input_names(snapshot):
        if name in files:
            continue
        if name.startswith("sources/corroboration/"):
            files[name] = _read(FIXTURE, name.removeprefix("sources/"))
        elif name.startswith("sources/"):
            files[name] = _read(case, name.removeprefix("sources/"))
        elif name.startswith("supports/"):
            files[name] = _read(FIXTURE, "support-targets.json")
        else:
            files[name] = _read(FIXTURE, name.removeprefix("evolution/"))
    return files


def _definition(root: Path, model: str = MODEL) -> dict:
    document = load_model(root / model)
    facts = {row["id"]: row for row in document.fact_types}
    asserted = facts[FACT]
    return {"predicate": FACT, "reading": asserted["reading"], "roles": asserted["roles"]}


def _rule(root: Path, model: str = MODEL) -> dict:
    document = load_model(root / model)
    rule = next(row["derivation_rule"] for row in document.fact_types if row["id"] == ANCESTOR)
    return {"predicate": ANCESTOR, "derivation_rule": rule}


def _review_inputs(root: Path) -> dict:
    raw = _read(root, "review-inputs.json")
    require(sha256_hex(raw) == REVIEW_INPUTS_SHA256, "fixture review inputs differ")
    return _decode(raw)


def _review(root: Path, source: str, authored: dict, *, model: str = MODEL, expect_stale: bool = False) -> dict:
    evidence = f"sources/{source}"
    policy_sha = sha256_hex(_read(root, "interpretation.json"))
    require(authored.get("interpretation_sha256") == policy_sha, "saved review interpretation policy differs")
    with tempfile.TemporaryDirectory(prefix="gnd-revision-review-") as scratch:
        work = Path(scratch).resolve()
        _write(work, "policy.json", authored["policy"])
        _write(work, "receipts.json", authored["receipts"])
        result = _command(work, "judgments", "check", str(root / model), str(root / evidence / "population.json"),
                          "--policy", "policy.json", "--receipts", "receipts.json", "--trusted-root",
                          str(root / evidence), "--format", "json")
    report = _decode(result.stdout)
    if expect_stale:
        require(result.return_code == 3 and report["error"] == {
            "reason": "binding", "message": "stale judgment subject",
        }, "expected stale judgment subject")
        targets = []
    else:
        require(result.return_code in (0, 1), "public assertion review could not be checked")
        judgments = report["judgment_policy"]
        targets = judgments["targets"]
        require(judgments["verification_contract"] == "consumer-pinned-bytes-v1" and bool(targets),
                "assertion review lost its trust binding")
    return {
        "inputs": authored,
        "admitted": bool(targets) and all(target["admitted"] for target in targets),
        "targets": targets,
        "route": {"exit": result.return_code, "error": report["error"]},
        "definition_sha256": sha256_hex(canonical_json_bytes(_definition(root, model))),
        "policy_sha256": policy_sha,
        "source": source,
    }


def _proof(root: Path, folder: str, population: str, target: str, *, composition: str | None = None,
           model: str = MODEL) -> dict:
    witness = f"{folder}witness.json"
    composed = ("--composition", composition) if composition else ()
    proof = _command(root, "witness", model, population, "--targets", target,
                     *composed, "--raw", "--out", witness)
    repeated = _command(root, "replay", model, population, witness, *composed, "--raw")
    require(proof.return_code == repeated.return_code and proof.return_code in (0, 2),
            "witness and replay did not agree")
    emitted, replayed = _decode(proof.stdout), _decode(repeated.stdout)
    emitted_rows = [(row["target"], row["status"]) for row in emitted["results"]]
    require(emitted_rows == [(row["target"], row["status"]) for row in replayed["results"]],
            "witness outcomes differ on replay")
    return {
        "witness_sha256": sha256_hex(_read(root, witness)),
        "queries": [[*(value["value"] for value in target["tuple"]), state == "proved"]
                    for target, state in emitted_rows],
    }


def _check_asserted_anchors(root: Path, population: str, *evidence: str) -> dict:
    result = _command(root, "check", MODEL, population, *evidence, "--format", "json")
    report = _decode(result.stdout)
    relevant = [row for row in report["verdicts"] if row["constraint_ref"].startswith(f"fact_types[{FACT}]")]
    require(result.return_code == 4 and not report["counts"]["fail"] and len(relevant) == 2
            and all(row["verdict"] == "pass" for row in relevant)
            and all(row["reason_code"] == "derivation-not-covered" for row in report["derivations"]),
            "composed assertion anchors did not pass")
    return {"exit": result.return_code, "asserted_anchors": len(relevant),
            "derivation": "checked by separate witness"}


def _reading(root: Path) -> tuple[dict, dict]:
    retained = root / "reading"
    inputs = root / "reading-inputs"
    pins = {name: sha256_hex(_read(inputs, name)) for name in READING_INPUTS}
    require(sha256_hex(canonical_json_bytes(pins)) == READING_INPUTS_SHA256, "retained reading inputs differ")
    report = reading.replay(retained, fixture=inputs, vocabulary_fixture=inputs)
    require(report["absence"]["status"] == "qualified", "release needs the exact qualified reading scope")
    absence = {
        "status": "qualified",
        "reading_sha256": report["evidence_sha256"],
        "dependencies": {name: sha256_hex(_read(retained, name)) for name in
                         ("coverage.json", "scope.json", "closure.json", "fidelity-high.json")},
    }
    return absence, report


def _coverage_impact(root: Path, report: dict, changed_occurrences: list[dict]) -> dict:
    interpretation = _decode(_read(root, "interpretation.json"))
    roster = _decode(_read(root, "reading-inputs/roster.json"))
    sections = {row["id"]: row for row in roster["sections"]}
    opened = _decode(_read(root, "reading/payload-1.json"))["attempts"]
    earlier = {row["section"]: sections[row["section"]] for row in opened}
    # The fixture's method-family key covers the asserted ancestry predicate.
    keys = {interpretation["coverage_key"]} if any(row["occurrence"][1] == FACT for row in changed_occurrences) else set()
    revisit = reading.affected_sections(earlier, keys)
    require(not keys or revisit == report["revisit"], "migration and reading revisit disagree")
    affected = set(reading.affected_sections(sections, keys))
    rows = {row["question"]: row for row in report["coverage"]}
    scoped = _decode(_read(root, "reading/scope.json"))["questions"]
    changed = {question: "stale" for question in scoped if rows[question]["section"] in affected}
    unrelated = interpretation["unrelated_question"]
    require(rows[unrelated]["section"] not in affected, "the unrelated coverage is affected")
    return {"revisit": revisit, "affected": changed, "unrelated": {unrelated: "current"}}


def _compose(root: Path, snapshot: str) -> dict:
    _success(root, "compose", MODEL, "sources", "--out", "population.json", "--record", "composition.json")
    record = _decode(_read(root, "composition.json"))
    resolution_raw = _read(root, "sources/resolution.json") if snapshot == "after" else None
    require(record.get("resolution_sha256") == (sha256_hex(resolution_raw) if resolution_raw else None),
            "composition did not bind selected resolution")
    _write(root, "decisions.json", _decode(resolution_raw) if resolution_raw else {"mode": "flat"})
    return _check_asserted_anchors(root, "population.json", "--composition", "composition.json",
                                   "--sources", "sources")


def _snapshot(root: Path, snapshot: str, reviews: dict) -> tuple[dict, dict, dict]:
    _write(root, "definition.json", _definition(root))
    _write(root, "rule.json", _rule(root))
    check = _compose(root, snapshot)
    checked = {source: _review(root, source, reviews[source]) for source in CANDIDATES}
    require(all(review["admitted"] for review in checked.values()), "a saved source review is stale")
    _write(root, "reviews.json", checked)
    absence, reading_report = _reading(root)
    _write(root, "scoped-absence.json", absence)
    claims = _proof(root, "", "population.json", "targets.json", composition="composition.json")
    claims["assertion_check"] = check
    claims["scoped_absence"] = absence
    return claims, reading_report, checked


def _coordinates(record: dict) -> dict[tuple[str, str, int], int]:
    coordinates = {}
    for row in record["facts"]:
        for origin in row["sources"]:
            coordinate = (origin["source"], origin["fact_type"], origin["fact_index"])
            require(coordinate not in coordinates, "ambiguous source-qualified occurrence")
            coordinates[coordinate] = row["index"]
    return coordinates


def _migration(before: Path, after: Path, reading_report: dict, policy: Policy) -> dict:
    old = _coordinates(_decode(_read(before, "composition.json")))
    new = _coordinates(_decode(_read(after, "composition.json")))
    require(old.keys() == new.keys(), "source occurrence inventory differs")
    occurrences = [[*key, old[key], new[key]] for key in sorted(old)]
    before_facts = _decode(_read(before, "population.json"))["facts"]
    after_facts = _decode(_read(after, "population.json"))["facts"]
    changed = []
    label = _decode(_read(after, "interpretation.json"))["unqualified_mention"]
    candidates = set()
    for coordinate in sorted(old):
        _, fact_type, _ = coordinate
        original = before_facts[fact_type][old[coordinate]]
        revised = after_facts[fact_type][new[coordinate]]
        candidates.update(revised[role] for role, value in original.items() if value == label)
        if original != revised:
            changed.append({"occurrence": list(coordinate), "before": original, "after": revised})
    require(len(candidates) > 1, "rereading control has no competing senses")
    ambiguity = {"mention": label, "candidates": sorted(candidates)}
    coverage = _coverage_impact(after, reading_report, changed)
    changed_inputs = {"sources/resolution.json"}
    if coverage["affected"]:
        changed_inputs.add("scoped-absence.json")
    affected = policy.affected("after", changed_inputs)
    return {"occurrences": occurrences, "changed_occurrences": changed, "ambiguous": ambiguity,
            "coverage": coverage, "reread": [*coverage["revisit"], ambiguity],
            "affected_artifacts": sorted(affected)}


def _transition(root: Path, authored: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="gnd-revision-evolve-") as scratch:
        work = Path(scratch).resolve()
        _copy(work, {MODEL: _read(root, MODEL), "proposal.json": _read(root, "evolution/proposal.json")})
        (work / "records").mkdir()
        scope = ("--workspace", ".", "--records", "records", "--format", "json")
        additive = _command(work, "evolve", "preview", MODEL, "proposal.json", *scope,
                            "--out", "additive.json", "--policy", "additive")
        issues = _decode(_read(work, "additive.json"))["policy_issues"]
        require(additive.return_code == 3 and any(
            issue["operation_id"] == "change-reading" and issue["cell"] == "fact_types.modify"
            and issue["reference"] == f"fact_types[{FACT}]" for issue in issues
        ),
                "the additive control must reject the predicate edit")
        _success(work, "evolve", "preview", MODEL, "proposal.json", *scope, "--out", "preview.json")
        preview = _decode(_read(work, "preview.json"))
        require(preview["preview_sha256"] == APPROVED_PREVIEW_SHA256,
                "predicate evolution did not reproduce the approved preview")
        _success(work, "evolve", "apply", MODEL, "proposal.json", *scope, "--preview", "preview.json")
        proposal_id = preview["proposal"]["proposal_id"]
        applied = _decode(_read(work, f"records/{proposal_id}/record.json"))
        revised_raw = _read(work, MODEL)
    require(applied["new_model_sha256"] == sha256_hex(revised_raw) and
            applied["old_model_sha256"] == sha256_hex(_read(root, MODEL)), "evolved model binding differs")
    _copy(root, {f"evolution/{MODEL}": revised_raw})
    revised_definition = _definition(root, f"evolution/{MODEL}")
    _write(root, "evolution/definition.json", revised_definition)
    old_definition = _definition(root)
    require(old_definition["roles"] == revised_definition["roles"] and old_definition != revised_definition,
            "predicate definition control changed the role shape")
    stale = _review(root, "whale-a", authored["whale-a"], model=f"evolution/{MODEL}", expect_stale=True)
    renewed = _review(root, "whale-a", authored["evolved-whale-a"], model=f"evolution/{MODEL}")
    require(not stale["admitted"] and renewed["admitted"], "semantic review did not require renewal")
    for old, new in zip(stale["inputs"]["receipts"]["receipts"],
                        renewed["inputs"]["receipts"]["receipts"], strict=True):
        old_subject, new_subject = old["subject"], new["subject"]
        require(old["sources"] == new["sources"] and
                {**old_subject, "model_sha256": new_subject["model_sha256"]} == new_subject,
                "the review renewal changed source or occurrence evidence")
    _write(root, "evolution/reviews.json", {"stale": stale, "renewed": renewed})
    transition = {"additive_preview": additive.return_code, "preview": 0, "apply": 0,
                  "old_review": "stale", "new_review": "current"}
    _write(root, "evolution/transition.json", {**transition, "preview": preview, "applied": applied})
    return transition


def _rule_comparison(root: Path) -> dict:
    observed = _decode(_success(root, "check", "comparison/head.orm.json", "comparison/population.json",
                                "--baseline-model", "comparison/base.orm.json", "--format", "json"))
    rules = observed["rules"]
    result = {"exit": observed["exit_code"],
              "base_only": sum(len(row["delta"]["base_only"]) for row in rules),
              "head_only": sum(len(row["delta"]["head_only"]) for row in rules)}
    _write(root, "comparison/result.json", result)
    return result


def _support(root: Path, source: str, reviewed: dict, editions: dict, *, model: str = MODEL) -> dict:
    evidence, folder = f"sources/{source}", f"supports/{source}/"
    _check_asserted_anchors(root, f"{evidence}/population.json", "--document", f"{evidence}/document.txt",
                            "--anchors", f"{evidence}/population.json.anchors.json")
    require(reviewed["admitted"], "support review is stale")
    review_raw = _write(root, folder + "review.json", reviewed)
    proof = _proof(root, folder, f"{evidence}/population.json", folder + "targets.json", model=model)
    require(len(proof["queries"]) == 1 and proof["queries"][0][-1], "support did not prove the selected claim")
    target = _decode(_read(root, folder + "targets.json"))["targets"][0]
    roles = dict(zip(("method", "base_method"), (part["value"] for part in target["tuple"]), strict=True))
    population = _decode(_read(root, f"{evidence}/population.json"))
    i = population["facts"][FACT].index(roles)
    receipt = next(row for row in reviewed["inputs"]["receipts"]["receipts"]
                   if row["subject"]["fact_type"] == FACT and row["subject"]["index"] == i)
    occurrence = {"source": source, "fact_type": FACT, "index": i,
                  "population_sha256": sha256_hex(_read(root, f"{evidence}/population.json")),
                  "document_sha256": sha256_hex(_read(root, f"{evidence}/document.txt")),
                  "span": receipt["sources"][0]["quote"]}
    return {"source": source, "occurrence": occurrence, "claim": target,
            "witness_sha256": proof["witness_sha256"], "review_sha256": sha256_hex(review_raw), **editions}


def _editions(root: Path) -> dict:
    resolution = _read(root, "sources/resolution.json")
    decisions = _read(root, "decisions.json")
    require(sha256_hex(resolution) == REVIEWED_RESOLUTION_SHA256
            and canonical_json_bytes(_decode(resolution)) == decisions,
            "support resolution differs from the reviewed edition")
    return {"resolution_edition": sha256_hex(decisions),
            "rule_edition": sha256_hex(_read(root, "rule.json"))}


def _evaluate(work: Path, snapshot: str | None, policy: Policy) -> dict:
    before = work / "before"
    prior, _, _ = _snapshot(before, "before", _review_inputs(before))
    _write(before, "claims.json", prior)
    if snapshot == "before":
        return prior
    after = work / "after"
    reviews = _review_inputs(after)
    current, reading_report, reviewed = _snapshot(after, "after", reviews)
    require(prior["scoped_absence"]["reading_sha256"] == current["scoped_absence"]["reading_sha256"],
            "migration reading run differs between snapshots")
    migration = _migration(before, after, reading_report, policy)
    if migration["coverage"]["affected"]:
        absence = current["scoped_absence"]
        current["scoped_absence"] = {**absence, "status": "stale", "prior_status": absence["status"]}
        _write(after, "scoped-absence.json", current["scoped_absence"])
    _write(after, "migration.json", migration)
    transition = _transition(after, reviews)
    comparison = _rule_comparison(after)
    editions = _editions(after)
    reviewed["corroboration"] = _review(after, "corroboration", reviews["corroboration"])
    supports = [_support(after, source, reviewed[source], editions) for source in SUPPORTS]
    claim = supports[0]["claim"]
    claim_values = [cell["value"] for cell in claim["tuple"]]
    require(all(support["claim"] == claim for support in supports) and [*claim_values, True] in current["queries"],
            "independent supports must prove the same released claim")
    for support in supports:
        _write(after, f"supports/{support['source']}/support.json", support)
    _write(after, "claims.json", {**current, "supports": supports, **editions})
    queries = [[*old, new[-1]] for old, new in zip(prior["queries"], current["queries"], strict=True)
               if old[:2] == new[:2]]
    require(len(queries) == len(prior["queries"]), "query roster differs between snapshots")
    return {"queries": queries, "before_witness_sha256": prior["witness_sha256"],
            "after_witness_sha256": current["witness_sha256"], "evolution": transition,
            "rule_comparison": comparison, "supports": supports, **migration, **editions}


def run(reading_run: Path, out: Path) -> dict:
    """Recheck captured evidence and publish both snapshots under a new root."""
    policy = Policy.load()
    retained = {f"reading/{name}": _read(reading_run, name) for name in READING_FILES}
    with tempfile.TemporaryDirectory(prefix="gnd-revision-") as temporary:
        work = Path(temporary).resolve()
        for snapshot in policy.entries:
            _copy(work / snapshot, _fixture_inputs(snapshot, retained))
        report = _evaluate(work, None, policy)
        files = {f"{name}/{path}": raw for name in policy.entries
                 for path, raw in policy.capture(work / name, name).items()}
    publish(out.absolute(), {**files, RELEASE: canonical_json_bytes(report)})
    return report


def _current(policy: Policy, root: Path, name: str) -> dict[str, bytes]:
    observed, files = policy.inspect(root / name, name)
    require(observed["status"] == "current", "release dependencies are stale")
    return files


def replay(root: Path, *, snapshot: str | None = None) -> dict:
    """Re-derive the release from authenticated retained inputs in private scratch."""
    policy = Policy.load()
    require(snapshot in (None, "before"), "invalid replay snapshot")
    selected = ("before",) if snapshot else tuple(policy.entries)
    with tempfile.TemporaryDirectory(prefix="gnd-revision-replay-") as temporary:
        work = Path(temporary).resolve()
        captures = {name: _current(policy, root, name) for name in selected}
        for name, files in captures.items():
            _copy(work / name, {path: files[path] for path in _input_names(name)})
        report = _evaluate(work, snapshot, policy)
        for name, files in captures.items():
            checked = policy.capture(work / name, name)
            differences = [path for path, raw in checked.items() if path != MARKER and files[path] != raw]
            require(not differences, f"release replay differs at {', '.join(differences)}")
    if snapshot is None:
        require(_read(root, RELEASE) == canonical_json_bytes(report), "release report differs")
    return report


def replay_support(root: Path, source: str) -> dict:
    """Check one certificate against the independent source and review inputs."""
    require(source in SUPPORTS, "unknown support source")
    policy = Policy.load()
    folder = f"supports/{source}/"
    state, files = policy.inspect(root / "after", "after")
    require(folder + "support.json" in state["current"], "support evidence is stale")
    with tempfile.TemporaryDirectory(prefix="gnd-revision-support-") as temporary:
        work = Path(temporary).resolve()
        needed = (MODEL, "interpretation.json", "review-inputs.json", "decisions.json", "sources/resolution.json",
                  *(f"sources/{source}/{name}" for name in SOURCE_FILES),
                  folder + "targets.json")
        _copy(work, {path: files[path] for path in needed})
        _write(work, "rule.json", _rule(work))
        require(_read(work, "rule.json") == files["rule.json"], "support rule binding differs")
        reviewed = _review(work, source, _review_inputs(work)[source])
        computed = _support(work, source, reviewed, _editions(work))
        require(_read(work, folder + "witness.json") == files[folder + "witness.json"] and
                _read(work, folder + "review.json") == files[folder + "review.json"] and
                canonical_json_bytes(computed) == files[folder + "support.json"], "support evidence differs")
    return computed


def replay_renewed_support(root: Path) -> dict:
    """Verify the selected replacement review and proof for the evolved predicate."""
    policy = Policy.load()
    state, files = policy.inspect(root / "after", "after")
    source = "whale-a"
    evolved = f"evolution/{MODEL}"
    observed = (evolved, "evolution/definition.json", "evolution/reviews.json", "evolution/transition.json")
    inputs = (
        MODEL, "interpretation.json", "review-inputs.json", "evolution/proposal.json",
        "rule.json", "decisions.json", "sources/resolution.json", f"supports/{source}/targets.json",
        *(f"sources/{source}/{name}" for name in SOURCE_FILES),
    )
    require({*observed, *inputs} <= set(state["current"]), "renewed support evidence is stale")
    with tempfile.TemporaryDirectory(prefix="gnd-revision-renewed-") as temporary:
        work = Path(temporary).resolve()
        _copy(work, {path: files[path] for path in inputs})
        _transition(work, _review_inputs(work))
        require(all(_read(work, path) == files[path] for path in observed), "renewed evidence differs on replay")
        pinned_rule = _read(work, "rule.json")
        require(canonical_json_bytes(_rule(work)) == pinned_rule
                and canonical_json_bytes(_rule(work, evolved)) == pinned_rule, "renewed support rule binding differs")
        review = _decode(_read(work, "evolution/reviews.json"))["renewed"]
        return _support(work, source, review, _editions(work), model=evolved)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fresh = commands.add_parser("run")
    fresh.add_argument("reading_run", type=Path)
    fresh.add_argument("--out", required=True, type=Path)
    repeat = commands.add_parser("replay")
    repeat.add_argument("root", type=Path)
    repeat.add_argument("--snapshot", choices=("before",))
    inspect = commands.add_parser("status")
    inspect.add_argument("root", type=Path)
    inspect.add_argument("--policy", type=Path, default=POLICY)
    inspect.add_argument("--policy-sha256", default=POLICY_SHA256)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            report = run(args.reading_run, args.out)
        elif args.command == "replay":
            report = replay(args.root, snapshot=args.snapshot)
        else:
            report = status(args.root, policy=args.policy, policy_sha256=args.policy_sha256)
    except (ArtifactError, ModelLoadError, ModelValidationError, OSError,
            ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
        report = {"status": "incomplete", "reason": str(error)}
    sys.stdout.buffer.write(canonical_json_bytes(report))
    return 3 if report.get("status") in {"stale", "incomplete"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
