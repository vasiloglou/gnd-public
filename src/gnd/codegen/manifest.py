"""The codegen manifest: GND's third digest-bound record, and the first with a
real WRITER.

``gnd install`` has a receipt (``install.py``) and the extraction lane has a
document manifest plus a sidecar (``extract/manifest.py``). Codegen needs a
third, and it is the one that unblocks plan 05: conformance assertion #1
(integrity — every derived file matches its recorded digest) and assertion #2
(currency — the recorded model digest equals the model's current digest) both
READ this file. Without a writer they have nothing to check.

**The writer is the half that did not exist.** RESEARCH §1.3 item 6 found the
``artifacts.json`` writer and its recorded-vs-actual digest loop INLINE in
``cli.py:829-877`` — not as reusable functions — so codegen would otherwise have
been their third hand-written copy.

**And this module deliberately does NOT refactor ``cli.py``'s extraction bundle
index to share its schema.** That looks like the obvious deduplication and it is
the wrong one: the two records answer different questions. The extraction bundle
index binds four artifacts to one model for a CONSUMER that re-derives them
(``gnd verify``), carries a ``header_template``, and has no ownership axis at
all, because everything in it is code-emitted by construction. This manifest
binds a whole PROJECT TREE whose files are split between code-emitted and
user-owned, and the ownership axis is the entire point — it is what lets
regeneration rewrite one file and refuse to touch its neighbour. Merging them
would widen one contract to serve two claims, and a contract that serves two
claims is checked against neither. The duplication is a stated choice; what is
NOT duplicated is the naming and header convention the two bundles share, which
plan 03-04 gave a single owner in :mod:`gnd.extract.bundle`.

**The blind spot, stated rather than implied (RESEARCH §2.5).** A manifest
cannot record its own digest. So assertion #1 detects a UNILATERAL edit to a
derived file, and does not detect a CO-EDIT of that file together with its
manifest entry. ``gnd doctor`` carries the identical bound, and the extraction
bundle index does too — its ``artifacts`` map does not include itself
(``cli.py:968-976``). This is an integrity bound, not tamper evidence, and it is
published as DATA in :data:`INTEGRITY_LIMITS` so plan 05's conformance payload
can carry it into the result rather than leaving it in prose one skim away from
not existing.

**Path safety is applied at READ time, and it is the LEXICAL half only.** The
manifest is untrusted committed metadata whose entries are paths: it crosses
machines in git, and nothing about "we wrote it ourselves last time" survives
that. Every ``relpath`` is refused when it is empty, absolute under POSIX **or**
Windows rules, drive-lettered, or carries a ``..`` component — reusing
:func:`gnd.extract.manifest.manifest_path_issue`, so a future correction to those
rules cannot land in one lane and miss this one (T-03-18). A relpath that passes
those checks is contained by construction unless a component is a symlink.

**Symlinks are deliberately NOT a read-time refusal, and that is the shipped
rule rather than a relaxation of it.** ``install.safe_destination`` states it
outright: *"Gates every write and every delete; never a read. […] A symlink
standing AT a destination is a classification verdict (``collided``), not a path
error."* Measured during this plan: applying
:func:`~gnd.extract.manifest.resolve_manifest_relative_path` here made a single
symlink planted at one derived path refuse the WHOLE manifest at band 3, so a
planted link became a denial of regeneration for every other file in the project
— a strictly worse outcome than the per-file refusal at band 11 the classifier
already produces. The filesystem half therefore lives where it can act on one
file: :func:`gnd.codegen.plan.classify_file` opens with ``lstat`` and follows no
link (T-03-20), and every WRITE routes through ``synth.paths.safe_output_path``
— i.e. ``install.safe_destination`` — which refuses a symlinked ancestor and a
containment escape at the moment it matters.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationError,
)

from gnd.extract.manifest import manifest_path_issue

__all__ = [
    "CODEGEN_MANIFEST_VERSION",
    "INTEGRITY_LIMITS",
    "MANIFEST_FILENAME",
    "MAX_CODEGEN_MANIFEST_BYTES",
    "CodegenManifest",
    "CodegenManifestError",
    "ManagedFile",
    "ManifestModelRef",
    "Ownership",
    "build_manifest",
    "digest_text",
    "manifest_path",
    "read_manifest",
    "read_manifest_bytes",
    "render_manifest",
    "write_manifest",
]

#: Bumped when a field's MEANING changes, never for an additive field with a
#: safe default. A manifest declaring a HIGHER version is reported and refused,
#: never guessed at (``install.py``'s ``MANIFEST_SCHEMA`` posture): regeneration
#: driven by a misinterpreted document rewrites real files. Published as a
#: module constant with this rule attached, following ``fidelity/report.py:64``.
CODEGEN_MANIFEST_VERSION = 1

#: The manifest's name at the generated project's ROOT. Leading dot, mirroring
#: ``install.MANIFEST_NAME`` (``.gnd-install.json``), so the two records read as
#: siblings. It is never one of the project's own managed relpaths and is never
#: classified — it is codegen metadata, not a generated artifact.
MANIFEST_FILENAME = ".gnd-codegen.json"

#: Byte cap on a manifest read, applied BEFORE the parse. A nine-file project's
#: manifest is about 1 KB, so 1 MB is roughly a thousand times headroom — wide
#: enough that no legitimate project approaches it and narrow enough that a
#: hostile 10 GB "manifest" is refused rather than slurped (the
#: ``MAX_MANIFEST_BYTES`` posture, T-03-21).
MAX_CODEGEN_MANIFEST_BYTES = 1 * 1024 * 1024

#: The file-ownership vocabulary, as module-level DATA (G-04/G-05).
#:
#: ``derived`` means CODE-EMITTED and therefore digest-gated. ``extension``
#: means anything a human or an LLM authored, and it is never digest-gated —
#: not by leniency but because an LLM-authored file is not byte-reproducible, so
#: a digest over it would false-fail on every regeneration or be quietly dropped
#: and weaken the gate over exactly the files nobody is watching. Recording an
#: extension file here is how regeneration knows to LEAVE IT ALONE; the
#: ``sha256`` on such an entry is a record of what was placed, never a gate.
Ownership = Literal["derived", "extension"]

#: The integrity bounds this record cannot close, published as DATA so plan 05's
#: conformance payload carries them into the result (G-08's posture, applied one
#: plan early). A limitation that lives only in a docstring is one skim away
#: from not existing.
INTEGRITY_LIMITS: tuple[str, ...] = (
    (
        "a manifest cannot record its own digest, so an edit to a derived file "
        "that is CO-EDITED with its manifest entry is undetectable by digest "
        "comparison; this is an integrity bound, not tamper evidence (gnd "
        "doctor has the identical limit)"
    ),
    (
        "extension files are recorded but never digest-gated, because LLM- and "
        "human-authored text is not byte-reproducible (G-05); their recorded "
        "sha256 says what was placed and never what must still be there"
    ),
    (
        "a green digest comparison says the derived surface is unedited and "
        "current, never that the generated code is correct (G-08)"
    ),
)

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256String = Annotated[
    str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9a-f]{64}$")
]

#: Every ``relpath`` refusal carries this rule id, so plan 05 maps a refusal
#: into its payload without re-deriving the message.
MANIFEST_RULE_ID = "codegen:manifest-invalid"


class CodegenManifestError(Exception):
    """The manifest failed to read, parse, validate, or named an unsafe path.

    Loud by design and fail-closed: a silently-skipped manifest would make
    regeneration treat an existing managed project as unmanaged, which is the
    exact state where every derived path classifies as a collision.
    """


class ManifestModelRef(BaseModel):
    """The model this project was generated from, bound by digest.

    ``path`` is provenance for a human reading the file; ``sha256`` is the
    IDENTITY, and it is what assertion #2 (currency) compares against the
    model's current bytes.
    """

    model_config = ConfigDict(extra="forbid")

    path: NonEmptyString
    sha256: Sha256String


class ManagedFile(BaseModel):
    """One file codegen placed: where it is, what it hashed to, who owns it."""

    model_config = ConfigDict(extra="forbid")

    relpath: NonEmptyString
    sha256: Sha256String
    ownership: Ownership


class CodegenManifest(BaseModel):
    """The whole record. Closed (``extra="forbid"``) at every level, so a
    swapped-format or schema-drifted document can never read as valid."""

    model_config = ConfigDict(extra="forbid")

    manifest_version: Literal[1]
    gnd_version: NonEmptyString
    model: ManifestModelRef
    files: list[ManagedFile]

    def entries(self) -> dict[str, ManagedFile]:
        """``{relpath: entry}`` — the classifier's lookup."""
        return {entry.relpath: entry for entry in self.files}


