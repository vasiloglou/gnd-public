"""VG2 (reviewed-vocabulary-growth): the sources a new constraint may carry in ``gnd evolve``.

Issue 218. Rule D-12 admits a new ``sample`` and a new ``common-sense``
constraint when it is ``proposed`` and ``deontic``, as
``unattended-growth.md`` tells a host to write them. The spec is
``.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG2-spec.md``;
the test names are its section 8 rows (T5 lives in
``tests/test_induced_provenance.py``).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import test_evolve_additive_policy as policy
import test_unattended_model_growth_acceptance as acceptance
from support.cli_runner import run_main
from support.markdown_sections import markdown_section

REPO = Path(__file__).resolve().parents[1]
REFUSAL = "new sample and common-sense constraints must be proposed/deontic (D-12)"
DOCUMENT = (
    "A loan is renewed by a borrower on a date.\n"
    "Renewals seen: ana renewed L-1, ben renewed L-2.\n"
    "Each loan is renewed by at most one borrower.\n"
)
ROWS = "Each loan is renewed by at most one borrower"


def _reply() -> dict:
    """One growth round in the reply shape of unattended-growth.md: a fact type, a rows rule, a library rule."""
    return {
        "document": "round-4.txt",
        "object_types": [],
        "fact_types": [{
            "id": "loan_renewed_by_borrower",
            "reading": "{Loan} is renewed by {Borrower}",
            "roles": [{"object_type": "loan", "role_name": "loan"},
                      {"object_type": "borrower", "role_name": "borrower"}],
            "quote": "A loan is renewed by a borrower",
            "rows": [{"values": {"loan": "L-1", "borrower": "ana"}, "quote": "ana renewed L-1"},
                     {"values": {"loan": "L-2", "borrower": "ben"}, "quote": "ben renewed L-2"}],
        }],
        "subtype_links": [],
        "constraints": [
            {"host": "loan_renewed_by_borrower", "basis": "rows",
             "constraint": {"type": "uniqueness", "roles": ["loan"]}, "quote": ROWS,
             "rationale": "No loan in the rows is renewed by two borrowers."},
            {"host": "loan_renewed_by_borrower", "basis": "library", "library_entry": "ring-irreflexive",
             "constraint": {"type": "mandatory", "role": "loan"}, "quote": "A loan is renewed",
             "rationale": "Library entry: a renewal names its loan."},
        ],
    }


def _grown(tmp_path: Path) -> dict[str, Path]:
    ws = acceptance._workspace(tmp_path / "ws")
    for n, reply in enumerate(acceptance.ROUNDS, 1):
        acceptance._round(ws, n, reply)
    return ws


def _round(ws: dict[str, Path], reply: dict, tag: str, *, expect: int = 0):
    raw = DOCUMENT.encode()
    (ws["workspace"] / "round-4.txt").write_bytes(raw)
    acceptance._declare(ws["model"], raw, "round-4.txt")
    paths = acceptance._write_proposal(ws, tag, acceptance._operations(reply, raw))
    preview, result = acceptance._preview(paths, "--policy", "additive", expect=expect)
    return paths, preview, result


def _documents(ws: dict[str, Path]) -> tuple[Path, ...]:
    return (*(acceptance.FIXTURES / f"round-{n}.txt" for n in (1, 2, 3)), acceptance.SEED_DOCUMENT,
            ws["workspace"] / "round-4.txt")


# --- T1 (VG2-C1, C4): the growth document's proposal on an unattended model ---


def test_T1_a_rows_and_a_library_constraint_preview_and_apply(tmp_path):
    ws = _grown(tmp_path)
    paths, preview, _ = _round(ws, _reply(), "vg2")
    assert preview["policy"] == "additive" and preview["policy_issues"] == []
    applied = run_main(policy._apply_argv(paths, "--policy", "additive"))
    assert applied.returncode == 0, applied.stderr.decode()
    published = policy._doc(ws["model"].read_text(encoding="utf-8"))
    fact = policy._fact(published, "loan_renewed_by_borrower")
    assert [(c["source"], c["status"], c["modality"]) for c in fact["constraints"]] == [
        ("sample", "proposed", "deontic"), ("common-sense", "proposed", "deontic")]
    validated = acceptance._validate(ws["model"], _documents(ws))
    assert validated["exit_code"] == 0
    argv = ["validate", str(ws["model"]), "--require-documents", "--format", "json"]
    for document in _documents(ws):
        argv += ["--document", str(document)]
    assert run_main(argv).returncode == 0


# --- T2 (VG2-C2): confirmed or alethic is refused by name ---------------------


def _new(source: str, status: str, modality: str) -> dict:
    constraint = {"type": "mandatory", "role": "order", "source": source, "status": status,
                  "modality": modality, "rationale": "r"}
    constraint["provenance"] = ({"sample_size": 2} if source == "sample"
                                else {"library_entry": "ring-irreflexive"})
    return constraint


def _preview(tmp_path: Path, constraint: dict):
    operation = policy._op("add", policy._constraint_locator(policy.CONTROL, None, "mandatory"), after=constraint)
    return policy._preview(tmp_path, (operation,))


@pytest.mark.parametrize("source", ["sample", "common-sense"])
@pytest.mark.parametrize(("status", "modality"), [("confirmed", "deontic"), ("proposed", "alethic")])
def test_T2_confirmed_or_alethic_is_refused_by_name(tmp_path, source, status, modality):
    from gnd.evolve import EvolutionError

    with pytest.raises(EvolutionError, match=re.escape(REFUSAL)):
        _preview(tmp_path, _new(source, status, modality))


@pytest.mark.parametrize("source", ["sample", "common-sense"])
def test_T2_control_proposed_and_deontic_is_admitted_on_a_model_without_the_mode(tmp_path, source):
    preview = _preview(tmp_path, _new(source, "proposed", "deontic"))
    assert preview.policy_issues == ()


def test_T2_the_induction_refusal_still_comes_first(tmp_path):
    from gnd.evolve import EvolutionError

    constraint = _new("sample", "proposed", "deontic")
    constraint["provenance"]["induction"] = {}
    with pytest.raises(EvolutionError, match=re.escape("provenance.induction is allowed only under source induced")):
        _preview(tmp_path, constraint)


# --- T3 (VG2-C3): the three pages and the code agree --------------------------


def _section(path: str, heading: str) -> str:
    return markdown_section((REPO / path).read_text(encoding="utf-8"), heading)


def test_T3_the_d12_home_its_restatement_and_the_growth_page_agree():
    from gnd.evolve.service import EvolutionError, _enforce_d12

    def admitted(source: str) -> bool:
        before = {"version": 1, "fact_types": [{"id": "f", "roles": [], "constraints": []}]}
        candidate = json.loads(json.dumps(before))
        provenance = {"rationale_world_fact": "w"} if source == "llm-inferred" else {}
        candidate["fact_types"][0]["constraints"].append(
            {"type": "mandatory", "role": "r", "source": source, "status": "proposed", "modality": "deontic",
             "provenance": provenance})
        try:
            _enforce_d12(before, candidate)
        except EvolutionError:
            return False
        return True

    sources = ("explicit", "sample", "common-sense", "llm-inferred", "user-supplied", "imported", "induced")
    proposed_deontic = {source for source in sources if admitted(source)}
    # D-12 admits a proposed deontic induced constraint; its induction block is
    # required by candidate validation, not here.
    assert proposed_deontic == {"sample", "common-sense", "llm-inferred", "induced"}

    home = _section("src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md",
                    "## Evolve admission (D-12)")
    contract = _section("src/gnd/skills/gnd-model-evolve/references/evolution-contract.md",
                        "## 6. D-12 provenance and D-13 record")
    growth = _section("src/gnd/skills/gnd-model-from-text/references/unattended-growth.md",
                      "## Evidence for Steps 3 to 7")
    for source in ("sample", "common-sense", "llm-inferred", "induced"):
        assert f"A new `{source}` constraint is `proposed` and `deontic`" in home, source
    assert "`sample` or\n  `common-sense`, `proposed`, `deontic`" in contract
    assert "`rows` is `sample`" in growth and "`library` is `common-sense`" in growth
    assert REFUSAL in home


# --- T4 (VG2-C4): U5 and U8 still run on the unattended model ------------------


def _changed(ws: dict[str, Path], index: int, change) -> tuple:
    """The round's operations, the constraint at INDEX rebuilt with CHANGE applied (operations are immutable)."""
    raw = DOCUMENT.encode()
    (ws["workspace"] / "round-4.txt").write_bytes(raw)
    acceptance._declare(ws["model"], raw, "round-4.txt")
    operations = list(acceptance._operations(_reply(), raw))
    old = operations[index]
    after = json.loads(json.dumps(old.after, default=dict))
    change(after)
    operations[index] = policy._op("add", old.locator, after=after, operation_id=old.operation_id)
    return tuple(operations)


