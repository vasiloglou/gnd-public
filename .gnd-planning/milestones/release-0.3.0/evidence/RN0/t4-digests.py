"""T4: digest every Ossie export (json and yaml) and import over the census. Usage: t4.py OUT"""
import hashlib, json, sys, tempfile
from pathlib import Path
ROOT = Path.cwd()
from gnd.export.ossie import render_ossie
from gnd.ossie_import import plan_ossie_import
census = (ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS0/revised/census.txt").read_text().splitlines()
extra = ["src/gnd/examples/refunds/model.orm.yaml", "src/gnd/examples/growth/model.orm.yaml"]
h = lambda b: hashlib.sha256(b).hexdigest()
rows = []
for rel in sorted(set(census + extra)):
    for fmt in ("json", "yaml"):
        for strict in (False, True):
            key = f"{rel} {fmt} strict={strict}"
            try:
                b = render_ossie(ROOT / rel, output_format=fmt, strict=strict)
            except Exception as e:
                rows.append(f"{key} EXC {type(e).__name__}: {str(e)[:200]}")
                continue
            rows.append(f"{key} doc={h(b.document)} sidecar={h(b.sidecar)} loss={h(b.loss_report)}")
            if strict:
                continue
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / f"o.ossie.{fmt}"
                p.write_bytes(b.document); Path(str(p) + ".gnd.json").write_bytes(b.sidecar)
                Path(str(p) + ".loss.json").write_bytes(b.loss_report)
                for with_side in (True, False):
                    if not with_side:
                        Path(str(p) + ".gnd.json").unlink(); 
                    try:
                        r = plan_ossie_import(p)
                        parts = {k: (h(v) if isinstance(v, bytes) else repr(v)[:80]) for k, v in sorted(vars(r).items())} if hasattr(r, "__dict__") else {f: (h(getattr(r, f)) if isinstance(getattr(r, f), bytes) else repr(getattr(r, f))[:80]) for f in r.__dataclass_fields__}
                        rows.append(f"{key} import side={with_side} {json.dumps(parts, sort_keys=True)}")
                    except Exception as e:
                        rows.append(f"{key} import side={with_side} EXC {type(e).__name__}: {str(e)[:200]}")
Path(sys.argv[1]).write_text("\n".join(rows) + "\n")
print(len(rows), h(Path(sys.argv[1]).read_bytes()))
