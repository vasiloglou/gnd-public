"""P3-SY: ``gnd synth`` refuses a structured-derivation model, by name (T3.3).

Corpus: ``tests/fixtures/phase3-consumers`` story 1. Committed RED: at commit
time synth exits 0 over the structured model while labelling a band-1
population "conforming" -- the silently mislabelled corpus case the refusal
exists to prevent.
"""

from __future__ import annotations

import json
from pathlib import Path

from support.cli_runner import run_main

CORPUS = Path(__file__).parent / "fixtures" / "phase3-consumers"
REFUSAL = json.loads((CORPUS / "answers" / "synth-refusal.json").read_text(encoding="utf-8"))


def _run(arguments: list[str]) -> tuple[int, str]:
    result = run_main(arguments, capture_stderr=False)
    return result.returncode, result.stdout.decode("utf-8", errors="surrogatepass")


def test_synth_refuses_a_structured_derivation_model_at_the_generator_band(
    tmp_path: Path,
) -> None:
    """P3-SY-1: exit 5 with the exact named refusal, before any corpus byte."""

    out = tmp_path / "corpus"
    code, stdout = _run(
        [
            "synth",
            str(CORPUS / "eligibility.orm.yaml"),
            "--class",
            "conforming",
            "--seed",
            "7",
            "--out",
            str(out),
            "--format",
            "json",
        ]
    )
    assert code == REFUSAL["exit_code"] == 5
    record = json.loads(stdout)
    assert record["exit_code"] == 5
    assert record["error"] == REFUSAL["error"]
    assert not out.exists() or not any(out.iterdir())


def test_synth_refusal_message_names_the_structured_fact_types(tmp_path: Path) -> None:
    """The message is a named stand-down, not a generic failure."""

    code, stdout = _run(
        [
            "synth",
            str(CORPUS / "eligibility.orm.yaml"),
            "--class",
            "conforming",
            "--seed",
            "7",
            "--out",
            str(tmp_path / "corpus"),
            "--format",
            "json",
        ]
    )
    assert code == 5
    error = json.loads(stdout)["error"]
    assert error.startswith("synth-derivation-unsupported:")
    assert "book_is_eligible" in error


def test_synth_over_a_legacy_string_derivation_model_is_unchanged(tmp_path: Path) -> None:
    """P3-SY-2: the A10 synth half -- a string rule does not trip the refusal."""

    out = tmp_path / "corpus"
    code, _ = _run(
        [
            "synth",
            str(CORPUS / "legacy-derived.orm.yaml"),
            "--class",
            "conforming",
            "--seed",
            "7",
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert (out / "index.json").is_file()
