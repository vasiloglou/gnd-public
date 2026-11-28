"""Located samples from a second source through the ordinary evolution CLI."""
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest
import test_evolve_additive_policy as policy
from support.cli_runner import run_main

from gnd.evolve import SourceDocumentLocator


def setup_append(tmp_path, *, order=12, customer=3, alter=None, repeat_at=None):
    base = Path(__file__).parent / "fixtures/unattended/conforming.orm.yaml"
    text = base.read_text()
    fact = policy._doc(text)["fact_types"][0]
    after = deepcopy(fact)
    raw = f"Customer {customer} placed order {order}.".encode()
    excerpt = raw
    if repeat_at is not None:
        raw = excerpt + b" " + excerpt
    digest = sha256(raw).hexdigest()
    span = {"document_sha256": digest, "start": 0, "end": len(excerpt), "excerpt_sha256": sha256(excerpt).hexdigest()}
    after["sample_population"].append({"order": order, "customer": customer})
    after["provenance"]["sample_spans"].append({"row": 2, "span": span})
    if repeat_at is not None:
        second = dict(span, start=repeat_at, end=repeat_at + len(excerpt))
        after["sample_population"].append(dict(after["sample_population"][-1]))
        after["provenance"]["sample_spans"].append({"row": 3, "span": second})
    if alter is not None:
        alter(after)
    operations = (policy._op("add", SourceDocumentLocator(sha256=digest),
                            after={"sha256": digest, "label": "second"}, operation_id="declare"),
                  policy._op("modify", policy._element("fact_types", fact["id"]), before=fact, after=after))
    paths = policy._cli_workspace(tmp_path, operations, before_text=text)
    doc = tmp_path / "second.txt"
    doc.write_bytes(raw)
    return paths, doc


@pytest.mark.parametrize("order,customer", [(12, 3), (10, 1)])
def test_append_from_second_document(tmp_path, order, customer):
    paths, doc = setup_append(tmp_path, order=order, customer=customer)
    args = ("--policy", "additive", "--sample-document", str(doc))
    preview = run_main(policy._preview_argv(paths, *args))
    assert preview.returncode == 0, preview.stderr
    apply = run_main(policy._apply_argv(paths, *args))
    assert apply.returncode == 0, apply.stderr
    fact = policy._doc(paths["model"].read_text())["fact_types"][0]
    assert len(fact["sample_population"]) == len(fact["provenance"]["sample_spans"]) == 3


def test_conflicting_append_is_refused(tmp_path):
    paths, doc = setup_append(tmp_path, order=10, customer=3)
    result = run_main(policy._preview_argv(paths, "--policy", "additive", "--sample-document", str(doc)))
    assert result.returncode == 3, result.stderr
    assert json.loads(paths["preview"].read_text())["policy_issues"]
    before = paths["model"].read_bytes()
    assert run_main(policy._apply_argv(paths, "--policy", "additive", "--sample-document", str(doc))).returncode != 0
    assert paths["model"].read_bytes() == before


@pytest.mark.parametrize("alter", [
    lambda fact: fact["sample_population"][0].update(order=900),
    lambda fact: fact["sample_population"].reverse(),
    lambda fact: fact["provenance"]["sample_spans"][-1]["span"].update(excerpt_sha256="0" * 64),
    lambda fact: fact["provenance"]["sample_spans"].pop(),
    lambda fact: fact.update(reading="{Customer} ordered {Order}"),
])
def test_edits_and_bad_citations_refused(tmp_path, alter):
    paths, doc = setup_append(tmp_path, alter=alter)
    before = paths["model"].read_bytes()
    result = run_main(policy._preview_argv(paths, "--policy", "additive", "--sample-document", str(doc)))
    assert result.returncode != 0
    assert paths["model"].read_bytes() == before


@pytest.mark.parametrize("change", ["source", "model", "omit-source"])
def test_apply_rechecks_current_inputs(tmp_path, change):
    paths, doc = setup_append(tmp_path)
    args = ("--policy", "additive", "--sample-document", str(doc))
    assert run_main(policy._preview_argv(paths, *args)).returncode == 0
    if change == "source":
        doc.write_bytes(b"a different source")
    elif change == "model":
        with paths["model"].open("a") as f:
            f.write("\n")
    else:
        args = ("--policy", "additive")
    before = paths["model"].read_bytes()
    assert run_main(policy._apply_argv(paths, *args)).returncode != 0
    assert paths["model"].read_bytes() == before


