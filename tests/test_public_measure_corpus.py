"""Complete synthetic corpus guards for the current measure CLI."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

import pytest


def _workspace():
    fixture = Path(__file__).parent / "fixtures/public-measure-corpus/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    with fixture.open("rb") as stream:
        compressed = stream.read(128 * 1024 + 1)
    assert len(compressed) <= 128 * 1024
    assert hashlib.sha256(compressed).hexdigest() == "5a5c8fca86c1bfe23b7c77ce8a5b2914ed41b8fe3ad2a345419311096edf7d38"
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        expanded = stream.read(2 * 1024 * 1024 + 1)
    assert len(expanded) <= 2 * 1024 * 1024
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1 and len(payload["members"]) == 320
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-measure-corpus-")
    root = Path(holder.name).resolve()
    for value, member in payload["members"].items():
        relative = PurePosixPath(value)
        assert relative.parts and not relative.is_absolute() and ".." not in relative.parts
        assert relative.as_posix() == value
        data = member["text"].encode("utf-8")
        assert len(data) <= 128 * 1024
        assert hashlib.sha256(data).hexdigest() == member["sha256"]
        destination = root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        assert member["mode"] in {0o644, 0o755}
        destination.chmod(member["mode"])
    return holder, root


_HOLDER, REPO_ROOT = _workspace()
PHASE_DIR = REPO_ROOT / "fixtures" / "measure"
COMMITTED_CORPUS = PHASE_DIR / "02-corpus" / "full_vocabulary" / "faker"
MEASUREMENTS = PHASE_DIR / "measurements"
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"

pinning = pytest.mark.skipif(
    not COMMITTED_CORPUS.exists(),
    reason="the committed corpus is a phase artifact; absent in a source-only checkout",
)


def _measure(populations: Path, out: Path) -> subprocess.CompletedProcess[str]:
    """Run the published reproduction command FROM THE REPO ROOT.

    Running from the repo root is the whole point: that is the working directory
    in which the stored repo-root-relative paths used to resolve, so a run that
    still succeeds here is a run that ignored ``--populations``.
    """
    return subprocess.run(
        [
            sys.executable, "-m", "gnd", "measure",
            str(FULL_VOCAB.relative_to(REPO_ROOT)),
            "--populations", str(populations),
            "--format", "json", "--out", str(out),
        ],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=False,
    )


def _copy_corpus(destination: Path) -> Path:
    shutil.copytree(COMMITTED_CORPUS, destination)
    return destination


@pinning
def test_an_emptied_corpus_cannot_reproduce_the_committed_payload(tmp_path):
    """The reviewer's reproduction, as a gate.

    Copy the corpus, delete every population, keep ``index.json`` and the pool,
    then measure. Before CR-01 this exited 0 and wrote a payload whose sha256
    equalled the committed one exactly.
    """
    corpus = _copy_corpus(tmp_path / "corp")
    for path in corpus.rglob("*.json"):
        if path.name == "index.json" or path.name.endswith(".pool.json"):
            continue
        path.unlink()
    out = tmp_path / "m.json"

    result = _measure(corpus, out)

    assert result.returncode != 0, (
        "a corpus containing ZERO populations measured successfully — "
        "--populations was ignored and some other directory was read"
    )
    assert not out.exists() or out.read_bytes() != (
        MEASUREMENTS / "full_vocabulary.faker.json"
    ).read_bytes(), "an emptied corpus reproduced the committed payload byte-for-byte"
    assert "does not resolve" in (result.stdout + result.stderr)


@pinning
def test_one_missing_population_is_an_error_not_a_silent_narrowing(tmp_path):
    """An index entry with no file under the root is an INCOMPLETE corpus.

    Falling back to a copy elsewhere on disk (the old behaviour) or skipping the
    entry (the tempting alternative) both publish a rate over a denominator the
    reader cannot see.
    """
    corpus = _copy_corpus(tmp_path / "corp")
    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    # Located by basename so the receipt is about the RESOLVER, not about which
    # path convention the index happens to store.
    name = Path(index["populations"][0]["population"]).name
    next(corpus.rglob(name)).unlink()

    result = _measure(corpus, tmp_path / "m.json")

    assert result.returncode == 3, result.stdout + result.stderr
    assert name in (result.stdout + result.stderr)


@pinning
@pytest.mark.parametrize(
    "hostile",
    ["/etc/passwd", "../../../etc/passwd", "conforming/../../escape.json"],
    ids=["absolute", "parent-escape", "embedded-escape"],
)
def test_an_index_entry_that_escapes_the_corpus_root_is_refused(hostile, tmp_path):
    """``index.json`` is untrusted input; there was no containment check at all."""
    corpus = _copy_corpus(tmp_path / "corp")
    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    index["populations"][0]["population"] = hostile
    (corpus / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    result = _measure(corpus, tmp_path / "m.json")

    assert result.returncode == 3, result.stdout + result.stderr
    output = result.stdout + result.stderr
    assert any(phrase in output for phrase in ("escapes", "outside", "does not resolve")), output


@pinning
def test_resolution_ignores_the_working_directory_entirely(tmp_path):
    """The precise anti-CWD assertion, with a DECOY that would win the old race.

    Two trees carry the same relative layout: the real corpus under
    ``--populations``, and a decoy the process is run from whose populations have
    different bytes. The old resolver tried ``Path(stored)`` first, so the decoy
    would be measured and its digests published. The corpus digests must be the
    real corpus's.
    """
    corpus = _copy_corpus(tmp_path / "real")
    decoy = _copy_corpus(tmp_path / "decoy")
    for path in decoy.rglob("*.json"):
        if path.name == "index.json" or path.name.endswith(".meta.json"):
            continue
        # Different bytes, same structure — enough to move every digest.
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    out = tmp_path / "m.json"
    result = subprocess.run(
        [
            sys.executable, "-m", "gnd", "measure", str(FULL_VOCAB),
            "--populations", str(corpus),
            "--format", "json", "--out", str(out),
        ],
        capture_output=True, text=True, cwd=str(decoy), check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    committed = json.loads((MEASUREMENTS / "full_vocabulary.faker.json").read_text())
    assert [entry["sha256"] for entry in payload["corpus"]] == [
        entry["sha256"] for entry in committed["corpus"]
    ], "the decoy tree under the working directory was measured instead of --populations"


@pinning
def test_a_relocated_corpus_reproduces_the_committed_payload_byte_for_byte(tmp_path):
    """The containment rule must not make a corpus unmovable — and since F-05,
    moving one does not move a single byte of its payload.

    A whole-tree copy elsewhere on disk measures to the SAME BYTES as the
    committed payload, because every published path is corpus-root-relative.
    Before F-05 this test could only compare the numbers and the content
    digests: ``corpus[].path``, ``corpus[].sidecar_path`` and
    ``per_constraint[].evidence.population`` each recorded the path they were
    GIVEN, so 157 values in the payload were functions of where the tree
    happened to sit.
    """
    corpus = _copy_corpus(tmp_path / "elsewhere" / "corp")
    out = tmp_path / "m.json"

    result = _measure(corpus, out)

    assert result.returncode == 0, result.stdout + result.stderr
    committed = MEASUREMENTS / "full_vocabulary.faker.json"
    assert out.read_bytes() == committed.read_bytes(), (
        "a relocated corpus changed the payload — a published path is still a "
        "function of the invocation rather than of the corpus"
    )


@pinning
def test_the_payload_is_identical_under_an_absolute_and_a_relative_populations_arg(
    tmp_path,
):
    """F-05, stated as the receipt it protects.

    ``02-MEASUREMENT.md`` publishes a sha256 for each payload. Before this fix
    that receipt held for ONE invocation — the documented relative one from the
    repo root — and for no other: measuring the identical corpus through an
    absolute ``--populations`` produced a different digest, over 157 differing
    values, every one a path string and not one of them a number. A receipt that
    depends on how the corpus was spelled is not a receipt for the corpus.
    """
    corpus = _copy_corpus(tmp_path / "corp")
    relative_out = tmp_path / "relative.json"
    absolute_out = tmp_path / "absolute.json"

    import os

    relative = Path(os.path.relpath(corpus, REPO_ROOT))
    assert not relative.is_absolute()

    assert _measure(relative, relative_out).returncode == 0
    assert _measure(corpus.resolve(), absolute_out).returncode == 0

    assert relative_out.read_bytes() == absolute_out.read_bytes(), (
        "the payload still records the form of --populations, so its sha256 is "
        "conditional on the invocation"
    )


@pinning
def test_no_published_path_is_absolute(tmp_path):
    """The direct assertion, over every path-bearing field the payload has.

    Kept separate from the byte-comparison above because that one would also
    pass if BOTH runs baked in the same machine path.
    """
    corpus = _copy_corpus(tmp_path / "corp")
    out = tmp_path / "m.json"
    assert _measure(corpus.resolve(), out).returncode == 0
    payload = json.loads(out.read_text(encoding="utf-8"))

    published: list[str] = []
    for entry in payload["corpus"]:
        published += [entry["path"], entry["sidecar_path"]]
    for row in payload["per_constraint"]:
        if row.get("evidence"):
            published.append(row["evidence"]["population"])
    for defect in payload["checker_defects"]:
        published += [defect["population"], defect["sidecar"]]

    assert published, "nothing was checked — the payload carries no paths"
    offenders = [p for p in published if Path(p).is_absolute() or str(tmp_path) in p]
    assert not offenders, f"machine paths baked into the payload: {offenders[:3]}"
