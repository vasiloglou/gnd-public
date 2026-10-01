"""Development-time proof-currency events shared by proof-scope tooling."""

from gnd.semantic_registry import record_branch

EVIDENCE_NOT_CURRENT = "applicability:refusal:n-a:evidence-not-current"


def record_evidence_not_current() -> str:
    """Record and return the sole reason for refusing stale proof evidence."""
    record_branch(EVIDENCE_NOT_CURRENT)
    return "evidence-not-current"
