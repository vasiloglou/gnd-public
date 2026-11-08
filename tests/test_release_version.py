"""The package version has one home, and everything that repeats it agrees with it.

`pyproject.toml` declares the version. The lock entry, the plugin manifests and
the release notes heading repeat it and a drift in any one is refused. While the
declared version is not in `RELEASED`, nothing in the notes, the compatibility
page or the support page may say it is published, and no install command may pin
it. Release preparation changes none of the pins; publication does, together with
`RELEASED`.
"""

import json
import re
import shutil
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Versions that exist on the package index. Publication adds the new version
# here, in the same patch that moves the install pins (historical data: the one
# literal of its kind in the tests).
RELEASED = {"0.1.0"}

MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
)
PIN_FILES = ("README.md", "docs/installation.md", "docs/index.md", "docs/marketplace-plugins.md")
VERSION_HEADING = re.compile(r"^## (\d+\.\d+\.\d+\S*)(?: \((.*)\))?\s*$")


def declared_version(root: Path = ROOT) -> str:
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def lock_version(root: Path = ROOT) -> str:
    """The version of the editable `get-nick-done` entry of `uv.lock`."""
    text = (root / "uv.lock").read_text(encoding="utf-8")
    match = re.search(r'^\[\[package\]\]\nname = "get-nick-done"\nversion = "([^"]+)"\nsource = \{ editable', text, re.M)
    assert match, "uv.lock has no editable get-nick-done entry"
    return match.group(1)


def manifest_versions(root: Path = ROOT) -> dict[str, str]:
    versions = {}
    for relative in MANIFESTS:
        document = json.loads((root / relative).read_text(encoding="utf-8"))
        # marketplace.json carries the version on its one plugin entry
        node = document["plugins"][0] if "plugins" in document else document
        versions[relative] = node["version"]
    return versions


def notes_headings(root: Path = ROOT) -> list[str]:
    lines = (root / "docs/release-notes.md").read_text(encoding="utf-8").splitlines()
    return [line for line in lines if line.startswith("## ")]


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.match(r"\d+(?:\.\d+)*", version).group(0).split("."))


def assert_versions_agree(declared: str, lock: str, manifests: dict[str, str], headings: list[str]) -> None:
    """Raise AssertionError unless every repeat of the version equals the declared one."""
    assert lock == declared, f"uv.lock says {lock}, pyproject.toml says {declared}"
    for name, value in manifests.items():
        assert value == declared, f"{name} says {value}, pyproject.toml says {declared}"
    versioned = [m.group(1) for h in headings if (m := VERSION_HEADING.match(h))]
    assert versioned, "docs/release-notes.md has no version heading"
    assert versioned[0] == declared, f"the newest notes heading is {versioned[0]}, pyproject.toml says {declared}"


def assert_no_publication_claim(declared: str, released: set[str], headings: list[str], compatibility: str, other: dict[str, str]) -> None:
    """While `declared` is unpublished, the notes and pages must not say it is."""
    if declared in released:
        return
    heading = next((h for h in headings if (m := VERSION_HEADING.match(h)) and m.group(1) == declared), None)
    assert heading is not None, f"no notes heading for {declared}"
    assert "not published" in heading, f"the notes heading {heading!r} does not say {declared} is not published"
    assert "not published" in compatibility, "docs/compatibility.md does not say the prepared version is not published"
    claim = re.compile(rf"\b{re.escape(declared)}\b[^.\n]*\b(?:is|was|has been|are|were) (?:now )?(?:published|released|available on)", re.I)
    for name, text in {"docs/compatibility.md": compatibility, **other}.items():
        assert not claim.search(text), f"{name} says {declared} is published"


def pinned_install_versions(root: Path = ROOT) -> dict[str, set[str]]:
    pins = {}
    for relative in PIN_FILES:
        found = set(re.findall(r"get-nick-done==(\d+\.\d+\.\d+[\w.]*)", (root / relative).read_text(encoding="utf-8")))
        pins[relative] = found
    return pins


def assert_pins_name_published_versions(pins: dict[str, set[str]], declared: str, released: set[str]) -> None:
    """An install pin may name only a version that exists and is not newer than the declared one."""
    for name, versions in pins.items():
        for version in versions:
            assert version in released, f"{name} pins {version}, which is not in RELEASED"
            assert version_key(version) <= version_key(declared), f"{name} pins {version}, newer than {declared}"


