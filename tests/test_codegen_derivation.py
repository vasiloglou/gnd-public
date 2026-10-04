






from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

from gnd.cli import main
from gnd.model import load_model, structured_derivation_ids

CORPUS = Path(__file__).parent / "fixtures" / "phase3-consumers"


def _generate(out: Path) -> None:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.chdir(CORPUS):
        code = main(["codegen", "eligibility.orm.yaml", "--out", str(out)])
    assert code == 0, stdout.getvalue()


def _tree_digest(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def test_the_one_predicate_names_exactly_the_structured_fact_types() -> None:


    structured = structured_derivation_ids(load_model(CORPUS / "eligibility.orm.yaml"))
    assert structured == ("book_is_eligible",)
    legacy = structured_derivation_ids(load_model(CORPUS / "legacy-derived.orm.yaml"))
    assert legacy == ()


def test_no_constructor_is_emitted_for_a_structured_derived_fact_type(
    tmp_path: Path,
) -> None:


    out = tmp_path / "eligibility"
    _generate(out)
    tools = (out / "eligibility" / "tools.py").read_text(encoding="utf-8")
    assert "def book_listed(" in tools
    assert "def book_blocked(" in tools
    assert "def book_is_eligible(" not in tools
    assert "'book_is_eligible'" not in tools

    package_init = (out / "eligibility" / "__init__.py").read_text(encoding="utf-8")
    assert "book_is_eligible" not in package_init

    skill = (out / "SKILL.md").read_text(encoding="utf-8")
    tools_table = skill.split("## Derived tools")[1].split("## Derived fact types")[0]
    assert "| `book_listed` |" in tools_table
    assert "book_is_eligible" not in tools_table


def test_the_emitted_docs_say_why_the_constructor_is_absent(tmp_path: Path) -> None:


    out = tmp_path / "eligibility"
    _generate(out)
    tools = (out / "eligibility" / "tools.py").read_text(encoding="utf-8")
    assert "book_is_eligible" in tools                                             
    assert "derivation rule" in tools

    skill = (out / "SKILL.md").read_text(encoding="utf-8")
    assert "## Derived fact types" in skill
    assert "`book_is_eligible`" in skill


def test_the_projection_schema_still_admits_the_derived_fact_type(
    tmp_path: Path,
) -> None:


    out = tmp_path / "eligibility"
    _generate(out)
    projection = (out / "artifacts" / "eligibility.projection.schema.json").read_text(
        encoding="utf-8"
    )
    assert "book_is_eligible" in projection


def test_generated_instructions_separate_general_claims_from_extractions(
    tmp_path: Path,
) -> None:


    out = tmp_path / "eligibility"
    _generate(out)
    skill = (out / "SKILL.md").read_text(encoding="utf-8")
    assert "### Check a general population" in skill
    assert "### Verify a document extraction" in skill
    assert "add every structured fact type whose extension you publish" in skill
    assert 'gnd check "$MODEL_PATH" population.json' in skill
    assert "extraction sidecar" in skill

    artifact = json.loads(
        (out / "artifacts" / "eligibility.artifacts.json").read_text(encoding="utf-8")
    )
    header = dict(artifact["header_template"])
    assert "book_is_eligible" not in header["covers"], (
        "the emitted template remains the document-extraction header"
    )
    header["covers"] = sorted([*header["covers"], "book_is_eligible"])
    population = {
        "population": header,
        "instances": {},
        "facts": {
            "book_listed": [{"book": "dune"}],
            "book_blocked": [],
            "book_is_eligible": [{"book": "dune"}],
        },
    }
    population_path = out / "population.json"
    population_path.write_text(json.dumps(population), encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        code = main(["check", str(CORPUS / "eligibility.orm.yaml"), str(population_path)])
    assert code == 0, "the general-claim recipe must reach and pass derivation comparison"


def test_a_second_run_over_the_structured_model_is_byte_identical(
    tmp_path: Path,
) -> None:


    out = tmp_path / "eligibility"
    _generate(out)
    before = _tree_digest(out)
    stamps = {
        path: path.stat().st_mtime_ns
        for path in sorted(out.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }
    _generate(out)
    assert _tree_digest(out) == before
                                                                            
                                                                           
    assert {
        path: path.stat().st_mtime_ns
        for path in sorted(out.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    } == stamps


                                                                      
                                                                      
                                                                        
                                                                         
                                                                       
             
MIXED_STRUCTURED_MODEL = """\
version: 1
model_id: urn:gnd-fixture:phase3-consumers:all-structured@1
source: { kind: text-conversation, confidence: standard, mode: one-shot }
object_types:
  - { id: item, name: Item, kind: value, primitive: String }
fact_types:
  - id: seed
    reading: "{Item} is seeded"
    roles: [{ object_type: item, role_name: item }]
    derivation: derived
    derivation_rule:
      body: [{ fact_type: result, bind: { item: "$i" } }]
      head: { item: "$i" }
  - id: result
    reading: "{Item} results"
    roles: [{ object_type: item, role_name: item }]
constraints: []
rejected_proposals: []
"""


def test_a_single_kept_fact_type_still_reexports_and_parses(tmp_path: Path) -> None:


    model_path = tmp_path / "all-structured.orm.yaml"
    model_path.write_text(MIXED_STRUCTURED_MODEL, encoding="utf-8")
    out = tmp_path / "generated"
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.chdir(tmp_path):
        code = main(["codegen", "all-structured.orm.yaml", "--out", str(out)])
    assert code == 0, stdout.getvalue()
    package_init = (out / "all_structured" / "__init__.py").read_text(encoding="utf-8")
    assert "result" in package_init
    assert "seed" not in package_init.replace("is seeded", "")
    compile(package_init, "__init__.py", "exec")
    tools = (out / "all_structured" / "tools.py").read_text(encoding="utf-8")
    assert "def result(" in tools
    assert "def seed(" not in tools
    compile(tools, "tools.py", "exec")
