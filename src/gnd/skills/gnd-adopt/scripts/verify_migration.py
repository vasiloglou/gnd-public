# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "ruamel.yaml==0.19.1",
#   "jsonschema==4.26.0",
# ]
# ///
"""Verify one GSD-to-GND migration record against the bytes it claims.

Bundled with the ``gnd-adopt`` skill and runnable anywhere ``uv`` is::

    uv run <skill-dir>/scripts/verify_migration.py \
        --migration model.migration.json \
        --model model.orm.yaml \
        --requirements .planning/REQUIREMENTS.md \
        --root .

The script never imports ``gnd`` -- it runs on machines where GND is not
installed. Its record shape has ONE home, ``../migration.schema.json``, which
this script enforces by LOADING, never by restating (D15).

Exit contract (0/1/3 -- these are this script's bands, NOT gnd's exit table):

* **0** -- every assertion holds. The model-element count is printed.
* **1** -- at least one assertion failed; each failure is one stdout line
  ``<assertion-id>: <cause>``, grouped in the declared assertion order, and
  the model-element count is still printed last.
* **3** -- the input was refused before the assertions could speak: bad argv,
  a missing file, a byte cap, a document that is not JSON, or a record the
  schema rejects.

Totality (section 0, rule 1): every read is bounded AT the read, the whole
run carries an aggregate byte budget, and the number of distinct documents is
itself capped -- a per-document cap would leave the input in control of how
many documents get read.

What a green exit does NOT establish: every assertion here is about FORM --
that an id was disposed exactly once, that an anchor's bytes are present,
that a named element exists at the named kind. None is about whether a
disposition is RIGHT. A requirement mapped to the wrong element passes every
check in this file; the owner's review of the full mapping table is the only
instrument against that, and it is a human one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

#: The declared assertion ids, in the order they are checked and reported.
#: This literal is load-bearing twice over: the corpus harness reads it by AST
#: to prove every declared assertion has a case that can red it, and failures
#: are printed grouped in THIS order, which is what pins the reporting order
#: by source (rule 3 -- two orderings that both reject are otherwise
#: indistinguishable from the exit code).
ASSERTIONS = ["A0", "A1", "A2a", "A2b", "A2c", "A3", "A3b", "A4", "A5", "A6"]

#: Per-document byte cap, applied to the READ, not after it.
CAP_BYTES = 10 * 1024 * 1024
#: Whole-run byte budget across every document opened.
AGGREGATE_CAP_BYTES = 32 * 1024 * 1024
#: Cap on the number of distinct documents a run may open. Without it, the
#: migration record controls how many files get read (panel finding P-12).
MAX_ARTIFACTS = 64

EXIT_OK = 0
EXIT_ASSERTION_FAILED = 1
EXIT_REFUSED = 3

#: The GSD checkbox grammar (owner ruling D3). The claim this grammar supports
#: is deliberately the narrow one: totality over the ids THIS grammar finds in
#: the ONE artifact named on argv -- never "totality" unqualified.
_ID_LINE = re.compile(r"^- \[([ x])\] \*\*([A-Z][A-Z0-9-]*)\*\*", re.MULTILINE)

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "migration.schema.json"


class Refusal(Exception):
    """Input refused before the assertions could speak (exit 3).

    ``resource`` marks cap/budget/containment refusals that must abort the
    whole run even when raised mid-assertion -- typed, never sniffed out of
    the message text.
    """

    def __init__(self, message: str, *, resource: bool = False) -> None:
        super().__init__(message)
        self.resource = resource


class _Budget:
    """Tracks the aggregate byte budget and the document count."""

    def __init__(self) -> None:
        self.bytes_read = 0
        self.documents = 0

    def charge_document(self) -> None:
        self.documents += 1
        if self.documents > MAX_ARTIFACTS:
            raise Refusal(
                f"A0: refused, more than {MAX_ARTIFACTS} distinct documents cited "
                f"(documents={self.documents}); the number of files a run "
                "opens is capped because the record controls it",
                resource=True,
            )

    def charge_bytes(self, count: int) -> None:
        self.bytes_read += count
        if self.bytes_read > AGGREGATE_CAP_BYTES:
            raise Refusal(
                f"A0: refused, aggregate read budget exceeded "
                f"(bytes_read={self.bytes_read}, cap={AGGREGATE_CAP_BYTES})",
                resource=True,
            )


def read_bounded_bytes(path: Path, *, budget: _Budget, cap: int = CAP_BYTES) -> bytes:
    """Read at most ``cap`` bytes; refuse if the file holds even one more.

    The cap is applied to the READ: at most ``cap + 1`` bytes are ever
    consumed, however large the file is, and the refusal reports the exact
    count so a cap applied after a whole-file read is observably different.
    """
    budget.charge_document()
    # The read is bounded by BOTH caps up front, so the run can never consume
    # past the aggregate budget on its final file (the overshoot the review
    # measured at ~42 MiB when the charge came after the read).
    remaining = AGGREGATE_CAP_BYTES - budget.bytes_read
    allowance = min(cap, max(remaining, 0))
    try:
        with path.open("rb") as handle:
            data = handle.read(allowance + 1)
    except OSError as error:
        raise Refusal(f"A0: refused, cannot read {path}: {error.strerror}") from error
    except ValueError as error:
        # A recorded path containing an escaped NUL passes the schema and
        # raises ValueError at open(), not OSError.
        raise Refusal(f"A0: refused, unreadable path {path!r}: {error}") from error
    budget.charge_bytes(len(data))
    if len(data) > cap:
        raise Refusal(
            f"A0: refused, {path} exceeds the per-document cap "
            f"(bytes_read={len(data)}, cap={cap})",
            resource=True,
        )
    return data


def _refuse_constant(name: str) -> Any:
    raise Refusal(f"A0: refused, {name} is not JSON (NaN/Infinity are rejected)")


def load_migration(path: Path, *, budget: _Budget) -> dict[str, Any]:
    """Parse and schema-validate the migration record. Total over bytes."""
    raw = read_bounded_bytes(path, budget=budget)
    try:
        document = json.loads(raw, parse_constant=_refuse_constant)
    except Refusal:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise Refusal(f"A0: refused, {path} is not JSON: {error}") from error
    except (ValueError, RecursionError) as error:
        # A very long integer literal raises ValueError; deep nesting raises
        # RecursionError. Neither is the exception an implementer reaches for
        # first, which is why rule 1 names them.
        raise Refusal(f"A0: refused, {path} is not parseable JSON: {error}") from error
    # The top-level shape is the schema's to refuse -- restating it here would
    # be a second home for one rule (review finding F8).

    import jsonschema

    try:
        schema = json.loads(read_bounded_bytes(_SCHEMA_PATH, budget=budget))
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, RecursionError) as error:
        raise Refusal(
            f"A0: refused, the bundled {_SCHEMA_PATH.name} is unreadable: {error}"
        ) from error
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        where = "/".join(str(part) for part in first.absolute_path) or "top level"
        raise Refusal(f"A0: refused, {path} fails migration.schema.json at {where}: {first.message}")
    return document


def declared_requirement_ids(artifact_bytes: bytes) -> list[tuple[str, bool]]:
    """Every ``(id, closed)`` pair the checkbox grammar finds, in order."""
    text = artifact_bytes.decode("utf-8", errors="replace")
    return [(m.group(2), m.group(1) == "x") for m in _ID_LINE.finditer(text)]


def _load_model_surface(model_bytes: bytes, path: Path) -> dict[str, Any]:
    """The element surface A5 resolves against. Total over hostile bytes."""
    from ruamel.yaml import YAML
    from ruamel.yaml.error import YAMLError

    try:
        loaded = YAML(typ="safe").load(model_bytes.decode("utf-8", errors="replace"))
    except (YAMLError, ValueError, RecursionError) as error:
        raise Refusal(f"A0: refused, {path} is not parseable YAML: {error}") from error
    if not isinstance(loaded, dict):
        raise Refusal(f"A0: refused, {path} must hold a YAML mapping at the top level")

    def _ids(section: str) -> set[str]:
        entries = loaded.get(section) or []
        found: set[str] = set()
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                    found.add(entry["id"])
        return found

    constraint_ids: set[str] = set()
    constraint_counts: dict[str, int] = {}
    fact_types = loaded.get("fact_types") or []
    if isinstance(fact_types, list):
        for entry in fact_types:
            if not isinstance(entry, dict):
                continue
            constraints = entry.get("constraints") or []
            if isinstance(entry.get("id"), str) and isinstance(constraints, list):
                real = [c for c in constraints if isinstance(c, dict)]
                constraint_counts[entry["id"]] = len(real)
                constraints = real
                for constraint in constraints:
                    if isinstance(constraint, dict) and isinstance(constraint.get("id"), str):
                        constraint_ids.add(constraint["id"])
    return {
        "object_type": _ids("object_types"),
        "fact_type": _ids("fact_types"),
        "operation": _ids("operations"),
        "constraint": constraint_ids,
        "constraint_counts": constraint_counts,
    }


def _contained(root: Path, recorded: str, *, label: str) -> Path:
    """Resolve a RECORDED path and refuse any escape from --root.

    Three escape vectors, all reproduced before this function existed: an
    absolute path (``root / "/etc/hosts"`` IS ``/etc/hosts`` under pathlib),
    a ``..`` segment, and an in-root symlink pointing outside. ``resolve()``
    follows symlinks, so ``relative_to`` catches all three. A recorded path
    is untrusted data and never widens what the run may read (the skill's
    quoted-data posture, as a check rather than a sentence).
    """
    candidate = Path(recorded)
    if candidate.is_absolute():
        raise Refusal(
            f"A0: refused, {label} {recorded!r} is absolute; recorded paths "
            "are root-relative data and never select files outside --root",
            resource=True,
        )
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise Refusal(
            f"A0: refused, {label} {recorded!r} escapes --root after "
            "resolution; a hostile record does not choose what gets read",
            resource=True,
        ) from None
    return resolved


def _relative(root: Path, value: Path, *, label: str) -> str:
    try:
        return value.resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise Refusal(f"A0: refused, {label} {value} is not under --root {root}") from error


def verify(
    migration: dict[str, Any],
    *,
    root: Path,
    requirements_rel: str,
    budget: _Budget,
) -> tuple[list[tuple[str, str]], int]:
    """Run assertions A1..A6. Returns (failures, model_element_count).

    Failures are ``(assertion_id, cause)`` pairs; the caller prints them
    grouped in ``ASSERTIONS`` order. All assertions run -- the first failure
    does not silence the rest.
    """
    failures: list[tuple[str, str]] = []

    def fail(assertion: str, cause: str) -> None:
        failures.append((assertion, cause))

    # --- A1: every digest the record carries replays -- roots AND model ---
    root_bytes: dict[str, bytes] = {}
    digest_entries = [(entry["path"], entry["sha256"]) for entry in migration["roots"]]
    digest_entries.append((migration["model"]["path"], migration["model"]["sha256"]))
    for rel_path, recorded in digest_entries:
        target = _contained(root, rel_path, label="recorded path")
        try:
            data = read_bounded_bytes(target, budget=budget)
        except Refusal as refusal:
            if refusal.resource:
                raise
            fail("A1", f"{rel_path} could not be read: {refusal}")
            continue
        root_bytes[rel_path] = data
        actual = hashlib.sha256(data).hexdigest()
        if actual != recorded:
            fail("A1", f"{rel_path} digest mismatch: recorded {recorded[:12]}..., bytes are {actual[:12]}...")

    pinned = {entry["path"] for entry in migration["roots"]}

    # --- A2a: every document the run reads for evidence is a pinned root ---
    if requirements_rel not in pinned:
        fail("A2a", f"the requirements document {requirements_rel} is not among the pinned roots; totality would be measured against bytes nothing vouched for")
    for row in migration["mapping"]:
        if row["artifact"] not in pinned:
            fail("A2a", f"{row['id']}: artifact {row['artifact']} is not among the pinned roots")

    # --- A2b: anchors are present and non-blank ---
    for row in migration["mapping"]:
        if not row["anchor"].strip():
            fail("A2b", f"{row['id']}: anchor is empty or whitespace; an empty anchor is a substring of every document, so it verifies nothing")

    # --- A2c: anchors occur verbatim in their artifact's bytes ---
    for row in migration["mapping"]:
        anchor = row["anchor"]
        if not anchor.strip():
            continue  # already an A2b failure; do not double-report
        if row["artifact"] not in pinned:
            continue  # unpinned artifact is A2a's finding; the gate is already red
        data = root_bytes.get(row["artifact"])
        if data is None:
            continue  # unreadable root is A1's finding
        try:
            needle = anchor.encode("utf-8")
        except UnicodeEncodeError:
            # An escaped lone surrogate passes the JSON string schema and
            # cannot be UTF-8 encoded -- so it certainly does not occur in
            # the artifact's bytes. A finding, never a traceback.
            fail("A2c", f"{row['id']}: anchor is not UTF-8 encodable and cannot occur in {row['artifact']}")
            continue
        if needle not in data:
            fail("A2c", f"{row['id']}: anchor not found verbatim in {row['artifact']}: {anchor[:60]!r}")

    # --- A3: totality over the ids the declared grammar finds ---
    requirements_data = root_bytes.get(requirements_rel)
    if requirements_data is None:
        requirements_data = read_bounded_bytes(root / requirements_rel, budget=budget)
    declared = declared_requirement_ids(requirements_data)
    declared_ids = [identifier for identifier, _ in declared]
    checkbox_state = dict(declared)
    row_counts: dict[str, int] = {}
    for row in migration["mapping"]:
        row_counts[row["id"]] = row_counts.get(row["id"], 0) + 1
    for identifier in declared_ids:
        count = row_counts.get(identifier, 0)
        if count == 0:
            fail("A3", f"{identifier} is declared in {requirements_rel} and has no disposition")
        elif count > 1:
            fail("A3", f"{identifier} is disposed {count} times; exactly one disposition per id")
    for identifier in row_counts:
        if identifier not in checkbox_state:
            fail("A3", f"{identifier} has a disposition but the declared grammar finds no such id in {requirements_rel}")

    # --- A3b: the closed flag agrees with the document's own checkbox ---
    for row in migration["mapping"]:
        state = checkbox_state.get(row["id"])
        if state is not None and row["closed"] != state:
            fail("A3b", f"{row['id']}: the record says closed={row['closed']} but the document's checkbox says closed={state}; the record does not get to certify its own completions")

    # --- A4: an unclosed id is never history ---
    for row in migration["mapping"]:
        # A4 judges the record's own closed flag; whether that flag TELLS THE
        # TRUTH is A3b's finding. Splitting them keeps c19 (a lie) an A3b
        # case and c10 (an honest unclosed history) an A4 case, instead of
        # one row double-reporting through both.
        if row["disposition"] == "history" and not row["closed"]:
            fail("A4", f"{row['id']}: an unclosed requirement may not be filed as history")

    # --- A5: every model-element reference resolves at the named kind ---
    model_rel = migration["model"]["path"]
    model_data = root_bytes.get(model_rel)
    surface = _load_model_surface(model_data, root / model_rel) if model_data is not None else None
    model_element_rows = 0
    for row in migration["mapping"]:
        if row["disposition"] != "model-element":
            continue
        model_element_rows += 1
        elements = row.get("model_elements") or []
        if not elements:
            fail("A5", f"{row['id']}: a model-element disposition with no model_elements is a claim with a zero-length body")
            continue
        if surface is None:
            continue  # the model failed A1; its digest failure is already reported
        for ref in elements:
            if "index" in ref:
                fact_type = ref["fact_type"]
                count = surface["constraint_counts"].get(fact_type)
                if count is None:
                    fail("A5", f"{row['id']}: positional constraint reference names fact type {fact_type}, which the model does not declare")
                elif ref["index"] >= count:
                    fail("A5", f"{row['id']}: {fact_type} has {count} constraints; index {ref['index']} is out of range")
                continue
            kind, identifier = ref["kind"], ref["id"]
            if identifier in surface[kind]:
                continue
            actual_kinds = [
                other for other in ("object_type", "fact_type", "operation", "constraint")
                if other != kind and identifier in surface[other]
            ]
            if actual_kinds:
                fail("A5", f"{row['id']}: {identifier} is an {actual_kinds[0]}, not a {kind}")
            else:
                fail("A5", f"{row['id']}: no {kind} named {identifier} exists in the model")

    # --- A6: the migration carried something, and says how much ---
    if model_element_rows == 0:
        fail("A6", "no requirement landed in the model (model-elements: 0); a migration that carried nothing may not present itself as a completed migration")

    return failures, model_element_rows


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a GSD-to-GND migration record against the bytes it claims.",
    )
    parser.add_argument("--migration", required=True, help="path to model.migration.json")
    parser.add_argument("--model", required=True, help="path to the published model.orm.yaml")
    parser.add_argument(
        "--requirements", required=True,
        help="the GSD requirements document the id census is measured against; "
        "this argv path is authoritative and nothing in the record can redirect it",
    )
    parser.add_argument("--root", required=True, help="repository root every recorded path is relative to")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return EXIT_REFUSED if error.code not in (0, None) else EXIT_OK

    budget = _Budget()
    try:
        root = Path(args.root).resolve()
        if not root.is_dir():
            raise Refusal(f"A0: refused, --root {args.root} is not a directory")
        migration = load_migration(Path(args.migration), budget=budget)
        requirements_rel = _relative(root, Path(args.requirements), label="--requirements")
        model_rel = _relative(root, Path(args.model), label="--model")
        if migration["model"]["path"] != model_rel:
            raise Refusal(
                f"A0: refused, the record's model.path is {migration['model']['path']} "
                f"but --model resolves to {model_rel}; the record and the argv "
                "must agree on which model is being verified"
            )
        failures, count = verify(
            migration, root=root, requirements_rel=requirements_rel, budget=budget
        )
    except Refusal as refusal:
        print(str(refusal), file=sys.stderr)
        return EXIT_REFUSED
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        # Totality backstop, never a traceback. ValueError covers NUL-bearing
        # paths; UnicodeError covers surrogate-bearing strings on paths this
        # module did not anticipate.
        print(f"A0: refused, {error}", file=sys.stderr)
        return EXIT_REFUSED

    order = {assertion: position for position, assertion in enumerate(ASSERTIONS)}
    for assertion, cause in sorted(failures, key=lambda pair: order[pair[0]]):
        # One failure is exactly one line. Ids, paths and anchors are hostile
        # data; a newline smuggled through them would let a record forge a
        # second assertion line, so the whole cause is flattened here -- the
        # single choke point every failure passes through.
        flat = cause.replace("\r", " ").replace("\n", " ")
        print(f"{assertion}: {flat}")
    print(f"model-elements: {count}")
    return EXIT_ASSERTION_FAILED if failures else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
