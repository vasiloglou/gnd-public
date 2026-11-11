"""Re-record the committed outputs that carry gnd_version, for a release bump OLD -> NEW.

Run from the repository root with the bumped package installed:

    uv run -q python _work/rerecord.py

It edits only files under tests/fixtures/ and sha256 literals in test files. It
reads the working tree, so a second run changes nothing. Everything temporary is
written under _work/tmp (removed at the start of each run).

Two ways a new value is obtained (each family says which):

  LIVE       the real command (or the test's own capture path) is run and its
             output, or the digest of its output, is recorded.
  TRANSFORM  a recorded document is stored inside the fixture; its gnd_version
             field is moved OLD -> NEW and every digest of a moved document is
             re-derived (sha256 of the new bytes) wherever a named dependent
             member cites it. The owning test compares these bytes with the live
             command, so the test run is the check that the transform equals
             live output.

Every family refuses (raises Stop) when it would need any other kind of change.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

OLD, NEW = "0.2.0", "0.3.0"
ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_work"
TMP = WORK / "tmp"
FIX = ROOT / "tests/fixtures"
PY = sys.executable
GND = [PY, "-m", "gnd"]
VERSION_FIELD = re.compile(r'("gnd_version"\s*:\s*")' + re.escape(OLD) + '"')
HEX64 = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")


class Stop(Exception):
    """A family needs a change the rules do not allow; nothing of it is written."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def head(relative: str) -> bytes:
    return subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=ROOT, capture_output=True, check=True).stdout


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write(path: Path, data: bytes) -> None:
    allowed = rel(path).startswith("tests/fixtures/") or re.fullmatch(r"tests/test_[a-z0-9_]+\.py", rel(path))
    if not allowed:
        raise Stop(f"refusing to write outside the allowed set: {rel(path)}")
    if path.read_bytes() != data:
        path.write_bytes(data)
        print(f"  wrote {rel(path)}")


def run(argv, *, cwd=ROOT, env=None, check=True):
    full = {**os.environ, **(env or {})}
    done = subprocess.run(argv, cwd=cwd, env=full, capture_output=True, check=False)
    if check and done.returncode != 0:
        raise Stop(f"command failed ({done.returncode}): {argv}\n{done.stdout[-3000:].decode()}\n{done.stderr[-3000:].decode()}")
    return done


def bump(text: str, where: str) -> str:
    """Move the gnd_version field OLD -> NEW; the document must carry exactly one such field."""
    out, count = VERSION_FIELD.subn(rf'\g<1>{NEW}"', text)
    carried = len(re.findall(r'"gnd_version"\s*:\s*"' + re.escape(NEW) + '"', out))
    if carried != 1 or count > 1:
        raise Stop(f"{where}: expected one gnd_version field at {OLD} or {NEW}, found {count} moved, {carried} at {NEW}")
    return out


def masked(data: bytes) -> bytes:
    data = re.sub(rb'("gnd_version\\?"\s*:\s*\\?")[^"\\]*', rb"\1<V>", data)
    return re.sub(rb"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", b"<H>", data)


def same_but_version_and_digests(old: bytes, new: bytes, where: str) -> None:
    if masked(old) != masked(new) or len(old) != len(new):
        raise Stop(f"{where}: differs by more than the version value and 64-hex digests")


def replace_digests(text: str, mapping: dict[str, str]) -> str:
    return HEX64.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)


def pin_literal(test_file: str, old_values: set[str], new_value: str) -> None:
    """Replace one sha256 hex literal in a test file; nothing else in the file is touched."""
    path = ROOT / test_file
    text = path.read_text(encoding="utf-8")
    present = [v for v in old_values | {new_value} if v in text]
    if len(present) != 1 or text.count(present[0]) != 1:
        raise Stop(f"{test_file}: expected exactly one pinned literal among {sorted(old_values | {new_value})}, found {present}")
    write(path, text.replace(present[0], new_value).encode("utf-8"))


# --- gzip containers ---------------------------------------------------------
# Convention (measured on every container at HEAD and asserted here before any
# write): payload = json.dumps(doc, separators=(",", ":"), ensure_ascii=<as found>)
# with insertion order kept and no trailing newline; container =
# gzip.compress(payload, compresslevel=9, mtime=0), whose header is
# 1f 8b 08 00 | 00 00 00 00 | 02 | ff (no name, mtime 0, XFL 2, OS 255).

