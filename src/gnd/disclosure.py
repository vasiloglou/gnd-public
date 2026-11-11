"""The disclosure mode: whether GND emits population values.

One resolver decides it at the public boundary, after any verdict: the CLI
sets the mode for one invocation, and API functions read it together with the
``GND_DISCLOSURE`` environment variable. ``customer`` from either source wins.
The normative text is docs/reference/disclosure.md.
"""

from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal

MODES = ("internal", "customer")
ENVIRONMENT = "GND_DISCLOSURE"

_MODE: ContextVar[str | None] = ContextVar("gnd_disclosure_mode", default=None)


class DisclosureRefused(ValueError):
    """A request for values refused by policy; the message names the option or
    the variable, never a value."""


def checked_environment(environ: Mapping[str, str] | None = None) -> str | None:
    """The environment's mode, or None; a malformed value is refused."""
    value = (os.environ if environ is None else environ).get(ENVIRONMENT)
    if value is not None and value not in MODES:
        raise DisclosureRefused(f"{ENVIRONMENT} must be 'internal' or 'customer'")
    return value


def resolve(environ: Mapping[str, str] | None = None) -> str | None:
    """The effective mode: 'internal', 'customer' or None (unset)."""
    env = checked_environment(environ)
    ctx = _MODE.get()
    if "customer" in (ctx, env):
        return "customer"
    return ctx or env


def values_allowed(requested: bool, option: str) -> bool:
    """Whether a site emits values: customer never (a request is refused),
    internal always, unset as requested."""
    mode = resolve()
    if mode == "customer":
        if requested:
            raise DisclosureRefused(f"{option} is refused in customer disclosure mode")
        return False
    return True if mode == "internal" else requested


