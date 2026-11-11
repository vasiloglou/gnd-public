"""Issue 175: the package declares a long description that reads correctly on PyPI.

0.2.0 and 0.3.0 were published without a ``readme`` key, so their PyPI page
shows no text. PyPI renders the description on its own page: a relative link
or image path does not resolve there, and a pinned version would go stale at
the next release.
"""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)[^)]*\)")
VERSION = re.compile(r"\b\d+\.\d+\.\d+\b")


def description_problems(text: str) -> list[str]:
    """Say what would read wrongly on the PyPI project page."""
    problems = []
    for match in LINK.finditer(text):
        target = match[1]
        if match[0].startswith("!"):
            problems.append(f"image: {target}")
        elif not target.startswith("https://"):
            problems.append(f"link is not absolute: {target}")
    problems.extend(f"version: {found}" for found in VERSION.findall(text))
    if not text.startswith("# "):
        problems.append("no title")
    return problems


def declared_readme() -> Path:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert isinstance(project.get("readme"), str), "pyproject.toml declares no readme file"
    return ROOT / project["readme"]


def test_the_package_declares_a_description_that_reads_correctly_on_pypi():
    path = declared_readme()
    assert path.suffix == ".md" and path.is_file()
    text = path.read_text(encoding="utf-8")
    assert description_problems(text) == []
    assert "uv tool install get-nick-done\n" in text
    assert len(text.split()) >= 150, "the description is too short to describe the package"


def test_the_checks_report_what_pypi_would_not_render():
    assert description_problems("# T\n[guide](docs/installation.md)") == [
        "link is not absolute: docs/installation.md"
    ]
    assert description_problems("# T\n![hero](https://example.org/hero.svg)") == [
        "image: https://example.org/hero.svg"
    ]
    assert description_problems("# T\nuv tool install get-nick-done==0.3.0") == ["version: 0.3.0"]
    assert description_problems("text") == ["no title"]
    assert description_problems("# T\n[site](https://example.org/a)") == []
