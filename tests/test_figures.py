"""The documentation figures are generated, current and small."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "tools/figures"
ASSETS = ROOT / "docs/assets"


def _load(name: str):
    sys.path.insert(0, str(FIGURES))
    spec = importlib.util.spec_from_file_location(f"gnd_docs_figures_{name}", FIGURES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


build = _load("build")
hero = _load("hero")
svgkit = _load("svgkit")


@pytest.mark.parametrize("name", sorted(build.figures()))
def test_committed_svg_matches_generator(name):
    assert (ASSETS / name).read_text(encoding="utf-8") == build.figures()[name], (
        f"{name} is stale; run python tools/figures/build.py")


@pytest.mark.parametrize("name", sorted(build.figures()))
def test_svg_is_theme_aware_and_accessible(name):
    svg = build.figures()[name]
    assert 'role="img"' in svg and "<title" in svg and "<desc" in svg
    assert "prefers-color-scheme: dark" in svg and ":where(#" in svg
    assert re.search(r'\bfill="#|\bstroke="#', svg) is None, "colours must come from theme tokens"


def test_hero_text_fits_its_cards():
    for node, _ in hero.storyboard().items:
        for text in _texts(node):
            content = text.text or "".join(child.text or "" for child in text.children)
            mono = "mono" in str(text.attrs.get("class", ""))
            right = float(text.attrs["x"]) + svgkit.text_width(content, float(text.attrs["font-size"]), mono)
            if text.attrs.get("text-anchor") is None:
                limit = 364 if float(text.attrs["x"]) < 400 else 764
                assert right <= limit, (content, right)


def test_hero_final_frame_is_the_accepted_plan():
    final = hero.frame_svg(hero.STORY)
    assert "exit 0 · plan accepted" in final and "check themselves" in final
    assert "exit 1 · plan rejected" not in final


def test_asset_sizes():
    assert (ASSETS / "hero.svg").stat().st_size < 60 * 1024
    assert (ASSETS / "hero.gif").stat().st_size < 2.5 * 1024 * 1024


def _texts(node):
    if node.tag == "text":
        yield node
    for child in node.children:
        yield from _texts(child)
