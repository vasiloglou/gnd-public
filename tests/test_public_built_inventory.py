"""Built public wheel and sdist controls over the declared current skill inventory."""
from __future__ import annotations

import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest
from test_packaged_skills import (
    EXPECTED_SKILL_FILE_COUNT,
    EXPECTED_SKILL_FILES,
    EXPECTED_SKILL_NAMES,
)

pytestmark = pytest.mark.distribution


REPO_ROOT = Path(__file__).resolve().parent.parent


SKILLS_SRC = REPO_ROOT / "src" / "gnd" / "skills"


PHASE_FOUR_RESOURCES = (
    "gnd-model-evolve/SKILL.md",
    "gnd-model-evolve/references/evolution-contract.md",
    "gnd-model-from-code/SKILL.md",
    "gnd-model-from-code/references/recovery-contract.md",
    "gnd-review-panel/SKILL.md",
    "gnd-review-panel/references/review-contract.md",
)


WHEEL_SKILL_PREFIX = "gnd/skills/"


FORBIDDEN_PATH_PARTS = frozenset(
    {".git", ".github", ".planning", ".venv", "venv", ".env", "__pycache__", ".pytest_cache",
     ".ruff_cache", ".claude", ".codex", "node_modules"}
)


@pytest.fixture(scope="session")
def built_artifacts(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """Plain ``uv build`` — NOT ``--wheel``. See the module docstring."""
    if shutil.which("uv") is None:
        pytest.skip("uv is not available on PATH")
    out = tmp_path_factory.mktemp("dist")
    subprocess.run(
        ["uv", "build", "--out-dir", str(out)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    wheels = sorted(out.glob("*.whl"))
    sdists = sorted(out.glob("*.tar.gz"))
    assert len(wheels) == 1, f"expected exactly one wheel, got {[w.name for w in wheels]}"
    assert len(sdists) == 1, f"expected exactly one sdist, got {[s.name for s in sdists]}"
    return wheels[0], sdists[0]


def _wheel_names(wheel: Path) -> list[str]:
    """File entries only. Both archives carry directory entries too, and counting
    those inflates every count assertion by the tree's depth — a count that is
    right for the wrong reason is worse than no count at all."""
    with zipfile.ZipFile(wheel) as archive:
        return [info.filename for info in archive.infolist() if not info.is_dir()]


def _sdist_names(sdist: Path) -> list[str]:
    with tarfile.open(sdist) as archive:
        # Strip the single top-level `<name>-<version>/` component so paths are
        # comparable with the wheel's.
        return [
            "/".join(member.name.split("/")[1:])
            for member in archive.getmembers()
            if member.isfile()
        ]


def _wheel_skill_files(wheel: Path) -> set[str]:
    """Read the wheel's own entry list (zipfile)."""
    return {
        name[len(WHEEL_SKILL_PREFIX) :]
        for name in _wheel_names(wheel)
        if name.startswith(WHEEL_SKILL_PREFIX)
    }


def _sdist_skill_files(sdist: Path) -> set[str]:
    """Read the sdist's own member list (tarfile)."""
    prefix = "src/gnd/skills/"
    return {
        name[len(prefix) :] for name in _sdist_names(sdist) if name.startswith(prefix)
    }


def _source_skill_files() -> set[str]:
    """Read the source tree itself (rglob), never a build artifact."""
    if not SKILLS_SRC.is_dir():  # pragma: no cover - the set assertion reports it
        return set()
    return {
        path.relative_to(SKILLS_SRC).as_posix()
        for path in SKILLS_SRC.rglob("*")
        if path.is_file()
    }


def _skill_names(entries: set[str]) -> set[str]:
    return {rel.split("/")[0] for rel in entries}


def _diff(surface: str, entries: set[str]) -> str:
    missing = sorted(EXPECTED_SKILL_FILES - entries)
    extra = sorted(entries - EXPECTED_SKILL_FILES)
    return (
        f"the {surface} is not the pinned inventory.\n"
        f"  missing ({len(missing)}): " + ", ".join(missing) + "\n"
        f"  extra   ({len(extra)}): " + ", ".join(extra) + "\n"
        "Set difference, not arithmetic: a dropped file and an unrelated added "
        "one cancel in a count and are both named here (plan 04-12, mutation M2)."
    )


def test_the_wheel_carries_exactly_the_pinned_skill_file_set(
    built_artifacts: tuple[Path, Path],
) -> None:
    """T-04-13-01, the wheel's half. Read from the wheel's own entry list."""
    wheel, _ = built_artifacts
    entries = _wheel_skill_files(wheel)
    assert entries == EXPECTED_SKILL_FILES, _diff("wheel", entries)
    assert _skill_names(entries) == EXPECTED_SKILL_NAMES, (
        f"the wheel ships skills {sorted(_skill_names(entries))}, expected "
        f"{sorted(EXPECTED_SKILL_NAMES)}."
    )


def test_the_sdist_carries_exactly_the_pinned_skill_file_set(
    built_artifacts: tuple[Path, Path],
) -> None:
    """T-04-13-01, the sdist's half. The default ``uv build`` path builds the
    wheel FROM the sdist, so a file absent here is absent everywhere downstream —
    and an include mechanism can work one way and silently drop files the other.
    """
    _, sdist = built_artifacts
    entries = _sdist_skill_files(sdist)
    assert entries == EXPECTED_SKILL_FILES, _diff("sdist", entries)
    assert _skill_names(entries) == EXPECTED_SKILL_NAMES, (
        f"the sdist ships skills {sorted(_skill_names(entries))}, expected "
        f"{sorted(EXPECTED_SKILL_NAMES)}."
    )


def test_the_source_tree_carries_exactly_the_pinned_skill_file_set() -> None:
    """The surface the other two are built from, read on its own terms.

    Without this, a source-tree change that the pin was updated to match would
    make the artifact assertions above green about the wrong tree.
    """
    entries = _source_skill_files()
    assert entries == EXPECTED_SKILL_FILES, _diff(f"source tree at {SKILLS_SRC}", entries)
    assert _skill_names(entries) == EXPECTED_SKILL_NAMES, (
        f"the source tree holds skills {sorted(_skill_names(entries))}, expected "
        f"{sorted(EXPECTED_SKILL_NAMES)}."
    )


@pytest.mark.parametrize("resource", PHASE_FOUR_RESOURCES)
def test_every_phase_four_resource_ships_in_every_built_surface(
    resource: str, built_artifacts: tuple[Path, Path]
) -> None:
    """Named individually so a compensating substitution cannot pass quietly.

    The set assertions above already imply these, but they imply them as a diff.
    A build change that dropped ``gnd-review-panel/references/review-contract.md``
    and picked up some unrelated file would satisfy both counts; here the file is
    named, per surface.
    """
    wheel, sdist = built_artifacts
    for name, entries in (
        ("source tree", _source_skill_files()),
        ("sdist", _sdist_skill_files(sdist)),
        ("wheel", _wheel_skill_files(wheel)),
    ):
        assert resource in entries, (
            f"{resource} is absent from the {name}. It is one of the six resources "
            "Phase 4 adds; without it the skill it belongs to is installed "
            "half-formed and its sibling-relative links point nowhere."
        )


def test_wheel_carries_every_skill_file(built_artifacts: tuple[Path, Path]) -> None:
    wheel, _ = built_artifacts
    entries = [n for n in _wheel_names(wheel) if n.startswith(WHEEL_SKILL_PREFIX)]
    assert len(entries) == EXPECTED_SKILL_FILE_COUNT, (
        f"the wheel carries {len(entries)} entries under {WHEEL_SKILL_PREFIX}, "
        f"expected {EXPECTED_SKILL_FILE_COUNT}. An installer cannot place assets "
        f"that are not in the artifact. Do NOT reach for a [tool.uv.build-backend] "
        f"stanza — the backend ignores unknown keys and would report success "
        f"regardless; the skill tree must physically live under src/gnd/skills/. "
        f"Found: {sorted(entries)}"
    )


def test_sdist_carries_every_skill_file(built_artifacts: tuple[Path, Path]) -> None:
    _, sdist = built_artifacts
    entries = [n for n in _sdist_names(sdist) if n.startswith("src/gnd/skills/")]
    assert len(entries) == EXPECTED_SKILL_FILE_COUNT, (
        f"the sdist carries {len(entries)} skill files, expected "
        f"{EXPECTED_SKILL_FILE_COUNT}. The default `uv build` path builds the "
        f"wheel FROM the sdist, so anything missing here is missing downstream. "
        f"Found: {sorted(entries)}"
    )


def test_source_tree_count_matches_the_expected_constant() -> None:
    """Keeps EXPECTED_SKILL_FILE_COUNT honest against the tree it describes."""
    on_disk = sorted(p for p in SKILLS_SRC.rglob("*") if p.is_file()) if SKILLS_SRC.is_dir() else []
    assert len(on_disk) == EXPECTED_SKILL_FILE_COUNT, (
        f"{SKILLS_SRC} holds {len(on_disk)} files, but EXPECTED_SKILL_FILE_COUNT "
        f"is {EXPECTED_SKILL_FILE_COUNT}. If a skill file was deliberately added "
        f"or removed, update the constant here and in tests/test_packaged_skills.py."
    )


def test_wheel_contains_nothing_outside_the_package(built_artifacts: tuple[Path, Path]) -> None:
    wheel, _ = built_artifacts
    names = _wheel_names(wheel)

    unexpected = [
        n for n in names if not (n.startswith("gnd/") or ".dist-info/" in n or n.endswith(".dist-info"))
    ]
    assert not unexpected, (
        "the wheel contains entries outside gnd/ and the .dist-info directory: "
        f"{sorted(unexpected)}"
    )

    leaked = [n for n in names if FORBIDDEN_PATH_PARTS & set(n.split("/"))]
    assert not leaked, (
        "the wheel leaks version-control, virtualenv, planning, cache, or dotenv "
        f"paths — this is a disclosure failure, not noise (T-01.2-01): {sorted(leaked)}"
    )


VENDORED_SCHEMAS = (
    "gnd/assurance-anchor.schema.json",
    "gnd/assurance-evidence.schema.json",
    "gnd/report.schema.json",
    "gnd/diff.schema.json",
    "gnd/pool.schema.json",
    "gnd/measurement.schema.json",
    "gnd/fidelity.schema.json",
    "gnd/conformance.schema.json",
    "gnd/coverage.schema.json",
    "gnd/rai-alias.schema.json",
    "gnd/batch-report.schema.json",
    "gnd/discover.schema.json",
    "gnd/labels.schema.json",
    "gnd/ilp.schema.json",
    "gnd/ilp-clauses.schema.json",
    "gnd/ilp-run.schema.json",
    "gnd/ilp-import.schema.json",
)


def test_wheel_carries_every_vendored_runtime_schema(built_artifacts: tuple[Path, Path]) -> None:
    """measurement.schema.json is a runtime contract this plan adds; like
    report.schema.json and pool.schema.json it must physically ship under the
    module root, or `gnd measure` cannot resolve it through importlib.resources
    once installed (C12)."""
    wheel, _ = built_artifacts
    names = set(_wheel_names(wheel))
    missing = [schema for schema in VENDORED_SCHEMAS if schema not in names]
    assert not missing, (
        f"the wheel is missing vendored runtime schema(s): {missing}. Each must "
        f"live at src/<name>.schema.json for the module root to carry it — do NOT "
        f"reach for a build-backend include stanza (the backend ignores unknown "
        f"keys and would report success regardless)."
    )


def test_wheel_is_named_for_the_distribution(built_artifacts: tuple[Path, Path]) -> None:
    wheel, _ = built_artifacts
    assert wheel.name.startswith("get_nick_done-"), (
        f"wheel is named {wheel.name!r}; the distribution is `get-nick-done` "
        "(D-01 — `gnd` is taken on PyPI), which normalises to the "
        "`get_nick_done-` filename prefix. The import package and console script "
        "stay `gnd`."
    )



def test_public_built_surfaces_agree_with_current_inventory(
    built_artifacts: tuple[Path, Path],
) -> None:
    """Owned current boundary; the older literal15 assertion remains source-owned."""
    wheel, sdist = built_artifacts
    surfaces = {
        "source": _source_skill_files(),
        "sdist": _sdist_skill_files(sdist),
        "wheel": _wheel_skill_files(wheel),
    }
    assert len(EXPECTED_SKILL_FILES) == EXPECTED_SKILL_FILE_COUNT == 65
    assert len(EXPECTED_SKILL_NAMES) == 16
    for label, entries in surfaces.items():
        assert entries == EXPECTED_SKILL_FILES, _diff(label, entries)
        assert _skill_names(entries) == EXPECTED_SKILL_NAMES
        assert len(entries) == 65
        assert len(_skill_names(entries)) == 16
    assert surfaces["source"] == surfaces["sdist"] == surfaces["wheel"]
