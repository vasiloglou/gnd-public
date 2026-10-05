"""Deterministic SVG building blocks for the documentation figures.

Every figure is a small tree of :class:`Node` objects rendered to text with
fixed number formatting and sorted attributes, so regenerating a figure from
unchanged source yields identical bytes. Colours are theme tokens: a figure
embeds its own light and dark values (used when it is shown as an image, for
example on GitHub), while the documentation site overrides the same tokens
from its stylesheet so that the site's theme toggle wins when the figure is
inlined. ``bake`` resolves the tokens to literal colours for rasterizers that
do not evaluate CSS custom properties.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

LIGHT = {
    "bg": "#f1f4ef", "card": "#ffffff", "line": "#b7cec5", "ink": "#183936", "muted": "#5b6f6b",
    "primary": "#164f4b", "accent": "#b34e26", "ok": "#1f7a4d", "ok-bg": "#dcece3",
    "fail": "#b3261e", "fail-bg": "#f7dcd6", "warn": "#8a5e00", "warn-bg": "#fbecc2",
    "bubble": "#164f4b", "bubble-ink": "#ffffff", "code": "#f6f8f5",
    "alethic": "#6b3fa0", "deontic": "#1f5fa8",
}
DARK = {
    "bg": "#1b2b28", "card": "#0f1917", "line": "#2d4440", "ink": "#e6efec", "muted": "#9fb3ae",
    "primary": "#7bd4c6", "accent": "#ffb38b", "ok": "#6fd39a", "ok-bg": "#163b2b",
    "fail": "#ff8f85", "fail-bg": "#4a1f1b", "warn": "#f2c14e", "warn-bg": "#4a3a10",
    "bubble": "#123d39", "bubble-ink": "#e6efec", "code": "#142320",
    "alethic": "#c3a6ff", "deontic": "#8ab8ff",
}

# Paint classes shared by every figure: fill or stroke from one token.
PAINT = {
    **{f"f-{name}": f"fill:var(--gf-{name})" for name in LIGHT},
    **{f"s-{name}": f"stroke:var(--gf-{name})" for name in LIGHT},
    "sans": f"font-family:{SANS}",
    "mono": f"font-family:{MONO};white-space:pre",
    "nofill": "fill:none",
}

# Approximate advance widths (em) used to keep text inside its box.
_WIDTH_SANS = 0.56
_WIDTH_MONO = 0.61


def fmt(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in {"-0", ""} else text


def text_width(text: str, size: float, mono: bool = False) -> float:
    """A conservative width estimate for layout checks (not a font metric)."""
    per = _WIDTH_MONO if mono else _WIDTH_SANS
    wide = sum(1 for ch in text if ch.isupper() or ch in "mwMW@%&")
    return size * (per * len(text) + 0.12 * wide)


@dataclass
class Node:
    tag: str
    attrs: dict[str, object] = field(default_factory=dict)
    children: list[Node] = field(default_factory=list)
    text: str | None = None
    inline: bool = False

    def add(self, *nodes: Node) -> Node:
        self.children.extend(nodes)
        return self


def _attr(value: object) -> str:
    text = fmt(value) if isinstance(value, float) else str(value)
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(node: Node, indent: int = 0) -> str:
    pad = "  " * indent
    attrs = "".join(f' {key}="{_attr(value)}"' for key, value in sorted(node.attrs.items()))
    if node.text is not None and not node.children:
        return f"{pad}<{node.tag}{attrs}>{_escape(node.text)}</{node.tag}>"
    if not node.children:
        return f"{pad}<{node.tag}{attrs}/>"
    if node.inline:
        inner = "".join(render(child).strip() for child in node.children)
        return f"{pad}<{node.tag}{attrs}>{inner}</{node.tag}>"
    inner = "\n".join(render(child, indent + 1) for child in node.children)
    return f"{pad}<{node.tag}{attrs}>\n{inner}\n{pad}</{node.tag}>"


# ---------------------------------------------------------------- primitives

def g(*children: Node, **attrs: object) -> Node:
    return Node("g", _clean(attrs), list(children))


def rect(x: float, y: float, w: float, h: float, cls: str, rx: float = 0, **attrs: object) -> Node:
    base = {"x": float(x), "y": float(y), "width": float(w), "height": float(h), "class": cls}
    if rx:
        base["rx"] = float(rx)
    return Node("rect", {**base, **_clean(attrs)})


def line(x1: float, y1: float, x2: float, y2: float, cls: str, **attrs: object) -> Node:
    return Node("line", {"x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2),
                         "class": cls, **_clean(attrs)})


def circle(cx: float, cy: float, r: float, cls: str, **attrs: object) -> Node:
    return Node("circle", {"cx": float(cx), "cy": float(cy), "r": float(r), "class": cls, **_clean(attrs)})


def path(d: str, cls: str, **attrs: object) -> Node:
    return Node("path", {"d": d, "class": cls, **_clean(attrs)})


def text(x: float, y: float, content: str, cls: str, size: float, weight: int | None = None,
         anchor: str | None = None, **attrs: object) -> Node:
    base: dict[str, object] = {"x": float(x), "y": float(y), "class": cls, "font-size": float(size)}
    if weight:
        base["font-weight"] = weight
    if anchor:
        base["text-anchor"] = anchor
    if "mono" in cls.split():
        base["xml:space"] = "preserve"
    return Node("text", {**base, **_clean(attrs)}, text=content)


def spans(x: float, y: float, parts: list[tuple[str, str]], size: float, **attrs: object) -> Node:
    """One monospace line made of coloured runs: ``[(paint_class, text), ...]``."""
    node = Node("text", {"x": float(x), "y": float(y), "class": "mono", "font-size": float(size),
                         "xml:space": "preserve", **_clean(attrs)}, inline=True)
    node.children = [Node("tspan", {"class": cls}, text=content) for cls, content in parts]
    return node


def _clean(attrs: dict[str, object]) -> dict[str, object]:
    return {key.rstrip("_").replace("_", "-"): value for key, value in attrs.items()}


# ---------------------------------------------------------------- glyphs

def check_mark(cx: float, cy: float, cls: str = "s-ok") -> Node:
    return path(f"M{fmt(cx - 5)} {fmt(cy)}L{fmt(cx - 1.5)} {fmt(cy + 4)}L{fmt(cx + 5.5)} {fmt(cy - 4.5)}",
                f"{cls} nofill", stroke_width=2.4, stroke_linecap="round", stroke_linejoin="round")


def cross_mark(cx: float, cy: float, cls: str = "s-fail") -> Node:
    d = (f"M{fmt(cx - 4.5)} {fmt(cy - 4.5)}L{fmt(cx + 4.5)} {fmt(cy + 4.5)}"
         f"M{fmt(cx + 4.5)} {fmt(cy - 4.5)}L{fmt(cx - 4.5)} {fmt(cy + 4.5)}")
    return path(d, f"{cls} nofill", stroke_width=2.4, stroke_linecap="round")


def warn_mark(cx: float, cy: float) -> Node:
    tri = f"M{fmt(cx)} {fmt(cy - 6.5)}L{fmt(cx + 7)} {fmt(cy + 5.5)}L{fmt(cx - 7)} {fmt(cy + 5.5)}Z"
    bang = f"M{fmt(cx)} {fmt(cy - 2.5)}L{fmt(cx)} {fmt(cy + 1.5)}"
    return g(path(tri, "s-warn nofill", stroke_width=1.8, stroke_linejoin="round"),
             path(bang, "s-warn nofill", stroke_width=1.8, stroke_linecap="round"),
             circle(cx, cy + 3.8, 0.9, "f-warn"))


# ---------------------------------------------------------------- documents

def style_block(figure_id: str, extra: str = "") -> str:
    def tokens(values: dict[str, str]) -> str:
        return ";".join(f"--gf-{key}:{value}" for key, value in values.items())

    paint = "".join(f"#{figure_id} .{name}{{{rule}}}" for name, rule in PAINT.items())
    return (f":where(#{figure_id}){{{tokens(LIGHT)}}}"
            f"@media (prefers-color-scheme: dark){{:where(#{figure_id}){{{tokens(DARK)}}}}}"
            f"{paint}{extra}")


def document(figure_id: str, width: int, height: int, title: str, desc: str,
             body: list[Node], extra_css: str = "") -> str:
    root = Node("svg", {
        "xmlns": "http://www.w3.org/2000/svg", "viewBox": f"0 0 {width} {height}",
        "id": figure_id, "class": "gnd-figure", "role": "img",
        "aria-labelledby": f"{figure_id}-title {figure_id}-desc",
    })
    root.add(Node("title", {"id": f"{figure_id}-title"}, text=title),
             Node("desc", {"id": f"{figure_id}-desc"}, text=desc),
             Node("style", text=style_block(figure_id, extra_css)))
    root.add(*body)
    return render(root) + "\n"


_VAR = re.compile(r"var\(--gf-([a-z-]+)\)")


def bake(svg: str, palette: dict[str, str]) -> str:
    """Resolve colour tokens to literal values for rasterizers such as librsvg."""
    svg = re.sub(r":where\(#[a-z0-9-]+\)\{[^}]*\}", "", svg)
    svg = re.sub(r"@media \(prefers-color-scheme: dark\)\{\}", "", svg)
    return _VAR.sub(lambda match: palette[match.group(1)], svg)
