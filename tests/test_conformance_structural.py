"""Assertion #3 — the ANTI-TAUTOLOGY gate (G-07, G-07″, G-09′, G-21).

Assertions #1 and #2 are exact, cheap, corroborating — and **self-referential**.
Integrity compares a derived file against a digest the generator wrote; currency
compares the model against a digest the generator wrote. Both are green on a
project that is 100% derived and 0% useful, because "regenerate and diff" passes
whenever codegen is deterministic, which it is by construction.

Assertion #3 reads the **model** and the **filesystem**. Nothing it compares was
written by the generator, which is why a generator emitting well-formed nothing
is caught here with one finding per model fact type and nowhere else.

Four shapes recur below, each of them a defect this project has already shipped
at least once:

* **The over-correction control runs first.** A freshly generated project must
  yield ZERO findings. Plan 05 measured the alternative directly: under a
  mutation that made ``check_integrity`` always fire, BOTH headline mutation
  tests still passed and only the control red. A gate that always fires looks
  exactly like a working gate.
* **Every assertion names the FACT TYPE**, never merely a count. RESEARCH's
  Common Pitfall 1 is a mutation that reds for the wrong reason, and
  ``len(findings) == 16`` cannot tell a correct detection from a crash.
* **The C0 trap is pinned separately** (task 2, below). A one-line fact-type
  rename makes the MODEL invalid, so ``load_model`` raises before conformance
  runs; the test then reds for the wrong reason while looking like proof.
* **The gate must agree with the emitter.** Both call
  :func:`gnd.codegen.identifiers.tool_symbol`. Two copies would disagree and #3
  would red on correct output — the worst failure available here, because it
  trains a reader to ignore the gate.

**Measured, not asserted: which test catches what.** Two mutations were run
against the shipped module during execution and the results are recorded here
because they are the only evidence that these tests are scoped rather than
merely numerous.

===========================================  ==========================  ==========================
mutation                                      what reds                   what stays green
===========================================  ==========================  ==========================
M-06-1: the ORPHAN direction removed          ONLY the consistent-rename  every other test in this
(``if not symbol.in_tool_module …`` →         pair test, on its           file, including the C0
``if True: continue``)                        ``orphan-tool-symbol``      trap and case B
                                              clause
M-06-2: the gate ALWAYS fires                 12 tests, first among       **case B** (16 findings)
(``if not candidates:`` → ``if True:``)       them the case-A control     **and the C0 trap** —
                                              on a fresh generation       both headline mutation
                                                                          tests pass a gate broken
                                                                          in the loudest way
===========================================  ==========================  ==========================

M-06-2 is the receipt this project asks for every time: a check that always
fires looks exactly like a working gate to the tests that exist to prove the gate
works. Only the control tells them apart, which is why it is the first test in
the file and why it carries non-vacuity floors on both ``expected`` and
``scanned`` — zero findings over zero expectations is not a passing gate either.

M-06-1 is the scoping receipt for G-09 mutation #3: the pair of findings is
carried by ONE test, and removing half the assertion reds that test alone rather
than the whole file.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gnd import cli, resolve_version
from gnd.cli import main
from gnd.codegen.emit import TOOLS_MODULE, GeneratedProject, emit_project, write_project
from gnd.codegen.identifiers import tool_symbol
from gnd.codegen.manifest import (
    build_manifest,
    manifest_path,
    read_manifest,
    render_manifest,
)
from gnd.conformance import Finding, FindingKind
from gnd.conformance.currency import check_currency, model_digest
from gnd.conformance.integrity import MAX_CONFORMANCE_BYTES, check_integrity
from gnd.conformance.report import (
    LIMITS,
    build_conformance_payload,
    load_conformance_schema,
)
from gnd.conformance.structural import (
    ExpectedTool,
    ObservedSymbol,
    SatisfiedBy,
    check_structural,
    derived_tool_relpath,
    expected_surface,
    observed_surface,
)
from gnd.model import ModelValidationError, load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "models"
FULL_VOCABULARY = FIXTURES / "full_vocabulary.orm.yaml"
KEYWORDS = FIXTURES / "keywords.orm.yaml"

#: RESEARCH §2.2 case B measured 16 findings over ``full_vocabulary`` — one per
#: declared fact type. Asserted against the MODEL rather than hard-coded, so a
#: fixture edit cannot leave this file quietly checking a smaller claim; the
#: literal is kept only as a floor that the fixture is still the large one.
FULL_VOCABULARY_FACT_TYPES = 16


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #


def _model_copy(tmp_path: Path, source: Path = FULL_VOCABULARY) -> Path:
    """A COPY of a fixture model, so a mutation can edit it on the filesystem."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    destination = tmp_path / "model.orm.yaml"
    shutil.copyfile(source, destination)
    return destination


def _generate(root: Path, model_path: Path) -> GeneratedProject:
    """A real generated project, written through the shipped emitter.

    Deliberately NOT through ``gnd codegen``: assertion #3 must be callable with
    no CLI in the picture (Phase 4's MODEL-02 calls it from a third entry
    point), and a fixture that reached for the CLI would make that untestable.
    """
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    write_project(
        project,
        str(root),
        manifest_text=render_manifest(build_manifest(project, str(model_path))),
    )
    return project


def _fact_type_ids(model_path: Path) -> list[str]:
    return [str(fact_type.get("id")) for fact_type in load_model(str(model_path)).fact_types]


