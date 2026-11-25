import json, sys
def row(path):
    d = json.load(open(path))
    layer = {m["module"]: m.get("layer") for m in d["modules"]}
    multi = [s for s in d["sccs"]["runtime"] if len(s) > 1]
    core = {"model", "population", "checking", "semantics"}
    core_multi = [s for s in multi if any(layer.get(m) in core for m in s)]
    largest = sorted(d["modules"], key=lambda m: -m["lines"])[:5]
    lay = d["layering"]
    return {
        "modules": d["scope"]["module_count"], "lines": d["scope"]["line_count"],
        "runtime SCCs >1": len(multi), "largest SCC": max((len(s) for s in multi), default=0),
        "core-layer SCCs >1": len(core_multi),
        "private imports": len(d["private_imports"]),
        "AST-identical groups": len(d["duplicates"].get("ast_identical", [])),
        "families": {k: (len(v) if isinstance(v, list) else v) for k, v in d["duplicates"].get("families", {}).items()} if isinstance(d["duplicates"].get("families"), dict) else len(d["duplicates"].get("families", [])),
        "wrong-way edges": len(lay["wrong_way"]), "cross-lane edges": len(lay["cross_lane"]),
        "clean layers": len(lay["clean_layers"]),
        "entry-point violations": len(d["entrypoints"]["violations"]) if "entrypoints" in d else "n/a",
        "unmapped modules": sum(1 for m in d["modules"] if not m.get("layer")),
        "largest": [(m["module"], m["lines"]) for m in largest],
    }
for p in sys.argv[1:]:
    print("==", p)
    for k, v in row(p).items(): print(f"  {k}: {v}")
