"""MG3 probe: an option-only size blow-up past the 10 MiB preview read cap."""
import json, sys, hashlib
from pathlib import Path
REPO = Path("<repo>")
sys.path.insert(0, str(REPO / "tests"))
import test_evolve_shape_matches as T  # noqa
from support.cli_runner import run_main  # noqa
from ruamel.yaml import YAML
import io


def test_cap(tmp_path):
    doc = T._doc()
    N, K = 400, 200
    for i in range(N):
        doc["fact_types"].append({"id": f"order_memo_{i}", "reading": f"{{Order}} keeps memo{i} {{Memo}}",
                                  "roles": [{"object_type": "order", "role_name": "order"},
                                            {"object_type": "memo", "role_name": "memo"}]})
    buf = io.StringIO(); YAML().dump(doc, buf); text = buf.getvalue()
    ops = tuple(T._op("add", "fact_types", f"order_memo_new_{i}",
                      after={"id": f"order_memo_new_{i}", "reading": f"{{Order}} notes memo{i} {{Memo}}",
                             "roles": [{"object_type": "order", "role_name": "order"},
                                       {"object_type": "memo", "role_name": "memo"}]},
                      operation_id=f"op{i}") for i in range(K))
    root = tmp_path; (root / "records").mkdir()
    model = root / "model.orm.yaml"; model.write_text(text)
    (root / "model.verbalization.txt").write_text("pre\n")
    prop = root / "proposal.json"
    prop.write_text(json.dumps(T._proposal(text, ops).model_dump(mode="json"), indent=2, sort_keys=True) + "\n")
    paths = {"workspace": root, "model": model, "proposal": prop, "preview": root / "preview.json", "records": root / "records"}
    for flag in ((), ("--shape-report",)):
        r = run_main(T._preview_argv(paths, *flag))
        size = paths["preview"].stat().st_size if paths["preview"].exists() else None
        print(f"[CAP] preview {flag or 'plain'} exit={r.returncode} bytes={size} stderr={r.stderr[-200:]!r}")
        if flag:
            r2 = run_main(T._apply_argv(paths))
            print(f"[CAP] apply after --shape-report exit={r2.returncode} stderr={r2.stderr[-300:]!r}")
        else:
            paths["preview"].unlink()