def _tools_file(root: Path) -> Path:
    """The one emitted module that defines the derived tool namespace."""
    matches = sorted(root.rglob(TOOLS_MODULE))
    assert len(matches) == 1, f"expected exactly one {TOOLS_MODULE} under {root}: {matches}"
    return matches[0]


def _well_formed_nothing(root: Path) -> None:
    """A syntactically perfect tree that says nothing about any model.

    G-07's literal phrase, and RESEARCH §2.2 case B. This is what a generator
    that "ran successfully" and produced a shell looks like on disk.
    """
    root.mkdir(parents=True, exist_ok=True)
    (root / "main.py").write_text(
        "from __future__ import annotations\n\n\ndef main():\n    return None\n",
        encoding="utf-8",
    )


def _messages(findings: Sequence[Finding]) -> str:
    return "\n".join(f"[{finding.kind}] {finding.target}: {finding.message}" for finding in findings)


def _of_kind(findings: Sequence[Finding], kind: str) -> list[Finding]:
    return [finding for finding in findings if finding.kind == kind]


# --------------------------------------------------------------------------- #
# case A — the over-correction control (G-09's demand, and plan 05's receipt)
# --------------------------------------------------------------------------- #


def test_a_fresh_generation_reports_zero_structural_findings(tmp_path: Path) -> None:
    """RESEARCH §2.2 case A: PASS, 0 findings.

    This runs FIRST because every case below is worthless without it. A gate
    that fires unconditionally satisfies case B, case C and case D and fails
    only here — measured directly at plan 05 (M-05-4), where both G-09
    mutations passed a check broken in the loudest possible way.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    assert result.findings == (), (
        f"a freshly generated project reported structural drift:\n{_messages(result.findings)}"
    )
    # Non-vacuity, both directions: the control is only a control if the gate
    # actually looked at something. Zero findings over zero expectations is not
    # a passing gate, and neither is zero findings over an unread tree.
    assert len(result.expected) == FULL_VOCABULARY_FACT_TYPES, (
        f"the model contributed {len(result.expected)} expected tools; the "
        f"fixture is supposed to declare {FULL_VOCABULARY_FACT_TYPES}"
    )
    assert len(result.satisfied) == len(result.expected), (
        "some fact type was neither satisfied nor reported — the partition leaks"
    )
    assert result.scanned, "the control parsed no files, so it proves nothing"


def test_every_fact_type_is_satisfied_by_a_derived_file_on_a_fresh_generation(
    tmp_path: Path,
) -> None:
    """The satisfied-by partition, on the happy path: every fact type names the
    DERIVED file that satisfied it, and the ownership comes from the manifest."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    assert {entry.ownership for entry in result.satisfied} == {"derived"}
    assert {entry.relpath for entry in result.satisfied} == {
        _tools_file(root).relative_to(root).as_posix()
    }
    for entry in result.satisfied:
        assert entry.symbol == tool_symbol(entry.fact_type_id)


# --------------------------------------------------------------------------- #
# case B — well-formed nothing. THE reason assertion #3 exists.
# --------------------------------------------------------------------------- #


def test_a_tree_of_well_formed_nothing_reports_one_finding_per_model_fact_type(
    tmp_path: Path,
) -> None:
    """RESEARCH §2.2 case B: FAIL, 16 findings, each naming a fact type.

    A generator emitting a syntactically perfect module with no derived tools
    passes assertion #1 (nothing is recorded, so nothing mismatches) and
    assertion #2 (no model moved). It is caught only here.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _well_formed_nothing(root)

    result = check_structural(load_model(str(model_path)), root, None, model_path=model_path)

    unimplemented = _of_kind(result.findings, "fact-type-unimplemented")
    declared = _fact_type_ids(model_path)
    assert len(declared) == FULL_VOCABULARY_FACT_TYPES
    assert len(unimplemented) == len(declared), (
        f"expected one finding per fact type, got {len(unimplemented)}:\n"
        f"{_messages(result.findings)}"
    )
    # The claim is on the TEXT, not the count: a count cannot tell a correct
    # detection from an unrelated crash that produced sixteen of something.
    for fact_type_id in declared:
        assert any(
            fact_type_id in finding.message and finding.target == fact_type_id
            for finding in unimplemented
        ), f"no finding names the fact type {fact_type_id!r}:\n{_messages(unimplemented)}"
    assert result.satisfied == (), "nothing was emitted, so nothing can be satisfied"


def test_well_formed_nothing_survives_both_digest_assertions(tmp_path: Path) -> None:
    """The corroboration for the paragraph above, measured rather than asserted.

    If assertions #1 and #2 caught this shape, #3 would be decorative. They do
    not: a tree with no manifest entries has nothing to mismatch.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    # Gut the derived surface, then re-record the manifest over what remains, as
    # a generator that "succeeded" would have.
    _tools_file(root).write_text(
        "from __future__ import annotations\n\n\ndef main():\n    return None\n",
        encoding="utf-8",
    )
    regenerated = build_manifest(None, str(model_path), entries=[])
    (manifest_path(root)).write_text(render_manifest(regenerated), encoding="utf-8")
    hollow = read_manifest(manifest_path(root))

    assert check_integrity(root, hollow).findings == (), (
        "integrity found drift over an empty record; the point of this test is "
        "that it CANNOT, so #3 is not redundant"
    )
    assert check_currency(model_path, hollow) == (), (
        "currency found drift over an unmoved model; #3's independence is the claim"
    )
    structural = check_structural(load_model(str(model_path)), root, hollow, model_path=model_path)
    assert _of_kind(structural.findings, "fact-type-unimplemented"), (
        "the gutted surface passed all three assertions"
    )
    assert manifest.files, "the fixture never recorded anything to begin with"


