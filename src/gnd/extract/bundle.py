"""The ONE owner of the two per-model bundle conventions: the slugged stem and
the population header template.

Both were inline in ``src/gnd/cli.py`` (``_extract_stem`` at 838, and
``_extraction_header_template`` at 855). G-03′ names that inlining and warns
that *"codegen would be their third copy"*. By the end of plan 03-03 the tree
held **two and a half** copies of the pair: ``cli.py``'s originals,
``codegen/emit.py``'s hand-written re-implementation of the stem rule, and a
function-local ``from gnd.cli import _extraction_header_template`` inside
``emit.py`` for the header.

Plan 03-04 extracted them here rather than copying them a third time, and rather
than leaving the reach-in. Three reasons, in the order they weigh:

1. **The reach-in inverted the layering.** A library module (``gnd.codegen``)
   imported a private function from the CLI — the application layer that imports
   everything else.
2. **It made scan 5 a package-wide scan wearing the generation lane's name.**
   MEASURED at plan-04 start: the generation lane's transitive import closure was
   **45 modules** with the ``gnd.cli`` edge and **21 without** — the edge pulled
   in the whole checker / measure / fidelity / synth stack. A network import
   anywhere reachable from ``cli.py`` would have red the codegen offline guard
   for a reason with nothing to do with codegen.
3. **``extract_stem`` was already a second hand-written copy**, so the "one
   owner" claim was not true before this module existed.

Neither function derives anything new (G-03's rule stands): they are the
naming and header CONVENTIONS that ``gnd extract``, ``gnd verify`` and
``gnd codegen`` must agree on to the byte, and agreeing to the byte is exactly
what a single owner buys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gnd.extraction_scope import fact_type_scope
from gnd.synth import paths as _paths

__all__ = ["MODEL_SUFFIXES", "bundle_stem", "header_template"]

#: Filename suffixes stripped before slugging. Published because the stem is a
#: cross-command contract: ``gnd extract`` names four files after it and
#: ``gnd codegen`` must name the same four, byte for byte.
MODEL_SUFFIXES: tuple[str, ...] = (".orm.yaml", ".orm.yml", ".yaml", ".yml", ".json")


def bundle_stem(model_path: str) -> str:
    """The slugged filename stem the bundle's four files share.

    ``full_vocabulary.orm.yaml`` -> ``full_vocabulary``. ``paths.slug`` is the
    front-line normaliser for the model-derived segment (T-02.1-03);
    ``paths.safe_output_path`` at each write site remains the backstop.
    """
    name = Path(model_path).name
    for suffix in MODEL_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return _paths.slug(name)


def header_template(model_path: str, model: Any) -> dict[str, Any]:
    """The one deterministic owner of the extraction population header.

    PANEL-6 header ownership: ``model``, ``model_id``, ``source`` and ``covers``
    are set by deterministic code — the caller contract the ``gnd-extract`` skill
    copies VERBATIM and ``gnd verify`` re-derives and enforces. The LLM never
    chooses header fields, because an extractor that quietly shortened ``covers``
    to the fact types it happened to find would turn every miss into a vacuous
    non-question and score perfectly while measuring nothing.
    """
    scope = fact_type_scope(model)
    header: dict[str, Any] = {
        "model": Path(model_path).as_posix(),
        "source": "agent-output",
        "covers": sorted(
            fact_type_id
            for fact_type_id, inapplicable_reason in scope.items()
            if inapplicable_reason is None
        ),
    }
    if model.model_id:
        header["model_id"] = model.model_id
    return header
