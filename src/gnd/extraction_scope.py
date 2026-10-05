"""One policy walk for document-extraction fact-type scope."""

from __future__ import annotations

from gnd.documents import Model
from gnd.model import structured_derivation_ids

__all__ = [
    "STRUCTURED_DERIVATION_INAPPLICABLE_REASON",
    "fact_type_scope",
]

STRUCTURED_DERIVATION_INAPPLICABLE_REASON = (
    "structured-derived fact types are computed from asserted facts "
    "and are outside document extraction scope"
)


def fact_type_scope(model: Model) -> dict[str, str | None]:
    """Classify every fact type once; ``None`` means document-extractable."""
    structured = set(structured_derivation_ids(model))
    return {
        fact_type_id: (
            STRUCTURED_DERIVATION_INAPPLICABLE_REASON
            if fact_type_id in structured
            else None
        )
        for fact_type in model.fact_types
        for fact_type_id in [str(fact_type.get("id"))]
    }
