from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gnd.exp.frontmatter import read_frontmatter

COMPLETED_FIELD = "requirements-completed"
PHASES_ROOT = Path(__file__).parent
pinning = pytest.mark.skipif(not PHASES_ROOT.is_dir(), reason="the public fixture parent is absent")

def _frontmatter(path: Path) -> dict[str, Any]:
    """The document's frontmatter through the SHIPPED reader.

    Not ``yaml.safe_load`` over a hand-split file: ``read_frontmatter`` applies
    the byte cap before the read and refuses anchors and aliases, and running
    phase 3's own parser over this project's own artifacts is the dogfooding the
    plan asked for.
    """
    mapping, _body = read_frontmatter(path)
    return mapping


def _declares(mapping: dict[str, Any], field: str) -> bool:
    """Is ``field`` DECLARED — present with a value that is not empty?

    ``requirements-completed: []`` is not a claim of completion, and treating it
    as one would make the gate fire on a plan that completed nothing. Absent and
    empty are the same state for this rule, and saying so once here is what keeps
    the call sites from disagreeing about it.
    """
    value = mapping.get(field)
    if value is None:
        return False
    if isinstance(value, (list, tuple, set, dict, str)):
        return len(value) > 0
    return bool(value)


@pinning
def test_a_body_mention_is_not_a_declaration(tmp_path):
    """A grep-based gate would flag the closing plan's own prose.

    ``03-07-PLAN.md`` writes ``requirements-completed`` ten times in its body
    while explaining the rule, so a text scan cannot tell an explanation from a
    declaration. This test builds both documents and asserts the reader
    separates them — and asserts the NAIVE SCAN fires on both, so the test
    cannot pass over a gate that stopped distinguishing anything.
    """
    body_only = tmp_path / "03-99-PLAN.md"
    body_only.write_text(
        "---\n"
        "phase: 03-experiments-codegen-conformance\n"
        "plan: 99\n"
        "requirements: [EXP-01]\n"
        "requirements-partial: [EXP-01]\n"
        "---\n\n"
        "This plan explains that only the closing plan may record\n"
        "`requirements-completed`, and this plan is not it.\n",
        encoding="utf-8",
    )
    declaring = tmp_path / "03-98-PLAN.md"
    declaring.write_text(
        "---\n"
        "phase: 03-experiments-codegen-conformance\n"
        "plan: 98\n"
        "requirements: [EXP-01]\n"
        "requirements-completed: [EXP-01]\n"
        "---\n\nNo prose at all.\n",
        encoding="utf-8",
    )

    assert not _declares(_frontmatter(body_only), COMPLETED_FIELD), (
        "a body mention was read as a declaration — the gate is scanning text"
    )
    assert _declares(_frontmatter(declaring), COMPLETED_FIELD), (
        "a real frontmatter declaration was not seen — the gate reads nothing"
    )

    # The negative control: the naive scan this gate replaces fires on BOTH, so
    # the distinction above is a property of the reader and not of the fixtures.
    naive = [
        path.name
        for path in (body_only, declaring)
        if COMPLETED_FIELD in path.read_text(encoding="utf-8")
    ]
    assert naive == [body_only.name, declaring.name], (
        f"the naive text scan did not fire on both documents ({naive}); the "
        f"fixtures no longer demonstrate the difference the reader makes"
    )


@pinning
def test_an_empty_completion_list_is_not_a_completion(tmp_path):
    """``requirements-completed: []`` claims nothing, and must not be a finding.

    Stated as its own test because the alternative reading — presence is the
    declaration — makes the gate fire on a plan that completed nothing, and a
    gate that fires on a compliant document is one somebody switches off.
    """
    empty = tmp_path / "03-97-PLAN.md"
    empty.write_text(
        "---\nphase: p\nplan: 97\nrequirements-completed: []\n---\n\nbody\n",
        encoding="utf-8",
    )
    assert not _declares(_frontmatter(empty), COMPLETED_FIELD)
