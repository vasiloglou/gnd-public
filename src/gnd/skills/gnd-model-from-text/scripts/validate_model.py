# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema==4.26.0",
#   "ruamel.yaml==0.19.1",
# ]
# ///
"""Portable structural validator for GND model.orm.yaml files.

A zero-install **fallback** for environments where the ``gnd`` console script is
not available. It is not an equivalent of ``gnd validate`` and must never be
described as one — see the limits below. Resolve ``<skill-dir>`` to this skill's
own directory and run::

    uv run <skill-dir>/scripts/validate_model.py model.orm.yaml [--schema PATH]

What it DOES: parses the model with a safe YAML loader and validates its
structure against the canonical GND ORM meta-schema (JSON Schema Draft
2020-12). That is layer-1 structural validation, and it is the whole of it.

What it CANNOT check — install the distribution and use ``gnd validate`` /
``gnd check`` for any of these:

1. **Layer-2 semantic model rules** — identifier integrity, cross-reference
   resolution, roles naming undeclared object types, and the modality-policy
   warnings. A model this script calls valid can still fail ``gnd validate``.
2. **Population checking of any kind** — it validates models only. There is no
   code path here that reads a population document.
3. **Model-relative population validation** — the checks that exist only when a
   population is read against the model it claims to describe (coverage
   claims, per-constraint verdicts, deontic vs alethic resolution).
4. **Exit band 4, indeterminate** — it has no notion of an alethic constraint
   the checker never evaluated, so it can never report "could not decide". Its
   silence on that band is an absence of machinery, not a verdict of pass.
5. **``--format json``** — there is no machine-readable report payload. Output
   is human-readable lines only, so no eval harness can consume it structurally.
6. **``acceptance_ready``** — it never emits the acceptance flag, so nothing
   automated can read acceptance from this script's output.

Exit codes:
    0  — model is structurally valid
    1  — validation errors (printed as "ERROR at <json_path>: <message>")
    64 — EX_USAGE: malformed invocation (a missing, unknown or invalid argument)
    65 — EX_DATAERR: the model or the meta-schema could not be read or parsed
    66 — EX_NOINPUT: the meta-schema file was not found

**Only 0 and 1 are verdicts.** Everything else is deliberately OUTSIDE the
normative gnd band contract (0/1/2/3/4), and for one reason: a consumer keying
on the bands cannot tell a verdict from a mishap. Returning 2 for a usage error
would masquerade as "vacuous population"; returning 1 for a missing model file
or unparseable YAML would masquerade as "your model violates an alethic
constraint", sending the caller to inspect a document that was never read.
64/65/66 are sysexits.h values and are disjoint from the whole allocated
vocabulary: the verdict bands 0-4, the reserved headroom 5-9, the lifecycle
codes 10/11/12, EX_USAGE 64 and EX_SOFTWARE 70 in ``gnd.cli``, and EX_IOERR 74.

argparse's own default for a usage error is ``SystemExit(2)``, which no amount
of returning named constants from ``main()`` can prevent — hence the band-safe
parser below, the same shape ``gnd.cli`` uses. ``tests/test_review_fixes.py``
asserts these codes by RUNNING the script; a source grep for a returned literal
cannot observe an exception argparse raises (CR-03).

Threat note: the model document is parsed with ruamel's safe loader and only
ever validated against the schema — no string from the document is evaluated,
interpolated, or executed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ruamel.yaml.events import AliasEvent

#: EX_NOINPUT from sysexits.h. The schema-missing case must stay OUT of the
#: 0-4 verdict bands: 2 means "vacuous population", and a consumer keying on
#: the bands cannot tell a missing file from a verdict if this returns it.
EX_NOINPUT = 66

#: EX_USAGE from sysexits.h, the same value ``gnd.cli`` uses for the same
#: reason. argparse's default is ``SystemExit(2)`` — "vacuous population".
EX_USAGE = 64

#: EX_DATAERR from sysexits.h: the model or the meta-schema could not be read
#: or parsed AT ALL. Distinct from 1, which means the document was read and
#: found invalid. Reporting an unreadable file as a validation failure sends
#: the caller to inspect content that was never loaded.
EX_DATAERR = 65

# Same parser-event budget as gnd.model. Kept local so this PEP 723 fallback
# remains runnable without importing (or installing) the gnd package.
MAX_YAML_EVENTS = 1_000_000


def yaml_stream_guard_error(path: str | Path) -> str | None:
    """Reject aliases and event streams that can amplify before node loading."""
    yaml = YAML(typ="safe")
    with open(path, encoding="utf-8") as handle:
        for count, event in enumerate(yaml.parse(handle), start=1):
            if count > MAX_YAML_EVENTS:
                return (
                    f"YAML document '{path}' exceeds the {MAX_YAML_EVENTS} "
                    "parse-event budget for untrusted input"
                )
            if isinstance(event, AliasEvent):
                return (
                    f"YAML document '{path}' uses an anchor/alias "
                    f"('*{event.anchor}') — aliases are rejected for untrusted "
                    "input (alias-amplification defense)"
                )
    return None


class _BandSafeParser(argparse.ArgumentParser):
    """Usage errors exit 64, not argparse's default 2 (CR-03).

    Mirrors ``gnd.cli._BandSafeParser`` deliberately: the fallback ships the
    same band contract to users as the runtime does, and this is the only way to
    intercept the ``SystemExit(2)`` argparse raises before ``main()`` returns.
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(EX_USAGE)


