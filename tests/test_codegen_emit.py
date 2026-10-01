"""Derived tool docstrings and the emitted project tree.

Two claims are load-bearing here and both are asserted structurally rather than
by reading strings:

1. **`tools.py` is 100% derived** — signatures AND docstrings — so the file
   needs no in-file sentinel and G-04's file-level ownership survives contact.
   Docstrings come from the model's `reading`; the codegen skill does not
   author them.
2. **A hostile `reading` cannot become code.** The emitted module is parsed and
   its AST shape is asserted node-by-node, so "the docstring was escaped" is
   proven by the absence of injected statements rather than by a substring
   check that a cleverer payload would slip past.
"""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from gnd.codegen.docstrings import tool_docstring
from gnd.codegen.emit import (
    BANNER_LINE,
    DERIVED,
    GENERATED_BANNER,
    PROVIDER_AND_NETWORK_LIBS,
    EmitGateError,
    ProjectExistsError,
    SkillNameError,
    emit_project,
    render_skill_document,
    render_tools_module,
    scan_tree_for_provider_imports,
    write_project,
)
from gnd.codegen.identifiers import tool_symbol
from gnd.exp.frontmatter import read_frontmatter
from gnd.extract.vocabulary import reading_text
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parents[1]
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
KEYWORDS = REPO_ROOT / "tests" / "fixtures" / "models" / "keywords.orm.yaml"
DISPATCH = REPO_ROOT / "tests" / "fixtures" / "models" / "dispatch.orm.yaml"

#: The structural line count of `tool_docstring` over a ONE-ROLE fact type:
#: the reading line, a blank, the derived-from line, and one role line. The
#: fixtures below all declare exactly one role, so this is a number the TEST
#: controls — which is what makes "a hostile reading forged a line" detectable.
DOCSTRING_LINES_FOR_ONE_ROLE = 4


class _FakeModel:
    """The smallest thing `resolve_primitive` and the emitter accept."""

    def __init__(self, object_types: list[dict], fact_types: list[dict]) -> None:
        self.object_types = object_types
        self.fact_types = fact_types


def _model(reading: str, *, role_name: str = "a") -> _FakeModel:
    return _FakeModel(
        object_types=[
            {"id": "thing", "name": "Thing", "kind": "value", "primitive": "String"}
        ],
        fact_types=[
            {
                "id": "thing_is",
                "reading": reading,
                "roles": [{"object_type": "thing", "role_name": role_name}],
            }
        ],
    )


# --------------------------------------------------------------------------
# reading_text — the public extraction (G-03 clean: visibility, not behavior)
# --------------------------------------------------------------------------


def test_reading_text_instantiates_placeholders() -> None:
    assert reading_text("{Employee} has {EmployeeName}") == "Employee has EmployeeName"


def test_reading_text_renders_a_role_qualified_placeholder() -> None:
    assert reading_text("{Employee:manager}") == "Employee (manager)"
    assert reading_text("{A} has {B:r}") == "A has B (r)"


def test_reading_text_of_none_is_the_empty_string() -> None:
    """A fact type may omit its reading; a docstring builder must not explode."""
    assert reading_text(None) == ""


def test_reading_text_is_public_in_the_module_all() -> None:
    from gnd.extract import vocabulary

    assert "reading_text" in vocabulary.__all__


# --------------------------------------------------------------------------
# tool_docstring — derived from the model, neutralized at the emission site
# --------------------------------------------------------------------------


def test_tool_docstring_names_the_reading_and_every_role() -> None:
    model = _FakeModel(
        object_types=[
            {"id": "employee", "name": "Employee", "kind": "entity",
             "reference": {"mode": "popular", "value_type": "employee_id"}},
            {"id": "employee_id", "name": "EmployeeId", "kind": "value",
             "primitive": "Integer"},
            {"id": "employee_name", "name": "EmployeeName", "kind": "value",
             "primitive": "String"},
        ],
        fact_types=[
            {
                "id": "employee_has_name",
                "reading": "{Employee} has {EmployeeName}",
                "roles": [
                    {"object_type": "employee", "role_name": "employee"},
                    {"object_type": "employee_name", "role_name": "name"},
                ],
            }
        ],
    )
    text = tool_docstring(model, model.fact_types[0])

    assert "Employee has EmployeeName" in text
    assert "employee: Employee" in text
    assert "name: EmployeeName (String)" in text
    assert "employee_has_name" in text


