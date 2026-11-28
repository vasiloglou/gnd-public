"""Drive one reviewed consolidation decision with the ordinary evolution transaction."""

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gnd import input_policy
from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    publish_leaf_atomic,
    read_regular_bounded,
    sha256_hex,
)
from gnd.errors import (
    ModelLoadError,
    ModelValidationError,
    PopulationLoadError,
    ReferenceInputError,
)
from gnd.model import load_model_bytes_composed
from gnd.model_index import ModelIndex
from gnd.values import identity_key

from .candidates import discover_candidates
from .models import EvolutionPreview
from .population_check import sample_population_report
from .service import EvolutionError, EvolutionService, _missing_artifact


class Move(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source: str
    target: str
    roles: dict[str, str]


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    action: Literal["leave", "merge", "demote-to-row", "link-subtype"]
    actor: str = Field(min_length=1)
    model_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    group_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    evidence_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    preview: EvolutionPreview | None = None
    moves: tuple[Move, ...] = ()


def _located_rows(fact, mapping):
    spans = {
        entry["row"]: entry["span"]
        for entry in (fact.get("provenance") or {}).get("sample_spans", [])
    }
    result = Counter()
    for i, row in enumerate(fact.get("sample_population") or []):
        mapped = tuple(sorted((mapping[key], identity_key(value)) for key, value in row.items()))
        result[mapped, canonical_json_bytes(spans.get(i))] += 1
    return result


def _check_mutation(decision, group, before, after):
    old, new = ModelIndex.for_model(before), ModelIndex.for_model(after)
    old_roles, new_roles = old.role_object_types(), new.role_object_types()
    members = set(group["members"])
    old_facts = {fact["id"]: fact for fact in old.iter_fact_types_shared()}
    new_facts = {fact["id"]: fact for fact in new.iter_fact_types_shared()}
    old_objects, new_objects = old.object_types_by_id(), new.object_types_by_id()
    surviving = new_facts if group["kind"] == "fact" else new_objects
    removed = members.difference(surviving)
    if decision.action in ("merge", "demote-to-row") and not removed:
        raise ValueError("the reviewed decision did not remove a selected member")
    if decision.action == "link-subtype" and (
        group["kind"] != "object"
        or removed
        or not any(
            members.intersection(
                set(new_objects[m].get("subtype_of", ()))
                - set(old_objects[m].get("subtype_of", ()))
            )
            for m in members
        )
    ):
        raise ValueError("the reviewed decision did not link two group members")

    if decision.action == "merge" and not (members & surviving.keys()):
        raise ValueError("a merge needs a surviving group member")
    if (old_objects.keys() - new_objects.keys()) - members:
        raise ValueError("an unrelated object was removed")
    if decision.action == "merge" and group["kind"] == "object":
        survivor_ids = members & new_objects.keys()
        for fact_id, roles in old_roles.items():
            for role, player in roles.items():
                if player in removed and fact_id in new_roles and new_roles[fact_id].get(role) not in survivor_ids:
                    raise ValueError("a removed object role must reference a surviving group member")
    destinations = {}
    required = {}
    affected = set()
    for move in decision.moves:
        if move.source not in old_facts or move.source in new_facts or move.target not in new_facts:
            raise ValueError("a row transfer must name a removed source and surviving target")
        if (
            move.source in destinations
            or set(move.roles) != set(old_roles[move.source])
            or (
                set(move.roles.values()) != set(new_roles[move.target])
                or len(set(move.roles.values())) != len(move.roles)
            )
        ):
            raise ValueError(
                "each transfer requires a distinct source and a total role correspondence"
            )
        if group["kind"] == "fact" and (move.source not in members or move.target not in members):
            raise ValueError("row move is outside the selected fact group")
        destinations[move.source] = move.target
        required.setdefault(move.target, Counter()).update(
            _located_rows(old_facts[move.source], move.roles)
        )
        affected.add(move.target)
    for key, fact in old_facts.items():
        if key not in new_facts:
            if key not in removed and key not in destinations and not removed.intersection(old_roles[key].values()):
                raise ValueError("an unrelated fact was removed")
            if fact.get("sample_population") and key not in destinations:
                raise ValueError("deleted observations lack a declared destination")
            continue
        if fact != new_facts[key]:
            affected.add(key)
        if fact.get("sample_population"):
            if not set(old_roles[key]) <= set(new_roles[key]):
                raise ValueError("a surviving sampled fact lost a role")
            required.setdefault(key, Counter()).update(
                _located_rows(fact, {r: r for r in old_roles[key]})
            )
    for key, rows in required.items():
        present = _located_rows(new_facts[key], {r: r for r in new_roles[key]})
        if rows - present:
            raise ValueError("the proposal lost a required sample row or source span")
    affected.update(new_facts.keys() - old_facts.keys())
    if decision.action == "demote-to-row" and not any(
        len(new_facts[k].get("sample_population", []))
        > len(old_facts.get(k, {}).get("sample_population", []))
        for k in affected
    ):
        raise ValueError("demotion requires a surviving fact to acquire a sample row")
    if new_facts and affected:
        if after.reference_populations:
            raise ValueError("a reference-bound population needs separate review")
        facts, results, subjects = sample_population_report(after)
        for ref, constraint, host in new.iter_constraints_shared():
            touched = subjects.for_constraint(constraint, host["id"] if host else None)
            if not touched or (
                touched & affected and (touched.difference(facts) or results.get(ref) != "pass")
            ):
                raise ValueError("candidate samples do not establish an affected constraint")


def step(
    model_path,
    *,
    decision=None,
    minimum_score=0,
    max_decisions=100,
    max_items=100_000,
    max_pairs=25_000,
):
    """Recover a pending decision, apply one supplied decision, or return the next group."""
    if min(max_decisions, max_items, max_pairs, minimum_score) < 0 or minimum_score > 100:
        raise ValueError("invalid consolidation limits")
    path = Path(model_path).absolute()
    root = path.parent
    folder = ".gnd-consolidation/" + sha256_hex(path.name.encode())
    journal = folder + "/decisions.json"
    service = EvolutionService(
        model_path=path, evidence_root=root / folder, allowed_project_root=root
    )
    cap = 64 * 1024 * 1024
    try:
        raw, stamp = read_regular_bounded(root, journal, max_bytes=cap)
    except (FileNotFoundError, ArtifactError) as error:
        if not _missing_artifact(error):
            raise
        stamp = None
        state = {"version": 1, "completed": [], "pending": None}
    else:
        state = input_policy.loads(raw, max_bytes=cap)

    def save():
        nonlocal stamp
        payload = canonical_json_bytes(state)
        if len(payload) > cap:
            raise ValueError("decision journal size limit")
        stamp = publish_leaf_atomic(root, journal, payload, expected=stamp)

    pending = state["pending"]
    supplied = Decision.model_validate(decision) if decision is not None else None
    decision_id = (
        sha256_hex(canonical_json_bytes(supplied.model_dump(mode="json"))) if supplied else None
    )
    if pending and supplied and pending["id"] != decision_id:
        raise ValueError("recover the pending decision before submitting another")
    if not pending:
        if supplied and any(row["id"] == decision_id for row in state["completed"]):
            return {"reason": "already-completed", "decision_id": decision_id}
        if len(state["completed"]) >= max_decisions:
            return {"reason": "decision-limit", "completed": len(state["completed"])}
        raw, observed = read_regular_bounded(root, path.name, max_bytes=input_policy.MAX_BYTES)
        model = load_model_bytes_composed(raw, source=path, root=root)
        spent = {
            counter: sum(entry["work"][counter] for entry in state["completed"])
            for counter in ("items", "pairs")
        }
        report = discover_candidates(
            model,
            max_items=max(0, max_items - spent["items"]),
            max_pairs=max(0, max_pairs - spent["pairs"]),
        )
        if not report["complete"]:
            return {"reason": report["reason"], "work": report["work"]}
        declined = {
            (d["group_id"], d["evidence_sha256"])
            for d in state["completed"]
            if d["action"] == "leave"
        }
        group = next(
            (
                g
                for g in report["groups"]
                if g["score"] >= minimum_score
                and (g["group_id"], g["evidence_sha256"]) not in declined
            ),
            None,
        )
        if group is None:
            return {"reason": "no-eligible-group", "work": report["work"]}
        if not supplied:
            return {
                "reason": "needs-decision",
                "model_sha256": observed.sha256,
                "group": group,
                "work": report["work"],
            }
        if (supplied.model_sha256, supplied.group_id, supplied.evidence_sha256) != (
            observed.sha256,
            group["group_id"],
            group["evidence_sha256"],
        ):
            raise ValueError("decision differs from the current model or selected group")
        preview = supplied.preview
        if supplied.action == "leave":
            if preview or supplied.moves:
                raise ValueError("a leave cannot carry a mutation")
        else:
            if not preview or preview.before_model.sha256 != observed.sha256:
                raise ValueError("mutation requires the reviewed preview for this model")
            if (
                preview.breaking
                and preview.accepted_blast_radius_sha256 != preview.blast_radius.report_sha256
            ):
                raise ValueError("mutation needs acceptance of the reviewed blast radius")
            if preview.proposal.audit.actor_id != supplied.actor:
                raise ValueError("decision and proposal actors differ")
            candidate = load_model_bytes_composed(
                preview.candidate_model.text.encode(), source=path, root=root
            )
            _check_mutation(supplied, group, model, candidate)
        pending = {
            "id": decision_id,
            "decision": supplied.model_dump(mode="json"),
            "work": report["work"],
        }
        state["pending"] = pending
        save()
    accepted = Decision.model_validate(pending["decision"])
    if pending["id"] != sha256_hex(canonical_json_bytes(accepted.model_dump(mode="json"))):
        raise ValueError("pending decision identity differs from its contents")
    if accepted.preview:
        record = service.finalize(service.apply(accepted.preview))
        result = {
            "after": record.new_model_sha256,
            "proposal_sha256": record.proposal_sha256,
            "conformance_exit": record.conformance_exit_code,
        }
    else:
        result = {"after": accepted.model_sha256}
    completed = {
        **accepted.model_dump(exclude={"preview", "moves"}),
        **result,
        "id": pending["id"],
        "work": pending["work"],
    }
    state["completed"].append(completed)
    state["pending"] = None
    save()
    return {"reason": "completed", "decision": completed}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--decision", type=Path, help="one reviewed JSON decision")
    parser.add_argument("--minimum-score", type=int, default=0)
    parser.add_argument("--max-decisions", type=int, default=100)
    parser.add_argument("--max-items", type=int, default=100_000)
    parser.add_argument("--max-pairs", type=int, default=25_000)
    args = parser.parse_args(argv)
    try:
        decision = None
        if args.decision:
            decision_path = args.decision.absolute()
            data, _ = read_regular_bounded(
                decision_path.parent, decision_path.name, max_bytes=input_policy.MAX_BYTES
            )
            decision = input_policy.loads(data)
        result = step(
            args.model,
            decision=decision,
            minimum_score=args.minimum_score,
            max_decisions=args.max_decisions,
            max_items=args.max_items,
            max_pairs=args.max_pairs,
        )
    except (
        OSError,
        ValueError,
        ArtifactError,
        EvolutionError,
        PopulationLoadError,
        ModelValidationError,
        ModelLoadError,
        ReferenceInputError,
    ) as error:
        print(f"consolidation refused: {error}", file=sys.stderr)
        return 3
    print(canonical_json_bytes(result).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
