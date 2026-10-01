"""Independent certificate replay: finite local inference, never fixpoint search.

Only intake/identity and the immutable wire contract are shared with production.
The scalar table, body unification and rule instantiation below are independent.
"""

from __future__ import annotations

from datetime import date

from gnd.artifacts import canonical_json_bytes
from gnd.model import ModelLoadError, ModelValidationError, iter_derivation_clauses
from gnd.population import PopulationLoadError
from gnd.witness.io import (
    certificate_shape,
    classify_targets,
    identity,
    intake,
    roster,
    validate_targets,
)
from gnd.witness.types import (
    DEFAULT_LIMITS,
    WitnessResult,
    WitnessWorkError,
    checked_limits,
    reduce_results,
    result_rows,
)


class InvalidProof(ValueError):
    """A structurally admitted inference is false or ungrounded."""


class UnsupportedScalar(ValueError):
    """A scalar is outside the independently implemented fragment."""


def _scalar(v):
    p, value = v["primitive"], v["value"]
    if p in {"Integer", "Number"}:
        if type(value) is bool:
            raise InvalidProof("Boolean is not an integer")
        if type(value) is not int:
            raise UnsupportedScalar("only exact integral JSON numbers")
    elif p == "Boolean":
        if type(value) is not bool:
            raise InvalidProof("Boolean type mismatch")
    elif p in {"String", "Date"}:
        if type(value) is not str:
            raise InvalidProof("string type mismatch")
        if p == "Date":
            try:
                value = date.fromisoformat(value)
                if value.isoformat() != v["value"]:
                    raise ValueError
            except ValueError:
                raise InvalidProof("noncanonical Date") from None
    else:
        raise UnsupportedScalar("primitive outside fragment")
    return p, value


def _equal(a, b):
    pa, va = _scalar(a)
    pb, vb = _scalar(b)
    return pa == pb and type(va) is type(vb) and va == vb


def _term(term, bindings, primitive=None):
    if type(term) is str and term.startswith("$"):
        try:
            return bindings[term[1:]]
        except KeyError:
            raise InvalidProof("unbound variable") from None
    if isinstance(term, (dict, list)):
        raise UnsupportedScalar("expression")
    inferred = "Boolean" if type(term) is bool else "Integer" if type(term) is int else "String"
    return {"primitive": primitive or inferred, "value": term}


def _compare(w, bindings):
    left, right = w["left"], w["right"]
    l = _term(left, bindings)
    r = _term(right, bindings)
    # Scalar literals inherit numeric primitive, never a Date from a raw string.
    if type(left) is int and r["primitive"] in {"Integer", "Number"}:
        l["primitive"] = r["primitive"]
    if type(right) is int and l["primitive"] in {"Integer", "Number"}:
        r["primitive"] = l["primitive"]
    lp, lv = _scalar(l)
    rp, rv = _scalar(r)
    numeric_pair = lp in {"Integer", "Number"} and rp in {"Integer", "Number"}
    if (lp != rp and not numeric_pair) or type(lv) is not type(rv):
        raise InvalidProof("comparison type mismatch")
    op = w["operator"]
    if lp in {"String", "Boolean"} and op not in {"=", "!="}:
        raise UnsupportedScalar("ordering outside fragment")
    return {
        "=": lambda: lv == rv,
        "!=": lambda: lv != rv,
        "<": lambda: lv < rv,
        "<=": lambda: lv <= rv,
        ">": lambda: lv > rv,
        ">=": lambda: lv >= rv,
    }[op]()