def test_tool_docstring_falls_back_to_the_fact_type_id_when_the_reading_is_absent() -> (
    None
):
    model = _model(reading="")
    text = tool_docstring(model, model.fact_types[0])
    assert "thing_is" in text
    assert text.strip(), "an empty docstring would make the tool undocumented"


@pytest.mark.parametrize(
    "hostile",
    [
        "'''",
        '"""',
        "{Thing} '''\n\nimport os\nos.system('touch /tmp/pwned')\n'''",
        "\\'''",
        "\\\\'''",
        "'''+__import__('os').system('id')+'''",
        # Written as escapes on purpose: U+2028/U+2029 are LINE separators to
        # Python's own tokenizer and to str.splitlines(), so a literal pair
        # here would silently break this file apart rather than test anything.
        "{Thing} \r\n tail",
        "{Thing}\u2028\u2029\u0085next",
    ],
)
def test_a_hostile_reading_cannot_terminate_or_reshape_the_docstring(
    hostile: str,
) -> None:
    """Two properties, both asserted against values THIS fixture controls.

    1. No ``'''`` run survives — that is the delimiter the emitter uses, and
       ``_neutralize`` escaping every single quote is what makes it unreachable.
    2. The LINE COUNT is exactly the structural one for a one-role fact type.
       Asserting "no newline in the text" would be wrong (the docstring is
       deliberately multi-line); asserting the count catches a reading that
       forged an extra line, which is the actual attack.
    """
    model = _model(reading=hostile)
    text = tool_docstring(model, model.fact_types[0])

    assert len(text.splitlines()) == DOCSTRING_LINES_FOR_ONE_ROLE, (
        f"the hostile reading changed the docstring's line structure: "
        f"{text.splitlines()}"
    )
    for control in ("\r", "\x00", "\u2028", "\u0085"):
        assert control not in text, f"{control!r} survived into the docstring"
    assert "'''" not in text, "an unescaped ''' run survived neutralization"


def test_tool_docstring_routes_model_text_through_the_shipped_neutralizer() -> None:
    """Not "a neutralizer" — THE one `vocabulary.py:38` already imports."""
    from gnd.verbalize import _neutralize

    model = _model(reading="{Thing} it's fine")
    text = tool_docstring(model, model.fact_types[0])
    assert _neutralize("it's fine") in text


def test_the_docstring_module_imports_the_public_extraction_not_a_copy() -> None:
    """G-03: `reading_text` is reused, never re-implemented next door."""
    import inspect

    from gnd.codegen import docstrings

    source = inspect.getsource(docstrings)
    assert "reading_text" in source
    assert "re.compile" not in source, (
        "docstrings.py appears to re-derive the placeholder pattern instead of "
        "calling the public reading_text extraction"
    )


def test_a_hostile_reading_still_produces_a_module_that_parses() -> None:
    """The end-to-end claim, at the docstring layer: splice the produced text
    into a minimal module and parse it."""
    model = _model(reading="{Thing} ''' + __import__('os').system('id') + '''")
    text = tool_docstring(model, model.fact_types[0])
    module = f"def t():\n    '''{text}'''\n    return None\n"

    tree = ast.parse(module)
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    assert len(function.body) == 2, (
        "the hostile reading added statements to the function body — it escaped "
        "the docstring"
    )


# --------------------------------------------------------------------------
# The tree emitter
# --------------------------------------------------------------------------


def _emit(model_path: Path):
    model = load_model(str(model_path))
    return model, emit_project(model, str(model_path))


def _write(model_path: Path, out_root: Path):
    model = load_model(str(model_path))
    project = emit_project(
        model, str(model_path), skill_name=out_root.resolve().name
    )
    write_project(project, out_root)
    return model, project


def _python_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py"))