# --------------------------------------------------------------------------- #
# case D — a generator that dropped exactly one fact type
# --------------------------------------------------------------------------- #


def test_a_generator_that_dropped_one_fact_type_reports_exactly_that_one(
    tmp_path: Path,
) -> None:
    """RESEARCH §2.2 case D: FAIL, 1 finding.

    The scoping claim: #3 reports the fact type that is missing and stays silent
    about the fifteen that are not, so a reader is sent to one place.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    dropped = "employee_leads_project"
    symbol = tool_symbol(dropped)
    tools = _tools_file(root)
    source = tools.read_text(encoding="utf-8")
    assert f"def {symbol}(" in source, "the fixture never emitted the tool being dropped"
    kept = re.sub(
        rf"\n\n\ndef {re.escape(symbol)}\(.*?(?=\n\n\ndef |\Z)", "", source, flags=re.DOTALL
    )
    assert f"def {symbol}(" not in kept, "the surgical drop did not remove the def"
    tools.write_text(kept, encoding="utf-8")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    assert [finding.target for finding in result.findings] == [dropped], (
        f"expected exactly the dropped fact type:\n{_messages(result.findings)}"
    )
    assert result.findings[0].kind == "fact-type-unimplemented"
    assert dropped in result.findings[0].message


# --------------------------------------------------------------------------- #
# case E — the keyword model. The gate agrees with the emitter or it is useless.
# --------------------------------------------------------------------------- #


def test_the_keywords_fixture_yields_zero_findings_on_correctly_sanitized_output(
    tmp_path: Path,
) -> None:
    """G-21, measured. RESEARCH's prototype reported 7 findings here because it
    re-derived ``fact_<id>`` itself; the shipped gate imports ``tool_symbol``,
    so it agrees with the emitter and reports NOTHING.

    That difference is the whole point of sharing the mapping. A gate that red
    on correct output would be worse than no gate — it trains a reader to skip
    the report.
    """
    model_path = _model_copy(tmp_path, KEYWORDS)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    assert result.findings == (), (
        f"the keyword model red on correctly sanitized output:\n{_messages(result.findings)}"
    )
    # The floor that makes the zero meaningful: the expected symbols really are
    # the SANITIZED ones, so this is not passing over an empty expectation.
    symbols = {tool.symbol for tool in result.expected}
    assert symbols == {"import_", "global_", "yield_"}, symbols
    parameters = {tool.fact_type_id: tool.parameters for tool in result.expected}
    assert parameters["import"] == ("from_", "return_"), parameters


def test_the_expected_surface_is_computed_through_the_published_symbol_mapping() -> None:
    """The structural claim behind case E, immune to the emitter agreeing by
    coincidence: every expected symbol IS ``tool_symbol(fact_type_id)``."""
    model = load_model(str(KEYWORDS))
    tools, findings = expected_surface(model)

    assert findings == ()
    assert tools
    for tool in tools:
        assert tool.symbol == tool_symbol(tool.fact_type_id), (
            f"{tool.fact_type_id!r} expected symbol {tool.symbol!r}, but the "
            f"published mapping says {tool_symbol(tool.fact_type_id)!r} — the "
            f"gate has grown a second copy of the sanitizer (G-21)"
        )


def test_the_structural_module_imports_the_published_mapping_rather_than_copying_it() -> None:
    """G-21 as a source fact. Two copies disagree eventually, and the failure
    lands on CORRECT output, where it is least likely to be believed."""
    source = Path(check_structural.__globals__["__file__"]).read_text(encoding="utf-8")
    assert "from gnd.codegen.identifiers import" in source, source[:400]
    assert "tool_symbol" in source
    assert "keyword.iskeyword" not in source, (
        "the module re-derives the keyword rule instead of composing "
        "gnd.codegen.identifiers, which is exactly the second copy G-21 forbids"
    )


# --------------------------------------------------------------------------- #
# module-level only (T-03-34) — a nested or dead def is not the public surface
# --------------------------------------------------------------------------- #


def test_a_def_nested_inside_a_function_does_not_satisfy_the_gate(tmp_path: Path) -> None:
    """``tree.body``, never ``ast.walk``. RESEARCH Common Pitfall 6."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _well_formed_nothing(root)
    declared = _fact_type_ids(model_path)
    hidden = declared[0]
    (root / "sneaky.py").write_text(
        "def outer():\n"
        f"    def {tool_symbol(hidden)}(employee, employee_name):\n"
        "        return {}\n"
        "    return None\n",
        encoding="utf-8",
    )

    result = check_structural(load_model(str(model_path)), root, None, model_path=model_path)

    assert any(finding.target == hidden for finding in result.findings), (
        f"a nested def satisfied the gate:\n{_messages(result.findings)}"
    )
    assert hidden not in {entry.fact_type_id for entry in result.satisfied}