class Container:
    def __init__(self, relative: str) -> None:
        self.path = FIX / relative
        self.wire_before = self.path.read_bytes()
        self.wire_head = head(rel(self.path))
        raw = gzip.decompress(self.wire_before)
        self.raw_before = raw
        self.doc = json.loads(raw)
        for ascii_only in (True, False):
            if self._dump(ascii_only) == raw:
                self.ascii_only = ascii_only
                break
        else:
            raise Stop(f"{relative}: payload is not compact json.dumps output; convention unknown")
        if self._pack(raw) != self.wire_before:
            raise Stop(f"{relative}: container is not gzip.compress(level 9, mtime 0) of its payload")

    def _dump(self, ascii_only: bool) -> bytes:
        return json.dumps(self.doc, separators=(",", ":"), ensure_ascii=ascii_only).encode("utf-8")

    @staticmethod
    def _pack(raw: bytes) -> bytes:
        return gzip.compress(raw, compresslevel=9, mtime=0)

    def save(self) -> tuple[str, str]:
        raw = self._dump(self.ascii_only)
        wire = self._pack(raw)
        assert json.loads(gzip.decompress(wire)) == self.doc
        write(self.path, wire)
        return sha(wire), sha(raw)

    def old_wire_digests(self) -> set[str]:
        return {sha(self.wire_before), sha(self.wire_head)}


class B64Members:
    """{"members": {path: {"data": base64, "sha256": hex, ...}}} containers."""

    def __init__(self, container: Container) -> None:
        self.c = container
        self.members = container.doc["members"]

    def get(self, name: str) -> bytes:
        return base64.b64decode(self.members[name]["data"], validate=True)

    def put(self, name: str, data: bytes) -> None:
        member = self.members[name]
        old = self.get(name)
        assert sha(old) == member["sha256"]
        same_but_version_and_digests(old, data, f"{rel(self.c.path)}::{name}")
        member["data"] = base64.b64encode(data).decode("ascii")
        member["sha256"] = sha(data)


def assert_no_stale(container: Container, texts: dict[str, str], moved: dict[str, str], touched: set[str]) -> None:
    """No member outside the named ones may cite a digest that moved."""
    stale = {old for old, new in moved.items() if old != new}
    for name, text in texts.items():
        if name not in touched and any(d in text for d in stale):
            raise Stop(f"{rel(container.path)}::{name} cites a moved digest but is not a named dependent")


def transform_tree(get, put, names: list[str], moved: dict[str, str]) -> None:
    """Bump the version field of each named document, then re-derive cited digests to a fixed point."""
    current = {name: get(name).decode("utf-8") for name in names}
    originals = {name: sha(text.encode("utf-8")) for name, text in current.items()}
    for name in names:
        current[name] = bump(current[name], name)
    for _ in range(len(names) + 2):
        mapping = {**moved, **{originals[n]: sha(current[n].encode("utf-8")) for n in names}}
        updated = {n: replace_digests(current[n], mapping) for n in names}
        if updated == current:
            break
        # A digest re-derived in an earlier round maps forward too.
        for n in names:
            moved[sha(current[n].encode("utf-8"))] = sha(updated[n].encode("utf-8"))
        current = updated
    else:
        raise Stop("digest cascade did not settle")
    for name in names:
        moved[originals[name]] = sha(current[name].encode("utf-8"))
        put(name, current[name].encode("utf-8"))


# --- families ----------------------------------------------------------------

def family_setfam_artifacts() -> None:
    """LIVE: `gnd extract tests/fixtures/checker/setfam.orm.yaml` (test_fidelity_stub_gate).

    The test message names tests/fixtures/roundtrip/build_fixtures.py, which does
    not exist in this tree; the test's own extract command is used instead.
    """
    out = TMP / "setfam-extract"
    run([*GND, "extract", "tests/fixtures/checker/setfam.orm.yaml", "--out", str(out)])
    target = FIX / "roundtrip/artifacts"
    for path in sorted(target.iterdir()):
        fresh = (out / path.name).read_bytes()
        if path.name != "setfam.artifacts.json" and fresh != path.read_bytes():
            raise Stop(f"{rel(path)} moved; only setfam.artifacts.json may")
    committed = target / "setfam.artifacts.json"
    fresh = (out / committed.name).read_bytes()
    same_but_version_and_digests(committed.read_bytes(), fresh, rel(committed))
    write(committed, fresh)


