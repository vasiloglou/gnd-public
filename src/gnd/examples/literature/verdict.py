"""Evaluate consumer-pinned verdicts on the literature fixture's derived claim."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gnd.artifacts import ArtifactError, canonical_json_bytes, publish_directory_once, sha256_hex
from gnd.errors import ModelLoadError, ModelValidationError

from . import revision
from .depth import _decode, _read
from .revision_manifest import _digest, require

OPINIONS = Path(__file__).with_name("verdict_fixture") / "opinions.json"
OPINIONS_SHA256 = "096613fa54def036cdeb4c85d137ec84fcfa1fae7b500bd080e56b01824276f2"
EDITIONS = ("current", "revised")
RENEWED_SOURCE = "whale-a"
CASE_IDS = ("both-approved", "reject-whale-a", "reject-both", "renew-whale-a")
SHARED = {
    "claim": "claims.json",
    "decision": "decisions.json",
    "rule": "rule.json",
    "resolution_edition": "decisions.json",
    "definition": "definition.json",
    "interpretation": "interpretation.json",
}
SUPPORT_BINDINGS = {"occurrence_sha256", "review_sha256", "witness_sha256", "resolution_edition", "rule_edition"}
EVIDENCE_ERRORS = (ArtifactError, ModelLoadError, ModelValidationError, OSError, ValueError,
                   KeyError, TypeError, IndexError, AttributeError, StopIteration)


def _opinions(path: Path, expected_sha: str) -> tuple[dict, dict[str, dict]]:
    raw = _read(path.parent, path.name)
    require(_digest(expected_sha) and sha256_hex(raw) == expected_sha, "saved verdict digest differs")
    doc = _decode(raw)
    require(set(doc) == {"format", "claim", "authorship", "cases"}
            and doc["format"] == "literature-derived-verdicts/1"
            and doc["authorship"] == "synthetic corpus opinions", "invalid saved verdicts")
    claim = doc["claim"]
    require(isinstance(claim, dict) and set(claim) == {"fact_type", "tuple"}
            and claim["fact_type"] == revision.ANCESTOR and isinstance(claim["tuple"], list)
            and len(claim["tuple"]) == 2
            and all(isinstance(cell, dict) and set(cell) == {"primitive", "value"} and cell["primitive"] == "String"
                    and isinstance(cell["value"], str) and bool(cell["value"]) for cell in claim["tuple"]),
            "invalid derived claim")
    cases = doc["cases"]
    require(isinstance(cases, list) and len(cases) == len(CASE_IDS), "invalid verdict case roster")
    indexed = {}
    for case, identifier in zip(cases, CASE_IDS, strict=True):
        require(isinstance(case, dict) and set(case) == {"id", "edition", "binding", "source_opinions"}
                and case["id"] == identifier and case["edition"] in EDITIONS, "invalid verdict case")
        binding = case["binding"]
        require(isinstance(binding, dict) and set(binding) == set(SHARED)
                and all(_digest(digest) for digest in binding.values()), "invalid shared verdict binding")
        supports = case["source_opinions"]
        require(isinstance(supports, list) and len(supports) == len(revision.SUPPORTS), "invalid support roster")
        for opinion, source in zip(supports, revision.SUPPORTS, strict=True):
            require(isinstance(opinion, dict) and set(opinion) == SUPPORT_BINDINGS | {"source", "verdict"}
                    and opinion["source"] == source and opinion["verdict"] in ("approve", "reject")
                    and all(_digest(opinion[field]) for field in SUPPORT_BINDINGS), "invalid saved support opinion")
        indexed[identifier] = case
    return claim, indexed


def _stale_shared(root: Path, expected: dict, edition: str) -> list[str]:
    paths = dict(SHARED)
    if edition == "revised":
        paths["definition"] = "evolution/definition.json"
    stale = []
    for key, path in paths.items():
        try:
            actual = sha256_hex(_read(root, path))
        except (ArtifactError, OSError):
            stale.append(key)
        else:
            if actual != expected[key]:
                stale.append(key)
    return stale


def _support_change(support: dict, opinion: dict, claim: dict) -> str | None:
    if support.get("claim") != claim or support.get("source") != opinion["source"]:
        return "claim"
    if sha256_hex(canonical_json_bytes(support.get("occurrence"))) != opinion["occurrence_sha256"]:
        return "occurrence"
    for name, key in (("resolution_edition", "resolution_edition"), ("rule_edition", "rule_edition"),
                      ("review", "review_sha256"), ("witness", "witness_sha256")):
        if support.get(key) != opinion[key]:
            return name
    return None


def _observation(root: Path, edition: str, opinion: dict, claim: dict) -> dict:
    source = opinion["source"]
    try:
        if edition == "revised":
            if source != RENEWED_SOURCE:
                return {"source": source, "state": "stale", "reason": "definition"}
            current = revision.replay_renewed_support(root)
        else:
            after = root / "after"
            folder = f"supports/{source}"
            captured = _decode(_read(after, f"{folder}/support.json"))
            change = _support_change(captured, opinion, claim)
            if change is None:
                for key in ("review", "witness"):
                    if sha256_hex(_read(after, f"{folder}/{key}.json")) != opinion[f"{key}_sha256"]:
                        change = key
                        break
            if change is not None:
                return {"source": source, "state": "stale", "reason": change}
            current = revision.replay_support(root, source)
    except EVIDENCE_ERRORS:
        return {"source": source, "state": "stale", "reason": "evidence"}
    change = _support_change(current, opinion, claim)
    if change is not None:
        return {"source": source, "state": "stale", "reason": change}
    outcome = "approved" if opinion["verdict"] == "approve" else "rejected"
    return {"source": source, "state": outcome, "reason": "saved-opinion"}


def _evaluate(root: Path, claim: dict, case: dict, edition: str) -> dict:
    require(edition in EDITIONS, "invalid observed verdict edition")
    stale = _stale_shared(root / "after", case["binding"], edition)
    if case["edition"] != edition and "definition" not in stale:
        stale.append("definition")
    opinions = case["source_opinions"]
    if stale:
        supports = [{"source": row["source"], "state": "stale", "reason": "shared-binding"} for row in opinions]
        decision = "revalidation-required"
    else:
        supports = [_observation(root, edition, row, claim) for row in opinions]
        decision = "supported" if any(row["state"] == "approved" for row in supports) else "unsupported"
    return {"claim": claim, "edition": edition, "decision": decision, "stale_bindings": stale,
            "effective": [row["source"] for row in supports if row["state"] == "approved"], "supports": supports}


def evaluate(root: Path, case: str, *, edition: str | None = None, opinions: Path = OPINIONS,
             opinions_sha256: str = OPINIONS_SHA256) -> dict:
    """Check one independently pinned reading opinion set against the release."""
    claim, cases = _opinions(opinions, opinions_sha256)
    require(isinstance(case, str) and case in cases, "unknown verdict case")
    return _evaluate(root, claim, cases[case], cases[case]["edition"] if edition is None else edition)


def _demonstrate(root: Path) -> dict[str, dict]:
    claim, cases = _opinions(OPINIONS, OPINIONS_SHA256)
    reports = {name: _evaluate(root, claim, case, case["edition"]) for name, case in cases.items()}
    reports["old-review-on-revised"] = _evaluate(root, claim, cases["both-approved"], "revised")
    return reports


def run(root: Path, out: Path) -> dict[str, dict]:
    """Capture the reproducible worked verdicts in a new directory."""
    report = _demonstrate(root)
    raw = canonical_json_bytes(report)
    marker = canonical_json_bytes({"format": "literature-derived-verdict-run/1", "opinions_sha256": OPINIONS_SHA256,
                                   "report_sha256": sha256_hex(raw)})
    destination = out.absolute()
    publish_directory_once(destination.parent, destination.name, {"report.json": raw, "run.json": marker},
                           manifest_name="run.json")
    return report


def replay(root: Path, out: Path) -> dict[str, dict]:
    """Recompute a retained verdict report from the expected release evidence."""
    marker = _decode(_read(out, "run.json"))
    require(set(marker) == {"format", "opinions_sha256", "report_sha256"}
            and marker["format"] == "literature-derived-verdict-run/1"
            and marker["opinions_sha256"] == OPINIONS_SHA256 and _digest(marker["report_sha256"]),
            "invalid retained verdict run")
    raw = _read(out, "report.json")
    require(sha256_hex(raw) == marker["report_sha256"], "stale retained verdict report")
    report = _demonstrate(root)
    require(raw == canonical_json_bytes(report), "verdict replay differs")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    routes = parser.add_subparsers(dest="command", required=True)
    fresh = routes.add_parser("run")
    fresh.add_argument("root", type=Path)
    fresh.add_argument("--out", type=Path, required=True)
    repeat = routes.add_parser("replay")
    repeat.add_argument("root", type=Path)
    repeat.add_argument("out", type=Path)
    single = routes.add_parser("evaluate")
    single.add_argument("root", type=Path)
    single.add_argument("--case", choices=CASE_IDS, required=True)
    single.add_argument("--edition", choices=EDITIONS)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            report = run(args.root, args.out)
        elif args.command == "replay":
            report = replay(args.root, args.out)
        else:
            report = evaluate(args.root, args.case, edition=args.edition)
    except EVIDENCE_ERRORS as error:
        sys.stdout.buffer.write(canonical_json_bytes({"status": "incomplete", "reason": str(error)}))
        return 3
    sys.stdout.buffer.write(canonical_json_bytes(report))
    return {"unsupported": 2, "revalidation-required": 3}.get(report.get("decision"), 0)


if __name__ == "__main__":
    sys.exit(main())