def test_a_def_inside_a_dead_if_false_block_does_not_satisfy_the_gate(
    tmp_path: Path,
) -> None:
    """The other half of the same rule, and the one ``ast.walk`` makes invisible:
    unreachable code is not a public surface."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _well_formed_nothing(root)
    declared = _fact_type_ids(model_path)
    hidden = declared[1]
    (root / "dead.py").write_text(
        "if False:\n"
        f"    def {tool_symbol(hidden)}(employee, gender):\n"
        "        return {}\n",
        encoding="utf-8",
    )

    result = check_structural(load_model(str(model_path)), root, None, model_path=model_path)

    assert any(finding.target == hidden for finding in result.findings)
    assert hidden not in {entry.fact_type_id for entry in result.satisfied}


def test_the_module_walks_tree_body_and_never_calls_ast_walk() -> None:
    """The source-level form of the two tests above, because both of them would
    keep passing if the walk were widened and the fixtures happened to miss it."""
    source = Path(check_structural.__globals__["__file__"]).read_text(encoding="utf-8")
    assert "tree.body" in source
    assert "ast.walk(" not in source, (
        "ast.walk lets a def inside a dead branch satisfy the assertion (T-03-34)"
    )


# --------------------------------------------------------------------------- #
# G-08's partition, applied to assertion #3
# --------------------------------------------------------------------------- #


def test_a_fact_type_satisfied_only_by_an_extension_file_is_reported_with_that_file(
    tmp_path: Path,
) -> None:
    """Whole-tree discovery means a HAND-WRITTEN file can satisfy #3. That is not
    forbidden — it is REPORTED, with the satisfying file and its ownership from
    the plan-04 manifest. A silent pass here would be G-08's failure inside the
    one assertion that was supposed to be the honest one."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    moved = "employee_is_active"
    symbol = tool_symbol(moved)
    tools = _tools_file(root)
    source = tools.read_text(encoding="utf-8")
    block = re.search(
        rf"\n\n\ndef {re.escape(symbol)}\(.*?(?=\n\n\ndef |\Z)", source, flags=re.DOTALL
    )
    assert block is not None, "the fixture never emitted the tool being moved"
    tools.write_text(source.replace(block.group(0), ""), encoding="utf-8")

    # `references/` is an EXTENSION path in the shipped layout, so a .py placed
    # beside the notes is unmanaged; the manifest's own extension entry is what
    # the ownership below is read from.
    extension = root / "references" / "handwritten.py"
    extension.parent.mkdir(parents=True, exist_ok=True)
    extension.write_text(block.group(0).lstrip("\n") + "\n", encoding="utf-8")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    satisfied = {entry.fact_type_id: entry for entry in result.satisfied}
    assert moved in satisfied, "the extension file did not satisfy the fact type at all"
    entry = satisfied[moved]
    assert entry.relpath == "references/handwritten.py"
    assert entry.ownership == "unmanaged", entry
    reported = _of_kind(result.findings, "fact-type-satisfied-by-non-derived")
    assert [finding.target for finding in reported] == [moved], (
        f"a fact type satisfied only outside the derived surface passed silently:\n"
        f"{_messages(result.findings)}"
    )
    assert "references/handwritten.py" in reported[0].message
    assert "unmanaged" in reported[0].message


def test_a_fact_type_satisfied_by_both_derived_and_extension_code_prefers_the_derived_one(
    tmp_path: Path,
) -> None:
    """The complement of the test above, and the reason it says "only".

    A duplicate helper in an extension file is not drift; reporting it as such
    would make the gate fire on a project that is entirely correct.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    duplicated = "employee_is_active"
    symbol = tool_symbol(duplicated)
    extension = root / "references" / "handwritten.py"
    extension.parent.mkdir(parents=True, exist_ok=True)
    extension.write_text(f"def {symbol}(employee):\n    return {{}}\n", encoding="utf-8")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    assert result.findings == (), _messages(result.findings)
    satisfied = {entry.fact_type_id: entry for entry in result.satisfied}
    assert satisfied[duplicated].ownership == "derived"


def test_discovery_scans_the_whole_tree_and_not_the_manifests_file_list(
    tmp_path: Path,
) -> None:
    """RESEARCH §2.4. If #3 inspected only manifest-listed files, a generator
    could hide a missing tool by omitting the file from the manifest — the
    tautology in a different costume.

    The two halves are asserted apart, because they are different claims:
    **discovery** is manifest-independent (an omitted file is still read), while
    **classification** is manifest-dependent by design (an omitted file has no
    recorded owner, so it reports ``unmanaged``). Blending them would let a
    future edit make discovery manifest-dependent and still pass here.
    """
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    tools_relpath = _tools_file(root).relative_to(root).as_posix()
    hollow = manifest.model_copy(
        update={"files": [e for e in manifest.files if e.relpath != tools_relpath]}
    )
    assert tools_relpath not in hollow.entries()

    # Discovery: the file is still on disk and still correct, so every fact type
    # is still COVERED even though the manifest no longer mentions the file.
    omitted = check_structural(load_model(str(model_path)), root, hollow, model_path=model_path)
    assert _of_kind(omitted.findings, "fact-type-unimplemented") == [], _messages(
        omitted.findings
    )
    assert len(omitted.satisfied) == len(_fact_type_ids(model_path))

    # Classification: and the report says, per fact type, that the file which
    # satisfied it is one GND has no record of placing. The omission is
    # published, not absorbed.
    assert {entry.ownership for entry in omitted.satisfied} == {"unmanaged"}
    assert len(_of_kind(omitted.findings, "fact-type-satisfied-by-non-derived")) == len(
        omitted.satisfied
    )

    # ...and deleting the file is caught even though the manifest never named it.
    _tools_file(root).unlink()
    hidden = check_structural(load_model(str(model_path)), root, hollow, model_path=model_path)
    assert len(_of_kind(hidden.findings, "fact-type-unimplemented")) == len(
        _fact_type_ids(model_path)
    ), _messages(hidden.findings)


# --------------------------------------------------------------------------- #
# hostile / malformed input (T-03-35): a finding, never a crash
# --------------------------------------------------------------------------- #


def test_an_unparseable_file_yields_a_finding_rather_than_an_exception(
    tmp_path: Path,
) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    (root / "broken.py").write_text("def (:\n", encoding="utf-8")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    parse = _of_kind(result.findings, "unparseable-source")
    assert [finding.target for finding in parse] == ["broken.py"], _messages(result.findings)
    assert "SyntaxError" in parse[0].message
    # The rest of the tree was still read: one broken file must not deny the
    # answer for the other eight.
    assert not _of_kind(result.findings, "fact-type-unimplemented")


def test_an_oversized_python_file_is_reported_from_its_stat_and_never_parsed(
    tmp_path: Path,
) -> None:
    """T-03-35, the plan-04 byte cap carried forward. The assertion is that the
    file was never READ, not merely that a finding was produced."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    huge = root / "huge.py"
    huge.write_bytes(b"# " + b"x" * MAX_CONFORMANCE_BYTES + b"\n")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    oversized = _of_kind(result.findings, "unparseable-source")
    assert [finding.target for finding in oversized] == ["huge.py"], _messages(result.findings)
    assert str(MAX_CONFORMANCE_BYTES) in oversized[0].message
    assert "huge.py" not in result.scanned, "the oversized file was parsed after all"