@pytest.mark.parametrize("offset,distinct", [(0, False), (len(b"Customer 3 placed order 12. "), True)])
def test_repeated_tuple_in_one_document(tmp_path, offset, distinct):
    paths, doc = setup_append(tmp_path, repeat_at=offset)
    args = ("--policy", "additive", "--sample-document", str(doc))
    before = paths["model"].read_bytes()
    preview = run_main(policy._preview_argv(paths, *args))
    assert preview.returncode == (0 if distinct else 3), preview.stderr
    applied = run_main(policy._apply_argv(paths, *args))
    if distinct:
        assert applied.returncode == 0, applied.stderr
        fact = policy._doc(paths["model"].read_text())["fact_types"][0]
        assert len(fact["provenance"]["sample_spans"]) == 4
    else:
        assert applied.returncode != 0
        assert paths["model"].read_bytes() == before


def test_service_preserves_reviewed_refusal(tmp_path):
    from gnd.evolve import EvolutionService, read_evolution_proposal_document
    from gnd.evolve.service import EvolutionPolicyRefusedError

    paths, doc = setup_append(tmp_path)
    options = {"model_path": paths["model"], "evidence_root": paths["records"], "allowed_project_root": tmp_path}
    proposal = read_evolution_proposal_document(json.loads(paths["proposal"].read_text()))
    refused = EvolutionService(**options).preview(proposal, policy="additive")
    assert refused.policy_issues
    before = paths["model"].read_bytes()
    with pytest.raises(EvolutionPolicyRefusedError):
        EvolutionService(**options, sample_documents=(str(doc),)).apply(refused)
    assert paths["model"].read_bytes() == before


def test_shorter_citation_for_same_tuple_is_redundant(tmp_path):
    def shorten(fact):
        span = fact["provenance"]["sample_spans"][-1]["span"]
        span.update(end=8, excerpt_sha256=sha256(b"Customer").hexdigest())

    paths, doc = setup_append(tmp_path, repeat_at=0, alter=shorten)
    result = run_main(policy._preview_argv(paths, "--policy", "additive", "--sample-document", str(doc)))
    assert result.returncode == 3, result.stderr


def test_recovery_preserves_published_model(tmp_path):
    paths, doc = setup_append(tmp_path)
    args = ("--policy", "additive", "--sample-document", str(doc))
    assert run_main(policy._preview_argv(paths, *args)).returncode == 0
    assert run_main(policy._apply_argv(paths, *args)).returncode == 0
    published = paths["model"].read_bytes()
    doc.write_bytes(b"changed after publication")
    assert run_main(policy._apply_argv(paths, *args)).returncode == 0
    assert paths["model"].read_bytes() == published


def test_sample_document_does_not_transfer_ownership(tmp_path):
    import shutil

    import test_mc3_evolution as composition

    workspace = tmp_path / "included"
    shutil.copytree(composition.CORPUS, workspace)
    proposal = composition.read(workspace / "combined.proposal.json")
    fact = composition.read(workspace / "vocabulary-v1.orm.json")["fact_types"][0]
    candidate = deepcopy(fact)
    candidate.setdefault("sample_population", []).append({role["role_name"]: "a" for role in fact["roles"]})
    source = workspace / "observation.txt"
    source.write_bytes(b"a")
    digest = sha256(source.read_bytes()).hexdigest()
    candidate.setdefault("provenance", {}).setdefault("sample_spans", []).append(
        {"row": len(candidate["sample_population"]) - 1,
         "span": {"document_sha256": digest, "start": 0, "end": 1, "excerpt_sha256": digest}}
    )
    proposal["operations"] = [{"operation_id": "append", "kind": "modify",
        "locator": {"locator_kind": "element", "collection": "fact_types", "element_id": fact["id"]},
        "before": fact, "after": candidate}]
    composition.write(workspace / "append.json", proposal)
    result = composition.preview(workspace, "append.json", "--policy", "additive", "--sample-document", str(source))
    assert result.returncode != 0
    assert composition.ANSWERS["C02"]["reason"].encode() in result.stderr + result.stdout
    assert not (workspace / "records").exists()