def test_T4_without_its_span_the_rows_constraint_is_refused_by_U5(tmp_path):
    ws = _grown(tmp_path)
    operations = _changed(ws, -2, lambda after: after["provenance"].pop("spans"))
    paths = acceptance._write_proposal(ws, "vg2-u5", operations)
    _, result = acceptance._preview(paths, "--policy", "additive", expect=3)
    # evolve prints the rule's message (U5), not its id
    assert b"constraints[0]: constraint cites no source span (provenance.spans)" in result.stderr


def test_T4_an_alethic_library_constraint_is_refused(tmp_path):
    ws = _grown(tmp_path)
    operations = _changed(ws, -1, lambda after: after.update(modality="alethic"))
    paths = acceptance._write_proposal(ws, "vg2-u8", operations)
    _, result = acceptance._preview(paths, "--policy", "additive", expect=3)
    # candidate validation runs before D-12, so U8 refuses it first (its message)
    assert b"constraints[1]: an unreviewed common-sense mandatory constraint cannot be alethic" in result.stderr


# --- review round 1 (notes/reviews/phase-VG2-r1), regression cases ----------


@pytest.mark.parametrize("source", ["sample", "common-sense"])
@pytest.mark.parametrize(("status", "modality"), [("confirmed", "deontic"), ("proposed", "alethic"),
                                                  ("confirmed", "alethic")])
