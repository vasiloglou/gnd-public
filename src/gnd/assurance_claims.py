"""Validate serialized proof-input edges inside an authenticated release.

This module never runs a provider or establishes release authenticity. It checks
that claimed rows agree with the provider receipts and exact source inputs that
the trusted publisher placed in the package.
"""

from __future__ import annotations

from pathlib import PurePosixPath

INPUT_FIELDS = frozenset(
    {
        "schema_version",
        "production_roster_digest",
        "production_paths",
        "sources",
        "runtime_domain",
        "tools",
        "formal_map_sha256",
        "corpus_manifest_sha256",
        "output_nodes",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "provider",
        "status",
        "inputs",
        "exports",
        "assumptions",
        "tool",
        "process",
        "findings",
    }
)
OUTPUT_NODES = [
    "src/gnd/_assurance_evidence/anchor.json",
    "src/gnd/_assurance_evidence/manifest.json",
]


def _closed(document, fields, label):
    if not isinstance(document, dict) or set(document) != fields:
        raise ValueError(f"proof {label} has an invalid field census")


def _strings(value, label):
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) for item in value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"proof {label} is not sorted unique strings")
    return set(value)


def _validate_inputs(result, manifest, addresses, raw_documents, roles, production):
    from gnd.assurance_evidence import _json, _relative

    _closed(result["inputs"], {"path", "sha256"}, "input edge")
    input_path = result["inputs"]["path"]
    _relative(input_path)
    if (
        roles.get(input_path) != "proof-source"
        or addresses[input_path]["sha256"] != result["inputs"]["sha256"]
    ):
        raise ValueError("proof result does not name its bound input document")
    inputs = _json(raw_documents[input_path])
    _closed(inputs, INPUT_FIELDS, "inputs")
    if (
        inputs["schema_version"] != 1
        or inputs["production_roster_digest"] != manifest["production_roster_digest"]
        or inputs["runtime_domain"] != manifest["runtime_domain"]
        or inputs["production_paths"] != [entry["path"] for entry in production]
        or inputs["output_nodes"] != OUTPUT_NODES
    ):
        raise ValueError("proof inputs do not describe this release producer")
    sources = inputs["sources"]
    if not isinstance(sources, list) or not sources or len(sources) > 10000:
        raise ValueError("proof source census is empty or oversized")
    _strings([source["path"] for source in sources], "source paths")
    for source in sources:
        if (
            source != addresses.get(source["path"])
            or source["path"] in OUTPUT_NODES
            or roles.get(source["path"]) == "proof-result"
            or source["path"] == input_path
        ):
            raise ValueError("proof input has an unbound or cyclic source edge")
    source_paths = {source["path"] for source in sources}
    if not set(inputs["production_paths"]) <= source_paths:
        raise ValueError("proof source closure omits production")
    contracts = {}
    for field in ("formal_map_sha256", "corpus_manifest_sha256"):
        matches = [source for source in sources if source["sha256"] == inputs[field]]
        if len(matches) != 1:
            raise ValueError("proof input omits its formal or corpus contract")
        contracts[field] = matches[0]["path"]
    formal_map = _json(raw_documents[contracts["formal_map_sha256"]])
    if (
        not isinstance(formal_map, dict)
        or not {"bindings", "input_paths", "proof_sources", "normative_sources"}
        <= formal_map.keys()
    ):
        raise ValueError("proof formal map is incomplete")
    corpus = _json(raw_documents[contracts["corpus_manifest_sha256"]])
    if not isinstance(corpus, dict) or not isinstance(corpus.get("files"), list):
        raise ValueError("proof corpus manifest is incomplete")  # noqa: TRY004 -- preserve graph admission errors
    expected_paths = set(inputs["production_paths"]) | set(contracts.values())
    expected_paths |= _strings(formal_map["input_paths"], "formal source paths")
    for source in corpus["files"]:
        if source != addresses.get(source["path"]):
            raise ValueError("proof corpus source is not bound")
        expected_paths.add(source["path"])
    if source_paths != expected_paths:
        raise ValueError("proof transitive source closure differs from its contracts")
    for role in ("proof_sources", "normative_sources"):
        for source in formal_map[role]:
            if source != addresses.get(source["path"]) or source["path"] not in source_paths:
                raise ValueError("proof formal source is not bound")
    bindings = formal_map["bindings"]
    if not isinstance(bindings, list) or len({binding["scope_id"] for binding in bindings}) != len(
        bindings
    ):
        raise ValueError("proof scope binding census is invalid")
    return inputs, formal_map, bindings