def graph_work(certificate, *, limits=DEFAULT_LIMITS):
    nodes = certificate["nodes"]
    edges = sum(len(n.get("premises", [])) for n in nodes)
    cells = sum(len(n.get("bindings", {})) for n in nodes)
    if len(nodes) > limits.nodes or edges > limits.edges or cells > limits.binding_cells:
        raise WitnessWorkError("graph cardinality ceiling")
    depths, cycle = [], False
    for n in nodes:
        premises = n.get("premises", [])
        if any(e >= n["id"] for e in premises):
            cycle = True
            depths.append(1)
        else:
            depths.append(1 + max((depths[e] for e in premises), default=0))
    if max(depths, default=0) > limits.proof_depth:
        raise WitnessWorkError("proof depth ceiling")
    if cycle:
        raise InvalidProof("non-grounded topology")
    return {
        "nodes": len(nodes),
        "edges": edges,
        "binding_cells": cells,
        "proof_depth": max(depths, default=0),
    }


def _replay_graph(model, candidate, refs, certificate, flags):
    nodes = certificate["nodes"]
    roles = roster(model)
    facts = {ft["id"]: ft for ft in model.fact_types}
    clauses = {fid: iter_derivation_clauses(ft.get("derivation_rule")) for fid, ft in facts.items()}
    active, stack = (
        set(),
        [
            r["root"]
            for r, flag in zip(certificate["results"], flags, strict=True)
            if flag and r["root"] is not None
        ],
    )
    while stack:
        i = stack.pop()
        if i not in active:
            active.add(i)
            stack.extend(nodes[i].get("premises", []))
    valid = []
    # Wire references are checked before indexing; all inference errors stay local.
    for n in nodes:
        if n["id"] not in active:
            valid.append(False)
            continue
        try:
            if any(valid[edge] is None for edge in n.get("premises", [])):
                raise UnsupportedScalar("unsupported proof dependency")
            kind = n["kind"]
            fid = n.get("fact_type", n.get("rule_fact_type"))
            if fid not in facts:
                raise InvalidProof("unknown inference owner")
            if kind == "base":
                if facts[fid].get("derivation") in {"derived", "semiderived"}:
                    raise InvalidProof("computed relation is not a base axiom")
                origin = n["origin"]
                pop = (
                    candidate if origin["kind"] == "candidate" else refs.get(origin["reference_id"])
                )
                rows = pop.facts.get(fid, ()) if pop is not None else ()
                i = origin["fact_index"]
                if i >= len(rows):
                    raise InvalidProof("false base occurrence")
                expected = [{"primitive": p, "value": rows[i][role]} for role, p in roles[fid]]
                if len(expected) != len(n["tuple"]) or not all(
                    _equal(a, b) for a, b in zip(expected, n["tuple"], strict=True)
                ):
                    raise InvalidProof("false base tuple")
            else:
                ci = n["clause_index"]
                if ci >= len(clauses[fid]):
                    raise InvalidProof("wrong clause")
                clause = clauses[fid][ci]
                bindings = n["bindings"]
                for v in bindings.values():
                    _scalar(v)
                if kind == "comparison":
                    wi = n["where_index"]
                    if (
                        n["premises"]
                        or wi >= len(clause.get("where", []))
                        or not _compare(clause["where"][wi], bindings)
                    ):
                        raise InvalidProof("false comparison")
                else:
                    body, where = clause.get("body", []), clause.get("where", [])
                    if len(n["premises"]) != len(body) + len(where):
                        raise InvalidProof("body/where premise count")
                    inferred = {}
                    for a, edge in zip(body, n["premises"][: len(body)], strict=True):
                        premise = nodes[edge]
                        afid = a["fact_type"]
                        if (
                            not valid[edge]
                            or premise["kind"] == "comparison"
                            or premise["fact_type"] != afid
                            or len(premise["tuple"]) != len(roles[afid])
                        ):
                            raise InvalidProof("false body premise")
                        for (role, p), cell in zip(roles[afid], premise["tuple"], strict=True):
                            term = a["bind"][role]
                            if cell["primitive"] != p:
                                raise InvalidProof("body primitive mismatch")
                            if type(term) is str and term.startswith("$"):
                                name = term[1:]
                                if name in inferred and not _equal(inferred[name], cell):
                                    raise InvalidProof("variable conflict")
                                inferred[name] = cell
                            elif not _equal(_term(term, {}, p), cell):
                                raise InvalidProof("body literal mismatch")
                    if set(inferred) != set(bindings) or not all(
                        _equal(bindings[k], v) for k, v in inferred.items()
                    ):
                        raise InvalidProof("incorrect grounding bindings")
                    for wi, edge in enumerate(n["premises"][len(body) :]):
                        premise = nodes[edge]
                        if (
                            not valid[edge]
                            or premise["kind"] != "comparison"
                            or premise["rule_fact_type"] != fid
                            or premise["clause_index"] != ci
                            or premise["where_index"] != wi
                            or canonical_json_bytes(premise["bindings"])
                            != canonical_json_bytes(bindings)
                        ):
                            raise InvalidProof("comparison premise identity")
                    expected = [_term(clause["head"][role], bindings, p) for role, p in roles[fid]]
                    if len(n["tuple"]) != len(expected) or not all(
                        _equal(a, b) for a, b in zip(expected, n["tuple"], strict=True)
                    ):
                        raise InvalidProof("false head")
            valid.append(True)
        except UnsupportedScalar:
            valid.append(None)
        except (InvalidProof, KeyError, TypeError, IndexError):
            valid.append(False)
    reachable, stack = set(), [r["root"] for r in certificate["results"] if r["root"] is not None]
    while stack:
        edge = stack.pop()
        if edge not in reachable:
            reachable.add(edge)
            stack.extend(nodes[edge].get("premises", []))
    junk = len(reachable) != len(nodes)
    if junk:
        raise InvalidProof("unreachable graph nodes")
    rows = []
    for r, flag in zip(certificate["results"], flags, strict=True):
        row = dict(r)
        if not flag:
            row.update(status="unsupported", reason="fragment-unsupported", root=None)
            rows.append(row)
            continue
        if r["status"] == "proved":
            root = nodes[r["root"]]
            target = r["target"]
            if valid[r["root"]] is None:
                row.update(status="unsupported", reason="fragment-unsupported", root=None)
                rows.append(row)
                continue
            ok = (
                valid[r["root"]]
                and not junk
                and root["kind"] != "comparison"
                and root["fact_type"] == target["fact_type"]
                and len(root["tuple"]) == len(target["tuple"])
                and all(_equal(a, b) for a, b in zip(root["tuple"], target["tuple"], strict=True))
            )
            if not ok:
                row.update(status="invalid", reason="proof-invalid", root=None)
        rows.append(row)
    return rows