def read_other_pages(root: Path = ROOT) -> dict[str, str]:
    return {name: (root / name).read_text(encoding="utf-8") for name in ("docs/support.md", "docs/release-notes.md")}


def make_tree(tmp_path: Path) -> Path:
    for relative in ("pyproject.toml", "uv.lock", "docs/release-notes.md", "docs/compatibility.md", "docs/support.md", *MANIFESTS, *PIN_FILES):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return tmp_path


def values(root: Path):
    return declared_version(root), lock_version(root), manifest_versions(root), notes_headings(root)


def test_lock_manifests_and_notes_agree_with_pyproject():
    assert_versions_agree(*values(ROOT))


def test_agreement_control_passes_on_an_unmutated_copy(tmp_path):
    assert_versions_agree(*values(make_tree(tmp_path)))


def _rewrite(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, (path, old)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


@pytest.mark.parametrize("site", ["pyproject", "lock", "manifest", "notes"])
def test_drift_is_refused(tmp_path, site):
    root = make_tree(tmp_path)
    declared = declared_version(root)
    other = "9.9.9"
    if site == "pyproject":
        _rewrite(root / "pyproject.toml", f'version = "{declared}"', f'version = "{other}"')
    elif site == "lock":
        _rewrite(root / "uv.lock", f'name = "get-nick-done"\nversion = "{declared}"', f'name = "get-nick-done"\nversion = "{other}"')
    elif site == "manifest":
        _rewrite(root / ".codex-plugin/plugin.json", f'"version": "{declared}"', f'"version": "{other}"')
    else:
        _rewrite(root / "docs/release-notes.md", f"## {declared}", f"## {other}")
    with pytest.raises(AssertionError):
        assert_versions_agree(*values(root))


def test_notes_and_compatibility_do_not_claim_publication():
    assert_no_publication_claim(
        declared_version(), RELEASED, notes_headings(), (ROOT / "docs/compatibility.md").read_text(encoding="utf-8"), read_other_pages()
    )


@pytest.mark.parametrize("mutation", ["heading-status-removed", "compatibility-claims", "support-claims", "heading-missing"])
def test_publication_claim_mutants_are_refused(tmp_path, mutation):
    root = make_tree(tmp_path)
    declared = "9.9.9"  # an unpublished version, whatever the tree declares
    headings = [f"## {declared} (prepared, not published)"]
    compatibility = "9.9.9 is prepared and not published.\n"
    other = {"docs/support.md": "No profile is observed for 9.9.9.\n"}
    assert_no_publication_claim(declared, RELEASED, headings, compatibility, other)  # the control passes
    if mutation == "heading-status-removed":
        headings = [f"## {declared}"]
    elif mutation == "compatibility-claims":
        compatibility += "Version 9.9.9 is published on the package index.\n"
    elif mutation == "support-claims":
        other["docs/support.md"] += "9.9.9 has been released.\n"
    else:
        headings = ["## Unreleased: something"]
    with pytest.raises(AssertionError):
        assert_no_publication_claim(declared, RELEASED, headings, compatibility, other)


def test_install_pins_name_a_published_version():
    assert_pins_name_published_versions(pinned_install_versions(), declared_version(), RELEASED)


@pytest.mark.parametrize("pin", ["0.2.0", "9.9.9"])
def test_pin_mutants_are_refused(pin):
    declared = "0.2.0"
    assert_pins_name_published_versions({"README.md": {"0.1.0"}}, declared, {"0.1.0"})  # the control passes
    with pytest.raises(AssertionError):
        assert_pins_name_published_versions({"README.md": {pin}}, declared, {"0.1.0"})


def test_a_pin_to_the_next_version_is_refused_until_it_is_released():
    with pytest.raises(AssertionError):
        assert_pins_name_published_versions({"README.md": {"0.2.0"}}, "0.2.0", {"0.1.0"})
    assert_pins_name_published_versions({"README.md": {"0.2.0"}}, "0.2.0", {"0.1.0", "0.2.0"})


def test_every_pin_file_carries_a_pin_so_the_rule_cannot_pass_vacuously():
    pins = pinned_install_versions()
    assert all(pins[name] for name in PIN_FILES), pins
