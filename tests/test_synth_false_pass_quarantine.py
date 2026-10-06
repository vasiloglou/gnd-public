"""Both directions of a checker/witness disagreement quarantine and RETAIN (CR-04).

C1's contract is that a disagreement between the checker and the independent
constructive witness is retained under quarantine at exit 6 and never discarded
or relabelled. It held in exactly one direction.

- **False FAIL** (checker fails what the witness proves satisfied):
  :class:`CheckerWitnessDiscrepancy` carrying the document -> the CLI writes it
  under ``quarantine/`` and exits 6.
- **False PASS** (checker reports no alethic fail while the witness proves the
  constraint violated): a bare ``GeneratorError`` whose message NAMED the
  disagreement but carried no document -> exit 5, nothing written, and the event
  filed as a generator limitation (``not-derivable``) — a label that invites
  nobody to look.

That is backwards. A checker that fails to fail is the more dangerous direction
and the exact defect class D-01 says is a defect at any count and must be
reproduced, fixed and promoted; discarding the one artifact that reproduces it is
precisely the "defect vanishes from its own evaluation corpus" circularity.

A genuine generator failure — witness violated AND the checker fails too — is
still exit 5: the oscillation and budget branches keep their meaning, and the
final-verification fault path below proves the two causes did not collapse.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import gnd.correspondence
from gnd.cli import main
from gnd.model import load_model
from gnd.synth.assemble import (
    CheckerWitnessDiscrepancy,
    GeneratorError,
    _Builder,
    assemble_conforming,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
SETFAM = REPO_ROOT / "tests" / "fixtures" / "checker" / "setfam.orm.yaml"

_REAL_DOC = _Builder.doc


def _duplicating_doc(self, model_ref: str) -> dict:
    """Inject a duplicate row into every populated fact type.

    Breaks the constructive uniqueness witness while leaving the population
    structurally valid, so the checker is the only thing that could catch it.
    """
    doc = _REAL_DOC(self, model_ref)
    for rows in doc["facts"].values():
        if rows:
            rows.append(dict(rows[0]))
    return doc


@pytest.fixture
def false_pass_checker(monkeypatch):
    """A checker that waves through a population the witness proves violated."""
    from test_measure_negative_control import _ALWAYS_PASS

    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _ALWAYS_PASS)
    monkeypatch.setattr(_Builder, "doc", _duplicating_doc)


def test_the_false_pass_direction_raises_a_discrepancy_not_a_generator_error(
    false_pass_checker,
):
    """The type carries the document, which is what makes retention possible."""
    model = load_model(str(FULL_VOCAB))
    with pytest.raises(CheckerWitnessDiscrepancy) as caught:
        assemble_conforming(model, 1, model_ref=FULL_VOCAB.name)

    discrepancy = caught.value
    assert discrepancy.doc, "the population was discarded — nothing to reproduce with"
    kinds = {record["kind"] for record in discrepancy.discrepancies}
    assert kinds == {"candidate-false-pass"}, kinds
    for record in discrepancy.discrepancies:
        assert record["witness"] == "violated"
        assert record["observed"] == "pass"


def test_the_cli_quarantines_and_retains_the_false_pass_case(false_pass_checker, tmp_path):
    """Exit 6, the document on disk, and the discrepancy record beside it —
    symmetric with the false-FAIL direction, which already did all three."""
    out = tmp_path / "corpus"
    code = main(
        [
            "synth",
            str(FULL_VOCAB),
            "--out",
            str(out),
            "--seed",
            "1",
            "--class",
            "conforming",
            "--format",
            "json",
        ]
    )
    assert code == 6, "the false-pass direction still exits 5 and discards the case"

    quarantined = sorted((out / "quarantine").glob("*.json"))
    populations = [p for p in quarantined if not p.name.endswith(".discrepancy.json")]
    assert populations, "nothing was retained"
    doc = json.loads(populations[0].read_text(encoding="utf-8"))
    assert doc["facts"], "the retained document is empty"

    records = json.loads(
        populations[0].with_suffix(".discrepancy.json").read_text(encoding="utf-8")
    )
    assert {record["kind"] for record in records} == {"candidate-false-pass"}


def test_the_quarantine_message_names_the_direction(false_pass_checker, tmp_path, capsys):
    """`not-derivable` invited nobody to look; a candidate false pass must say so."""
    out = tmp_path / "corpus"
    assert main(["synth", str(FULL_VOCAB), "--out", str(out), "--seed", "1"]) == 6
    assert "false-pass" in capsys.readouterr().out


def test_a_genuine_generator_failure_is_still_exit_5(tmp_path):
    """The two causes did NOT collapse.

    With the REAL checker, an injected duplicate is caught by BOTH the witness and
    the checker — a generator failure, not a checker disagreement — so it stays a
    ``GeneratorError`` at exit 5.
    """
    model = load_model(str(SETFAM))

    def inject_duplicate(doc: dict) -> None:
        rows = doc["facts"].get("booking_by_person")
        if rows:
            rows.append(dict(rows[0]))

    with pytest.raises(GeneratorError):
        assemble_conforming(model, 1, model_ref="setfam.orm.yaml", fault=inject_duplicate)


def test_the_fault_path_also_distinguishes_the_two_directions(monkeypatch):
    """The twin site: an injected fault the checker does NOT catch is the same
    candidate false pass, and must not be filed as a generator limitation."""
    model = load_model(str(SETFAM))

    def inject_duplicate(doc: dict) -> None:
        rows = doc["facts"].get("booking_by_person")
        if rows:
            rows.append(dict(rows[0]))

    from test_measure_negative_control import _ALWAYS_PASS

    monkeypatch.setattr(gnd.correspondence, "evaluate_snapshot", _ALWAYS_PASS)
    with pytest.raises(CheckerWitnessDiscrepancy) as caught:
        assemble_conforming(model, 1, model_ref="setfam.orm.yaml", fault=inject_duplicate)
    assert {r["kind"] for r in caught.value.discrepancies} == {"candidate-false-pass"}
    assert caught.value.doc


def test_both_directions_share_one_retention_path():
    """Structural: the false-fail direction's exception type is the false-pass
    direction's too, so a future edit cannot fix retention for one only."""
    import inspect

    from gnd.synth import assemble
    from gnd.synth.oracle import constructive

    scanned = {assemble, constructive}
    assert {assemble.assemble_conforming.__globals__["__name__"], assemble.CheckerWitnessDiscrepancy.__init__.__globals__["__name__"]} <= {module.__name__ for module in scanned}
    source = "\n".join(inspect.getsource(module) for module in scanned)
    assert "candidate-false-pass" in source
    assert "candidate-false-fail" in source
    assert "yet the checker reports no alethic" not in source, (
        "the bare GeneratorError for the false-pass direction is back"
    )
    # Every raise of the broken-witness branch goes through the discrepancy type.
    convergence = inspect.getsource(assemble.assemble_conforming)
    for fragment in convergence.split("if broken:")[1:]:
        head = fragment.split("\n\n")[0]
        assert "CheckerWitnessDiscrepancy" in head, (
            "a broken-witness branch that never raises the retaining type — the "
            "false-pass direction discards its document again"
        )