def digest_text(text: str) -> str:
    """Content identity by BYTES, over the UTF-8 encoding the emitter writes.

    The only identity that survives a copy: mtime is not preserved by copying
    and lies after a ``git checkout``, and size alone cannot tell an edit from a
    replacement.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def manifest_path(root: str | Path) -> Path:
    """``<project root>/.gnd-codegen.json``."""
    return Path(root) / MANIFEST_FILENAME


def build_manifest(
    project: Any,
    model_path: str,
    *,
    entries: Iterable[ManagedFile] | None = None,
) -> CodegenManifest:
    """The manifest for ``project``, or for an explicit ``entries`` list.

    ``entries`` is how :func:`gnd.codegen.plan.apply_codegen` records a run that
    did not write everything: a file whose write was REFUSED keeps its previous
    entry rather than adopting its current bytes. Recording the current bytes of
    a hand-edited derived file would make the next run classify it ``stale`` and
    silently rewrite it — the very destruction the refusal existed to prevent.
    """
    from gnd import resolve_version

    if entries is None:
        entries = [
            ManagedFile(
                relpath=file.relpath,
                sha256=digest_text(file.text),
                ownership=file.ownership,
            )
            for file in project.files
        ]
    return CodegenManifest(
        manifest_version=CODEGEN_MANIFEST_VERSION,
        gnd_version=resolve_version(),
        model=ManifestModelRef(
            path=Path(model_path).as_posix(),
            sha256=hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        ),
        files=sorted(entries, key=lambda entry: entry.relpath),
    )


def render_manifest(manifest: CodegenManifest) -> str:
    """The manifest's canonical BYTES.

    Sorted keys, sorted ``files``, ``allow_nan=False``, trailing newline — the
    ``_cmd_extract`` byte-determinism discipline. This is what makes G-06's
    "a second run leaves identical hashes" a statement about bytes rather than
    about intent, and it is why the idempotence test can compare two runs'
    manifests directly.
    """
    payload = manifest.model_dump(mode="json")
    payload["files"] = sorted(payload["files"], key=lambda entry: entry["relpath"])
    return (
        json.dumps(
            payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False
        )
        + "\n"
    )


def write_manifest(root: str | Path, manifest: CodegenManifest) -> Path:
    """Write the manifest at ``root``, atomically, and return its path.

    Callers write this LAST — after every artifact has landed — mirroring
    ``_cmd_extract``'s load-bearing index-last ordering, so a crashed run never
    leaves a manifest describing files that do not exist.
    """
    from gnd.safefs import atomic_write as _atomic_write
    from gnd.safefs import safe_destination

    root_path = Path(root)
    destination = safe_destination(root_path, MANIFEST_FILENAME)
    _atomic_write(
        root_path,
        MANIFEST_FILENAME,
        render_manifest(manifest).encode("utf-8"),
    )
    return destination


def _refuse(message: str) -> CodegenManifestError:
    return CodegenManifestError(message)


def _read_document(path: Path) -> Any:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise _refuse(f"{path} could not be read: {error}") from error
    if size > MAX_CODEGEN_MANIFEST_BYTES:
        raise _refuse(
            f"{path} is {size} bytes, over the {MAX_CODEGEN_MANIFEST_BYTES}-byte "
            f"cap for an untrusted codegen manifest (T-03-21)"
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _refuse(f"{path} is not parseable JSON: {error}") from error


def _validate_document(document: Any, source: str) -> CodegenManifest:
    """Validate one already-parsed manifest document from ``source``."""
    file_path = source

    if isinstance(document, dict):
        declared = document.get("manifest_version")
        if isinstance(declared, int) and declared > CODEGEN_MANIFEST_VERSION:
            raise _refuse(
                f"{file_path} declares manifest_version {declared}, newer than "
                f"the {CODEGEN_MANIFEST_VERSION} this gnd understands; it is "
                f"refused rather than guessed at, because regeneration driven "
                f"by a misinterpreted record rewrites real files"
            )

    try:
        manifest = CodegenManifest.model_validate(document)
    except ValidationError as error:
        raise _refuse(f"{file_path} is not a valid CodegenManifest:\n{error}") from error

    seen: set[str] = set()
    for entry in manifest.files:
        issue = manifest_path_issue("relpath", entry.relpath, MANIFEST_RULE_ID)
        if issue is not None:
            raise _refuse(f"{file_path} names an unsafe path: {issue.message}")
        if entry.relpath == MANIFEST_FILENAME:
            raise _refuse(
                f"{file_path} records itself as a managed file; a manifest "
                f"cannot record its own digest, so an entry claiming otherwise "
                f"is malformed (see INTEGRITY_LIMITS)"
            )
        if entry.relpath in seen:
            raise _refuse(
                f"{file_path} records {entry.relpath!r} twice; two entries for "
                f"one path make the classifier's answer depend on iteration order"
            )
        seen.add(entry.relpath)
    return manifest


def read_manifest_bytes(data: bytes, *, source: str) -> CodegenManifest:
    """Load strict manifest bytes already read through a bound descriptor."""
    if len(data) > MAX_CODEGEN_MANIFEST_BYTES:
        raise _refuse(
            f"{source} is {len(data)} bytes, over the {MAX_CODEGEN_MANIFEST_BYTES}-byte "
            "cap for an untrusted codegen manifest (T-03-21)"
        )
    try:
        document = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _refuse(f"{source} is not parseable JSON: {error}") from error
    return _validate_document(document, source)


def read_manifest(path: str | Path) -> CodegenManifest:
    """Load a manifest strictly, or raise :class:`CodegenManifestError`.

    Order matters and is the same order ``extract/manifest.py::_load`` uses:
    byte cap, parse, closed-schema validation, THEN path safety. Every step
    before the last is what keeps the last one from operating on a document
    whose shape it cannot trust.

    Every refusal names the offending value. A message that named only the
    manifest would leave a mutation check unable to tell a test that reds for
    the right reason from one that reds for any reason.
    """
    file_path = Path(path)
    manifest = _validate_document(_read_document(file_path), str(file_path))

    # ``model.path`` is deliberately NOT path-checked, and that is the shipped
    # precedent rather than an omission: ``ExtractionSidecar.model`` carries the
    # same comment — "an opaque reference string; never dereferenced" — and is
    # likewise absent from its module's path-field tuple. Nothing ever OPENS the
    # model through this field; codegen reads the model the caller named on
    # argv, and plan 05's currency assertion compares DIGESTS. The model also
    # legitimately lives outside the generated project, so a containment walk
    # would be wrong here in a way it is never wrong for ``relpath``. An
    # absolute path recorded here was measured during this plan: refusing it
    # made `gnd codegen /abs/path/model.orm.yaml` write a manifest its own
    # reader rejected — a fail-closed loop over a legitimate invocation.
    return manifest
