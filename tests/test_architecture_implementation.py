

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from gnd.architecture import (
    MAX_ARCHITECTURE_CONTRACT_BYTES,
    ArchitectureContractError,
    load_architecture_contract,
    parse_architecture_contract_bytes,
)


@pytest.mark.parametrize("version", ["true", "1.0"])
def test_contract_version_refuses_coercible_non_integers(version: str) -> None:
    data = (
        f"contract_version: {version}\n"
        "modules: []\n"
        "artifacts: []\n"
        "entry_points: []\n"
        "smoke: []\n"
    ).encode()

    with pytest.raises(ArchitectureContractError) as caught:
        parse_architecture_contract_bytes(data, source=f"contract-version-{version}")
    assert caught.value.issues[0].rule_id == "architecture:shape"


@pytest.mark.slow
def test_large_semantic_lists_finish_inside_the_declared_bound() -> None:
                                                                            
                                                                              
                                                                       
                                                      
    document = {
        "contract_version": 1,
        "modules": [],
        "artifacts": [],
        "entry_points": [
            {
                "module": f"package.entry_{index}",
                "subcommands": [],
                "flags": [],
                "consumes": [],
                "produces": [],
                "exits": [],
            }
            for index in range(4_500)
        ],
        "smoke": [],
    }
    data = json.dumps(document, separators=(",", ":")).encode("utf-8")
    assert len(data) < MAX_ARCHITECTURE_CONTRACT_BYTES
    assert len(data) > MAX_ARCHITECTURE_CONTRACT_BYTES * 2 // 5

    started = time.perf_counter()
    contract = parse_architecture_contract_bytes(data, source="generated-many-entry-points")
    elapsed = time.perf_counter() - started

    assert len(contract.entry_points) == 4_500
    assert elapsed < 5.0


def test_declared_exit_codes_are_indexed_once_not_once_per_smoke() -> None:
    from gnd import architecture as architecture_module

    reads = 0

    class ObservedExit:
        @property
        def code(self) -> int:
            nonlocal reads
            reads += 1
            return 0

    exit_count = 8
    smoke_count = 8
    entry_point = architecture_module.ArchitectureEntryPoint.model_construct(
        module="package.cli",
        subcommands=(),
        flags=(),
        consumes=(),
        produces=(),
        exits=tuple(ObservedExit() for _ in range(exit_count)),
    )
    contract = architecture_module.ArchitectureContract.model_construct(
        contract_version=1,
        modules=(),
        artifacts=(),
        entry_points=(entry_point,),
        smoke=tuple(
            architecture_module.ArchitectureSmoke(
                id=f"smoke-{index}",
                entry_point="package.cli",
                argv=(),
                expect_exit=0,
            )
            for index in range(smoke_count)
        ),
    )

    assert architecture_module._semantic_issues(contract) == ()
    assert reads == exit_count


def test_bad_caller_owned_root_descriptor_uses_the_closed_error_surface(
    tmp_path: Path,
) -> None:
    with pytest.raises(ArchitectureContractError) as caught:
        load_architecture_contract(tmp_path, root_fd=-1)
    assert caught.value.issues[0].rule_id == "architecture:read"


                                                                             
                                                                                 
 
                                                                              
                                                                              
                                                                              
                                                                             

_SMOKE_ID_CONTRACT = (
    "contract_version: 1\n"
    "modules: []\n"
    "artifacts: []\n"
    "entry_points:\n"
    "- module: package.cli\n"
    "  subcommands: []\n"
    "  flags: []\n"
    "  consumes: []\n"
    "  produces: []\n"
    "  exits: [{{code: 0, meaning: ok}}]\n"
    "smoke:\n"
    "- id: {smoke_id}\n"
    "  entry_point: package.cli\n"
    "  argv: []\n"
    "  expect_exit: 0\n"
)


@pytest.mark.parametrize(
    ("label", "smoke_id"),
    [
        ("open-bracket", '"known[user"'),
        ("close-bracket", '"known]user"'),
        ("both-brackets", '"smoke[0]"'),
        ("interior-space", '"known user"'),
        ("leading-space", '" known-user"'),
        ("trailing-space", '"known-user "'),
        ("tab", '"known\\tuser"'),
        ("newline", '"known\\nuser"'),
                                                                         
                                                                      
        ("no-break-space", '"known\u00a0user"'),
        ("em-space", '"known\u2003user"'),
        ("ideographic-space", '"known\u3000user"'),
    ],
)
def test_smoke_id_that_cannot_survive_the_node_id_bridge_is_refused(
    label: str, smoke_id: str
) -> None:




    data = _SMOKE_ID_CONTRACT.format(smoke_id=smoke_id).encode()

    with pytest.raises(ArchitectureContractError) as caught:
        parse_architecture_contract_bytes(data, source=f"smoke-id-{label}")

    rule_ids = [issue.rule_id for issue in caught.value.issues]
    assert "architecture:smoke-id-characters" in rule_ids, label
    offending = next(
        issue for issue in caught.value.issues
        if issue.rule_id == "architecture:smoke-id-characters"
    )
    assert offending.path == "smoke.0.id", label
    assert "test_smoke[<id>]" in offending.message, label


@pytest.mark.parametrize(
    "smoke_id",
    [
        "known-user-recommend",
        "unknown-user-refused",
        "report-smoke",
        "unknown-expense-refused",
        "a",
        "row_0.case-1",
    ],
)
def test_ordinary_smoke_ids_still_load(smoke_id: str) -> None:



    data = _SMOKE_ID_CONTRACT.format(smoke_id=smoke_id).encode()

    contract = parse_architecture_contract_bytes(data, source=f"smoke-id-{smoke_id}")

    assert [row.id for row in contract.smoke] == [smoke_id]
















