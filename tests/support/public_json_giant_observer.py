import json
import time
from pathlib import Path

from gnd import judgments
from gnd.exp import session_patch as patch

ROOT = Path(__file__).resolve().parents[2]


def observe(row, root, monkeypatch, *, after=False):
    # This projection admits only the four original giant-integer branches.
    consumer, variant = row["consumer"], row["variant"]
    assert consumer in {"patch-value", "fact-digest", "receipt-init", "receipt-digest"}
    assert variant == "giant-int" and not after
    root = root.resolve()
    began = time.monotonic()
    try:
        if consumer == "patch-value":
            result = {"v": 10**5000}
            patch.validate_json_value(result)
        elif consumer == "fact-digest":
            result = judgments.judgment_fact_digest("work", 0, {"v": 10**5000})
        else:
            result = json.loads(
                (ROOT / "tests/fixtures/v71/phase5/dispatch/receipts.json").read_bytes()
            )["receipts"][0]
            result["subject"]["index"] = 10**5000
            result = (
                judgments.JudgmentReceipt(b"not-reparsed", result)
                if consumer == "receipt-init"
                else judgments.judgment_receipt_digest(result)
            )
        raise AssertionError("the original giant input was unexpectedly accepted")
    except Exception as error:  # noqa: BLE001 - Observe every hostile-input exception and retain its type.
        return {
            "kind": "refused",
            "type": type(error).__name__,
            "reason": getattr(error, "reason", None),
            "message": str(error)
            .replace(str(root), "<case-root>")
            .replace(str(ROOT), "<repo>")[:512],
            "seconds": round(time.monotonic() - began, 6),
        }
