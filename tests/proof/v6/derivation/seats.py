"""Exact pure required-seat outcome algebra only; no seat/backend executors."""
def classify_outcome(*, timed_out: bool, available: bool, complete: bool, matched: bool) -> str:
    """Apply the frozen precedence for every required-seat termination."""
    if timed_out:
        return "timeout"
    if not available:
        return "backend-unavailable"
    if not complete:
        return "incomplete-subset"
    if not matched:
        return "mismatch"
    return "matched"