def test_the_gate_never_imports_the_tree_under_inspection() -> None:
    """T-03-30. Importing a generated module to inspect it executes arbitrary
    user code on every CI run; ``ast.parse`` is the whole mechanism."""
    source = Path(check_structural.__globals__["__file__"]).read_text(encoding="utf-8")
    for vector in ("importlib.import_module", "exec(", "eval(", "runpy", "__import__"):
        assert vector not in source, f"{vector} is reachable from the structural gate"


def test_a_symlinked_python_file_is_reported_and_never_followed(tmp_path: Path) -> None:
    """A link planted at a ``.py`` path is not the file GND wrote, and following
    it would read bytes from outside the tree (the ``classify_file`` rule)."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    outside = tmp_path / "outside.py"
    outside.write_text("def anything():\n    return None\n", encoding="utf-8")
    (root / "linked.py").symlink_to(outside)

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    assert "linked.py" not in result.scanned
    assert not _of_kind(result.findings, "fact-type-unimplemented")


# --------------------------------------------------------------------------- #
# signature agreement
# --------------------------------------------------------------------------- #


def test_a_tool_whose_parameters_disagree_with_the_role_names_is_reported(
    tmp_path: Path,
) -> None:
    """A symbol with the right name and the wrong signature is drift the name
    check alone cannot see — RESEARCH's ARITY finding."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))

    target = "employee_has_name"
    symbol = tool_symbol(target)
    tools = _tools_file(root)
    source = tools.read_text(encoding="utf-8")
    mangled = re.sub(
        rf"def {re.escape(symbol)}\([^)]*\):", f"def {symbol}(wrong):", source, count=1
    )
    assert mangled != source, "the fixture's signature rewrite matched nothing"
    tools.write_text(mangled, encoding="utf-8")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    mismatch = _of_kind(result.findings, "tool-signature-mismatch")
    assert [finding.target for finding in mismatch] == [target], _messages(result.findings)
    assert "wrong" in mismatch[0].message and "employee" in mismatch[0].message


def test_the_last_module_level_definition_is_the_effective_binding(tmp_path: Path) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = "employee_has_name"
    symbol = tool_symbol(target)
    tools = _tools_file(root)
    with tools.open("a", encoding="utf-8") as handle:
        handle.write(f"\n\ndef {symbol}(wrong):\n    return {{}}\n")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    mismatch = _of_kind(result.findings, "tool-signature-mismatch")
    assert [finding.target for finding in mismatch] == [target]
    assert "wrong" in mismatch[0].message


@pytest.mark.parametrize(
    "replacement",
    [
        "async def {symbol}(employee, name):",
        "def {symbol}(*args):",
        "def {symbol}(employee, name, **kwargs):",
        "def {symbol}(employee, name='default'):",
        "@staticmethod\ndef {symbol}(employee, name):",
    ],
    ids=["async", "varargs", "kwargs", "default", "decorator"],
)
def test_non_emitter_callable_shapes_are_signature_mismatches(
    tmp_path: Path, replacement: str
) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    target = "employee_has_name"
    symbol = tool_symbol(target)
    tools = _tools_file(root)
    source = tools.read_text(encoding="utf-8")
    mangled = re.sub(
        rf"def {re.escape(symbol)}\([^)]*\):",
        replacement.format(symbol=symbol),
        source,
        count=1,
    )
    tools.write_text(mangled, encoding="utf-8")

    result = check_structural(load_model(str(model_path)), root, manifest, model_path=model_path)

    mismatch = _of_kind(result.findings, "tool-signature-mismatch")
    assert [finding.target for finding in mismatch] == [target]


