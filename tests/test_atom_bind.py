"""`atom_bind` is total over arbitrary JSON, and it is the only reader.

v5.1 Phase 1 §6.7 (O10, D-P1.4, standing rule 1). Twenty-eight raw
`atom.get("bind")` sites existed across four modules and only five checked the
shape at the site. Totality belongs to the function.

The measured correction to the spec's sketch is asserted here as a case rather
than argued in prose: the meta-schema types a bind term as a SCALAR --
string, number or boolean -- so a str-only reader would silently empty valid
models.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd.atoms import atom_bind, atom_has_bind

REPO_ROOT = Path(__file__).resolve().parents[1]
#: These three modules consume bindings from untrusted model/population input.
#: Their shared total reader is the v5.1 correction's actual behavioural scope.
#: Synth planners instead receive validated model dictionaries and their own
#: internally built population documents; widening this static policy to that
#: separate production surface would force an assurance recertification without
#: improving malformed-input handling.
BIND_CONSUMERS = ("model/__init__.py", "model/_validation.py", "model/_operations.py",
                  "checker/__init__.py", "checker/_reports.py", "checker/_core.py", "model_verbalization.py",
                  # IK2 split its semantic rules into this module; the induced-knowledge
                  # close registers it (it reads no bind).
                  "model/_induction.py",
                  # The evolve-loading follow-up's JSON-value walk (it reads no bind).
                  "model/_documents.py")

#: `patterns.py` keeps the 28th raw read. It imports NOTHING from `gnd` -- a
#: boundary two reviewers enforced against an earlier draft and
#: `test_patterns_imports_nothing_but_the_standard_library` makes literal --
#: so it cannot import the reader, and injecting one through `ground_atom`'s
#: seven call sites would buy nothing: every atom reaching it comes from
#: `transition.py` walking an already-loaded model, where the meta-schema has
#: already accepted `bind` as a mapping (IF-P1-9). The exemption is verified,
#: not asserted: the case below re-derives the reason.
STDLIB_ONLY_EXEMPTION = "patterns.py"


# --------------------------------------------------------------------------- #
# T1.9a -- total over hostile shapes
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "atom",
    [
        None,
        42,
        "not-an-atom",
        [],
        ["bind"],
        {},
        {"bind": None},
        {"bind": []},
        {"bind": "roles"},
        {"bind": 7},
        {"bind": True},
        {"no-bind-key": {"item": "$item"}},
    ],
    ids=str,
)
def test_a_hostile_shape_yields_an_empty_mapping_and_never_raises(atom) -> None:
    """Each of these reached a raw `.get("bind")` before this phase; three of
    them would have raised at a `.items()` or `.values()` call downstream."""
    result = atom_bind(atom)

    assert result == {}
    assert isinstance(result, dict)


def test_every_scalar_term_the_schema_allows_survives_the_reader() -> None:
    """The spec's sketch said a bind "with non-string values" yields an empty
    mapping. Measured against `$defs/term` -> `$defs/scalar`, typed
    ["string", "number", "boolean"], that would discard VALID models -- every
    role in such an atom would vanish from role-name validation, guarded
    matching and verbalization at once (IF-P1-6)."""
    schema = json.loads(
        (REPO_ROOT / "src" / "gnd" / "schema" / "orm-meta.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["$defs"]["scalar"]["type"] == ["string", "number", "boolean"]

    atom = {"bind": {"item": "$item", "quantity": 3, "ratio": 1.5, "urgent": True}}
    assert atom_bind(atom) == {
        "item": "$item",
        "quantity": 3,
        "ratio": 1.5,
        "urgent": True,
    }


def test_keys_are_coerced_to_strings() -> None:
    """A YAML document can present `1:` as an integer key; every caller
    compares role names as strings."""
    assert atom_bind({"bind": {1: "$one", "two": "$two"}}) == {
        "1": "$one",
        "two": "$two",
    }


def test_presence_is_asked_separately_from_emptiness() -> None:
    """`atom_has_bind` answers the structural question two validation
    predicates ask; an empty mapping is present-but-empty, which the schema's
    `minProperties: 1` makes a defect worth reporting rather than skipping."""
    assert atom_has_bind({"bind": {}}) is True
    assert atom_bind({"bind": {}}) == {}

    assert atom_has_bind({"bind": None}) is False
    assert atom_has_bind({}) is False
    assert atom_has_bind(None) is False


# --------------------------------------------------------------------------- #
# T1.9b -- one reader, no survivors
# --------------------------------------------------------------------------- #


def test_no_raw_bind_access_remains_in_the_ruled_scope() -> None:
    """Untrusted model/population consumers use the one total reader.

    The original repository-wide scan conflated these public-input consumers
    with synth's validated internal representations. That overbroad static
    claim would change production bytes and invalidate the separately owned
    assurance evidence without making an untrusted input safer. The falsifier
    is a raw read returning to one of the three actual input consumers.
    """
    scope = {REPO_ROOT / 'src/gnd' / name for name in BIND_CONSUMERS}
    actual = set((REPO_ROOT / 'src/gnd/model').rglob('*.py')) | set((REPO_ROOT / 'src/gnd/checker').rglob('*.py'))
    assert actual | {REPO_ROOT / 'src/gnd/model_verbalization.py'} == scope
    offenders = {}
    for name in BIND_CONSUMERS:
        path = REPO_ROOT / "src" / "gnd" / name
        text = path.read_text(encoding="utf-8")
        hits = [
            number
            for number, line in enumerate(text.splitlines(), start=1)
            if 'get("bind")' in line or '["bind"]' in line
        ]
        if hits:
            offenders[path.relative_to(REPO_ROOT).as_posix()] = hits

    assert not offenders, f"raw bind access survives: {offenders}"


def test_the_one_exemption_re_derives_its_own_reason() -> None:
    """An exemption asserted in a comment is a wish; this one is measured.

    `patterns.py` keeps a raw read ONLY because it imports nothing from `gnd`.
    If a later change gives it a `gnd` import, the reason evaporates and the
    site must be rerouted -- so this case fails at that moment rather than
    letting a stale exemption stand (IF-P1-9).
    """
    import ast

    source = (REPO_ROOT / "src" / "gnd" / STDLIB_ONLY_EXEMPTION).read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imported = {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert not {name for name in imported if name.startswith("gnd")}, (
        f"{STDLIB_ONLY_EXEMPTION} now imports from gnd, so its exemption from "
        f"the one-reader rule no longer holds: reroute its bind read"
    )
    assert 'atom.get("bind")' in source, (
        "the exemption is stale -- the raw read it exempts is gone"
    )


def test_every_consumer_reaches_the_binding_through_the_one_reader() -> None:
    """The complement of the scan above: the four modules that read bindings
    import the reader, so 'no raw access' cannot be satisfied by a module that
    stopped reading bindings altogether."""
    texts = {name: (REPO_ROOT / 'src/gnd' / name).read_text(encoding='utf-8') for name in BIND_CONSUMERS}
    active = {name for name, text in texts.items() if 'atom_bind(' in text}
    assert active == {'model/_validation.py', 'model/_operations.py', 'checker/_core.py', 'model_verbalization.py'}
    for name in active:
        assert "from gnd.atoms import" in texts[name], name