def _digests(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_emit_project_describes_the_tree_without_touching_the_filesystem(
    tmp_path: Path,
) -> None:
    """Plan 06's assertion #3 needs the expected surface WITHOUT a write."""
    target = tmp_path / "nothing_here"
    model = load_model(str(FULL_VOCABULARY))
    project = emit_project(model, str(FULL_VOCABULARY))

    assert project.relpaths, "the emitter described an empty project"
    assert not target.exists(), "emit_project wrote to disk"
    assert not any(tmp_path.iterdir()), "emit_project left files behind"


def test_every_emitted_python_file_parses_over_every_fixture_model(
    tmp_path: Path,
) -> None:
    """T-03-14: a model can never leave broken Python on a user's disk."""
    for index, model_path in enumerate((FULL_VOCABULARY, KEYWORDS, DISPATCH)):
        root = tmp_path / f"p{index}"
        _write(model_path, root)
        files = _python_files(root)
        assert files, f"{model_path.name} emitted no Python at all"
        for path in files:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_the_keyword_model_emits_valid_python_with_sanitized_symbols(
    tmp_path: Path,
) -> None:
    """G-21 end to end: `def import(from, return)` becomes valid Python."""
    root = tmp_path / "kw"
    model, _project = _write(KEYWORDS, root)

    tools = next(path for path in _python_files(root) if path.name == "tools.py")
    tree = ast.parse(tools.read_text(encoding="utf-8"))
    emitted = {
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    expected = {tool_symbol(str(ft["id"])) for ft in model.fact_types}

    assert expected, "the keywords fixture declares no fact types"
    assert emitted == expected, f"emitted {emitted}, expected {expected}"
    assert "import_" in emitted, "the hard-keyword fact type was not sanitized"

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for argument in node.args.args:
                assert argument.arg.isidentifier()


def test_two_emissions_are_byte_identical_with_a_model_derived_floor(
    tmp_path: Path,
) -> None:
    """Determinism, asserted over a NON-VACUOUS set.

    "Two emissions are byte-identical" is trivially true of an emitter that
    produced nothing, so the floor lives INSIDE the comparison: the compared
    set is non-empty and carries exactly one derived tool per fact type, with
    the expected count DERIVED FROM THE LOADED MODEL rather than written as a
    literal. (For `full_vocabulary.orm.yaml` that number is 16 today; a
    hardcoded 16 would silently pass if the fixture changed.)
    """
    first = tmp_path / "a" / "project"
    second = tmp_path / "b" / "project"
    model, _project = _write(FULL_VOCABULARY, first)
    _write(FULL_VOCABULARY, second)

    left, right = _digests(first), _digests(second)
    assert left, "the emitted set is empty — determinism over nothing"
    assert left == right, "two emissions of one model disagree"

    expected_tools = [tool_symbol(str(ft["id"])) for ft in model.fact_types]
    assert len(expected_tools) == len(set(expected_tools))
    assert expected_tools, "the model declares no fact types"

    tools = next(path for path in _python_files(first) if path.name == "tools.py")
    tree = ast.parse(tools.read_text(encoding="utf-8"))
    emitted = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]

    assert emitted == expected_tools, (
        f"the emitted tool set is not one-per-fact-type: {emitted} vs "
        f"{expected_tools}"
    )
    assert len(emitted) == len(model.fact_types)
    assert "tools.py" in " ".join(left), "tools.py is not in the compared set"


def test_the_emitted_tree_imports_no_provider_or_network_library(
    tmp_path: Path,
) -> None:
    root = tmp_path / "clean"
    _write(FULL_VOCABULARY, root)

    assert _python_files(root), "nothing to scan"
    assert scan_tree_for_provider_imports(root) == {}


def test_planting_import_anthropic_in_a_copy_reds_the_scan(tmp_path: Path) -> None:
    """G-09's mandatory red-making construction for the emitted-tree scan.

    The mutation lands in a COPY, so no restore step can leave a planted import
    behind, and it must be NAMED by the offender map — a scan that merely
    returns "not empty" would pass with its walk pointed at the wrong tree.
    """
    root = tmp_path / "clean"
    _write(FULL_VOCABULARY, root)
    assert scan_tree_for_provider_imports(root) == {}

    mutated = tmp_path / "mutated"
    shutil.copytree(root, mutated)
    target = next(path for path in _python_files(mutated) if path.name == "tools.py")
    target.write_text(
        "import anthropic\n" + target.read_text(encoding="utf-8"), encoding="utf-8"
    )

    offenders = scan_tree_for_provider_imports(mutated)
    relative = str(target.relative_to(mutated))
    assert relative in offenders, f"the scan did not name {relative}: {offenders}"
    assert offenders[relative] == ["anthropic"]
    assert scan_tree_for_provider_imports(root) == {}, "the original was mutated"


def test_the_provider_table_is_published_and_covers_the_known_clients() -> None:
    assert {"anthropic", "openai", "httpx", "requests"} <= PROVIDER_AND_NETWORK_LIBS


def test_the_generated_skill_frontmatter_round_trips(tmp_path: Path) -> None:
    root = tmp_path / "sk"
    _write(FULL_VOCABULARY, root)

    mapping, body = read_frontmatter(root / "SKILL.md")
    assert set(mapping) == {"name", "description"}
    assert mapping["name"] == root.name
    assert mapping["description"] and isinstance(mapping["description"], str)
    assert body.strip(), "the generated skill document has an empty body"


def test_the_generated_skill_explains_and_binds_its_model_argument(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    _write(FULL_VOCABULARY, root)
    text = (root / "SKILL.md").read_text(encoding="utf-8")

    assert ".gnd-codegen.json" in text
    assert "reference['path']" in text
    assert "reference['sha256']" in text
    assert "MODEL_PATH=" in text
    assert 'gnd verify "$MODEL_PATH" population.json --artifacts artifacts' in text
    assert "gnd verify MODEL population.json" not in text


def test_default_skill_name_normalises_dotted_model_stems(tmp_path: Path) -> None:
    model_path = tmp_path / "library.v2.orm.yaml"
    shutil.copyfile(FULL_VOCABULARY, model_path)
    model = load_model(str(model_path))

    project = emit_project(model, str(model_path))
    assert project.skill_name == "gnd-library-v2"


def test_default_skill_name_refuses_more_than_sixty_four_characters(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / ("a" * 61 + ".orm.yaml")
    shutil.copyfile(FULL_VOCABULARY, model_path)
    model = load_model(str(model_path))

    with pytest.raises(SkillNameError, match="at most 64"):
        emit_project(model, str(model_path))


def test_the_banner_is_a_compiled_regex_matching_line_one(tmp_path: Path) -> None:
    """The banner marks DERIVED Python, and the partition is pinned BOTH ways.

    Until the smoke module landed, every emitted ``.py`` happened to be derived,
    so globbing the tree and requiring a banner everywhere was accidentally
    right. It is not a statement about emitted Python -- it is a statement about
    ownership, and stamping DO NOT EDIT on a create-once file the user owns
    would be a lie. So derived files must carry it and extension files must not.
    """
    root = tmp_path / "bn"
    _model, project = _write(FULL_VOCABULARY, root)

    assert GENERATED_BANNER.pattern, "GENERATED_BANNER is not a compiled regex"
    derived = {file.relpath for file in project.files if file.ownership == DERIVED}
    extension = {file.relpath for file in project.extensions}
    scanned = 0
    for path in _python_files(root):
        relpath = path.relative_to(root).as_posix()
        first = path.read_text(encoding="utf-8").splitlines()[0]
        if relpath in derived:
            scanned += 1
            assert GENERATED_BANNER.match(first), f"{relpath} line 1 is {first!r}"
        elif relpath in extension:
            scanned += 1
            assert not GENERATED_BANNER.match(first), (
                f"{relpath} is an extension file and must not claim DO NOT EDIT"
            )
        else:
            raise AssertionError(f"{relpath} is emitted Python owned by nobody")
    assert scanned == len(_python_files(root)), "a Python file escaped the partition"
    assert any(r.endswith(".py") for r in extension), (
        "no extension Python file exists, so the negative half of this test "
        "cannot fail and the partition claim is vacuous"
    )

    assert not GENERATED_BANNER.match("# just a comment")
    assert not GENERATED_BANNER.match("x = 1  # Code generated by gnd codegen")
    assert GENERATED_BANNER.match(BANNER_LINE.format(source="m.orm.yaml"))


def test_the_emitter_calls_the_shipped_projection_rather_than_re_deriving_it(
    tmp_path: Path,
) -> None:
    """G-03, asserted on BYTES: the emitted projection artifact must equal what
    `gnd.extract.projection.project` returns for the same model."""
    from gnd.extract.projection import project

    root = tmp_path / "pj"
    model, _p = _write(FULL_VOCABULARY, root)

    emitted = next(root.rglob("*.projection.schema.json"))
    assert json.loads(emitted.read_text(encoding="utf-8")) == project(model)

    import inspect

    from gnd.codegen import emit

    source = inspect.getsource(emit)
    assert "from gnd.extract.projection import" in source or "projection.project" in source


def test_the_applicable_artifact_equals_the_shipped_derivation(tmp_path: Path) -> None:
    from gnd.extract.refscheme import applicable_set

    root = tmp_path / "ap"
    model, _p = _write(FULL_VOCABULARY, root)
    emitted = next(root.rglob("*.applicable.json"))
    assert json.loads(emitted.read_text(encoding="utf-8")) == applicable_set(model)


def test_the_verbalization_artifact_equals_the_shipped_derivation(
    tmp_path: Path,
) -> None:
    from gnd.extract.vocabulary import render_verbalization

    root = tmp_path / "vb"
    model, _p = _write(FULL_VOCABULARY, root)
    emitted = next(root.rglob("*.verbalization.txt"))
    assert emitted.read_text(encoding="utf-8") == render_verbalization(model)


def test_a_non_empty_target_is_refused_and_nothing_is_destroyed(
    tmp_path: Path,
) -> None:
    root = tmp_path / "occupied"
    root.mkdir()
    planted = root / "user-work.txt"
    planted.write_text("do not lose me", encoding="utf-8")

    model = load_model(str(FULL_VOCABULARY))
    project = emit_project(
        model, str(FULL_VOCABULARY), skill_name=root.resolve().name
    )
    with pytest.raises(ProjectExistsError):
        write_project(project, root)

    assert planted.read_text(encoding="utf-8") == "do not lose me"
    assert list(root.iterdir()) == [planted]


def test_every_file_is_classified_derived_or_extension(tmp_path: Path) -> None:
    """G-04: ownership is per FILE, and pyproject.toml is the create-once
    extension RESEARCH §3.3 candidate 3 flagged."""
    _model, project = _emit(FULL_VOCABULARY)
    kinds = {file.relpath: file.ownership for file in project.files}

    assert set(kinds.values()) <= {"derived", "extension"}
    assert kinds["pyproject.toml"] == "extension"
    assert any(
        relpath.endswith("tools.py") and kind == "derived"
        for relpath, kind in kinds.items()
    )
    assert kinds["SKILL.md"] == "derived", (
        "the discovery-critical artifact must be code-emitted (RESEARCH §3.3 "
        "candidate 2)"
    )
    assert project.derived and project.extensions


def test_render_tools_module_and_render_skill_document_are_published() -> None:
    model = load_model(str(KEYWORDS))
    tools = render_tools_module(model, model_path=str(KEYWORDS), package="keywords")
    ast.parse(tools)
    assert "def import_(" in tools

    skill = render_skill_document(
        model, model_path=str(KEYWORDS), package="keywords", stem="keywords"
    )
    assert skill.startswith("---\n")


def test_an_emitted_module_that_does_not_parse_is_an_internal_gate_breach() -> None:
    """The gate is in PRODUCTION code, not only in a test (the
    ProjectionGateError precedent). Proven by feeding the gate directly."""
    from gnd.codegen.emit import GeneratedFile, assert_emitted_python_parses

    assert_emitted_python_parses(
        (GeneratedFile(relpath="ok.py", text="x = 1\n", ownership="derived"),)
    )
    with pytest.raises(EmitGateError):
        assert_emitted_python_parses(
            (GeneratedFile(relpath="bad.py", text="def (:\n", ownership="derived"),)
        )


def test_the_emitted_tool_is_callable_and_keys_facts_by_raw_role_names(
    tmp_path: Path,
) -> None:
    """G-01's headline claim, exercised: the generated project is runnable with
    zero network and no API key.

    The returned mapping is keyed by the model's RAW role names (`from`,
    `return`) and NOT by the sanitized Python parameter names — JSON keys are
    unconstrained and the projection schema enumerates the raw names, so
    sanitizing them would emit a fact the shipped checker rejects.
    """
    import importlib.util

    root = tmp_path / "call"
    _write(KEYWORDS, root)
    tools_path = next(path for path in _python_files(root) if path.name == "tools.py")

    spec = importlib.util.spec_from_file_location("emitted_tools", tools_path)
    assert spec and spec.loader
    emitted = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(emitted)

    assert emitted.import_("c1", 1) == {"from": "c1", "return": 1}
    assert emitted.global_("c1", "label") == {"for": "c1", "in": "label"}


def test_emitted_docstrings_keep_their_line_structure(tmp_path: Path) -> None:
    """Regression guard: `verbalize.line_text` escapes newlines, so handing it a
    multi-line docstring collapses every one of them onto a single line with
    literal `\\n` sequences. Measured once in execution; pinned here."""
    root = tmp_path / "ds"
    _write(FULL_VOCABULARY, root)
    tools = next(path for path in _python_files(root) if path.name == "tools.py")
    source = tools.read_text(encoding="utf-8")

    assert "\\n" not in source, "an emitter newline was escaped into a literal \\n"
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    assert functions, "no emitted tools to inspect"
    for node in functions:
        doc = ast.get_docstring(node)
        assert doc and len(doc.splitlines()) >= 3, (
            f"{node.name}'s docstring collapsed to {doc!r}"
        )
