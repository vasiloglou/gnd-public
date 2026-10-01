"""``gnd extract`` — the four-file bundle, its digests, and the caller contract.

Every assertion runs against emitted files on disk (P-3): the bundle is the
artifact boundary's currency, so the tests read what a skill would read.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import gnd.cli
from gnd.cli import main
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
FULL_VOCAB = FIXTURES / "models" / "full_vocabulary.orm.yaml"
INVALID_MODEL = FIXTURES / "models" / "invalid" / "role_seq_arity.orm.yaml"


def test_extract_cli_emits_the_bundle(tmp_path: Path) -> None:
    """Exit 0 and exactly four files, the index's sha256 digests matching the
    emitted bytes, and the PANEL-6 ``header_template`` — ``model``/``source``/
    ``covers`` (and ``model_id`` when declared) set by deterministic code, the
    caller contract the gnd-extract skill copies VERBATIM and ``gnd verify``
    re-derives and enforces. The LLM never chooses header fields."""
    out = tmp_path / "bundle"
    assert main(["extract", str(FULL_VOCAB), "--out", str(out)]) == 0

    names = sorted(path.name for path in out.iterdir())
    assert names == [
        "full_vocabulary.applicable.json",
        "full_vocabulary.artifacts.json",
        "full_vocabulary.projection.schema.json",
        "full_vocabulary.verbalization.txt",
    ], f"the bundle must be exactly four files; got {names}"

    index = json.loads(
        (out / "full_vocabulary.artifacts.json").read_text(encoding="utf-8")
    )

    assert sorted(index["artifacts"]) == [
        "full_vocabulary.applicable.json",
        "full_vocabulary.projection.schema.json",
        "full_vocabulary.verbalization.txt",
    ]
    for rel, meta in index["artifacts"].items():
        assert (
            meta["sha256"] == hashlib.sha256((out / rel).read_bytes()).hexdigest()
        ), f"digest mismatch for {rel} — the index does not bind its bundle"

    assert (
        index["model"]["sha256"] == hashlib.sha256(FULL_VOCAB.read_bytes()).hexdigest()
    )

    model = load_model(str(FULL_VOCAB))
    # full_vocabulary declares no model_id, so the template omits the key.
    assert index["header_template"] == {
        "model": Path(str(FULL_VOCAB)).as_posix(),
        "source": "agent-output",
        "covers": sorted(str(ft["id"]) for ft in model.fact_types),
    }

    # The applicable artifact carries the R-10' disposition end to end.
    applicable = json.loads(
        (out / "full_vocabulary.applicable.json").read_text(encoding="utf-8")
    )
    assert sum(1 for row in applicable["fact_types"] if not row["applicable"]) == 1


def test_extract_cli_rejects_invalid_model(tmp_path: Path) -> None:
    """A layer-2-invalid model exits 3 (the band-3 load arms mirror
    ``_cmd_check``) and writes nothing."""
    out = tmp_path / "bundle"
    assert main(["extract", str(INVALID_MODEL), "--out", str(out)]) == 3
    assert not out.exists(), "an invalid model must not leave a partial bundle"


def test_extract_cli_refuses_escaping_out_path(tmp_path: Path, monkeypatch) -> None:
    """An output path escaping the target root exits 74 (EXIT_IO), THROUGH
    ``paths.safe_output_path`` → ``install.safe_destination`` — never a fresh
    guard (a second copy of a security guard is how the two drift apart).

    ``paths.slug`` on the model-derived stem is the front-line normaliser, so
    an escaping stem is simulated by patching the stem derivation — proving
    the backstop in the command body refuses it even when the front line is
    bypassed (T-02.1-03)."""
    monkeypatch.setattr(gnd.cli, "_extract_stem", lambda _path: "../escape")
    out = tmp_path / "bundle"
    out.mkdir()
    assert main(["extract", str(FULL_VOCAB), "--out", str(out)]) == 74
    assert list(out.iterdir()) == [], "a refused path must not leave writes behind"
    assert not list(tmp_path.glob("escape*")), (
        "the escaping write landed OUTSIDE the target root — the guard is dead"
    )


def test_interrupted_bundle_replacement_leaves_a_rejectable_index(
    tmp_path: Path, monkeypatch
) -> None:
    old_model = tmp_path / "old" / FULL_VOCAB.name
    old_model.parent.mkdir()
    old_model.write_bytes(FULL_VOCAB.read_bytes() + b"\n")
    out = tmp_path / "bundle"
    assert main(["extract", str(old_model), "--out", str(out)]) == 0

    real_replace = os.replace
    calls = 0

    def fail_during_commit(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated interruption")
        real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_during_commit)

    assert main(["extract", str(FULL_VOCAB), "--out", str(out)]) == 74
    issue = gnd.cli._artifact_index_issue(
        str(FULL_VOCAB),
        str(out),
        ("full_vocabulary.applicable.json", "full_vocabulary.projection.schema.json"),
    )
    assert issue is not None, "a mixed post-interruption bundle must never validate"