def test_R1_F1_the_refusal_exits_3_at_the_command_line(tmp_path, source, status, modality):
    """F1: the refusal was missing from the CLI's exit classifier and exited 70."""
    operation = policy._op("add", policy._constraint_locator(policy.CONTROL, None, "mandatory"),
                           after=_new(source, status, modality))
    paths = policy._cli_workspace(tmp_path / "ws", (operation,))
    result = run_main(policy._preview_argv(paths))
    assert result.returncode == 3, result.stderr.decode()
    assert REFUSAL.encode() in result.stderr


@pytest.mark.parametrize("source", ["sample", "common-sense"])
def test_R1_F2_a_changed_sample_or_common_sense_constraint_is_judged_as_a_new_one(tmp_path, source):
    """F2: D-12 judges a new or changed constraint by one rule (its home's opening sentence).

    VG2's brief claimed a changed constraint was judged as before; it is judged
    as a new one, so a proposed, deontic sample or common-sense constraint whose
    roles change is now admitted, and refused when it becomes confirmed.
    """
    from gnd.evolve import EvolutionError

    before = dict(_new(source, "proposed", "deontic"), type="uniqueness", roles=["order"])
    before.pop("role")
    document = policy._doc()
    policy._fact(document, policy.CONTROL).setdefault("constraints", []).append(before)
    text = _yaml(document)
    locator = policy._constraint_locator(policy.CONTROL, before, "uniqueness")
    changed = dict(before, roles=["amount"])
    admitted = policy._preview(tmp_path / "a", (policy._op("modify", locator, before=before, after=changed),),
                               before_text=text)
    assert admitted.policy_issues == ()
    confirmed = dict(changed, status="confirmed")
    with pytest.raises(EvolutionError, match=re.escape(REFUSAL)):
        policy._preview(tmp_path / "b", (policy._op("modify", locator, before=before, after=confirmed),),
                        before_text=text)


def _yaml(document: dict) -> str:
    import io

    from ruamel.yaml import YAML

    buffer = io.StringIO()
    YAML().dump(document, buffer)
    return buffer.getvalue()


def test_R1_F4_a_fenced_copy_of_a_section_is_not_read_as_the_section():
    """F4: the section reader matched headings inside fenced examples."""
    text = ("# Page\n\n```markdown\n## Evolve admission (D-12)\n\n- A fenced example.\n```\n\n"
            "## Evolve admission (D-12)\n\n- The real rule.\n\n## Worked examples\n\n- after\n")
    section = markdown_section(text, "## Evolve admission (D-12)")
    assert "The real rule." in section and "A fenced example." not in section and "after" not in section
