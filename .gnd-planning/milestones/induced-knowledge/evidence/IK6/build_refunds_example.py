"""Write the refunds example's batches and label manifest (IK6, synthetic data).

Run from the repository root: uv run python <this file>. It rewrites
src/gnd/examples/refunds/batches/*.yaml and labels.json deterministically.
"""

import hashlib
import json
from pathlib import Path

EXAMPLE = Path("src/gnd/examples/refunds")

# store -> (auditor's label, refunds as (refund no, customer, amount, channel))
BATCHES = {
    "north": ("clean", [(101, "c-anna", 40, "card"), (102, "c-ben", 120, "card"),
                        (103, "c-cara", 75, "cash")]),
    "south": ("clean", [(201, "c-dev", 500, "card"), (202, "c-eli", 60, "voucher"),
                        (203, "c-fay", 230, "card")]),
    "east": ("clean", [(301, "c-gus", 310, "cash"), (302, "c-hana", 90, "card")]),
    "west": ("clean", [(401, "c-ivo", 450, "card"), (402, "c-jo", 35, "card"),
                       (403, "c-kim", 180, "voucher")]),
    "harbor": ("flagged", [(501, "c-lea", 1200, "cash"), (502, "c-max", 80, "card")]),
    "market": ("flagged", [(601, "c-nia", 750, "card"), (602, "c-oli", 140, "card"),
                           (603, "c-pia", 55, "cash")]),
    "airport": ("flagged", [(701, "c-quin", 1500, "card"), (702, "c-rae", 260, "voucher")]),
    "station": ("flagged", [(801, "c-sam", 640, "cash"), (802, "c-tia", 95, "card")]),
}


def batch_text(store: str, label: str, refunds: list) -> str:
    lines = [
        f"# The {store} store's refunds for one week. The auditors marked this batch {label}.",
        "format_version: 2",
        "population:",
        "  model: model.orm.yaml",
        "  source: fixture",
        "  covers: [refund_by, refund_amount, refund_channel]",
        "instances:",
        "  refund: [" + ", ".join(str(no) for no, *_ in refunds) + "]",
        "  customer: [" + ", ".join(f'"{customer}"' for _, customer, *_ in refunds) + "]",
        "facts:",
        "  refund_by:",
    ]
    lines += [f'    - {{ refund: {no}, customer: "{customer}" }}' for no, customer, _, _ in refunds]
    lines.append("  refund_amount:")
    lines += [f"    - {{ refund: {no}, amount: {amount} }}" for no, _, amount, _ in refunds]
    lines.append("  refund_channel:")
    lines += [f'    - {{ refund: {no}, channel: "{channel}" }}' for no, _, _, channel in refunds]
    return "\n".join(lines) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    batches = EXAMPLE / "batches"
    batches.mkdir(exist_ok=True)
    populations = []
    for store, (label, refunds) in BATCHES.items():
        path = batches / f"{store}.yaml"
        path.write_text(batch_text(store, label, refunds), encoding="utf-8")
        populations.append({"id": store, "path": f"batches/{store}.yaml", "sha256": sha256(path),
                            "class": "positive" if label == "clean" else "negative"})
    manifest = {
        "schema_version": "gnd-labels/1",
        "model_sha256": sha256(EXAMPLE / "model.orm.yaml"),
        "mode": "class",
        "populations": populations,
        "rules": {"id:g_refund_limit": {"fires_on": "negative"}},
    }
    (EXAMPLE / "labels.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
