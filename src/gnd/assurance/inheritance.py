"""Pure comparison of inherited observations carried in release evidence.

This module reads through the caller's already-bound document lookup. It never
imports proof tools, reads a repository, invokes providers or authenticates a
release. Equal observations alone confer no execution capability or coverage.
"""

from __future__ import annotations

import ast
import json
import re

COUNTS = {"phase3": (827, 49), "phase4": (53, 146), "phase5": (26, 69)}
# Named v6.2 successors to two v6.0 trusted-admission cases, which carry no proof
# credit: Phase 4 changed the aggregate refusal (P5-024), leaving its two
# refusal mutants with no passing baseline, and Phase 2 admits the
# operations-plus-structured composition (P5-025), removing its two. Each case
# is compared against its exact successor, never the v6.0 answer.
PHASE5_SUCCESSOR_OBSERVATIONS = {
    "P5-024": {
        "layer2_diagnostic": None,
        "layer2_path_contains": None,
        "proof_credit": False,
        "public_exit": 3,
    },
    "P5-025": {
        "layer2_diagnostic": None,
        "layer2_path_contains": None,
        "proof_credit": False,
        "public_exit": 0,
    },
}
PHASE5_RETIRED_MUTATIONS = frozenset({"IN-024", "PR-024", "IN-025", "PR-025"})
CLAIM_FAMILY = "inherited-mathematics-with-current-correspondence"
RESULT_FIELDS = {
    "schema_version",
    "claim_family",
    "family",
    "provider",
    "status",
    "inputs",
    "map",
    "correspondence",
    "exports",
    "assumptions",
    "findings",
}
CORRESPONDENCE_FIELDS = {
    "schema_version",
    "claim_family",
    "family",
    "status",
    "inputs",
    "production_roster_digest",
    "runtime_domain",
    "observations",
    "mutations",
    "outputs",
    "findings",
}


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _index(rows: list[dict], keys: tuple[str, ...]) -> dict:
    indexed = {tuple(row[key] for key in keys): row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("duplicate inherited comparison coordinate")
    return indexed


def _phase3_output(read_document, row: dict) -> dict:
    value = read_document({"path": row["output_path"], "sha256": row["output_sha256"]})
    if any(value[key] != row[key] for key in ("case_id", "consumer", "scope_id")):
        raise ValueError("inherited route output disagrees with its coordinate")
    semantic = dict(value["semantic_observation"])
    for field in ("model", "population"):
        path = semantic.get(field)
        marker = "/runtime-inputs/"
        if isinstance(path, str) and marker in path:
            semantic[field] = "runtime-inputs/" + path.split(marker, 1)[1]
    return {"consumer_output": value["consumer_output"], "semantic_observation": semantic}


def compare_observations(family, prior, observations, mutations, read_document):
    if (len(observations), len(mutations)) != COUNTS[family]:
        raise ValueError("inherited observation or mutation census changed")
    keys = {
        "phase3": ("scope_id", "case_id", "consumer"),
        "phase4": ("scope_id", "case_id"),
        "phase5": ("case_id",),
    }[family]
    old, new = _index(prior["observations"], keys), _index(observations, keys)
    if set(old) != set(new):
        raise ValueError("inherited case/consumer membership changed")
    for key, current in new.items():
        previous = old[key]
        if family == "phase3":
            if current["branch_observed"] is not True:
                raise ValueError("inherited producer branch was not observed")
            expected, actual = (
                _phase3_output(read_document, previous),
                _phase3_output(read_document, current),
            )
        elif family == "phase4":
            if (
                current["proved"] != previous["proved"]
                or current["claim_family"] != previous["claim_family"]
            ):
                raise ValueError("inherited transition claim membership changed")
            # Only instrumentation line locations are metadata. Preserve every
            # public diagnostic and any future output field in the comparison.
            expected = {
                key: item for key, item in previous["actual"].items() if key != "emission_sites"
            }
            actual = {
                key: item for key, item in current["actual"].items() if key != "emission_sites"
            }
        else:
            if (
                current["scope_ids"] != previous["scope_ids"]
                or current["proved"] != previous["proved"]
            ):
                raise ValueError("inherited derivation claim membership changed")
            expected, actual = previous["actual"], current["actual"]
            if key[0] in PHASE5_SUCCESSOR_OBSERVATIONS:
                if previous["proved"] is not False:
                    raise ValueError("inherited successor case carries proof credit")
                expected = PHASE5_SUCCESSOR_OBSERVATIONS[key[0]]
                if _canonical(expected) != _canonical(actual):
                    raise ValueError(f"inherited successor observation differs: {key[0]}")
        if _canonical(expected) != _canonical(actual):
            raise ValueError(f"inherited semantic or consumer output changed: {family}:{key}")
    mutation_keys = ("scope_id", "lane") if family == "phase4" else ("mutation_id",)
    old, new = _index(prior["mutations"], mutation_keys), _index(mutations, mutation_keys)
    if family == "phase5":
        retired = {(identifier,) for identifier in PHASE5_RETIRED_MUTATIONS}
        if not retired <= set(old):
            raise ValueError("inherited retired mutation is not a predecessor mutation")
        old = {key: row for key, row in old.items() if key not in retired}
    if set(old) != set(new):
        raise ValueError("inherited mutation membership changed")
    for key, current in new.items():
        previous = old[key]
        if family == "phase3":
            fields = ("expected_failure", "gate", "lane", "operator", "target", "one_change")
            if type(current["observed_exit"]) is not int or current["observed_exit"] != 1:
                raise ValueError("inherited mutation was not killed at its named gate")
        else:
            fields = ("failure_signature", "lane")
            if current["baseline_passed"] is not True or current["detected"] is not True:
                raise ValueError("inherited mutation has no passing baseline and detected change")
            detail = current["detail"]
            if detail.get("timed_out", False) is not False:
                raise ValueError("inherited mutation timeout is not a semantic kill")
            if current["failure_signature"] in {"stale-source", "missing-runner", "timeout"}:
                raise ValueError("inherited mutation failed at an inadmissible gate")
        if any(current[field] != previous[field] for field in fields):
            raise ValueError("inherited mutation changed its failure signature or target")
    return {
        "family": family,
        "observation_count": len(observations),
        "mutation_count": len(mutations),
        "comparison": "equal in the frozen semantic and mutation coordinates",
    }


class _Documents:
    def __init__(self, addresses, raw, sources):
        self.addresses, self.raw = addresses, raw
        self.sources = {entry["path"] for entry in sources}

    def bind(self, reference, *, upstream=None):
        from gnd.assurance._wire import (
            relative as _relative,
        )

        if not isinstance(reference, dict) or not {"path", "sha256"} <= reference.keys():
            raise ValueError("inherited document edge is incomplete")
        path = reference["path"]
        _relative(path)
        actual = self.addresses.get(path)
        if actual is None or any(actual.get(key) != value for key, value in reference.items()):
            raise ValueError("inherited document edge is not bound")
        if upstream is not None and (path in self.sources) != upstream:
            raise ValueError("inherited document is on the wrong side of the input boundary")
        return path

    def bytes(self, reference, *, upstream=None):
        return self.raw[self.bind(reference, upstream=upstream)]

    def json(self, reference, *, upstream=None):
        from gnd.assurance._wire import (
            decode_json as _json,
        )

        return _json(self.bytes(reference, upstream=upstream))


def _exports(documents, reference, provider):
    path = documents.bind(reference, upstream=True)
    text = documents.raw[path].decode("utf-8")
    if provider == "nagini":
        names = [node.name for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)]
    else:
        names = re.findall(r"^\s*(?:lemma|theorem)\s+([A-Za-z0-9_]+)\s*:", text, re.MULTILINE)
    return {f"{path}::{name}" for name in names}


