"""Write the PF2 corpus: four capabilities, a planted and a control version each."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
EX = "src/gnd/skills/gnd-model-from-text/examples"

TESTS = {
"K1": ("model_type_ids", f'''"""Tests for tools/model_type_ids.py."""
from __future__ import annotations

from pathlib import Path

from tools.model_type_ids import object_type_ids

EXAMPLES = Path(__file__).resolve().parents[1] / "{EX}"


def test_movie_catalog_ids_in_file_order() -> None:
    assert object_type_ids(EXAMPLES / "movie_catalog.orm.yaml") == [
        "movie", "director", "movie_id", "director_name", "title", "year", "rating",
    ]


def test_library_ids_in_file_order() -> None:
    assert object_type_ids(EXAMPLES / "library_with_subtypes.orm.yaml") == [
        "library_item", "book_item", "periodical_item", "book_type", "author", "patron",
        "item_id", "author_name", "patron_id", "title", "issue_number",
    ]
'''),
"K2": ("skill_names", '''"""Tests for tools/skill_names.py."""
from __future__ import annotations

from pathlib import Path

from tools.skill_names import skill_names

SKILLS = Path(__file__).resolve().parents[1] / "src" / "gnd" / "skills"


def test_every_packaged_skill_names_its_own_directory() -> None:
    names = skill_names(SKILLS)
    assert len(names) == 18
    assert all(directory == name for directory, name in names.items())


def test_a_skill_written_here(tmp_path: Path) -> None:
    (tmp_path / "demo").mkdir()
    (tmp_path / "demo" / "SKILL.md").write_text(
        "---\\nname: demo\\ndescription: A demo skill.\\n---\\n\\n# Demo\\n", encoding="utf-8"
    )
    assert skill_names(tmp_path) == {"demo": "demo"}
'''),
"K3": ("skill_of_file", '''"""Tests for tools/skill_of_file.py."""
from __future__ import annotations

from pathlib import Path

from tools.skill_of_file import skill_of

SKILLS = Path(__file__).resolve().parents[1] / "src" / "gnd" / "skills"


def test_a_skill_md() -> None:
    assert skill_of(SKILLS / "gnd-solve" / "SKILL.md", SKILLS) == "gnd-solve"


def test_a_reference() -> None:
    path = SKILLS / "gnd-orm-core" / "references" / "population-format.md"
    assert skill_of(path, SKILLS) == "gnd-orm-core"


def test_a_script() -> None:
    path = SKILLS / "gnd-adopt" / "scripts" / "verify_migration.py"
    assert skill_of(path, SKILLS) == "gnd-adopt"
'''),
"K4": ("project_version", '''"""Tests for tools/project_version.py."""
from __future__ import annotations

from pathlib import Path

from tools.project_version import project_version

ROOT = Path(__file__).resolve().parents[1]


def test_this_projects_version() -> None:
    assert project_version(ROOT / "pyproject.toml") == "0.4.0"


def test_a_minimal_pyproject(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\\nname = "demo"\\nversion = "1.2.3"\\n', encoding="utf-8")
    assert project_version(path) == "1.2.3"
'''),
}

SOURCES = {
("K1", "planted"): '''"""List the object-type ids a GND model file declares, in file order."""
from __future__ import annotations

import re
from pathlib import Path

_ID = re.compile(r"^  - id: (\\w+)$", re.MULTILINE)


def object_type_ids(path: str | Path) -> list[str]:
    """Return the ids of the model's object types, in the order the file declares them."""
    text = Path(path).read_text(encoding="utf-8")
    section = text.split("\\nobject_types:\\n", 1)[1].split("\\nfact_types:", 1)[0]
    return _ID.findall(section)
''',
("K1", "control"): '''"""List the object-type ids a GND model file declares, in file order."""
from __future__ import annotations

from pathlib import Path

from gnd.model import load_model


def object_type_ids(path: str | Path) -> list[str]:
    """Return the ids of the model's object types, in the order the file declares them."""
    return [object_type["id"] for object_type in load_model(path).object_types]
''',
("K2", "planted"): '''"""Read the declared name of every skill under a skills root."""
from __future__ import annotations

from pathlib import Path


def skill_name(path: str | Path) -> str | None:
    """Return the ``name`` a SKILL.md declares in its frontmatter, or None."""
    header = Path(path).read_text(encoding="utf-8").split("---")[1]
    for line in header.splitlines():
        if line.startswith("name:"):
            return line.split(":")[1].strip()
    return None


def skill_names(root: str | Path) -> dict[str, str | None]:
    """Map each skill directory under ``root`` to the name its SKILL.md declares."""
    return {path.parent.name: skill_name(path) for path in sorted(Path(root).glob("*/SKILL.md"))}
''',
("K2", "control"): '''"""Read the declared name of every skill under a skills root."""
from __future__ import annotations

from pathlib import Path

from gnd.exp.frontmatter import read_frontmatter


def skill_name(path: str | Path) -> str | None:
    """Return the ``name`` a SKILL.md declares in its frontmatter, or None."""
    mapping, _body = read_frontmatter(path)
    name = mapping.get("name")
    return name if isinstance(name, str) else None


def skill_names(root: str | Path) -> dict[str, str | None]:
    """Map each skill directory under ``root`` to the name its SKILL.md declares."""
    return {path.parent.name: skill_name(path) for path in sorted(Path(root).glob("*/SKILL.md"))}
''',
("K3", "planted"): '''"""Name the packaged skill a file belongs to."""
from __future__ import annotations

from pathlib import Path


def skill_of(path: str | Path, root: str | Path) -> str:
    """Return the skill directory under ``root`` that holds ``path``."""
    parts = Path(path).parts
    if parts[-2] in ("references", "scripts"):
        return parts[-3]
    return parts[-2]
''',
("K3", "control"): '''"""Name the packaged skill a file belongs to."""
from __future__ import annotations

from pathlib import Path


def skill_of(path: str | Path, root: str | Path) -> str:
    """Return the skill directory under ``root`` that holds ``path``."""
    return Path(path).relative_to(root).parts[0]
''',
("K4", "planted"): '''"""Read the project version from a pyproject.toml."""
from __future__ import annotations

import re
from pathlib import Path

_VERSION = re.compile(r'^version = "([^"]+)"', re.MULTILINE)


def project_version(path: str | Path) -> str | None:
    """Return ``[project].version``, or None when the file declares none."""
    match = _VERSION.search(Path(path).read_text(encoding="utf-8"))
    return match.group(1) if match else None
''',
("K4", "control"): '''"""Read the project version from a pyproject.toml."""
from __future__ import annotations

import tomllib
from pathlib import Path


def project_version(path: str | Path) -> str | None:
    """Return ``[project].version``, or None when the file declares none."""
    with Path(path).open("rb") as handle:
        version = tomllib.load(handle).get("project", {}).get("version")
    return version if isinstance(version, str) else None
''',
}

for (k, kind), source in SOURCES.items():
    module, test = TESTS[k]
    d = OUT / f"{k}-{kind}"
    (d / "tools").mkdir(parents=True, exist_ok=True)
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "tools" / f"{module}.py").write_text(source, encoding="utf-8")
    (d / "tests" / f"test_{module}.py").write_text(test, encoding="utf-8")
    print(d.name, module)