def family_measurement_publication() -> None:
    """LIVE: `gnd measure` over the committed corpus, the test's exact command."""
    phase = FIX / "public-launch-phase-3/measurement"
    for pool in ("faker", "llm-proposed"):
        committed = phase / "measurements" / f"movie.{pool}.json"
        rerun = TMP / f"movie.{pool}.json"
        run([*GND, "measure", "tests/fixtures/public-launch-phase-2/model.orm.yaml", "--populations",
             rel(phase / "02-corpus/movie" / pool), "--format", "json", "--out", str(rerun)])
        same_but_version_and_digests(committed.read_bytes(), rerun.read_bytes(), rel(committed))
        write(committed, rerun.read_bytes())


def _replace_json_values(path: Path, changes: dict[str, str]) -> None:
    """Textual old-digest -> new-digest replacement, keeping the file's formatting."""
    text = path.read_text(encoding="utf-8")
    before = json.loads(text)
    for old, new in changes.items():
        if old != new and text.count(old) != 1:
            raise Stop(f"{rel(path)}: digest {old} occurs {text.count(old)} times, expected 1")
        text = text.replace(old, new)
    assert masked(json.dumps(before).encode()) == masked(json.dumps(json.loads(text)).encode())
    write(path, text.encode("utf-8"))


def family_ik1_baseline() -> None:
    """LIVE: the test's own `_capture(stem)` (rows 1 to 6); only rows 4 and 5 may move."""
    import test_object_type_description as t7

    path = FIX / "induced_knowledge/ik1-baseline.json"
    recorded = json.loads(path.read_text(encoding="utf-8"))["sha256"]
    changes: dict[str, str] = {}
    for stem in ("full_vocabulary", "library", "keywords", "v2_worked_example"):
        rows = t7._capture(stem)
        if rows.keys() != recorded[stem].keys():
            raise Stop(f"ik1 {stem}: row set changed")
        for row, value in rows.items():
            if value != recorded[stem][row]:
                if row not in ("4", "5"):
                    raise Stop(f"ik1 {stem} row {row} moved; only rows 4 and 5 carry the version")
                changes[recorded[stem][row]] = value
    _replace_json_values(path, changes)


def family_ik6_walk() -> None:
    """LIVE: the test's own `walk_digests`, under the test's two hash seeds."""
    import test_ik6_walk as ik6

    path = FIX / "induced_knowledge/ik6-walk/goldens.json"
    recorded = json.loads(path.read_text(encoding="utf-8"))["files"]
    runs = []
    for seed in ("0", "4242"):
        os.environ["PYTHONHASHSEED"] = seed
        try:
            runs.append(ik6.walk_digests(TMP / f"ik6-seed-{seed}"))
        finally:
            del os.environ["PYTHONHASHSEED"]
    if runs[0] != runs[1] or runs[0].keys() != recorded.keys():
        raise Stop("ik6: the two seeds disagree or the written-file set changed")
    may_move = {"measure.json", "discovered.json", "discover-report.json", "discovered.preview.json"}
    changes = {}
    for name, value in runs[0].items():
        if value != recorded[name]:
            if name not in may_move:
                raise Stop(f"ik6: {name} moved; it carries no version")
            changes[recorded[name]] = value
    _replace_json_values(path, changes)


def family_rf2_measure() -> None:
    """LIVE: tests/test_rf2_pre_move_pins.py in its GND_RF2_CAPTURE mode."""
    capture = TMP / "rf2-capture"
    run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--basetemp={TMP / 'rf2-pytest'}",
         "tests/test_rf2_pre_move_pins.py::test_measure_output_bytes"], env={"GND_RF2_CAPTURE": str(capture)})
    observed = json.loads((capture / "measure_output_bytes.json").read_text())
    path = FIX / "rf2-pins/measure-successor.json"
    text = path.read_text(encoding="utf-8")
    doc = json.loads(text)
    if observed["size_bytes"] != doc["after"]["size_bytes"]:
        raise Stop("rf2: the measure output size moved; a version of equal length cannot do that")
    sentence = f"; release {NEW}: the recorded gnd_version moves from {OLD} to {NEW} and nothing else"
    if doc["after"]["sha256"] != observed["sha256"]:
        assert text.count(doc["after"]["sha256"]) == 1
        text = text.replace(doc["after"]["sha256"], observed["sha256"])
    if not doc["reason"].endswith(sentence):
        old_reason = json.dumps(doc["reason"])
        assert text.count(old_reason) == 1
        text = text.replace(old_reason, json.dumps(doc["reason"] + sentence))
    after = json.loads(text)
    assert after["before"] == doc["before"] and after["after"] == observed
    write(path, text.encode("utf-8"))