def test_observed_surface_reports_module_level_defs_with_their_file_and_line(
    tmp_path: Path,
) -> None:
    """The stage-2 contract, asserted directly so the stage-3 tests above are
    not the only thing standing between a broken walk and a green suite."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)

    symbols, findings = observed_surface(
        root, tool_relpath=derived_tool_relpath(model_path)
    )

    assert findings == ()
    assert symbols
    tools_relpath = _tools_file(root).relative_to(root).as_posix()
    by_name = {symbol.symbol: symbol for symbol in symbols}
    entry = by_name[tool_symbol("employee_has_name")]
    assert isinstance(entry, ObservedSymbol)
    assert entry.relpath == tools_relpath
    assert entry.lineno > 0
    assert entry.in_tool_module is True
    # The parameters really are the model's role names in DECLARED order, taken
    # from the model here rather than transcribed — a transcription would pass
    # over a walk that read `args` alone and dropped keyword-only parameters.
    expected = next(
        tool for tool in expected_surface(load_model(str(model_path)))[0]
        if tool.fact_type_id == "employee_has_name"
    )
    assert entry.parameters == expected.parameters == ("employee", "name")


def test_an_unrelated_extension_tools_module_does_not_claim_the_derived_namespace(
    tmp_path: Path,
) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    extension = root / "extension" / "tools.py"
    extension.parent.mkdir(parents=True)
    extension.write_text("def helper():\n    return None\n", encoding="utf-8")

    result = check_structural(
        load_model(str(model_path)), root, manifest, model_path=model_path
    )

    assert not _of_kind(result.findings, "orphan-tool-symbol")


# --------------------------------------------------------------------------- #
# the payload and the CLI
# --------------------------------------------------------------------------- #


def _validator() -> Draft202012Validator:
    return Draft202012Validator(load_conformance_schema())


def _json_run(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, dict]:
    capsys.readouterr()
    code = main([*argv, "--format", "json"])
    return code, json.loads(capsys.readouterr().out)


def test_the_structural_assertion_is_published_in_the_payload_and_reports_that_it_ran(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)

    assert code == 0
    _validator().validate(payload)
    assertions = {entry["id"]: entry for entry in payload["assertions"]}
    assert {"integrity", "currency", "structural"} <= set(assertions)
    assert assertions["structural"]["ran"] is True
    assert assertions["structural"]["findings"] == 0
    assert payload["model"]["fact_types"] == FULL_VOCABULARY_FACT_TYPES
    assert len(payload["satisfied"]) == FULL_VOCABULARY_FACT_TYPES


def test_the_cli_exits_thirteen_over_a_gutted_surface_and_names_every_fact_type(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    _tools_file(root).write_text(
        "from __future__ import annotations\n\n\ndef main():\n    return None\n",
        encoding="utf-8",
    )

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)

    assert code == cli.EXIT_MODEL_CODE_DRIFT
    _validator().validate(payload)
    named = {
        finding["target"]
        for finding in payload["findings"]
        if finding["kind"] == "fact-type-unimplemented"
    }
    assert named == set(_fact_type_ids(model_path)), named


def test_the_satisfied_partition_adds_up_from_the_payload_alone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``len(satisfied) + #unimplemented == model.fact_types`` — the audit trail
    a reader checks by counting the printed arrays, so a fact type cannot vanish
    from the report by appearing in neither."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    tools = _tools_file(root)
    symbol = tool_symbol("employee_leads_project")
    source = tools.read_text(encoding="utf-8")
    tools.write_text(
        re.sub(
            rf"\n\n\ndef {re.escape(symbol)}\(.*?(?=\n\n\ndef |\Z)", "", source, flags=re.DOTALL
        ),
        encoding="utf-8",
    )

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)

    assert code == cli.EXIT_MODEL_CODE_DRIFT
    _validator().validate(payload)
    unimplemented = [
        finding for finding in payload["findings"] if finding["kind"] == "fact-type-unimplemented"
    ]
    assert len(payload["satisfied"]) + len(unimplemented) == payload["model"]["fact_types"]


def test_a_model_that_will_not_load_reports_the_structural_assertion_as_not_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """R-13′: a check that could not run is never a check that passed. Band 3,
    not 13 — the obligations could not be EVALUATED."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    model_path.write_text("version: 1\nnot: a model\n", encoding="utf-8")

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)

    assert code == 3
    _validator().validate(payload)
    assertions = {entry["id"]: entry for entry in payload["assertions"]}
    assert assertions["structural"]["ran"] is False
    assert assertions["structural"]["findings"] == 0
    assert payload["error"]
    assert payload["satisfied"] == []
    assert payload["model"]["fact_types"] is None


def test_the_deferred_structural_limit_is_gone_now_that_the_assertion_ships() -> None:
    """Plan 05 emitted ``structural-conformance-deferred`` as a NON-required
    limit precisely so this plan could remove it. A published limit that no
    longer holds is a false statement about the check's own scope."""
    ids = {limit["id"] for limit in LIMITS}
    assert "structural-conformance-deferred" not in ids, ids
    assert {"manifest-co-edit", "extension-unexamined", "green-is-not-correctness"} <= ids
    assert "structural-surface-only" in ids, (
        "assertion #3 binds NAMES and SIGNATURES, never bodies; that bound has "
        "to be published in the same field the closed one was"
    )


def test_no_published_limit_carries_an_apostrophe_the_renderer_would_escape() -> None:
    """A regression guard for a defect that has now happened TWICE.

    ``render_conformance`` neutralizes every value through
    ``verbalize.path_segment``, which escapes apostrophes. That is the right
    uniform default for untrusted strings and pure noise over GND's own
    constants, where it prints ``the model\\'s fact types`` — and a published
    limitation that looks like a rendering bug is one a reader discounts. Plan 05
    hit it on ``structural-conformance-deferred`` and reworded; plan 06 hit it
    again on ``structural-surface-only`` the first time the end-to-end command
    was run. The second occurrence is what makes it a test rather than a habit.

    The repair is always the wording, never a trusted/untrusted branch in the
    renderer: a renderer with two branches is one refactor away from applying the
    wrong one to a hostile string.
    """
    from gnd import verbalize

    # Self-check: the escaping this guard exists for must actually happen, or
    # the guard is protecting against nothing.
    assert "\\'" in verbalize.path_segment("the model's fact types")

    assert LIMITS, "no limits are published, so this guard inspects nothing"
    for limit in LIMITS:
        assert "'" not in limit["description"], (
            f"limit {limit['id']!r} carries an apostrophe; it will render as "
            f"\\' and read as a rendering bug"
        )


