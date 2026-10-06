"""Measure the architecture of ``src/gnd`` for the code-refactoring milestone.

Two subcommands, both stdlib-only and read-only over the repository:

``measure``
    One AST pass per module classifies every import (module-level, lazy,
    type-only, dynamic), then derives strongly connected components, private
    cross-module imports, fan-in/fan-out, layering violations against
    ``tools/gnd_layers.json``, duplicate-helper candidates, the test-suite pin
    sites (monkeypatch targets, source scans, private imports), module
    citations in the packaged skills, and raw-model query sites. The output is
    canonical JSON with no timestamps and no absolute paths, so two runs over
    the same tree under the same interpreter produce identical bytes.

``compare``
    Counts added, removed and *moved* lines under ``src/gnd`` between two git
    revisions. A moved line is a removed line whose stripped content is added
    in a different file; blank lines are ignored.

Exit codes: 0 written; 2 usage; 3 invalid layer map, unparsable source, or a
git failure; 11 the ``--out`` path already exists (nothing is written).

The spec is ``.gnd-planning/milestones/code-refactoring/notes/phase-RF0-spec.md``.
AST hashes come from ``ast.dump`` and are comparable only under one Python
minor version, which the output records.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA_VERSION = 1
MAP_READ_CAP = 1024 * 1024
SOURCE_READ_CAP = 4 * 1024 * 1024
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = "src/gnd"
RUNTIME_KINDS = frozenset({"module", "lazy", "dynamic"})
MAP_KEYS = {
    "schema_version",
    "excluded",
    "layers",
    "lanes",
    "modules",
    "declared_clean",
    "allow_list",
    "helper_patterns",
}
SKILL_PATH_RE = re.compile(r"src/gnd/[A-Za-z0-9_/]+\.py")
SKILL_MODULE_RE = re.compile(r"\bgnd(?:\.[A-Za-z_][A-Za-z0-9_]*)+")


class ToolError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def _invalid(message: str) -> ToolError:
    return ToolError(3, message)


# ---------------------------------------------------------------- layer map


def _reject_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key {key!r}")
        seen[key] = value
    return seen


def _reject_constant(name):
    raise ValueError(f"non-finite number {name}")


def load_layer_map(path: Path) -> dict:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAP_READ_CAP + 1)
    except OSError as error:
        raise _invalid(f"layer map unreadable: {path.name}: {error.strerror}") from None
    if len(raw) > MAP_READ_CAP:
        raise _invalid(f"layer map exceeds {MAP_READ_CAP} bytes")
    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        raise _invalid(f"layer map is not strict JSON: {error}") from None
    _validate_layer_map(data)
    return data


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise _invalid(f"layer map: {message}")


def _is_str_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _validate_layer_map(data) -> None:
    _require(isinstance(data, dict), "top level must be an object")
    _require(set(data) == MAP_KEYS, f"keys must be exactly {sorted(MAP_KEYS)}")
    _require(data["schema_version"] == SCHEMA_VERSION, "unsupported schema_version")
    _require(_is_str_list(data["excluded"]), "excluded must be a list of strings")
    layers = data["layers"]
    _require(isinstance(layers, list) and layers, "layers must be a non-empty list")
    names, ranks = set(), set()
    for layer in layers:
        _require(
            isinstance(layer, dict)
            and set(layer) == {"name", "rank"}
            and isinstance(layer["name"], str)
            and isinstance(layer["rank"], int)
            and not isinstance(layer["rank"], bool),
            "each layer is {name: str, rank: int}",
        )
        _require(layer["name"] not in names, f"duplicate layer {layer['name']!r}")
        _require(layer["rank"] not in ranks, f"duplicate rank {layer['rank']}")
        names.add(layer["name"])
        ranks.add(layer["rank"])
    _require(_is_str_list(data["lanes"]), "lanes must be a list of strings")
    lanes = set(data["lanes"])
    modules = data["modules"]
    _require(isinstance(modules, dict), "modules must be an object")
    for module, entry in modules.items():
        _require(isinstance(entry, dict), f"{module}: entry must be an object")
        _require(
            set(entry) <= {"layer", "lane"} and "layer" in entry,
            f"{module}: entry keys are layer and optional lane",
        )
        _require(
            isinstance(entry["layer"], str) and entry["layer"] in names,
            f"{module}: unknown layer {entry['layer']!r}",
        )
        _require(
            "lane" not in entry or isinstance(entry["lane"], str),
            f"{module}: lane must be a string",
        )
        if entry["layer"] == "lanes":
            _require(entry.get("lane") in lanes, f"{module}: lanes-layer module needs a known lane")
        else:
            _require("lane" not in entry, f"{module}: only lanes-layer modules carry a lane")
    _require(
        _is_str_list(data["declared_clean"]) and set(data["declared_clean"]) <= names,
        "declared_clean must list known layers",
    )
    allow = data["allow_list"]
    _require(isinstance(allow, list), "allow_list must be a list")
    for item in allow:
        _require(
            isinstance(item, dict)
            and set(item) == {"from", "to", "reason", "successor"}
            and all(isinstance(item[key], str) and item[key] for key in item),
            "allow_list entries are {from, to, reason, successor} non-empty strings",
        )
    patterns = data["helper_patterns"]
    _require(isinstance(patterns, dict), "helper_patterns must be an object")
    for family, pattern in patterns.items():
        _require(isinstance(pattern, str), f"helper pattern {family!r} must be a string")
        try:
            re.compile(pattern)
        except re.error as error:
            raise _invalid(f"layer map: helper pattern {family!r}: {error}") from None


# ---------------------------------------------------------------- sources


def _excluded(rel: str, patterns) -> bool:
    return any(fnmatch.fnmatchcase(rel, pattern) for pattern in patterns)


def discover_modules(root: Path, excluded) -> dict[str, str]:
    """Map dotted module name -> repository-relative path."""
    base = root / PACKAGE_DIR
    if not base.is_dir():
        raise _invalid(f"no package directory at {PACKAGE_DIR}")
    found = {}
    for path in sorted(base.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts or _excluded(rel, excluded):
            continue
        parts = list(path.relative_to(root / "src").with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        found[".".join(parts)] = rel
    return found


def _parse(root: Path, rel: str) -> tuple[ast.Module, int]:
    try:
        with (root / rel).open("rb") as stream:
            raw = stream.read(SOURCE_READ_CAP + 1)
    except OSError as error:
        raise _invalid(f"cannot read {rel}: {error.strerror}") from None
    if len(raw) > SOURCE_READ_CAP:
        raise _invalid(f"{rel} exceeds {SOURCE_READ_CAP} bytes")
    try:
        text = raw.decode("utf-8")
        tree = ast.parse(text, filename=rel)
    except (SyntaxError, ValueError, RecursionError, MemoryError, UnicodeDecodeError) as error:
        raise _invalid(f"cannot parse {rel}: {type(error).__name__}: {error}") from None
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    return tree, lines


def _dotted(node) -> str | None:
    names = []
    while isinstance(node, ast.Attribute):
        names.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        names.append(node.id)
        return ".".join(reversed(names))
    return None


def _is_private(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")


def _is_type_checking(test) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        _dotted(test) == "typing.TYPE_CHECKING"
    )


_UNBOUND = object()


class _AliasScopes:
    """Lexically scoped import-alias bindings, shared by both visitors (RF0-OQ2).

    A name bound to None is a known non-gnd binding; an unbound name is absent.
    """

    def __init__(self) -> None:
        self._scopes: list[dict[str, str | None]] = [{}]

    def bind(self, name: str, target: str | None) -> None:
        self._scopes[-1][name] = target

    def lookup(self, name: str):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return _UNBOUND

    def push(self) -> None:
        self._scopes.append({})

    def pop(self) -> None:
        self._scopes.pop()


class _ModuleVisitor(ast.NodeVisitor):
    """One walk per module; every import kind is classified here."""

    def __init__(self, module: str, rel: str, modules: set[str]) -> None:
        self.module = module
        self.rel = rel
        self.modules = modules
        self.package = module if rel.endswith("/__init__.py") else module.rpartition(".")[0]
        self.function_depth = 0
        self.type_checking_depth = 0
        self.aliases = _AliasScopes()
        self.edges: set[tuple[str, str, int]] = set()
        self.unresolved: set[int] = set()
        self.private: set[tuple[str, str, int, str]] = set()
        self.functions: list[tuple[str, int, str]] = []
        self.fact_types: set[int] = set()
        self.get_roles: set[int] = set()

    def _kind(self) -> str:
        if self.type_checking_depth:
            return "type_only"
        return "lazy" if self.function_depth else "module"

    def _resolve(self, dotted: str) -> str | None:
        while dotted:
            if dotted in self.modules:
                return dotted
            dotted = dotted.rpartition(".")[0]
        return None

    def _bind(self, name: str, module: str) -> None:
        self.aliases.bind(name, module)

    def _lookup(self, name: str) -> str | None:
        found = self.aliases.lookup(name)
        return None if found is _UNBOUND else found

    def _edge(self, target: str | None, line: int, kind: str | None = None) -> None:
        if target is not None and target != self.module:
            self.edges.add((target, kind or self._kind(), line))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name != "gnd" and not alias.name.startswith("gnd."):
                continue
            target = self._resolve(alias.name)
            self._edge(target, node.lineno)
            if alias.asname and target:
                self._bind(alias.asname, target)
            elif not alias.asname:
                self._bind("gnd", "gnd")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            parts = self.package.split(".") if self.package else []
            if node.level - 1 >= len(parts):
                raise _invalid(f"{self.rel}:{node.lineno}: relative import climbs above gnd")
            base = ".".join(parts[: len(parts) - (node.level - 1)])
            full = f"{base}.{node.module}" if node.module else base
        else:
            full = node.module or ""
        if full != "gnd" and not full.startswith("gnd."):
            return
        for alias in node.names:
            candidate = f"{full}.{alias.name}"
            if alias.name != "*" and candidate in self.modules:
                self._edge(candidate, node.lineno)
                self._bind(alias.asname or alias.name, candidate)
                if _is_private(alias.name) and full != self.module:
                    self.private.add((full, alias.name, node.lineno, "from_import"))
                continue
            target = self._resolve(full)
            self._edge(target, node.lineno)
            if _is_private(alias.name) and target and target != self.module:
                self.private.add((target, alias.name, node.lineno, "from_import"))

    def visit_If(self, node: ast.If) -> None:
        if _is_type_checking(node.test):
            self.visit(node.test)
            self.type_checking_depth += 1
            for child in node.body:
                self.visit(child)
            self.type_checking_depth -= 1
            for child in node.orelse:
                self.visit(child)
        else:
            self.generic_visit(node)

    def _visit_function(self, node) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        self.visit(node.args)
        if node.returns:
            self.visit(node.returns)
        self.function_depth += 1
        self.aliases.push()
        for child in node.body:
            self.visit(child)
        self.aliases.pop()
        self.function_depth -= 1
        self.functions.append((node.name, node.lineno, _function_hash(node)))

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.visit(node.args)
        self.function_depth += 1
        self.aliases.push()
        self.visit(node.body)
        self.aliases.pop()
        self.function_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        name = _dotted(node.func) or ""
        if name == "__import__" or name.endswith("import_module"):
            first = node.args[0] if node.args else None
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                if first.value == "gnd" or first.value.startswith("gnd."):
                    kind = "type_only" if self.type_checking_depth else "dynamic"
                    self._edge(self._resolve(first.value), node.lineno, kind)
            else:
                self.unresolved.add(node.lineno)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "roles"
        ):
            self.get_roles.add(node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "fact_types" and isinstance(node.ctx, ast.Load):
            self.fact_types.add(node.lineno)
        if _is_private(node.attr):
            base = _dotted(node.value)
            if base:
                head, _, rest = base.partition(".")
                bound = self._lookup(head)
                if bound:
                    full = bound + (f".{rest}" if rest else "")
                    if full in self.modules and full != self.module:
                        self.private.add((full, node.attr, node.lineno, "attribute"))
        self.generic_visit(node)


def _function_hash(node) -> str:
    """sha256 of ast.dump with the function name and docstring removed."""
    name, body = node.name, node.body
    first = body[0] if body else None
    has_doc = (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    )
    node.name = "_"
    if has_doc:
        node.body = body[1:] or [ast.Pass()]
    try:
        dumped = ast.dump(node, include_attributes=False)
    finally:
        node.name, node.body = name, body
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- graph


def _sccs(nodes, edges) -> list[list[str]]:
    """Iterative Tarjan; components of two or more modules, sorted."""
    graph = defaultdict(set)
    for source, target in edges:
        graph[source].add(target)
    index, low, on_stack, stack, result = {}, {}, set(), [], []
    counter = 0
    for start in sorted(nodes):
        if start in index:
            continue
        work = [(start, iter(sorted(graph[start])))]
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        while work:
            node, children = work[-1]
            advanced = False
            for child in children:
                if child not in index:
                    index[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(sorted(graph[child]))))
                    advanced = True
                    break
                if child in on_stack:
                    low[node] = min(low[node], index[child])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                component = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                if len(component) > 1:
                    result.append(sorted(component))
    return sorted(result)


# ---------------------------------------------------------------- tests and skills


class _TestVisitor(ast.NodeVisitor):
    def __init__(self, rel: str, modules: set[str]) -> None:
        self.rel = rel
        self.modules = modules
        self.aliases = _AliasScopes()
        self.patches: set[tuple[int, str, str, bool]] = set()
        self.scans: set[tuple[int, str]] = set()
        self.private: set[tuple[int, str]] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            is_gnd = alias.name == "gnd" or alias.name.startswith("gnd.")
            if alias.asname:
                self.aliases.bind(alias.asname, alias.name if is_gnd else None)
            else:
                head = alias.name.partition(".")[0]
                self.aliases.bind(head, head if is_gnd else None)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        source = node.module or ""
        is_gnd = not node.level and (source == "gnd" or source.startswith("gnd."))
        for alias in node.names:
            self.aliases.bind(alias.asname or alias.name, f"{source}.{alias.name}" if is_gnd else None)
            if is_gnd and _is_private(alias.name):
                self.private.add((node.lineno, f"{source}.{alias.name}"))

    def _target(self, expression) -> tuple[str, bool] | None:
        base = _dotted(expression)
        if base is None:
            return ("<expression>", False)
        head, _, rest = base.partition(".")
        bound = self.aliases.lookup(head)
        if bound is _UNBOUND:
            return (base, False)
        if bound is None:
            return None
        return (bound + (f".{rest}" if rest else ""), True)

    def visit_Call(self, node: ast.Call) -> None:
        name = _dotted(node.func) or ""
        api = None
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"setattr", "delattr"}:
            if isinstance(node.func.value, ast.Name):
                api = node.func.attr
        elif name.endswith("patch.object"):
            api = "patch.object"
        elif name == "patch" or name.endswith(".patch"):
            api = "patch"
        keywords = {k.arg: k.value for k in node.keywords if k.arg}
        first = node.args[0] if node.args else keywords.get("target")
        if api and first is not None:
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                if first.value.startswith("gnd."):
                    self.patches.add((node.lineno, api, first.value, True))
            elif api != "patch":
                found = self._target(first)
                attr = node.args[1] if len(node.args) > 1 else None
                if attr is None:
                    attr = keywords.get("name", keywords.get("attribute"))
                if found and isinstance(attr, ast.Constant) and isinstance(attr.value, str):
                    target, resolved = found
                    self.patches.add((node.lineno, api, f"{target}.{attr.value}", resolved))
        if name.endswith("getsource"):
            self.scans.add((node.lineno, "getsource"))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if _dotted(node) == "sys.modules":
            self.scans.add((node.lineno, "sys_modules"))
        if _is_private(node.attr):
            base = _dotted(node.value)
            if base:
                head, _, rest = base.partition(".")
                bound = self.aliases.lookup(head)
                if bound is not _UNBOUND and bound:
                    full = bound + (f".{rest}" if rest else "")
                    if full in self.modules:
                        self.private.add((node.lineno, f"{full}.{node.attr}"))
        self.generic_visit(node)

    def _scoped(self, node) -> None:
        self.aliases.push()
        self.generic_visit(node)
        self.aliases.pop()

    visit_FunctionDef = _scoped
    visit_AsyncFunctionDef = _scoped
    visit_Lambda = _scoped

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            if node.value.endswith("cli.py"):
                self.scans.add((node.lineno, "cli_path"))
            # "module stays unloaded" checks usually run in a subprocess whose
            # code is a string literal.
            if "sys.modules" in node.value:
                self.scans.add((node.lineno, "sys_modules"))


def _scan_tests(root: Path, modules: set[str]) -> dict:
    patches, scans, private = [], [], []
    tests_dir = root / "tests"
    paths = sorted(tests_dir.rglob("*.py")) if tests_dir.is_dir() else []
    for path in paths:
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        tree, _ = _parse(root, rel)
        visitor = _TestVisitor(rel, modules)
        visitor.visit(tree)
        for line, api, target, resolved in visitor.patches:
            patches.append(
                {"file": rel, "line": line, "api": api, "target": target, "resolved": resolved}
            )
        scans += [{"file": rel, "line": line, "kind": kind} for line, kind in visitor.scans]
        private += [{"file": rel, "line": line, "target": t} for line, t in visitor.private]
    key = lambda item: (item["file"], item["line"], json.dumps(item, sort_keys=True))
    return {
        "patches": sorted(patches, key=key),
        "source_scans": sorted(scans, key=key),
        "private_imports": sorted(private, key=key),
    }


def _scan_skills(root: Path, modules: set[str], paths: dict[str, str]) -> list[dict]:
    known_paths = set(paths.values())
    citations = set()
    skills = root / PACKAGE_DIR / "skills"
    for path in sorted(skills.rglob("*.md")) if skills.is_dir() else []:
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise _invalid(f"cannot read {rel}: {error}") from None
        for number, line in enumerate(text.splitlines(), 1):
            for match in SKILL_PATH_RE.findall(line):
                if match in known_paths:
                    citations.add((rel, number, match))
            for match in SKILL_MODULE_RE.findall(line):
                if match in modules and match != "gnd":
                    citations.add((rel, number, match))
    return [{"file": f, "line": n, "cites": c} for f, n, c in sorted(citations)]


# ---------------------------------------------------------------- measure


def measure(root: Path, layers_path: Path) -> dict:
    layer_map = load_layer_map(layers_path)
    paths = discover_modules(root, layer_map["excluded"])
    modules = set(paths)
    mapped = set(layer_map["modules"])
    if modules - mapped:
        raise _invalid(f"layer map misses modules: {', '.join(sorted(modules - mapped))}")
    if mapped - modules:
        raise _invalid(f"layer map names unknown modules: {', '.join(sorted(mapped - modules))}")
    rank = {layer["name"]: layer["rank"] for layer in layer_map["layers"]}
    entry = layer_map["modules"]

    module_rows, edges, unresolved, private = [], [], [], []
    query_fact, query_roles = [], []
    function_sites: list[tuple[str, str, int, str]] = []
    total_lines = 0
    for module in sorted(modules):
        tree, lines = _parse(root, paths[module])
        total_lines += lines
        visitor = _ModuleVisitor(module, paths[module], modules)
        visitor.visit(tree)
        module_rows.append(
            {
                "module": module,
                "path": paths[module],
                "lines": lines,
                "layer": entry[module]["layer"],
                "lane": entry[module].get("lane"),
            }
        )
        edges += [
            {"from": module, "to": to, "kind": kind, "line": line}
            for to, kind, line in visitor.edges
        ]
        unresolved += [{"from": module, "line": line} for line in visitor.unresolved]
        private += [
            {"from": module, "to": to, "name": name, "line": line, "kind": kind}
            for to, name, line, kind in visitor.private
        ]
        query_fact += [{"module": module, "line": line} for line in visitor.fact_types]
        query_roles += [{"module": module, "line": line} for line in visitor.get_roles]
        function_sites += [(module, name, line, digest) for name, line, digest in visitor.functions]

    edge_key = lambda e: (e["from"], e["to"], e["line"], e["kind"])
    edges.sort(key=edge_key)
    runtime_pairs = {(e["from"], e["to"]) for e in edges if e["kind"] in RUNTIME_KINDS}
    module_pairs = {(e["from"], e["to"]) for e in edges if e["kind"] == "module"}

    fan_in, fan_out = Counter(), Counter()
    for source, target in runtime_pairs:
        fan_out[source] += 1
        fan_in[target] += 1

    wrong_way, cross_lane = [], []
    for e in edges:
        if e["kind"] not in RUNTIME_KINDS:
            continue
        source, target = entry[e["from"]], entry[e["to"]]
        if rank[source["layer"]] < rank[target["layer"]]:
            wrong_way.append(dict(e, from_layer=source["layer"], to_layer=target["layer"]))
        elif source.get("lane") and target.get("lane") and source["lane"] != target["lane"]:
            cross_lane.append(dict(e, from_lane=source["lane"], to_lane=target["lane"]))
    dirty = {entry[e["from"]]["layer"] for e in wrong_way}

    by_hash = defaultdict(list)
    for module, name, line, digest in function_sites:
        by_hash[digest].append(f"{module}:{name}:{line}")
    identical = [
        {"hash": digest, "sites": sorted(sites)}
        for digest, sites in by_hash.items()
        if len({site.split(":")[0] for site in sites}) > 1
    ]
    families = []
    for family, pattern in sorted(layer_map["helper_patterns"].items()):
        regex = re.compile(pattern)
        sites = [
            {"site": f"{module}:{name}:{line}", "hash": digest}
            for module, name, line, digest in function_sites
            if regex.search(name)
        ]
        sites.sort(key=lambda s: s["site"])
        families.append(
            {
                "family": family,
                "sites": sites,
                "distinct_hashes": len({s["hash"] for s in sites}),
            }
        )

    result = {
        "schema_version": SCHEMA_VERSION,
        "scope": {
            "package": PACKAGE_DIR,
            "excluded": sorted(layer_map["excluded"]),
            "python": f"{sys.version_info.major}.{sys.version_info.minor}",
            "module_count": len(modules),
            "line_count": total_lines,
        },
        "modules": module_rows,
        "edges": edges,
        "unresolved_dynamic": sorted(unresolved, key=lambda u: (u["from"], u["line"])),
        "sccs": {
            "runtime": _sccs(modules, runtime_pairs),
            "module_only": _sccs(modules, module_pairs),
        },
        "private_imports": sorted(
            private, key=lambda p: (p["from"], p["line"], p["to"], p["name"], p["kind"])
        ),
        "fan": [{"module": m, "fan_in": fan_in[m], "fan_out": fan_out[m]} for m in sorted(modules)],
        "layering": {
            "wrong_way": wrong_way,
            "cross_lane": cross_lane,
            "clean_layers": sorted(set(rank) - dirty),
        },
        "duplicates": {
            "ast_identical": sorted(identical, key=lambda g: g["sites"]),
            "families": families,
        },
        "tests": _scan_tests(root, modules),
        "skills": {"module_citations": _scan_skills(root, modules, paths)},
        "query_sites": {
            "fact_types_reads": sorted(query_fact, key=lambda q: (q["module"], q["line"])),
            "get_roles_calls": sorted(query_roles, key=lambda q: (q["module"], q["line"])),
        },
    }
    if (root / "tools/gnd_entrypoints.json").exists() or any(
        module == "gnd.commands" or module.startswith("gnd.commands.") for module in modules
    ):
        policy_path = root / "tools/gnd_entrypoints.json"
        try:
            raw = policy_path.read_bytes()
            if len(raw) > MAP_READ_CAP:
                raise ValueError("entry-point policy exceeds read bound")
            policy = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicates,
                                parse_constant=_reject_constant)
            result["entrypoints"] = entrypoint_rule(result, policy)
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise _invalid(f"invalid entry-point policy: {error}") from None
    return result



RF5_COMMAND_GROUPS = frozenset({
    "checking", "verify", "synth", "measure", "extract", "export", "codegen",
    "conformance", "recovery", "evolve", "doccheck", "fidelity", "review", "exp",
    "solve", "lifecycle", "judgments", "witness",
})


def entrypoint_rule(metrics: dict, policy: dict) -> dict:
    """Check the nonempty RF5 entry scope against explicit import boundaries.

    Exceptions name exact source/target module pairs and a reviewable reason.
    There are no wildcard exemptions, even for historical CLI aliases.
    """
    expected = {"gnd.cli", *("gnd.commands." + name for name in RF5_COMMAND_GROUPS)}
    scope = set(policy["scope"])
    actual = {row["module"] for row in metrics["modules"]}
    actual_groups = {module for module in actual
                     if module.startswith("gnd.commands.")
                     and not module.rsplit(".", 1)[-1].startswith("_")}
    if scope != expected or not scope <= actual or actual_groups != expected - {"gnd.cli"}:
        raise ValueError("incomplete RF5 entry-point scope")
    mapped = {row["module"]: row for row in metrics["modules"]}
    for target in policy["service_targets"]:
        if target not in mapped or mapped[target]["layer"] != "lanes" or not target.endswith(
            (".service", "_service")
        ):
            raise ValueError("invalid entry-point service target")
    bindings = policy["service_bindings"]
    if set(bindings) != scope or any(
        not isinstance(targets, list) or not set(targets) <= set(policy["service_targets"])
        for targets in bindings.values()
    ):
        raise ValueError("invalid per-source entry-point service bindings")
    if {target for targets in bindings.values() for target in targets} != set(policy["service_targets"]):
        raise ValueError("unused entry-point service target")
    common = {
        "gnd.commands._arguments", "gnd.commands._output", "gnd.exits"
    }
    edge_pairs = {(edge["from"], edge["to"]) for edge in metrics["edges"]}
    exceptions = {}
    for row in policy["exceptions"]:
        if set(row) != {"source", "target", "reason"} or not row["reason"].strip():
            raise ValueError("invalid entry-point exception")
        pair = (row["source"], row["target"])
        if pair in exceptions or row["source"] not in scope or row["target"] not in actual:
            raise ValueError("invalid entry-point exception scope")
        if pair not in edge_pairs:
            raise ValueError("unused entry-point exception")
        exceptions[pair] = row["reason"]
    violations = []
    for edge in metrics["edges"]:
        source, target = edge["from"], edge["to"]
        if source not in scope:
            continue
        # The bootstrap imports exactly the declared command groups.
        if source == "gnd.cli" and target in expected - {"gnd.cli"}:
            continue
        if target in common or target in bindings[source] or (source, target) in exceptions:
            continue
        violations.append(dict(edge, rule="entry-point imports a non-service module"))
    return {"scope": sorted(scope), "violations": violations,
            "exceptions": policy["exceptions"]}


# ---------------------------------------------------------------- compare


def _git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise _invalid(f"git failed: {error}") from None
    if result.returncode != 0:
        raise _invalid(f"git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout


def compare(root: Path, base: str, head: str) -> dict:
    base_sha = _git(root, "rev-parse", "--verify", f"{base}^{{commit}}").strip()
    head_sha = _git(root, "rev-parse", "--verify", f"{head}^{{commit}}").strip()
    diff = _git(
        root, "diff", "-U0", "--no-color", "--no-renames", base_sha, head_sha, "--", PACKAGE_DIR
    )
    added, removed = defaultdict(list), defaultdict(list)
    old = new = None
    in_header = False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            in_header, old, new = True, None, None
        elif in_header and line.startswith("@@"):
            in_header = False
        elif in_header and line.startswith("--- "):
            old = None if line == "--- /dev/null" else line[6:]
        elif in_header and line.startswith("+++ "):
            new = None if line == "+++ /dev/null" else line[6:]
        elif in_header:
            continue
        elif line.startswith("+") and new is not None:
            added[new].append(line[1:].strip())
        elif line.startswith("-") and old is not None:
            removed[old].append(line[1:].strip())
    pool = defaultdict(Counter)
    for path, lines in removed.items():
        pool[path].update(text for text in lines if text)
    moved_in, moved_out = Counter(), Counter()
    for path in sorted(added):
        for text in added[path]:
            if not text:
                continue
            for source in sorted(pool):
                if source != path and pool[source][text] > 0:
                    pool[source][text] -= 1
                    moved_in[path] += 1
                    moved_out[source] += 1
                    break
    files = sorted(set(added) | set(removed))
    rows = [
        {
            "path": p,
            "added": len(added[p]),
            "removed": len(removed[p]),
            "moved_in": moved_in[p],
            "moved_out": moved_out[p],
        }
        for p in files
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "base": base_sha,
        "head": head_sha,
        "files": rows,
        "totals": {
            key: sum(row[key] for row in rows)
            for key in ("added", "removed", "moved_in", "moved_out")
        },
    }


# ---------------------------------------------------------------- CLI


def _write(path: Path, payload: dict) -> None:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=1, allow_nan=False)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="gnd_arch.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("measure", help="measure src/gnd against the layer map")
    m.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    m.add_argument("--layers", type=Path)
    m.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("compare", help="count added, removed and moved lines between revisions")
    c.add_argument("base")
    c.add_argument("head")
    c.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    c.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.out.exists() or args.out.is_symlink():
            raise ToolError(11, f"--out already exists: {args.out}")
        if not args.out.parent.is_dir():
            raise ToolError(3, f"--out parent directory does not exist: {args.out.parent}")
        if args.command == "measure":
            layers = args.layers or args.root / "tools" / "gnd_layers.json"
            payload = measure(args.root, layers)
        else:
            payload = compare(args.root, args.base, args.head)
        _write(args.out, payload)
    except ToolError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return error.code
    except FileExistsError:
        print(f"ERROR: --out already exists: {args.out}", file=sys.stderr)
        return 11
    except OSError as error:
        print(f"ERROR: cannot write --out {args.out}: {error.strerror}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