def validate_claim_graph(manifest, addresses, raw_documents):
    # Import lazily to keep evidence loading as the sole public admission path.
    from gnd.assurance_evidence import _json

    claimed = [row for row in manifest["rows"] if row["status"] == "proved"]
    if not claimed:
        return
    roles = {row["address"]["path"]: row["role"] for row in manifest["files"]}
    results = {
        row["address"]["sha256"]: row["address"]["path"]
        for row in manifest["files"]
        if row["role"] == "proof-result"
    }
    production = sorted(
        (row["address"] for row in manifest["files"] if row["role"] in {"source", "schema"}),
        key=lambda row: row["path"],
    )
    tools_path = next(
        row["address"]["path"] for row in manifest["files"] if row["role"] == "toolchain"
    )
    tools = _json(raw_documents[tools_path])
    _closed(tools, {"schema_version", "providers"}, "toolchain")
    if tools["schema_version"] != 1 or not isinstance(tools["providers"], dict):
        raise ValueError("proof toolchain version or provider census is invalid")
    validated = {}
    inherited = {}
    for row in claimed:
        result_path = results.get(row["result_digest"])
        if result_path is None:
            raise ValueError("proof result is absent")
        candidate = _json(raw_documents[result_path])
        if isinstance(candidate, dict) and candidate.get("schema_version") == 2:
            from gnd.assurance_inheritance import validate_result

            if result_path not in inherited:
                current_inputs, _, _ = _validate_inputs(
                    candidate, manifest, addresses, raw_documents, roles, production
                )
                if (
                    not isinstance(current_inputs["tools"], dict)
                    or set(current_inputs["tools"]) != {"nagini", "isabelle"}
                    or current_inputs["tools"] != tools["providers"]
                ):
                    raise ValueError("inherited current tool identities differ from the release")
                inherited[result_path] = validate_result(
                    candidate, manifest, addresses, raw_documents, current_inputs
                )
            binding = inherited[result_path].get(row["scope_id"])
            if binding is None or (
                row["provider"] != candidate["provider"]
                or row["proof_inputs_digest"] != candidate["inputs"]["sha256"]
                or any(
                    row[key] != binding[key]
                    for key in ("theorems", "production_owners", "assumptions")
                )
            ):
                raise ValueError("inherited release row differs from its bound current result")
            continue
        if result_path not in validated:
            result = candidate
            _closed(result, RESULT_FIELDS, "result")
            if (
                result["schema_version"] != 1
                or result["status"] != "passed"
                or result["findings"] != []
                or result["provider"] not in {"nagini", "isabelle"}
            ):
                raise ValueError("proof result is not a successful assigned provider")
            exports = _strings(result["exports"], "exports")
            assumptions = _strings(result["assumptions"], "assumptions")
            if not exports or not assumptions <= set(manifest["assumptions"]):
                raise ValueError("proof exports are empty or assumptions undeclared")
            inputs, _formal_map, bindings = _validate_inputs(
                result, manifest, addresses, raw_documents, roles, production
            )
            if (
                not isinstance(inputs["tools"], dict)
                or inputs["tools"].get(result["provider"]) != result["tool"]
                or tools["providers"].get(result["provider"]) != result["tool"]
            ):
                raise ValueError("proof tool identity differs across the input/result edges")
            process = result["process"]
            if not isinstance(process, dict) or (
                process.get("status") != "passed"
                or process.get("exit") != 0
                or process.get("failure") is not None
                or process.get("cleanup_remaining") != []
            ):
                raise ValueError("proof process did not finish successfully")
            if (
                not isinstance(process.get("seconds"), (int, float))
                or not 0 <= process["seconds"] <= 600
            ):
                raise ValueError("proof process exceeds its bound")
            for name in ("stdout", "stderr"):
                stream = process.get(name)
                if not isinstance(stream, dict) or stream.get("path") != name:
                    raise ValueError("proof process stream shape is invalid")
                stream_path = (PurePosixPath(result_path).parent / "process" / name).as_posix()
                address = addresses.get(stream_path)
                if address is None or (
                    address["sha256"] != stream.get("sha256")
                    or address["bytes"] != stream.get("bytes")
                    or not isinstance(stream.get("raw_bytes"), int)
                    or not 0 <= stream["raw_bytes"] <= 64 * 1024 * 1024
                ):
                    raise ValueError("proof process stream is not bound")
            marker = (
                b"Verification successful"
                if result["provider"] == "nagini"
                else b"Finished GND_V60_P6"
            )
            stdout_path = (PurePosixPath(result_path).parent / "process/stdout").as_posix()
            if not any(line.startswith(marker) for line in raw_documents[stdout_path].splitlines()):
                raise ValueError("proof process has no provider success marker")
            assigned = {
                binding["theorem"]
                for binding in bindings
                if binding["provider"] == result["provider"]
            }
            if assigned != exports:
                raise ValueError("proof exports differ from their assigned scope census")
            validated[result_path] = result, inputs, exports, assumptions, bindings
        result, inputs, exports, assumptions, bindings = validated[result_path]
        if (
            row["provider"] != result["provider"]
            or row["proof_inputs_digest"] != result["inputs"]["sha256"]
            or not set(row["theorems"]) <= exports
            or not set(row["assumptions"]) <= assumptions
        ):
            raise ValueError("proof row disagrees with its provider result")
        binding = next(
            (binding for binding in bindings if binding["scope_id"] == row["scope_id"]), None
        )
        if binding is None or (
            binding["provider"] != row["provider"]
            or row["theorems"] != [binding["theorem"]]
            or row["production_owners"] != [binding["owner"]]
        ):
            raise ValueError("proof row is not the formal map's exact obligation")