def replay_witness(
    model_document: object,
    candidate_document: object,
    certificate: object,
    *,
    reference_inputs: tuple[tuple[str, bytes], ...] = (),
    limits=DEFAULT_LIMITS,
):
    targets = ()
    try:
        checked_limits(limits)
        certificate_shape(certificate, limits=limits)
        targets = tuple(r["target"] for r in certificate["results"])
        model, candidate, refs = intake(
            model_document, candidate_document, reference_inputs, limits=limits
        )
        if certificate["binding"] != identity(model, candidate, reference_inputs):
            return WitnessResult(3, reason="binding-stale")
        validate_targets(targets, model)
        flags, _, _ = classify_targets(model, targets, (candidate, *refs.values()))
        if not any(flags):
            return WitnessResult(2, result_rows(targets, "unsupported"))
        work = graph_work(certificate, limits=limits)
        rows = _replay_graph(model, candidate, refs, certificate, flags)
        return reduce_results(rows, work=work)
    except WitnessWorkError:
        return WitnessResult(4, result_rows(targets, "resource-refused"), reason="work-limit")
    except InvalidProof:
        return WitnessResult(1, result_rows(targets, "invalid"), reason="proof-invalid")
    except UnsupportedScalar:
        return WitnessResult(2, result_rows(targets, "unsupported"), reason="fragment-unsupported")
    except (
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        AttributeError,
        OSError,
        RecursionError,
        ModelLoadError,
        ModelValidationError,
        PopulationLoadError,
    ):
        return WitnessResult(3, reason="input-invalid")
