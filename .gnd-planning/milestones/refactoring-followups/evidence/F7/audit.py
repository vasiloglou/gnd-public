"""Rebuild the compatibility migration table from the historical inventories."""

from __future__ import annotations

import ast
import csv
import importlib
import importlib.util
import json
from collections import defaultdict
from functools import cache
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

ROOT = Path.cwd()
HISTORY = ROOT / ".gnd-planning/milestones/code-refactoring"
OUTPUT = ROOT / "docs/assets/refactoring-import-migration.tsv"


def bindings(nodes, package):
    names = {}
    for node in nodes:
        if isinstance(node, ast.Import):
            for item in node.names:
                top = item.name.split(".")[0]
                names[item.asname or top] = item.name if item.asname else top
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                if not package:
                    continue
                try:
                    module = importlib.util.resolve_name("." * node.level + module, package)
                except ImportError:
                    continue
            for item in node.names:
                names[item.asname or item.name] = f"{module}.{item.name}"
    return names


@cache
def module_bindings(module):
    file = ROOT / "src" / Path(*module.split("."))
    path = file / "__init__.py" if file.is_dir() else file.with_suffix(".py")
    package = module if file.is_dir() else module.rpartition(".")[0]
    return bindings(ast.parse(path.read_bytes()).body, package) if path.exists() else {}


def inventory():
    rows = []
    section = ""
    for line in (HISTORY / "notes/shim-inventory.md").read_text().splitlines():
        if line.startswith("## "):
            section = line[3:].split()[0]
        cells = [col.strip().strip("`") for col in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and cells[0].startswith("gnd."):
            old, new, phase = cells[:3]
            rows.append(
                (
                    old,
                    new.split()[0],
                    "MC1" if section == "MC1" else phase,
                    new + " " + " ".join(cells[3:]),
                )
            )
    assert len(rows) == 847, "historical inventory changed"
    moves = json.loads((HISTORY / "evidence/RF4/moves.json").read_bytes())
    for move in moves["names"]:
        old, new, name = move["old"], move["new"], move["name"]
        target = module_bindings(old).get(name)
        if not target or not target.startswith(new + "."):
            target = f"{new}.{name}"
        rows.append((f"{old}.{name}", target, "RF4", ""))
    module = "gnd.exp.session_v7"
    imports = module_bindings(module)
    names = json.loads((HISTORY / "evidence/RF8/v7-bindings.json").read_bytes())["names"]
    rows.extend((f"{module}.{name}", imports[name], "RF8 imports", "") for name in names)
    return rows


def qualified(node, names):
    if isinstance(node, ast.Name):
        return names.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        return qualified(node.value, names) + "." + node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ""


def usage(keys):
    consumers, patches = defaultdict(set), defaultdict(set)
    for home in ("src/gnd", "tests"):
        for path in sorted(Path(home).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_bytes())
            except (SyntaxError, UnicodeError):
                continue
            package = ".".join(path.parent.parts[1:]) if home.startswith("src") else ""
            names = bindings(ast.walk(tree), package)
            for target in set(names.values()) & keys:
                consumers[target].add(str(path))
            for node in ast.walk(tree):
                target = qualified(node, names)
                if target in keys:
                    consumers[target].add(str(path))
                if isinstance(node, ast.Call):
                    for patched in patch_targets(node, names) & keys:
                        patches[patched].add(f"{path}:{node.lineno}")
    return consumers, patches


def patch_targets(call, names):
    method = qualified(call.func, names).split(".")[-1]
    if method not in ("object", "multiple", "setattr", "delattr", "patch"):
        return set()
    kwargs = {k.arg: k.value for k in call.keywords if k.arg}
    target = call.args[0] if call.args else kwargs.get("target")
    owner = qualified(target, names)
    if method == "multiple":
        return {f"{owner}.{key}" for key in kwargs}
    attribute = call.args[1] if len(call.args) > 1 else kwargs.get("attribute", kwargs.get("name"))
    result = {owner}
    if isinstance(attribute, ast.Constant) and isinstance(attribute.value, str):
        result.add(f"{owner}.{attribute.value}")
    return result


def import_origin(name):
    seen = set()
    while name.startswith("gnd.") and name not in seen:
        seen.add(name)
        module, _, member = name.rpartition(".")
        origin = module_bindings(module).get(member)
        if not origin or resolve(origin) is not resolve(name):
            break
        name = origin
    return name


def bound_rule(old, target, note):
    rule_name = note.split("(bound ", 1)[1].split(")", 1)[0]
    module = importlib.import_module(old.rpartition(".")[0])
    rule = getattr(module, rule_name)
    error = SimpleNamespace(errors=lambda: [{"loc": ("x",), "msg": "invalid"}])
    expected = resolve(target)(error, rule)
    assert expected and resolve(old)(error) == expected, old
    return "bound " + rule_name


def resolve(name):
    parts = name.split(".")
    for i in range(len(parts), 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:i]))
        except ModuleNotFoundError:
            continue
        for member in parts[i:]:
            obj = getattr(obj, member)
        return obj
    raise ImportError(name)


def main():
    rows = inventory()
    retirement_file = (
        ROOT
        / ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/retired-names.json"
    )
    retired = {
        f"{r['module']}.{r['name']}": r for r in json.loads(retirement_file.read_text())["retired"]
    }
    candidates = defaultdict(set)
    for old, new, _, _ in rows:
        if old not in retired:
            candidates[old].add(import_origin(new))
    # Multiple historical move rows may denote the same object. Prefer the
    # public spelling at its defining home over another private spelling.
    targets = {
        old: min(options, key=lambda s: (s.split(".")[-1].startswith("_"), s.count("."), s))
        for old, options in candidates.items()
    }
    keys = set(targets) | set(targets.values()) | set(retired)
    consumers, patches = usage(keys)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with StringIO(newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(
            (
                "historical",
                "migration_target",
                "historical_move_target",
                "phase",
                "identity",
                "disposition",
                "release",
                "old_import_or_use",
                "patch_old",
                "patch_target",
            )
        )
        for old, new, phase, note in rows:
            historical_target = new
            if old in retired:
                ruling = retired[old]
                assert not hasattr(importlib.import_module(ruling["module"]), ruling["name"])
                assert not hasattr(importlib.import_module(ruling["home"]), ruling["name"])
                state, new = "absent", "no replacement (unused checker helper)"
                disposition, release = "retired (FU5, #114)", "FU5 retirement already accepted"
            else:
                new = targets[old]
                disposition = "retain" if old != new else "keep current import"
                release = "first release carrying this notice; later removal needs approval"
                if old == new:
                    release = "current defining home; no migration scheduled"
                if "(bound " in note:
                    state = bound_rule(old, new, note)
                else:
                    assert resolve(old) is resolve(historical_target) is resolve(new), old
                    state = "same object"
            writer.writerow(
                (
                    old,
                    new,
                    historical_target,
                    phase,
                    state,
                    disposition,
                    release,
                    " ".join(sorted(consumers[old])),
                    " ".join(sorted(patches[old])),
                    " ".join(sorted(patches[new])),
                )
            )

        OUTPUT.write_text(stream.getvalue())


if __name__ == "__main__":
    main()