def family_rf1_synth() -> None:
    """LIVE: tests/test_rf1_semantic_pins.py::test_synth in GND_RF1_CAPTURE mode (tests/support/rf1_pins.py).

    Captured under this interpreter only. The sem-synth goldens are plain
    (interpreter-independent) files, so no per-minor variant is involved; a moved
    golden that is interpreter-keyed stops the family.
    """
    capture = TMP / "rf1-capture" / f"py{sys.version_info.major}{sys.version_info.minor}"
    run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--basetemp={TMP / 'rf1-pytest'}",
         "tests/test_rf1_semantic_pins.py", "-k", "test_synth"], env={"GND_RF1_CAPTURE": str(capture)})
    goldens = FIX / "rf1-pins/goldens"
    manifest_path = FIX / "rf1-pins/goldens.sha256"
    manifest_before = manifest_path.read_bytes()
    manifest = manifest_before.decode("utf-8")
    captured = sorted((capture / "sem-synth").glob("*.json"))
    if len(captured) != len(list((goldens / "sem-synth").glob("*.json"))):
        raise Stop("rf1: captured sem-synth key set differs from the committed goldens")
    for fresh in captured:
        golden = goldens / "sem-synth" / fresh.name
        if not golden.is_file():
            raise Stop(f"rf1: no plain golden for sem-synth/{fresh.name}")
        old, new = golden.read_bytes(), fresh.read_bytes()
        if old == new:
            continue
        same_but_version_and_digests(old, new, rel(golden))
        line_old = f"{sha(old)}  sem-synth/{fresh.name}\n"
        if manifest.count(line_old) != 1:
            raise Stop(f"rf1: manifest line for sem-synth/{fresh.name} not found")
        manifest = manifest.replace(line_old, f"{sha(new)}  sem-synth/{fresh.name}\n")
        write(golden, new)
    write(manifest_path, manifest.encode("utf-8"))
    pin_literal("tests/test_rf1_pin_harness.py",
                {sha(manifest_before), sha(head(rel(manifest_path)))}, sha(manifest.encode("utf-8")))


