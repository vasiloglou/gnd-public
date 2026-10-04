"""Unit-only serialized graph shapes; these cannot pass release/schema admission.

The private graph validator receives already-hash-checked documents. The fixture
uses an invalid runtime domain and non-registry scope so it cannot accidentally
be used as a release or evidence of a provider execution.
"""

import hashlib
import json

import pytest

from gnd.assurance_claims import OUTPUT_NODES, validate_claim_graph


@pytest.fixture
def graph():
    files, addresses, raw = [], {}, {}

    def add(path, role, value):
        data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True).encode()
        address = {"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        raw[path] = data
        addresses[path] = address
        files.append({"role": role, "address": address})
        return address

    producer = add("src/gnd/unit.py", "source", b"# unit-only producer")
    case = add("case.json", "dependency", {"unit_case": True})
    proof = add("proof.py", "proof-source", b"# not a proof")
    normative = add("norms.txt", "semantics", b"unit-only normative input")
    corpus = add("corpus.json", "dependency", {"files": [case]})
    binding = {
        "scope_id": "unit-only:unregistered",
        "owner": "gnd.unit",
        "provider": "nagini",
        "theorem": "unit_only",
    }
    formal_map = add(
        "formal-map.json",
        "proof-source",
        {
            "bindings": [binding],
            "input_paths": ["norms.txt", "proof.py"],
            "proof_sources": [proof],
            "normative_sources": [normative],
        },
    )
    tool = {"path": "unit-provider", "sha256": "b" * 64, "version": "unit-only"}
    add("tools.json", "toolchain", {"schema_version": 1, "providers": {"nagini": tool}})
    runtime = {"unit_only_invalid_runtime": True}
    source_input = add(
        "proof-inputs.json",
        "proof-source",
        {
            "schema_version": 1,
            "production_roster_digest": "c" * 64,
            "production_paths": [producer["path"]],
            "sources": sorted(
                [producer, case, proof, normative, corpus, formal_map], key=lambda row: row["path"]
            ),
            "runtime_domain": runtime,
            "tools": {"nagini": tool},
            "formal_map_sha256": formal_map["sha256"],
            "corpus_manifest_sha256": corpus["sha256"],
            "output_nodes": OUTPUT_NODES,
        },
    )
    streams = {}
    for name, data in (("stdout", b"Verification successful\n"), ("stderr", b"")):
        address = add(f"process/{name}", "dependency", data)
        streams[name] = {
            "path": name,
            "sha256": address["sha256"],
            "bytes": len(data),
            "raw_bytes": len(data),
        }
    result = add(
        "result.json",
        "proof-result",
        {
            "schema_version": 1,
            "provider": "nagini",
            "status": "passed",
            "inputs": {"path": source_input["path"], "sha256": source_input["sha256"]},
            "exports": ["unit_only"],
            "assumptions": [],
            "tool": tool,
            "process": {
                "status": "passed",
                "exit": 0,
                "failure": None,
                "cleanup_remaining": [],
                "seconds": 0.01,
                **streams,
            },
            "findings": [],
        },
    )
    manifest = {
        "files": files,
        "production_roster_digest": "c" * 64,
        "runtime_domain": runtime,
        "assumptions": [],
        "rows": [
            {
                "scope_id": binding["scope_id"],
                "status": "proved",
                "provider": "nagini",
                "theorems": ["unit_only"],
                "production_owners": ["gnd.unit"],
                "assumptions": [],
                "proof_inputs_digest": source_input["sha256"],
                "result_digest": result["sha256"],
            }
        ],
    }
    return manifest, addresses, raw


def test_internally_consistent_graph_shape_passes_only_the_private_validator(graph):
    validate_claim_graph(*graph)


@pytest.mark.parametrize(
    "mutation",
    [
        "failed",
        "unknown-export",
        "assumption",
        "wrong-input",
        "source-omitted",
        "output-cycle",
        "runtime",
        "producer",
        "tool",
        "exit",
        "timeout",
        "orphan",
        "stream",
        "marker",
        "formal-scope",
        "formal-owner",
        "upstream-proof",
        "corpus-source",
    ],
)
def test_claim_graph_rejects_broken_semantic_and_identity_edges(graph, mutation):
    manifest, addresses, raw = graph

    def edit(path, change):
        value = json.loads(raw[path])
        change(value)
        raw[path] = json.dumps(value).encode()

    if mutation == "failed":
        edit("result.json", lambda value: value.update(status="failed"))
    elif mutation == "unknown-export":
        edit("result.json", lambda value: value.update(exports=["wrong"]))
    elif mutation == "assumption":
        edit("result.json", lambda value: value.update(assumptions=["undeclared"]))
    elif mutation == "wrong-input":
        edit("result.json", lambda value: value["inputs"].update(sha256="0" * 64))
    elif mutation == "source-omitted":
        edit("proof-inputs.json", lambda value: value["sources"].pop())
    elif mutation == "output-cycle":
        edit("proof-inputs.json", lambda value: value.update(output_nodes=[]))
    elif mutation == "runtime":
        edit("proof-inputs.json", lambda value: value.update(runtime_domain={}))
    elif mutation == "producer":
        edit("proof-inputs.json", lambda value: value.update(production_roster_digest="0" * 64))
    elif mutation == "tool":
        edit("result.json", lambda value: value["tool"].update(version="different"))
    elif mutation in {"exit", "timeout", "orphan", "stream"}:

        def change(value):
            process = value["process"]
            if mutation == "exit":
                process["exit"] = 1
            elif mutation == "timeout":
                process["seconds"] = 601
            elif mutation == "orphan":
                process["cleanup_remaining"] = [123]
            else:
                process["stdout"]["sha256"] = "0" * 64

        edit("result.json", change)
    elif mutation == "marker":
        raw["process/stdout"] = b"No provider ran\n"
    elif mutation in {"formal-scope", "formal-owner"}:
        key = "scope_id" if mutation == "formal-scope" else "owner"
        edit("formal-map.json", lambda value: value["bindings"][0].update({key: "wrong"}))
    elif mutation == "upstream-proof":
        edit("formal-map.json", lambda value: value["proof_sources"][0].update(sha256="0" * 64))
    else:
        edit("corpus.json", lambda value: value["files"][0].update(sha256="0" * 64))
    with pytest.raises(ValueError, match="proof"):
        validate_claim_graph(manifest, addresses, raw)