def forward(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """What a spawner adds to a child's environment: only ``customer`` is passed on."""
    return {ENVIRONMENT: "customer"} if resolve(environ) == "customer" else {}


@contextmanager
def invocation(mode: str | None) -> Iterator[None]:
    """Set the mode for one in-process CLI invocation; the token is reset on exit.

    An enclosing ``customer`` holds: a nested invocation never loosens it."""
    token = _MODE.set("customer" if _MODE.get() == "customer" else mode)
    try:
        yield
    finally:
        _MODE.reset(token)


@dataclass(frozen=True)
class Surface:
    kind: Literal["site", "value-free", "every-mode"]
    convention: Literal["declared", "view", "option"] | None = None
    spawns: bool = False
    note: str = ""


def _rows(kind, names, **fields):
    return {name: Surface(kind, **fields) for name in names}


_DECLARED = {"kind": "site", "convention": "declared"}
_VIEW = {"kind": "site", "convention": "view"}

#: The disclosure table: every CLI leaf, every public callable bound in gnd.api,
#: the EvaluationSession methods, gnd.export.service and every output kind.
SURFACES: Mapping[str, Surface] = {
    **{f"gnd {leaf}": Surface(**_DECLARED) for leaf in (
        "check", "validate", "diff", "verbalize population", "measure", "verify", "judgments check")},
    "gnd discover": Surface("site", convention="option",
                            note="--show-values follows the mode; redacted roles never get value candidates"),
    **{f"gnd {leaf}": Surface(**_VIEW) for leaf in (
        "witness", "witness-view", "replay", "why-not",
        "export lean", "export souffle", "export souffle-run", "export souffle-witness")},
    "gnd exp run": Surface("every-mode", spawns=True, note="session kinds are applied in every mode"),
    "gnd solve": Surface("value-free", spawns=True, note="stations are GND commands"),
    "gnd review panel": Surface("value-free", spawns=True, note="reviewers are agents"),
    "gnd review panel-light": Surface("value-free", spawns=True, note="reviewers are agents"),
    "gnd export ilp": Surface("every-mode", note="refuses declared roles; writes undeclared values"),
    "gnd fidelity": Surface("every-mode", note="quotes the extracted facts it measures"),
    "gnd doccheck": Surface("every-mode", note="quotes the population values a rendered document misses"),
    "gnd compose": Surface("every-mode", note="writes the caller's own composed population"),
    "gnd verbalize model": Surface("every-mode", note="reviews the caller's own model and authored samples"),
    **_rows("value-free", [f"gnd {leaf}" for leaf in (
        "codegen", "conformance", "coverage", "doctor", "evolve apply",
        "evolve finalize", "evolve preview", "exp author-expectation", "exp close", "exp init",
        "exp validate", "export lean-compile", "export lean-verify", "export pyrel",
        "export souffle-verify", "extract", "import ilp-rules", "import mined-rules",
        "import rai-orm", "install", "recovery inventory", "recovery verify", "review finalize",
        "synth", "uninstall")]),
    "gnd export ossie": Surface(
        "every-mode",
        note="writes the model's constraint literals and descriptions, also for a fact type that declares "
             "redact, and prints a count of those; populations are omitted and reported"),
    "gnd import ossie": Surface(
        "every-mode", note="restores whatever model content the ontology and its sidecar carry"),
    **{f"api:{name}": Surface(**_DECLARED) for name in (
        "validate", "check", "diff", "verbalize", "transition", "check_with_receipt", "judgments")},
    **{f"api:EvaluationSession.{name}": Surface(**_DECLARED, note="delegates to the gnd.api function")
       for name in ("check", "check_with_receipt", "transition")},
    **{f"api:{name}": Surface(**_VIEW) for name in (
        "witness", "replay", "why_not", "export_lean", "export_souffle", "run_souffle", "souffle_witness")},
    "api:EvaluationSession.check_with_feedback": Surface("every-mode", note="session feedback is applied"),
    "api:EvaluationSession.observe": Surface("every-mode", note="returns the caller's own population"),
    "api:compose": Surface("every-mode", note="returns the caller's own composed population"),
    "api:verbalize_model": Surface("every-mode", note="reviews the caller's own model and authored samples"),
    **_rows("value-free", [f"api:{name}" for name in (
        "CheckReceipt", "ReceiptRefused", "DisclosureRefused", "EvaluationSession", "verify_lean", "verify_souffle",
        "verbalize_rules",
        "compile_lean", "EvaluationSession.reset", "EvaluationSession.close",
        "EvaluationSession.stats")]),
    **_rows("value-free", [f"api:{name}" for name in (
        "Any", "AssuranceBlockV1", "BoundReferenceContext", "Callable", "CheckReport", "Mapping",
        "Model", "ModelIndex", "ModelValidationError", "Path", "Population", "PopulationLoadError",
        "PopulationValidationError", "ValidationIssue", "calculation_scope", "capture_branches",
        "certify_result", "dataclass", "derive_assurance_scope", "field", "index_scope",
        "load_assurance_evidence", "load_model", "load_population", "record_branch", "replace",
        "semantic_decision_for_band", "structured_derivation_ids", "uses_temporal")],
        note="a library binding, not an output"),
    **{f"export.service:{name}": Surface(**_VIEW) for name in (
        "export_lean", "export_souffle", "run_souffle", "souffle_witness")},
    **_rows("value-free", [f"export.service:{name}" for name in (
        "verify_lean", "verify_souffle", "compile_lean")]),
    **{f"kind:{name}": Surface(**_DECLARED) for name in (
        "validate", "check", "admission", "verify", "transition", "plan", "batch", "measure",
        "population-verbalization", "diff")},
    **_rows("every-mode", [f"kind:{name}" for name in (
        "session-feedback", "session-attempt", "session-result")],
        note="the session wire fixes applied"),
}


def bearing(leaf: str) -> bool:
    """Whether a CLI leaf resolves the mode: a site, or one that starts children."""
    surface = SURFACES.get(leaf)
    return surface is not None and (surface.kind == "site" or surface.spawns)
