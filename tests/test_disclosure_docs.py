"""NM4 T5: the disclosure docs keep one home per rule (why-not-near-misses NM4 spec).

The table on docs/reference/disclosure.md is pasted from disclosure_table(); a
change to gnd.disclosure.SURFACES fails test_page_table_equals_the_code until
the page is re-pasted from the printed table.
"""

from __future__ import annotations

import re
from pathlib import Path

from gnd.disclosure import SURFACES

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs/reference/disclosure.md"
START, END = "<!-- disclosure-table:start -->", "<!-- disclosure-table:end -->"
STATES = "| Mode | Declared sensitive roles"

CLASS = {
    ("site", "declared"): "declared roles: shown under `internal`, redacted under `customer`; `--unredacted` or `unredacted=True`, where taken, refused under `customer`",
    ("site", "view"): "every value: raw under `internal`, value-free under `customer`; `--raw` or `raw=True`, where taken, refused under `customer`",
    ("every-mode", None): "the same in every mode (see [outputs the same in every mode](#outputs-that-are-the-same-in-every-mode))",
    ("value-free", None): "emits no population values",
}
GROUP = {"gnd": "Command", "api": "`gnd.api`", "export.service": "`gnd.export.service`", "kind": "Output kind"}


def _name(key):
    if key.startswith("gnd "):
        return "gnd", f"`{key}`"
    prefix, _, rest = key.partition(":")
    return prefix, f"`{rest}`"


def disclosure_table() -> str:
    """The page's table, one row per (class, surface group), from SURFACES."""
    rows = {}
    for key, surface in SURFACES.items():
        if surface.note == "a library binding, not an output":
            continue
        prefix, label = _name(key)
        rows.setdefault((surface.kind, surface.convention), {}).setdefault(prefix, []).append(
            label + (" (starts processes)" if surface.spawns else ""))
    lines = ["| Surfaces | What they disclose |", "|---|---|"]
    for cls, text in CLASS.items():
        for prefix, group in GROUP.items():
            names = rows.get(cls, {}).get(prefix)
            if names:
                lines.append(f"| {group}: {', '.join(names)} | {text} |")
    return "\n".join(lines)


def table_on_page(text: str) -> str:
    return text.split(START, 1)[1].split(END, 1)[0].strip("\n")


def homes(needle: str, pages: dict[str, str] | None = None) -> set[str]:
    """The docs, packaged-skill and README files that contain needle."""
    if pages is None:
        files = [*ROOT.glob("docs/**/*.md"), *ROOT.glob("src/gnd/skills/**/*.md"), ROOT / "README.md"]
        pages = {str(path.relative_to(ROOT)): path.read_text(encoding="utf-8") for path in files}
    return {name for name, text in pages.items() if needle in text}


def test_page_table_equals_the_code():
    assert table_on_page(PAGE.read_text(encoding="utf-8")) == disclosure_table(), (
        "re-paste the table between the markers:\n" + disclosure_table())


def test_a_dropped_row_is_caught():
    text = PAGE.read_text(encoding="utf-8")
    row = next(line for line in table_on_page(text).splitlines() if line.startswith("| Command: `gnd check`"))
    assert table_on_page(text.replace(row + "\n", "")) != disclosure_table()


def test_normalization_has_one_home():
    assert homes("NFKC") == {"docs/reference/why-not.md"}


def test_mode_tables_have_one_home():
    assert homes(STATES) == {"docs/reference/disclosure.md"}
    assert homes(START) == {"docs/reference/disclosure.md"}


def test_a_restated_rule_is_caught():
    pages = {"docs/reference/why-not.md": "1. Unicode NFKC normalization;",
             "docs/reference/disclosure.md": f"{STATES} |\n{START}",
             "docs/reference/cli.md": "N is NFKC, then casefold."}
    assert homes("NFKC", pages) == {"docs/reference/why-not.md", "docs/reference/cli.md"}
    pages["docs/how-to/x.md"] = STATES
    assert homes(STATES, pages) != {"docs/reference/disclosure.md"}


def test_every_every_mode_command_is_named_on_the_page():
    text = PAGE.read_text(encoding="utf-8")
    section = text.split("## Outputs that are the same in every mode", 1)[1].split("\n## ", 1)[0]
    for key, surface in SURFACES.items():
        if surface.kind == "every-mode" and key.startswith("gnd "):
            assert re.search(rf"`{re.escape(key)}( [^`]*)?`", section), key