#: Default schema location: the canonical copy shipped in the gnd-orm-core
#: sibling skill, resolved relative to this script's own location so the
#: validator works from any working directory.
DEFAULT_SCHEMA = (
    Path(__file__).resolve().parent.parent.parent
    / "gnd-orm-core"
    / "references"
    / "orm-meta.schema.json"
)


def main(argv: list[str] | None = None) -> int:
    parser = _BandSafeParser(
        description=(
            "Structurally validate a GND model.orm.yaml against the canonical "
            "ORM meta-schema (layer 1). Zero-install fallback for environments "
            "without the `gnd` console script; `gnd validate` additionally runs "
            "the layer-2 semantic rules. This script's module docstring lists in "
            "full what it cannot check — it is not an equivalent."
        ),
    )
    parser.add_argument("model", help="path to the model.orm.yaml file to validate")
    parser.add_argument(
        "--schema",
        default=None,
        help=(
            "path to an ORM meta-schema JSON file "
            f"(default: the canonical copy at {DEFAULT_SCHEMA})"
        ),
    )
    args = parser.parse_args(argv)

    schema_path = Path(args.schema) if args.schema else DEFAULT_SCHEMA
    if not schema_path.is_file():
        print(
            f"ERROR: meta-schema not found at {schema_path}. This script "
            "resolves the canonical schema as a SIBLING-SKILL lookup: "
            "gnd-orm-core/references/orm-meta.schema.json, alongside this "
            "skill's own directory. The two skills must therefore be "
            "co-located under one skills root — installing gnd-model-from-text "
            "without gnd-orm-core points this lookup at nothing. Repair by "
            "installing both skills into the same root, or by passing an "
            "explicit --schema PATH."
        )
        return EX_NOINPUT

    # WR-05: same 10 MB stat-based cap as the gnd loaders — model documents
    # are untrusted input and the cap bounds parser exposure before parsing.
    max_model_bytes = 10 * 1024 * 1024
    model_path = Path(args.model)
    if model_path.is_file() and model_path.stat().st_size > max_model_bytes:
        print(
            f"ERROR at $: model file {args.model} is "
            f"{model_path.stat().st_size} bytes, exceeding the "
            f"{max_model_bytes}-byte cap for untrusted model input"
        )
        return 1

    # CR-03: an unreadable meta-schema, an absent model file and a model that is
    # not parseable YAML all used to escape as uncaught exceptions, which the
    # interpreter turns into exit 1 plus a raw traceback — indistinguishable
    # from "your model violates an alethic constraint". They are read failures,
    # not verdicts, so they get EX_DATAERR and a diagnosed message.
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"ERROR: meta-schema {schema_path} could not be read or parsed: {error}")
        return EX_DATAERR

    try:
        guard_error = yaml_stream_guard_error(args.model)
        if guard_error is not None:
            print(f"ERROR at $: model {args.model} could not be safely parsed: {guard_error}")
            return EX_DATAERR
        yaml = YAML(typ="safe")
        with open(args.model, encoding="utf-8") as handle:
            doc = yaml.load(handle)
    except (OSError, ValueError, YAMLError) as error:
        print(f"ERROR at $: model {args.model} could not be read or parsed: {error}")
        return EX_DATAERR

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: e.json_path)
    for error in errors:
        print(f"ERROR at {error.json_path}: {error.message}")
    if errors:
        return 1

    print(f"OK: {args.model} is structurally valid against {schema_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