def _mathematical_basis(documents, mapping, family, prior):
    basis = mapping["mathematical_basis"]
    for reference in basis["files"]:
        documents.bind(reference, upstream=True)
    primary = "nagini" if family == "phase3" else "isabelle"
    exported, formal_map = set(), None
    if family == "phase3":
        receipt = documents.json(basis[family]["formal"], upstream=True)
        runs = receipt["runs"]
        if len(runs) != 4 or {run["source"]["path"] for run in runs} != set(
            basis[family]["source_paths"]
        ):
            raise ValueError("inherited Phase 3 mathematical source census changed")
        documents.bind(receipt["formal_map"], upstream=True)
        documents.bind(receipt["runner"], upstream=True)
        for run in runs:
            if (
                type(run["exit_code"]) is not int
                or run["exit_code"] != 0
                or run["timed_out"] is not False
            ):
                raise ValueError("inherited Phase 3 provider did not pass")
            exported |= _exports(documents, run["source"], "nagini")
            if (
                b"Verification successful"
                not in documents.bytes(run["stdout"], upstream=True).splitlines()
            ):
                raise ValueError("inherited provider has no success marker")
            documents.bind(run["stderr"], upstream=True)
    else:
        old_results = prior["formal_evidence" if family == "phase4" else "formal_providers"]
        if {(row["path"], row["sha256"]) for row in old_results} != {
            (row["path"], row["sha256"]) for row in basis[family]["formal_results"]
        }:
            raise ValueError(
                "inherited mathematical results differ from the original correspondence"
            )
        providers = set()
        for reference in basis[family]["formal_results"]:
            result = documents.json(reference, upstream=True)
            provider = result["backend"]
            if provider in providers or provider not in {"nagini", "isabelle"}:
                raise ValueError("inherited finite provider census changed")
            providers.add(provider)
            if (
                result["status"] != "passed"
                or type(result["returncode"]) is not int
                or result["returncode"] != 0
                or result["timed_out"] is not False
                or result["assumptions"] != []
                or not result["sources"]
            ):
                raise ValueError("inherited finite provider did not pass")
            map_reference = result["formal_map"]
            if set(map_reference) not in ({"path", "sha256"}, {"path", "sha256", "binding_count"}):
                raise ValueError("inherited formal map edge has unknown metadata")
            current_map = documents.json(
                {key: map_reference[key] for key in ("path", "sha256")}, upstream=True
            )
            if "binding_count" in map_reference and map_reference["binding_count"] != len(
                current_map["bindings"]
            ):
                raise ValueError("inherited formal map binding count changed")
            if formal_map is not None and formal_map != current_map:
                raise ValueError("inherited providers name different formal maps")
            formal_map = current_map
            documents.bind(result["runner"], upstream=True)
            for source in result["sources"]:
                documents.bind(source, upstream=True)
                if provider == primary:
                    exported |= _exports(documents, source, provider)
            for stream in ("stdout", "stderr"):
                if result[stream]["truncated"] is not False:
                    raise ValueError("inherited provider stream was truncated")
                # Legacy stream records also contain retention metadata, which
                # is checked separately from the canonical content address.
                edge = {key: result[stream][key] for key in ("path", "sha256")}
                raw = documents.bytes(edge, upstream=True)
                marker = (
                    b"Verification successful" if provider == "nagini" else b"Finished GND_V60_"
                )
                if stream == "stdout" and not any(
                    line.startswith(marker) for line in raw.splitlines()
                ):
                    raise ValueError("inherited provider has no success marker")
        if providers != {"nagini", "isabelle"}:
            raise ValueError("inherited finite claim omits an assigned provider")
    if not exported:
        raise ValueError("inherited mathematical exports are empty")
    return primary, exported, formal_map


