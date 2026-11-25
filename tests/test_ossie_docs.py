"""OB5: the Ossie pages, the export skill and the release note agree with the code.

The pages describe and link; the rules live in representation-format.md,
"Relational mapping (Rmap)" and "Ossie interchange". These tests fail when a page names a rule the normative
section lacks, when a flag is undocumented, when the release note's exit
numbers drift from gnd.exits, or when the packaged example binding stops
exporting. The pages' commands and shown output run in the tutorial runner
(tests/test_documentation_tutorials.py, group ``ossie``).
"""

from __future__ import annotations

import argparse
import json
import re
import typing
from pathlib import Path

import pytest

from gnd import cli, exits
from gnd.export import physical_binding
from gnd.export.ossie import render_ossie
from gnd.export.ossie_relational import validate_relational
from gnd.rmap import UnmappedReason
from tests.support import ossie_relational_corpus as relational
from tests.support.markdown_sections import markdown_section

ROOT = Path(__file__).resolve().parents[1]
NORMATIVE = ROOT / "src/gnd/skills/gnd-orm-core/references/representation-format.md"
SKILL = ROOT / "src/gnd/skills/gnd-export/SKILL.md"
CLI_REFERENCE = ROOT / "docs/reference/cli.md"
RELEASE_NOTES = ROOT / "docs/release-notes.md"
EXAMPLE = ROOT / "src/gnd/examples/refunds"
HOMES = ("## Relational mapping (Rmap)", "## Ossie interchange")
PAGES = (
    ROOT / "docs/explanation/ossie.md",
    ROOT / "docs/how-to/share-an-ossie-ontology.md",
    ROOT / "docs/how-to/describe-delivered-tables-for-ossie.md",
    SKILL,
)

#: A rule or refusal id is a flat token: a namespace, a colon, lower-case words joined by hyphens.
RULE_ID = re.compile(r"\b(?:binding|ossie):[a-z0-9]+(?:-[a-z0-9]+)*")
#: The reasons a mapping link is listed for (gnd.export.ossie_relational), beside UnmappedReason.
LINK_REASONS = ("identification-differs", "arity-over-limit")


def normative() -> str:
    """The two normative sections: the relational mapping's rules, and the Ossie files."""
    text = NORMATIVE.read_text(encoding="utf-8")
    return "".join(markdown_section(text, heading) for heading in HOMES)


def cited_ids(text: str) -> set[str]:
    return set(RULE_ID.findall(text))


def missing_from_normative(text: str) -> set[str]:
    return cited_ids(text) - cited_ids(normative())


def names_flag(text: str, flag: str) -> bool:
    """Whether TEXT names the option FLAG itself, not a longer option that contains it."""
    return re.search(rf"(?<![\w-]){re.escape(flag)}(?![\w-])", text) is not None


class _Captured(Exception):
    pass


def ossie_options(group: str, monkeypatch) -> set[str]:
    """The long options of `gnd GROUP ossie`, read from the parser itself."""
    captured: list[argparse.ArgumentParser] = []

    def capture(parser, _args=None, _namespace=None):
        captured.append(parser)
        raise _Captured

    with monkeypatch.context() as patch:
        patch.setattr(cli._BandSafeParser, "parse_args", capture)
        with pytest.raises(_Captured):
            cli.main([])
    parser = captured[0]
    for name in (group, "ossie"):
        (children,) = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
        parser = children.choices[name]
    return {flag for action in parser._actions for flag in action.option_strings
            if flag.startswith("--") and flag != "--help"}


# --- T4a: every cited id exists in the one home -------------------------------------------


@pytest.mark.parametrize("page", PAGES, ids=lambda path: path.name)
def test_every_rule_id_on_a_page_is_in_the_normative_section(page):
    assert page.is_file(), f"{page} is not written"
    assert not missing_from_normative(page.read_text(encoding="utf-8"))


def test_a_planted_unknown_rule_id_is_caught():
    assert missing_from_normative("A refusal such as `binding:no-such-rule` exits 3.") == {"binding:no-such-rule"}
    assert missing_from_normative("`ossie:output-size` and `binding:syntax`") == set()


def test_the_normative_section_names_every_rule_and_reason_in_the_code():
    section = normative()
    reasons = (*typing.get_args(UnmappedReason), *LINK_REASONS)
    assert not [rule for rule in physical_binding.RULE_ORDER if rule not in section]
    assert not [reason for reason in reasons if f"`{reason}`" not in section]


# --- T4b: every flag is documented ----------------------------------------------------------


@pytest.mark.parametrize("group", ["export", "import"])
def test_every_ossie_flag_is_in_the_skill_and_the_cli_reference(group, monkeypatch):
    options = ossie_options(group, monkeypatch)
    assert "--out" in options
    skill = markdown_section(SKILL.read_text(encoding="utf-8"), "## Ossie interchange")
    reference = CLI_REFERENCE.read_text(encoding="utf-8")
    for name, text in (("skill", skill), ("CLI reference", reference), ("normative section", normative())):
        assert not sorted(flag for flag in options if not names_flag(text, flag)), name


def test_a_flag_is_matched_as_a_whole_option():
    assert names_flag("run `gnd export ossie M --out FILE`", "--out")
    assert not names_flag("see `--output` and `--max-output-bytes`", "--out")
    assert not names_flag("see `--max-output-bytes`", "--output-bytes")


# --- T5: the release note names the exits by constant ---------------------------------------


def test_the_release_note_states_the_exits_by_their_constants():
    section = markdown_section(RELEASE_NOTES.read_text(encoding="utf-8"), "## Unreleased: Ossie relational files")
    assert section, "the release-note section is missing"
    for name in ("EXIT_COLLISION", "EXIT_USAGE"):
        assert f"{getattr(exits, name)} (`{name}`)" in section, name
    assert cited_ids(section) <= cited_ids(normative())


# --- T6: the packaged example binding is real -----------------------------------------------


def test_the_example_binding_exports_and_validates():
    binding = EXAMPLE / "physical-binding.json"
    bound = render_ossie(EXAMPLE / "model.orm.yaml", output_format="yaml", physical_binding=binding)
    plain = render_ossie(EXAMPLE / "model.orm.yaml", output_format="yaml")
    semantic = relational.load_yaml_bytes(bound.semantic_model)
    mapping = relational.load_yaml_bytes(bound.mapping)
    validate_relational(semantic, mapping)
    assert bound.document == plain.document and bound.sidecar == plain.sidecar
    assert [dataset["name"] for dataset in semantic["datasets"]] == ["crm.customers", "fin.refunds"]
    (extension,) = mapping["custom_extensions"]
    rows = {row["id"]: row["reason"] for row in json.loads(extension["data"])["dispositions"]}
    assert rows["refund_by"] is None and rows["refund_amount"] is None
    assert rows["refund_channel"] == "unbound"
