











from __future__ import annotations

from pathlib import Path

import pytest

from gnd.exp.frontmatter import (
    MAX_DOCUMENT_BYTES,
    FrontmatterError,
    read_frontmatter,
    render_frontmatter,
)

SPEC = """---
id: EXP-001-probe
kind: codegen
questions:
  - id: Q1
    text: Does the emitter agree with the model?
---

# EXP-001-probe

Body prose the reader must hand back untouched.
"""


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_a_fenced_document_yields_its_mapping_and_its_body(tmp_path: Path) -> None:

    mapping, body = read_frontmatter(_write(tmp_path / "SPEC.md", SPEC))

    assert mapping["id"] == "EXP-001-probe"
    assert mapping["kind"] == "codegen"
    assert [q["id"] for q in mapping["questions"]] == ["Q1"]
    assert "Body prose the reader must hand back untouched." in body
    assert "kind: codegen" not in body, (
        "the frontmatter block leaked into the body — a reader that hands the "
        "fence back as prose makes every downstream body check meaningless"
    )


def test_a_document_with_no_opening_fence_is_refused(tmp_path: Path) -> None:






    path = _write(tmp_path / "SPEC.md", "# EXP-001-probe\n\nNo frontmatter here.\n")

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert "frontmatter" in str(caught.value).lower()


def test_a_document_with_no_closing_fence_is_refused(tmp_path: Path) -> None:

    path = _write(tmp_path / "SPEC.md", "---\nid: EXP-001-probe\n\nbody\n")

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert "closing" in str(caught.value).lower() or "unterminated" in str(caught.value).lower()


def test_a_document_over_the_byte_cap_is_refused_by_stat_before_any_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:







    path = tmp_path / "SPEC.md"
    path.write_bytes(b"---\nid: EXP-001-probe\n---\n" + b"x" * MAX_DOCUMENT_BYTES)

    def _never(*args: object, **kwargs: object) -> str:
        raise AssertionError("read_text was called — the cap did not precede the read")

    monkeypatch.setattr(Path, "read_text", _never)

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert str(MAX_DOCUMENT_BYTES) in str(caught.value)


def test_a_missing_document_is_refused_as_a_frontmatter_error(tmp_path: Path) -> None:

    with pytest.raises(FrontmatterError):
        read_frontmatter(tmp_path / "absent.md")


def test_a_sequence_frontmatter_block_is_refused(tmp_path: Path) -> None:

    path = _write(tmp_path / "SPEC.md", "---\n- one\n- two\n---\nbody\n")

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert "mapping" in str(caught.value).lower()


def test_a_scalar_frontmatter_block_is_refused(tmp_path: Path) -> None:

    path = _write(tmp_path / "SPEC.md", "---\njust a string\n---\nbody\n")

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert "mapping" in str(caught.value).lower()


def test_an_empty_frontmatter_block_is_refused(tmp_path: Path) -> None:

    path = _write(tmp_path / "SPEC.md", "---\n---\nbody\n")

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert "mapping" in str(caught.value).lower()


def test_unparseable_yaml_in_the_block_is_refused(tmp_path: Path) -> None:

    path = _write(tmp_path / "SPEC.md", "---\nid: [unclosed\n---\nbody\n")

    with pytest.raises(FrontmatterError):
        read_frontmatter(path)


@pytest.mark.parametrize(
    "hostile_value",
    (
        "9" * 10_000,
        "[" * 2_000 + "0" + "]" * 2_000,
    ),
    ids=("long-integer", "deep-nesting"),
)
def test_non_yaml_parser_failures_are_normalized(
    tmp_path: Path, hostile_value: str
) -> None:


    path = _write(
        tmp_path / "SPEC.md",
        f"---\nid: EXP-001-probe\nbomb: {hostile_value}\n---\nbody\n",
    )

    with pytest.raises(FrontmatterError, match="unparseable frontmatter"):
        read_frontmatter(path)


def test_an_anchor_alias_frontmatter_block_is_refused(tmp_path: Path) -> None:







    path = _write(
        tmp_path / "SPEC.md",
        "---\na: &anchor [x, x]\nb: [*anchor, *anchor]\n---\nbody\n",
    )

    with pytest.raises(FrontmatterError) as caught:
        read_frontmatter(path)
    assert "alias" in str(caught.value).lower()


def test_render_round_trips_through_read(tmp_path: Path) -> None:

    mapping = {
        "id": "EXP-001-probe",
        "kind": "codegen",
        "title": "Probe",
        "questions": [{"id": "Q1", "text": "Does the emitter agree with the model?"}],
        "follows": [],
    }
    path = _write(tmp_path / "SPEC.md", render_frontmatter(mapping, "# Probe\n"))

    loaded, body = read_frontmatter(path)
    assert loaded == mapping
    assert body.strip() == "# Probe"


def test_two_renders_of_one_mapping_are_byte_identical(tmp_path: Path) -> None:





    mapping = {"kind": "codegen", "id": "EXP-001-probe", "title": "Probe"}
    first = render_frontmatter(mapping, "# Probe\n")
    second = render_frontmatter(dict(reversed(list(mapping.items()))), "# Probe\n")

    assert first == second, "two renders of one mapping disagreed byte for byte"
    assert first.endswith("\n")
    assert first.startswith("---\n")


def test_render_sorts_its_keys(tmp_path: Path) -> None:

    rendered = render_frontmatter({"z": 1, "a": 2, "m": 3}, "body\n")
    block = rendered.split("---\n")[1]
    keys = [line.split(":")[0] for line in block.splitlines() if line and not line[0].isspace()]
    assert keys == sorted(keys)
