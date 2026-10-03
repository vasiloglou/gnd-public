from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

ADVERSARIAL=Path(__file__).resolve().parents[1]/"tests/fixtures/adversarial"

def test_every_adversarial_fixture_is_claimed_by_the_corpus_manifest():
    """The adversarial populations are deliberately NON-conforming, so they are
    excluded from the pairing table above — but they must not therefore be
    unowned. Each one is claimed by a manifest case that pins its exit code."""
    manifest = YAML(typ="safe").load(
        (ADVERSARIAL / "manifest.yaml").read_text(encoding="utf-8")
    )
    claimed = {
        ADVERSARIAL / str(case["population"])
        for case in manifest["cases"]
        if case.get("population")
    }
    on_disk = set((ADVERSARIAL / "populations").iterdir())
    assert claimed == on_disk, (
        f"every adversarial population must be claimed by a manifest case.\n"
        f"on disk but unclaimed: {sorted(p.name for p in on_disk - claimed)}\n"
        f"claimed but absent:    {sorted(p.name for p in claimed - on_disk)}"
    )