def family_extract_controls() -> None:
    """LIVE: the five control commands of test_public_extract_controls, run in the unpacked workspace.

    The recorded stdout digests (which carry no version) must equal what this
    replay prints; that is the check that the replay matches the test's own run.
    """
    container = Container("public-extract-controls/workspace.json.gz")
    members = B64Members(container)
    root = (TMP / "xc-root").resolve()
    for name in members.members:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(members.get(name))
    key_name = "tests/fixtures/v51-extraction-boundary/answers/pre-phase-controls.json"
    text = members.get(key_name).decode("utf-8")
    controls = json.loads(text)
    rows = {row["id"]: row for row in controls["commands"]}
    scratch = (TMP / "xc-out").resolve()
    scratch.mkdir()
    changes: dict[str, str] = {}

    def tree(out: Path) -> dict[str, str]:
        return {p.relative_to(out).as_posix(): sha(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()}

    def tree_row(control_id: str, argv: list[str], out: Path) -> None:
        done = run([*GND, *argv, "--out", str(out)], cwd=root)
        row = rows[control_id]
        stdout = done.stdout.decode("utf-8").replace(str(scratch), "<tmp>")
        if sha(stdout.encode("utf-8")) != row["stdout_sha256"]:
            raise Stop(f"extract-controls {control_id}: stdout digest moved (stdout carries no version)")
        fresh = tree(out)
        if fresh.keys() != row["files"].keys():
            raise Stop(f"extract-controls {control_id}: file set moved")
        for name, value in fresh.items():
            if value != row["files"][name]:
                if not name.endswith(("artifacts.json", ".gnd-codegen.json")):
                    raise Stop(f"extract-controls {control_id}: {name} moved; it carries no version")
                changes[row["files"][name]] = value

    tree_row("full-vocabulary-extract", ["extract", "tests/fixtures/models/full_vocabulary.orm.yaml"], scratch / "full-vocabulary")
    tree_row("legacy-opaque-extract", ["extract", "tests/fixtures/phase3-consumers/legacy-derived.orm.yaml"], scratch / "legacy-extract")
    tree_row("legacy-opaque-codegen", ["codegen", "tests/fixtures/phase3-consumers/legacy-derived.orm.yaml"], scratch / "legacy-codegen")
    roundtrip = root / "tests/fixtures/roundtrip"
    for case in ("faithful", "hoover"):
        cases = scratch / f"{case}-cases"
        shutil.copytree(roundtrip / case, cases / case)
        done = run([*GND, "fidelity", str(root / "tests/fixtures/checker/setfam.orm.yaml"), "--cases", str(cases),
                    "--artifacts", str(roundtrip / "artifacts"), "--format", "json"], cwd=root)
        row = rows[f"setfam-{case}-fidelity"]
        changes[row["output_sha256"]] = sha(done.stdout)
    moved = {old: new for old, new in changes.items() if old != new}
    new_text = replace_digests(text, moved)
    if sum(text.count(old) for old in moved) not in (0, 6):
        raise Stop("extract-controls: expected the six recorded digests of the previous bump to move")
    members.put(key_name, new_text.encode("utf-8"))
    wire, _ = container.save()
    pin_literal("tests/test_public_extract_controls.py", container.old_wire_digests(), wire)


def family_bookrec(moved: dict[str, str]) -> None:
    """TRANSFORM: five documents in public-book-runtime, then the citation in public-book-skills."""
    container = Container("public-book-runtime/workspace.json.gz")
    members = B64Members(container)
    names = [
        "examples/bookrec/project/artifacts/model.artifacts.json",
        "examples/bookrec/project/.gnd-codegen.json",
        "examples/bookrec/evidence/conformance-post-eligibility-extension.json",
        "examples/bookrec/EXP-007-bookrec-layout-gate/candidate/project/artifacts/model.artifacts.json",
        "examples/bookrec/EXP-007-bookrec-layout-gate/candidate/project/.gnd-codegen.json",
    ]
    texts = {n: members.get(n).decode("utf-8", errors="replace") for n in members.members}
    transform_tree(members.get, members.put, names, moved)
    assert_no_stale(container, texts, moved, set(names))
    wire, _ = container.save()
    pin_literal("tests/test_public_book_runtime.py", container.old_wire_digests(), wire)

    skills = Container("public-book-skills/workspace.json.gz")
    smembers = B64Members(skills)
    walkthrough = "examples/bookrec/WALKTHROUGH.md"
    stexts = {n: smembers.get(n).decode("utf-8", errors="replace") for n in smembers.members}
    old = stexts[walkthrough]
    new = replace_digests(old, moved)
    cited = "[evidence/conformance-post-eligibility-extension.json](sha256:"
    if [a for a, b in zip(old.splitlines(), new.splitlines()) if a != b and not a.startswith(cited)]:
        raise Stop("book-skills: a line other than the conformance evidence citation moved")
    smembers.put(walkthrough, new.encode("utf-8"))
    assert_no_stale(skills, stexts, moved, {walkthrough})
    wire, _ = skills.save()
    pin_literal("tests/test_public_book_skills.py", skills.old_wire_digests(), wire)


def family_expense() -> None:
    """TRANSFORM: conformance/post-conversion.json only; baseline.json and post-evolution.json keep their old value."""
    container = Container("public-expense-current/workspace.json.gz")
    members = B64Members(container)
    name = "examples/expense-tracker/conformance/post-conversion.json"
    texts = {n: members.get(n).decode("utf-8", errors="replace") for n in members.members}
    local: dict[str, str] = {}
    transform_tree(members.get, members.put, [name], local)
    assert_no_stale(container, texts, local, {name})
    wire, _ = container.save()
    pin_literal("tests/test_public_expense_current.py", container.old_wire_digests(), wire)


def family_legacy_codegen() -> None:
    """TRANSFORM: two documents of the flat {path: text} closure; pyproject.toml's own "0.1.0" stays."""
    container = Container("public-legacy-codegen/closure.json.gz")
    doc = container.doc
    names = ["answers/legacy-codegen/artifacts/legacy-derived.artifacts.json", "answers/legacy-codegen/.gnd-codegen.json"]
    texts = dict(doc)
    old_raw = {sha(container.raw_before), sha(gzip.decompress(container.wire_head))}

    def put(name: str, data: bytes) -> None:
        same_but_version_and_digests(doc[name].encode("utf-8"), data, f"legacy-codegen::{name}")
        doc[name] = data.decode("utf-8")

    local: dict[str, str] = {}
    transform_tree(lambda n: doc[n].encode("utf-8"), put, names, local)
    assert_no_stale(container, texts, local, set(names))
    old_wire = container.old_wire_digests()
    wire, raw = container.save()
    # Two literals in this test: the payload digest first (it cannot collide with the container digest).
    pin_literal("tests/test_public_legacy_codegen_pins.py", old_raw, raw)
    pin_literal("tests/test_public_legacy_codegen_pins.py", old_wire, wire)


def family_coverage_goldens() -> None:
    """TRANSFORM: the three */expected.payload.json rows of the list-shaped corpus."""
    container = Container("public-coverage-goldens/corpus.json.gz")
    for entry in container.doc:
        if not entry["path"].endswith("/expected.payload.json"):
            continue
        old = entry["utf8"]
        assert sha(old.encode("utf-8")) == entry["sha256"] and len(old.encode("utf-8")) == entry["bytes"]
        new = bump(old, entry["path"])
        same_but_version_and_digests(old.encode("utf-8"), new.encode("utf-8"), entry["path"])
        entry["utf8"], entry["sha256"] = new, sha(new.encode("utf-8"))
    wire, _ = container.save()
    pin_literal("tests/test_public_coverage_goldens.py", container.old_wire_digests(), wire)


def family_measure_corpus() -> None:
    """TRANSFORM: measurements/full_vocabulary.faker.json; the corpus sidecars keep their recorded 0.1.0."""
    container = Container("public-measure-corpus/workspace.json.gz")
    member = container.doc["members"]["fixtures/measure/measurements/full_vocabulary.faker.json"]
    old = member["text"]
    assert sha(old.encode("utf-8")) == member["sha256"]
    new = bump(old, "full_vocabulary.faker.json")
    same_but_version_and_digests(old.encode("utf-8"), new.encode("utf-8"), "full_vocabulary.faker.json")
    member["text"], member["sha256"] = new, sha(new.encode("utf-8"))
    wire, _ = container.save()
    pin_literal("tests/test_public_measure_corpus.py", container.old_wire_digests(), wire)


def main() -> int:
    os.chdir(ROOT)
    version = run([*GND, "--version"]).stdout.decode().strip()
    if version != f"gnd {NEW}":
        raise SystemExit(f"installed gnd is {version!r}, expected 'gnd {NEW}'")
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    # Every temporary file of this run and of the commands it starts stays under _work/tmp.
    os.environ["TMPDIR"] = str(TMP)
    os.environ.pop("GND_RF1_CAPTURE", None)
    os.environ.pop("GND_RF2_CAPTURE", None)
    import tempfile

    tempfile.tempdir = str(TMP)
    sys.path.insert(0, str(ROOT / "tests"))
    moved: dict[str, str] = {}
    families = [
        ("roundtrip setfam artifacts", family_setfam_artifacts),
        ("measurement publication payloads", family_measurement_publication),
        ("ik1 baseline rows 4 and 5", family_ik1_baseline),
        ("ik6 walk goldens", family_ik6_walk),
        ("rf2 measure successor", family_rf2_measure),
        ("rf1 sem-synth goldens, manifest, manifest pin", family_rf1_synth),
        ("public-extract-controls", family_extract_controls),
        ("public-book-runtime and public-book-skills", lambda: family_bookrec(moved)),
        ("public-expense-current", family_expense),
        ("public-legacy-codegen", family_legacy_codegen),
        ("public-coverage-goldens", family_coverage_goldens),
        ("public-measure-corpus", family_measure_corpus),
    ]
    stopped = []
    for title, family in families:
        print(f"[{title}]")
        try:
            family()
        except Stop as error:
            stopped.append(title)
            print(f"  STOPPED: {error}")
    shutil.rmtree(TMP, ignore_errors=True)
    print("stopped families:", stopped or "none")
    return 1 if stopped else 0


if __name__ == "__main__":
    raise SystemExit(main())