def validate_result(result, manifest, addresses, raw, inputs):
    """Check one current inherited result without treating old runs as new."""
    from gnd.assurance._wire import (
        closed as _closed,
    )
    from gnd.assurance._wire import (
        strings as _strings,
    )

    _closed(result, RESULT_FIELDS, "inherited result")
    family = result["family"]
    if (
        result["schema_version"] != 2
        or result["claim_family"] != CLAIM_FAMILY
        or family not in COUNTS
        or result["status"] != "passed"
        or result["findings"] != []
    ):
        raise ValueError("inherited result is not a successful current correspondence claim")
    documents = _Documents(addresses, raw, inputs["sources"])
    mapping = documents.json(result["map"], upstream=True)
    _closed(
        mapping,
        {
            "schema_version",
            "claim_family",
            "historical_scope",
            "historical_receipts",
            "mathematical_basis",
            "bindings",
        },
        "inherited map",
    )
    if mapping["schema_version"] != 1 or mapping["claim_family"] != CLAIM_FAMILY:
        raise ValueError("inherited map has a different claim family")
    all_bindings = mapping["bindings"]
    if len(all_bindings) != 291 or len({binding["scope_id"] for binding in all_bindings}) != 291:
        raise ValueError("inherited map does not contain 291 unique obligations")
    bindings = {row["scope_id"]: row for row in all_bindings if row["family"] == family}
    if len(bindings) != {"phase3": 230, "phase4": 40, "phase5": 21}[family]:
        raise ValueError("inherited map changes its family census")
    prior = documents.json(mapping["historical_receipts"][family], upstream=True)
    if prior["status"] != "passed" or prior["findings"] != []:
        raise ValueError("inherited comparison receipt did not pass")
    primary, exported, formal_map = _mathematical_basis(documents, mapping, family, prior)
    historical_scope = documents.json(mapping["historical_scope"], upstream=True)
    old_rows = {
        row["scope_id"]: row
        for row in historical_scope["rows"]
        if row["coverage_state"] == "covered"
    }
    if family == "phase3":
        expected_ids = set(old_rows)
        if set(mapping["mathematical_basis"][family]["scope_ids"]) != expected_ids:
            raise ValueError("inherited mathematical basis changed the historical scope census")
    elif family == "phase4":
        expected_ids = {row["scope_id"] for row in prior["observations"] if row["proved"]}
    else:
        expected_ids = {
            scope for row in prior["observations"] if row["proved"] for scope in row["scope_ids"]
        }
    if set(bindings) != expected_ids:
        raise ValueError("inherited obligations differ from the original covered census")
    for scope, binding in bindings.items():
        _closed(
            binding,
            {
                "scope_id",
                "family",
                "provider",
                "theorems",
                "production_owners",
                "historical_row",
                "historical_obligation",
                "assumptions",
            },
            "inherited obligation",
        )
        theorems = _strings(binding["theorems"], "inherited theorems")
        documents.bind(binding["historical_row"], upstream=True)
        if binding["provider"] != primary or not theorems or not theorems <= exported:
            raise ValueError("inherited row is not bound to its primary mathematical exports")
        if family == "phase3":
            old = old_rows[scope]
            receipt = documents.json(binding["historical_row"], upstream=True)
            expected = {
                key: value
                for key, value in old.items()
                if key not in {"coverage_state", "proof_digest"}
            }
            if (
                binding["historical_row"]["sha256"] != old["proof_digest"]
                or receipt["binding"] != expected
                or binding["historical_obligation"] != old["proof_obligation"]
                or binding["assumptions"] != sorted(old["assumptions"])
                or binding["production_owners"] != [old["production_owner"]]
                or theorems != exported
                or any(
                    receipt["formal_evidence"][key]
                    != mapping["mathematical_basis"][family]["formal"][key]
                    for key in ("path", "sha256")
                )
                or receipt["correspondence_receipt"] != mapping["historical_receipts"][family]
            ):
                raise ValueError("inherited Phase 3 row changed its original proof binding")
        elif family == "phase4":
            if documents.json(binding["historical_row"], upstream=True) != formal_map:
                raise ValueError("inherited transition row names another formal map")
            selected = [
                row for row in formal_map["bindings"] if scope.startswith(row["scope_prefix"])
            ]
            if len(selected) != 1 or binding["historical_obligation"] != selected[0]["clause_id"]:
                raise ValueError("inherited transition row changes its mathematical clause")
            expected = {
                name for name in exported if name.endswith("::" + selected[0]["isabelle_lemma"])
            }
            if theorems != expected or binding["assumptions"]:
                raise ValueError("inherited transition row changes its assigned theorem")
        else:
            if documents.json(binding["historical_row"], upstream=True) != formal_map:
                raise ValueError("inherited derivation row names another formal map")
            selected = [row for row in formal_map["bindings"] if row["scope_id"] == scope]
            if (
                len(selected) != 1
                or binding["historical_obligation"] != selected[0]["proof_mutation"]
            ):
                raise ValueError("inherited derivation row changes its mathematical clause")
            names = {
                name
                for row in formal_map["propositions"]
                if row["id"] in selected[0]["propositions"]
                for name in row["exports"]["isabelle"]
            }
            expected = {name for name in exported if name.split("::")[1] in names}
            if theorems != expected or binding["assumptions"]:
                raise ValueError("inherited derivation row changes its assigned theorem")
    required_exports = {name for row in bindings.values() for name in row["theorems"]}
    required_assumptions = {name for row in bindings.values() for name in row["assumptions"]}
    if (
        result["provider"] != primary
        or _strings(result["exports"], "inherited exports") != required_exports
        or _strings(result["assumptions"], "inherited assumptions") != required_assumptions
        or not required_assumptions <= set(manifest["assumptions"])
    ):
        raise ValueError("inherited result disagrees with its assigned rows")
    current = documents.json(result["correspondence"], upstream=False)
    _closed(current, CORRESPONDENCE_FIELDS, "current inherited correspondence")
    if (
        current["schema_version"] != 1
        or current["claim_family"] != "current-inherited-observations"
        or current["family"] != family
        or current["status"] != "passed"
        or current["findings"] != []
        or current["inputs"] != result["inputs"]
        or current["production_roster_digest"] != inputs["production_roster_digest"]
        or current["runtime_domain"] != inputs["runtime_domain"]
    ):
        raise ValueError("inherited correspondence does not bind the current producer")
    outputs = [documents.bind(edge, upstream=False) for edge in current["outputs"]]
    if len(outputs) != len(set(outputs)):
        raise ValueError("inherited current output census is duplicated")
    if family == "phase3":
        for observation in [*current["observations"], *current["mutations"]]:
            if observation["output_path"] not in outputs:
                raise ValueError("inherited current route output was not retained")
            documents.bind(
                {"path": observation["output_path"], "sha256": observation["output_sha256"]},
                upstream=False,
            )
    compare_observations(
        family, prior, current["observations"], current["mutations"], documents.json
    )
    return bindings

_canonical.__module__ = 'gnd.assurance_inheritance'
_index.__module__ = 'gnd.assurance_inheritance'
_phase3_output.__module__ = 'gnd.assurance_inheritance'
compare_observations.__module__ = 'gnd.assurance_inheritance'
_Documents.__module__ = 'gnd.assurance_inheritance'
_exports.__module__ = 'gnd.assurance_inheritance'
_mathematical_basis.__module__ = 'gnd.assurance_inheritance'
validate_result.__module__ = 'gnd.assurance_inheritance'

# Public dependency and compatibility spellings; same predecessor objects.
Documents = _Documents
canonical = _canonical
exports = _exports
index = _index
mathematical_basis = _mathematical_basis
phase3_output = _phase3_output
