from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "fixtures/public-lean-successors"
INPUTS = {'cases': [{'id': 'dispatch-S01-base', 'domain': 'dispatch', 'branch': 'S01', 'mode': 'export', 'parameters': {'action': 'base'}, 'lane': 'default', 'story': 'dispatch: S01 exercises base against the public Lean lane.'}]}

def load(path):
    return json.loads(Path(path).read_bytes())


def write(path, document):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")


def common(kind, **fields):
    return dict(
        type=kind,
        source="explicit",
        status="confirmed",
        modality="alethic",
        provenance={"user_quote": "Independently authored branch discriminator."},
        **fields,
    )


def materialize(row, root):
    """Recipes mutate supplied fixtures, never synthesize export semantics."""
    src = root.resolve() / "source"
    shutil.copytree(CORPUS / row["domain"] / "base", src)
    m, p, ref = (
        load(src / name)
        for name in ["model.orm.json", "candidate.pop.json", "references/catalog.pop.json"]
    )
    ft = m["fact_types"]
    fids = [f["id"] for f in ft]
    tid = [t["id"] for t in m["object_types"]]
    job = p["facts"][fids[0]][0]["job"]
    nodes = ref["instances"][tid[1]]
    action = row["parameters"].get("variant", row["parameters"]["action"])
    mode = row["mode"]
    target = {"S03": 0, "S04": 1, "S05": 2}.get(row["branch"], 3)
    constraints = ft[0]["constraints"] + m["constraints"]
    if row["parameters"].get("modality"):
        constraints[target]["modality"] = row["parameters"]["modality"]
    if action == "invalid-typed":
        p["facts"][fids[4]][0]["days"] = True
    elif action in {"mandatory-missing", "unique-empty", "subset-empty"}:
        p["facts"][fids[0]] = []
    elif action == "mandatory-empty":
        p["facts"] = {f: [] for f in p["facts"]}
        p["instances"] = {}
    elif action == "unique-conflict":
        p["facts"][fids[0]].append({"job": job, "node": nodes[1]})
    elif action == "unique-duplicate":
        p["facts"][fids[0]] *= 2
    elif action == "subset-missing":
        p["facts"][fids[0]][0]["node"] = nodes[2]
    elif action == "subset-joined":
        m["constraints"][0]["subset_role_seq"].append({"fact_type": fids[5], "role": "target"})
        m["constraints"][0]["superset_role_seq"].append({"fact_type": fids[5], "role": "target"})
    elif action == "guard-empty":
        p["facts"][fids[3]] = []
    elif action == "constant-head":
        ft[6]["derivation_rule"]["clauses"] = ft[6]["derivation_rule"]["clauses"][:1]
        ft[6]["derivation_rule"]["clauses"][0]["head"]["source"] = nodes[0]
    elif action == "repeated-variable":
        ft[6]["derivation_rule"]["clauses"] = [
            {
                "body": [{"fact_type": fids[5], "bind": {"source": "$x", "target": "$x"}}],
                "head": {"source": "$x", "target": "$x"},
            }
        ]
    elif action == "empty-derived":
        ref["facts"][fids[5]] = []
    elif action.startswith("date-") or action == "violation-and-overflow":
        start, days, due = {
            "date-zero": ("2026-01-01", 0, "2026-01-01"),
            "date-leap": ("2024-02-28", 1, "2024-02-29"),
            "date-rollover": ("2025-12-31", 1, "2026-01-01"),
            "date-boundary": ("9999-12-31", 0, "9999-12-31"),
            "date-late": ("2026-01-01", 3, "2026-01-03"),
            "date-overflow": ("9999-12-31", 1, "9999-12-31"),
            "date-subtract": ("2026-01-04", 3, "2026-01-01"),
            "date-underflow": ("0001-01-01", 1, "0001-01-01"),
            "violation-and-overflow": ("9999-12-31", 1, "9999-12-31"),
        }[action]
        p["facts"][fids[3]][0]["day"] = start
        p["facts"][fids[4]][0]["days"] = days
        p["facts"][fids[2]][0]["day"] = due
        if action in {"date-subtract", "date-underflow"}:
            m["constraints"][1]["consequent"]["comparison"]["left"]["fn"] = "date_sub"
        if action == "violation-and-overflow":
            p["facts"][fids[3]].insert(0, {"job": job + "-late", "day": "2026-01-01"})
            p["facts"][fids[2]].insert(0, {"job": job + "-late", "day": "2026-01-01"})
            p["facts"][fids[4]].append({"job": job + "-late", "days": 1})
    elif action.startswith("operator-"):
        primitive, op = row["parameters"]["primitive"], row["parameters"]["operator"]
        vals = {
            "Integer": (-1, 2),
            "Boolean": (False, True),
            "Date": ("2026-01-01", "2026-01-04"),
            "Duration": (0, 3),
            "String": ("A", "B"),
        }[primitive]
        left = {"duration_days": vals[0]} if primitive == "Duration" else vals[0]
        right = {"duration_days": vals[1]} if primitive == "Duration" else vals[1]
        if primitive == "Date":
            comparison = {"left": "$start", "operator": op, "right": "$due"}
        else:
            comparison = {"left": left, "operator": op, "right": right}
        m["constraints"][1]["consequent"]["comparison"] = comparison
    elif mode == "unsupported":
        refs = lambda i, r: {"fact_type": fids[i], "role": r}
        a, b = [refs(0, "node")], [refs(1, "node")]
        root_constraints = {
            "textual": common("textual", expression="Uninterpreted policy."),
            "equality": common("equality", role_seq_a=a, role_seq_b=b),
            "exclusion": common("exclusion", role_seq_a=a, role_seq_b=b),
            "exclusive-or": common("exclusive-or", role_seqs=[a, b]),
            "mandatory-disjunctive": common(
                "mandatory-disjunctive", role_refs=[refs(0, "node"), refs(5, "source")]
            ),
            "external-uniqueness": common(
                "uniqueness", scope="external", role_refs=[refs(0, "node"), refs(5, "source")]
            ),
            "value": common("value", object_type=tid[1], allowed=nodes[:2]),
            "cardinality": common(
                "cardinality", scope="object", object_type=tid[0], bound={"min": 1, "max": 2}
            ),
        }
        local_constraints = {
            "ring": common("ring", variant="transitive"),
            "frequency": common(
                "frequency", scope="internal", roles=["source"], bound={"min": 1, "max": 2}
            ),
            "anchored": common("anchored", role="source"),
            "value-comparison": common(
                "value-comparison", role_a="source", role_b="target", operator="="
            ),
        }
        if action in root_constraints:
            m["constraints"].append(root_constraints[action])
        elif action in local_constraints:
            ft[5]["constraints"] = [local_constraints[action]]
        elif action in {"guard-atom", "guard-absent", "guard-exists"}:
            atom = {"fact_type": fids[0], "bind": {"job": "$j", "node": "$n"}}
            m["constraints"][1]["antecedent"].append(atom)
            m["constraints"][1]["consequent"] = (
                {"atom": atom}
                if action == "guard-atom"
                else {"absence": atom}
                if action == "guard-absent"
                else {
                    "exists": {
                        "atoms": [{"fact_type": fids[0], "bind": {"job": "$j", "node": "$k"}}]
                    }
                }
            )
        elif action in {"entity", "subtype", "subtype-partition"}:
            if action == "entity":
                m["object_types"][0] = {
                    "id": tid[0],
                    "name": m["object_types"][0]["name"],
                    "kind": "entity",
                    "reference": {"mode": "external"},
                }
                m["constraints"].append(
                    common(
                        "uniqueness", scope="external", role_refs=[refs(0, "job"), refs(2, "job")]
                    )
                )
            else:
                child = {
                    "id": tid[0] + "_child",
                    "name": "SpecialJob",
                    "kind": "value",
                    "primitive": "String",
                    "subtype_of": [tid[0]],
                    "inherits_reference": False,
                }
                m["object_types"].append(child)
                if action == "subtype-partition":
                    m["constraints"].append(
                        common(
                            "subtype-partition",
                            supertype=tid[0],
                            subtypes=[child["id"]],
                            exclusive=True,
                            exhaustive=True,
                        )
                    )
        elif action in {"DateTime", "Number", "Float"}:
            i = 4
            m["object_types"][i]["primitive"] = action
            if action == "DateTime":
                p["facts"][fids[7]] = [{"job": job, "value": "2026-01-01T00:00:00Z"}]
        elif action in {
            "self-recursive",
            "empty-self-recursive",
            "mutual-recursive",
            "empty-mutual-recursive",
        }:
            ft[6]["derivation_rule"]["clauses"][0]["body"][0]["fact_type"] = fids[6]
            if "mutual" in action:
                other = copy.deepcopy(ft[6])
                other["id"] = fids[6] + "_other"
                ft[6]["derivation_rule"]["clauses"][0]["body"][0]["fact_type"] = other["id"]
                ft.append(other)
            if action.startswith("empty"):
                ref["facts"][fids[5]] = []
        elif action == "negative":
            clause = ft[6]["derivation_rule"]["clauses"][0]
            clause["negate"] = [copy.deepcopy(clause["body"][0])]
        elif action == "aggregate":
            # Valid count-valued derived relation, independent of route recursion.
            ft[6]["roles"][1]["object_type"] = tid[4]
            ft[6]["reading"] = (
                "{"
                + m["object_types"][1]["name"]
                + "} counts {"
                + m["object_types"][4]["name"]
                + "}"
            )
            ft[6]["derivation_rule"] = {
                "body": [{"fact_type": fids[5], "bind": {"source": "$x", "target": "$y"}}],
                "aggregate": {"fn": "count", "of": "$y", "over": ["$y"], "as": "$n"},
                "head": {"source": "$x", "target": "$n"},
            }
        elif action == "filter":
            ft[6]["derivation_rule"]["clauses"][0]["where"] = [
                {"left": "$x", "operator": "!=", "right": "$y"}
            ]
        elif action == "head-arithmetic":
            # Numeric derived head, leaving temporal arithmetic confined to guards.
            ft[6]["roles"][0]["object_type"] = tid[0]
            ft[6]["roles"][1]["object_type"] = tid[4]
            ft[6]["reading"] = (
                "{"
                + m["object_types"][0]["name"]
                + "} totals {"
                + m["object_types"][4]["name"]
                + "}"
            )
            ft[6]["derivation_rule"] = {
                "body": [{"fact_type": fids[7], "bind": {"job": "$j", "value": "$v"}}],
                "head": {"source": "$j", "target": {"fn": "add", "args": ["$v", 1]}},
            }
        elif action == "textual-derived":
            ft[6]["derivation_rule"] = "A manually described route."
        elif action == "semiderived":
            ft[6]["derivation"] = "semiderived"
        elif action in {"opaque", "unknown"}:
            if action == "opaque":
                p["facts"][fids[7]][0]["value"] = {"$opaque": "not interpreted"}
            else:
                ft[6]["derivation_rule"] = "Unknown supplied relation semantics."
        elif action.startswith("String-ordered-"):
            m["constraints"][1]["consequent"]["comparison"] = {
                "left": "A",
                "operator": row["parameters"]["operator"],
                "right": "B",
            }
        elif action == "partial":
            p["population"]["covers"].remove(fids[0])
        elif action == "asserted-derived":
            p["population"]["covers"].append(fids[6])
            p["facts"][fids[6]] = [{"source": nodes[0], "target": nodes[2]}]
        else:
            raise AssertionError("unmaterialized unsupported story " + action)
        if row["parameters"].get("modality"):
            extra = (
                m["constraints"][-1]
                if action in root_constraints or action == "subtype-partition"
                else ft[5]["constraints"][0]
                if action in local_constraints
                else m["constraints"][1]
            )
            extra["modality"] = "deontic"
    elif mode == "names":
        text = {
            "quotes": 'quote"\\value',
            "newline": "line\nbreak",
            "delimiter": "a; b -- c",
            "keywords": "import Init; axiom False",
            "unicode": "Ω雪🚀",
            "rename": "fresh-vocabulary",
        }[action]
        p["facts"][fids[0]][0]["job"] = text
        for rows in p["facts"].values():
            for v in rows:
                if v.get("job") == job:
                    v["job"] = text
        p["instances"][tid[0]] = [text]
        if action == "rename":
            replace_map = {
                t["id"]: "renamed_type_" + str(i) for i, t in enumerate(m["object_types"])
            } | {f["id"]: "renamed_fact_" + str(i) for i, f in enumerate(ft)}

            def rename(v):
                if isinstance(v, dict):
                    return {replace_map.get(k, k): rename(w) for k, w in v.items()}
                if isinstance(v, list):
                    return [rename(w) for w in v]
                return replace_map.get(v, v) if isinstance(v, str) else v

            m, p, ref = rename(m), rename(p), rename(ref)
    elif mode == "audit" and action == "inactive":
        m["rejected_proposals"] = [
            common("textual", expression="Rejected policy.", id="rejected_policy")
        ]
        m["rejected_proposals"][0]["status"] = "rejected"
    elif mode == "audit" and action == "repeated-shape":
        m["constraints"].append(copy.deepcopy(m["constraints"][0]))
        m["constraints"][-1].pop("id")
    write(src / "references/catalog.pop.json", ref)
    m["reference_populations"][0]["sha256"] = hashlib.sha256(
        (src / "references/catalog.pop.json").read_bytes()
    ).hexdigest()
    write(src / "model.orm.json", m)
    write(src / "candidate.pop.json", p)
    return src, target


def native_command(bundle, filename, *, output=None):
    lake = os.environ.get("GND_V71_LEAN_LAKE")
    assert lake and Path(lake).is_file(), (
        "Required pinned Lean toolchain missing; native gate cannot skip"
    )
    env = {**os.environ, "LEAN_PATH": "."}
    argv = [lake, "env", "lean"] + (["-o", output] if output else []) + [filename]
    result = subprocess.run(
        argv, cwd=bundle, env=env, capture_output=True, text=True, timeout=30, check=False
    )
    assert len(result.stdout.encode()) + len(result.stderr.encode()) <= 10485760
    return result


def evaluate(bundle, expression):
    build = native_command(bundle, "Definitions.lean", output="Definitions.olean")
    assert build.returncode == 0, build.stdout + build.stderr
    (bundle / "Probe.lean").write_text("import Definitions\nopen GND\n#eval " + expression + "\n")
    result = native_command(bundle, "Probe.lean")
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()