def test_a_drifted_report_renders_with_no_escaped_apostrophe_anywhere(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The behavioural half of the guard above, over the assertion-#3 findings
    rather than only over the limits.

    The first draft of every structural message used ``{fact_type_id!r}``, which
    the renderer turned into ``\\'employee_has_name\\'`` sixteen times. The repair
    was to drop the ``repr`` — the shipped integrity messages never used one
    either — rather than to teach the renderer about trusted strings.

    Scoped to the drift and satisfaction findings deliberately. The
    ``identifier-hazard`` message quotes an ``IdentifierError`` verbatim, and
    that refusal repr-quotes its ids ON PURPOSE (the interesting collision is
    ``import`` against ``import_``, and unquoted the first is a substring of the
    second). Rewording another module's refusal to flatter this renderer would
    trade a real disambiguation for a cosmetic one.
    """
    from gnd import verbalize

    assert "\\'" in verbalize.path_segment("the model's fact types")

    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    _tools_file(root).write_text(
        "from __future__ import annotations\n\n\ndef main():\n    return None\n",
        encoding="utf-8",
    )

    capsys.readouterr()
    assert main(["conformance", str(model_path), str(root)]) == cli.EXIT_MODEL_CODE_DRIFT
    printed = capsys.readouterr().out

    assert "fact-type-unimplemented" in printed, "the fixture printed no structural finding"
    assert "\\'" not in printed, (
        "the report escapes an apostrophe; a published finding that looks like a "
        "rendering bug is one a reader discounts"
    )


def test_the_schema_version_was_not_bumped_by_this_widening() -> None:
    """The stated disposition (plan 05's ``#:`` history, extended here): the key
    set was introduced two plans ago inside this same unreleased phase and has
    never shipped, so there is no consumer pinned to the narrower shape. The
    bump rule exists for a breaking change to a PUBLISHED key set."""
    from gnd.conformance.report import CONFORMANCE_SCHEMA_VERSION

    assert CONFORMANCE_SCHEMA_VERSION == 1
    assert load_conformance_schema()["properties"]["schema_version"]["minimum"] == 1


def test_the_satisfied_partition_is_schema_required_and_load_bearing(
    tmp_path: Path,
) -> None:
    """MUTATION over a COPY of the schema, in plan 05's idiom: strip ``satisfied``
    from ``required`` and a payload lacking the key becomes valid — so this pins
    the SCHEMA rather than restating the builder."""
    model_path = _model_copy(tmp_path)
    root = tmp_path / "project"
    _generate(root, model_path)
    manifest = read_manifest(manifest_path(root))
    payload = build_conformance_payload(
        model_path,
        manifest,
        check_integrity(root, manifest),
        check_currency(model_path, manifest),
        structural=check_structural(load_model(str(model_path)), root, manifest, model_path=model_path),
        actual_model_sha256=model_digest(model_path),
        gnd_version=resolve_version(),
    )
    schema = load_conformance_schema()
    assert Draft202012Validator(schema).is_valid(payload)

    stripped = copy.deepcopy(payload)
    del stripped["satisfied"]
    assert not Draft202012Validator(schema).is_valid(stripped)

    relaxed = copy.deepcopy(schema)
    relaxed["required"] = [key for key in relaxed["required"] if key != "satisfied"]
    assert Draft202012Validator(relaxed).is_valid(stripped), (
        "the key-less payload is invalid for some OTHER reason too, so the "
        "assertion above did not prove `required` is what rejected it"
    )


def test_structural_is_a_standalone_callable_with_no_cli_in_the_process() -> None:
    """Phase 4's MODEL-02 calls this from a third entry point. A check only the
    CLI can perform is a check no other entry point can reuse."""
    probe = (
        "import sys\n"
        "from gnd.conformance.structural import check_structural\n"
        "print('gnd.cli' in sys.modules)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False", result.stdout


def test_every_structural_finding_kind_is_emitted_by_the_structural_module() -> None:
    """The reachability guard, extended: an unreachable member reads as coverage
    that does not exist."""
    from gnd.conformance import structural as structural_module

    source = Path(structural_module.__file__).read_text(encoding="utf-8")
    structural_kinds = [
        kind
        for kind in FindingKind.__args__  # type: ignore[attr-defined]
        if kind
        in {
            "fact-type-unimplemented",
            "tool-signature-mismatch",
            "orphan-tool-symbol",
            "fact-type-satisfied-by-non-derived",
            "identifier-hazard",
            "unparseable-source",
        }
    ]
    assert len(structural_kinds) == 6, structural_kinds
    for kind in structural_kinds:
        assert f'"{kind}"' in source, kind


def test_an_expected_tool_and_a_satisfied_by_record_are_frozen() -> None:
    tool = ExpectedTool(fact_type_id="a", symbol="a", parameters=("b",))
    satisfied = SatisfiedBy(fact_type_id="a", symbol="a", relpath="p.py", ownership="derived")
    for record in (tool, satisfied):
        with pytest.raises(dataclasses.FrozenInstanceError):
            record.fact_type_id = "elsewhere"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# task 2 — G-09 mutation #3, and the C0 trap that makes a careless version look
# like proof
# --------------------------------------------------------------------------- #

#: The fact type renamed by mutation #3, and every site in the fixture that
#: names it. Written out rather than discovered so the NAIVE variant below is a
#: genuine one-line edit and the CONSISTENT one is genuinely consistent.
RENAME_FROM = "employee_heads_department"
RENAME_TO = "employee_directs_department"


def _renamed_model(tmp_path: Path, *, consistent: bool) -> Path:
    """The mutated model. ``consistent`` renames EVERY site; otherwise only the
    ``id:`` declaration, which is RESEARCH §2.2's case C0."""
    model_path = _model_copy(tmp_path)
    text = model_path.read_text(encoding="utf-8")
    assert text.count(RENAME_FROM) == 3, (
        f"the fixture names {RENAME_FROM!r} {text.count(RENAME_FROM)} times; the "
        f"naive/consistent distinction this test rests on has moved"
    )
    if consistent:
        text = text.replace(RENAME_FROM, RENAME_TO)
    else:
        text = text.replace(f"id: {RENAME_FROM}", f"id: {RENAME_TO}", 1)
    model_path.write_text(text, encoding="utf-8")
    return model_path


def test_the_naive_one_line_rename_is_refused_at_model_load_and_is_not_a_gate_catch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """**The C0 trap, pinned so it cannot be mistaken for proof later (G-09′).**

    Renaming only the ``id:`` line leaves two constraints referencing the old
    name, so the MODEL is invalid and ``load_model`` raises before conformance
    runs. A mutation test written this way goes red — and a reviewer reading the
    red would credit the structural gate with a catch it did not make, because
    the gate under test never executed at all.

    "A mutation that reds via an unrelated exception is not a mutation check."
    The distinguishing evidence is here in two forms: the exception type at the
    library level, and band **3** rather than band 13 at the CLI — the
    obligations could not be EVALUATED, so no fact about the project was
    established in either direction.
    """
    root = tmp_path / "project"
    _generate(root, _model_copy(tmp_path / "clean"))

    model_path = _renamed_model(tmp_path, consistent=False)

    with pytest.raises(ModelValidationError) as caught:
        load_model(str(model_path))
    assert RENAME_FROM in str(caught.value), (
        "the refusal does not name the dangling reference, so the test cannot "
        "tell WHICH unrelated exception it caught"
    )

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)
    assert code == 3, "band 13 here would claim the project drifted; it was never checked"
    assertions = {entry["id"]: entry for entry in payload["assertions"]}
    assert assertions["structural"]["ran"] is False
    assert not [
        finding
        for finding in payload["findings"]
        if finding["kind"].startswith(("fact-type", "orphan", "tool-"))
    ], "a structural finding was reported over a model that never loaded"


def test_a_consistent_rename_keeps_the_model_valid_and_reds_the_gate_with_both_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """**G-09 mutation #3, the real one.** RESEARCH §2.2 case C: 2 findings.

    The pair is what proves the gate reads the model and the filesystem
    INDEPENDENTLY: the missing side comes from the model, the orphan side comes
    from the tree, and neither could be produced by comparing either against the
    manifest.
    """
    root = tmp_path / "project"
    _generate(root, _model_copy(tmp_path / "clean"))

    model_path = _renamed_model(tmp_path, consistent=True)

    # The mutation is only a mutation if the model still LOADS. Asserted through
    # the shipped command, not through a library call, because exit 0 from
    # `gnd validate` is the claim a reader would check.
    capsys.readouterr()
    assert main(["validate", str(model_path)]) == 0, capsys.readouterr().out

    code, payload = _json_run(["conformance", str(model_path), str(root)], capsys)

    assert code == cli.EXIT_MODEL_CODE_DRIFT
    _validator().validate(payload)
    by_kind = {
        finding["kind"]: finding
        for finding in payload["findings"]
        if finding["kind"] in {"fact-type-unimplemented", "orphan-tool-symbol"}
    }
    assert set(by_kind) == {"fact-type-unimplemented", "orphan-tool-symbol"}, payload["findings"]

    missing = by_kind["fact-type-unimplemented"]
    assert missing["target"] == RENAME_TO
    assert RENAME_TO in missing["message"]

    orphan = by_kind["orphan-tool-symbol"]
    assert tool_symbol(RENAME_FROM) in orphan["message"], orphan
    assert TOOLS_MODULE in orphan["message"], (
        "the orphan finding does not name the file it was found in, so a reader "
        "cannot go and look at it"
    )


def test_the_consistent_rename_is_the_only_difference_between_the_two_models(
    tmp_path: Path,
) -> None:
    """The two mutations are DERIVED from one fixture, so the C0 test and the
    real mutation cannot drift into testing two unrelated documents."""
    naive = _renamed_model(tmp_path / "naive", consistent=False)
    consistent = _renamed_model(tmp_path / "consistent", consistent=True)
    original = FULL_VOCABULARY.read_text(encoding="utf-8")

    assert naive.read_text(encoding="utf-8") == original.replace(
        f"id: {RENAME_FROM}", f"id: {RENAME_TO}", 1
    )
    assert consistent.read_text(encoding="utf-8") == original.replace(RENAME_FROM, RENAME_TO)
    assert naive.read_text(encoding="utf-8") != consistent.read_text(encoding="utf-8")
