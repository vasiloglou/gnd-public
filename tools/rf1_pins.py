"""RF1 characterization-pin tool (code-refactoring milestone, phase RF1).

    rf1_pins.py capture --out DIR [--root REPO]
    rf1_pins.py merge --out DIR CAPTURE...
    rf1_pins.py mutate --out DIR [--root REPO] [--table PATH] [--source REL]
                       [--tests REL ...] [--only ID ...] [--timeout SECONDS] [--jobs N]

capture runs the RF1 pin files with GND_RF1_CAPTURE=DIR/<pyXY> under the current
interpreter. merge combines captures from several interpreters into one golden
tree plus goldens.sha256: a golden whose bytes agree everywhere is stored once,
and one that differs is stored per minor version (decision D2). mutate is the
RF1-C1 instrument: for each seeded mutation it copies the source package, applies
the row, runs the named pin nodes in a subprocess and requires every one to fail.

Exit codes: 0 done (every row killed and the control green); 1 a pytest run
failed, a row survived or timed out, or the control was red; 2 usage; 3 an
invalid table or tree; 11 --out already exists (nothing written).
Spec: .gnd-planning/milestones/code-refactoring/notes/phase-RF1-spec.md, 6.9.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TABLE = "tests/fixtures/rf1-pins/mutations.json"
DEFAULT_SOURCE = "src/gnd"
PIN_FILES = (
    "tests/test_rf1_cli_pins.py",
    "tests/test_rf1_helper_pins.py",
    "tests/test_rf1_semantic_pins.py",
    "tests/test_rf1_agent_cli_pins.py",
    "tests/test_rf1_session_pins.py",
)
MAX_TABLE_BYTES = 1024 * 1024
MINORS = ("py311", "py313", "py314")
ROW_KEYS = {"id", "file", "old", "new", "expect_red"}
OUTCOME_PLUGIN = '''
import json, os
_PATH = os.environ["RF1_OUTCOMES"]
def pytest_runtest_logreport(report):
    if report.when == "call" or report.outcome != "passed":
        with open(_PATH, "a", encoding="utf-8") as stream:
            stream.write(json.dumps({"node": report.nodeid, "when": report.when, "outcome": report.outcome}) + "\\n")
'''


class ToolError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def _invalid(message: str) -> ToolError:
    return ToolError(3, message)


def _canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=1) + "\n").encode()


def _fresh_out(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise ToolError(11, f"{path} already exists; nothing written")


# --- table ------------------------------------------------------------------

def _reject_duplicates(pairs):
    document = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key {key!r}")
        document[key] = value
    return document


def _reject_constant(name):
    raise ValueError(f"non-finite JSON constant {name}")


def load_table(path: Path) -> dict:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_TABLE_BYTES + 1)
    except OSError as error:
        raise _invalid(f"{path}: {error.strerror or error}") from None
    if len(raw) > MAX_TABLE_BYTES:
        raise _invalid(f"{path}: over {MAX_TABLE_BYTES} bytes")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        raise _invalid(f"{path}: {error}") from None
    if not isinstance(data, dict) or set(data) != {"schema_version", "rows", "exempt"} or data["schema_version"] != 1:
        raise _invalid(f"{path}: expected an object with schema_version 1, rows and exempt")
    exempt = data["exempt"]
    if not isinstance(exempt, list) or not all(
        isinstance(item, dict) and set(item) == {"node", "reason"}
        and all(isinstance(item[key], str) and item[key] for key in ("node", "reason"))
        for item in exempt
    ):
        raise _invalid(f"{path}: exempt must be a list of {{node, reason}} objects")
    rows = data["rows"]
    if not isinstance(rows, list) or not rows:
        raise _invalid(f"{path}: rows must be a non-empty list")
    seen = set()
    for index, row in enumerate(rows):
        where = f"{path}: rows[{index}]"
        if not isinstance(row, dict) or set(row) != ROW_KEYS:
            raise _invalid(f"{where}: expected exactly the keys {sorted(ROW_KEYS)}")
        if not all(isinstance(row[key], str) and row[key] for key in ("id", "file", "old")) or not isinstance(row["new"], str):
            raise _invalid(f"{where}: id, file and old must be non-empty strings and new a string")
        if row["old"] == row["new"]:
            raise _invalid(f"{where}: old and new are equal")
        nodes = row["expect_red"]
        if not isinstance(nodes, list) or not nodes or not all(isinstance(node, str) and node for node in nodes):
            raise _invalid(f"{where}: expect_red must be a non-empty list of node ids")
        if row["id"] in seen:
            raise _invalid(f"{where}: duplicate id {row['id']!r}")
        seen.add(row["id"])
    if path.resolve() == (ROOT / DEFAULT_TABLE).resolve():
        retarget_path = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/mutation-retargets.json'
        if retarget_path.is_file():
            try:
                text = retarget_path.read_text()
                if len(text.encode()) > MAX_TABLE_BYTES:
                    raise ValueError('retarget over byte cap')
                retarget = json.loads(text, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
                if hashlib.sha256(raw).hexdigest() != retarget['table_sha256']:
                    raise ValueError('historical mutation table identity changed')
                if not isinstance(retarget['rows'], list):
                    raise TypeError('retarget rows must be a list')
                by_id = {r['id']: r for r in data['rows']}
                seen_retargets = set()
                for row in retarget['rows']:
                    if row['id'] in seen_retargets:
                        raise ValueError('duplicate mutation retarget')
                    seen_retargets.add(row['id'])
                    original = by_id[row['id']]
                    if any(original[k] != row[k] for k in ('old', 'new', 'expect_red')) or original['file'] != row['before_file']:
                        raise ValueError('mutation retarget changed meaning')
                    if (not isinstance(row['after_file'], str) or not row['after_file']
                            or not isinstance(row['after_old'], str) or not row['after_old']
                            or not isinstance(row['after_new'], str) or row['after_old'] == row['after_new']):
                        raise ValueError('invalid mutation successor fields')
                    original['file'] = row['after_file']
                    original['old'] = row['after_old']
                    original['new'] = row['after_new']
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise _invalid(f'invalid mutation retarget: {error}') from None
    return data


def validate_rows(root: Path, source: str, rows: list[dict]) -> None:
    base = (root / source).resolve()
    for row in rows:
        target = (root / row["file"]).resolve()
        if base not in target.parents or not target.is_file():
            raise _invalid(f"{row['id']}: {row['file']} is not a file under {source}")
        count = target.read_text(encoding="utf-8").count(row["old"])
        if count != 1:
            raise _invalid(f"{row['id']}: snippet occurs {count} times in {row['file']} (exactly 1 required)")


def collect(root: Path, tests: list[str], env: dict, source: str) -> set[str]:
    env = dict(env)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str((root / source).parent), env.get("PYTHONPATH", "")]))
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *tests],
        cwd=root, env=env, capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        raise _invalid(f"collection failed:\n{completed.stdout[-2000:]}{completed.stderr[-2000:]}")
    return {line.strip() for line in completed.stdout.splitlines() if "::" in line and not line.startswith(" ")}


def validate_coverage(rows: list[dict], exempt: list[dict], collected: set[str]) -> None:
    named = {node for row in rows for node in row["expect_red"]}
    excused = {item["node"] for item in exempt}
    unknown = sorted((named | excused) - collected)
    overlap = sorted(named & excused)
    uncovered = sorted(collected - named - excused)
    if overlap:
        raise _invalid("nodes are both exempt and named by a row: " + ", ".join(overlap[:20]))
    if unknown:
        raise _invalid("rows name nodes that do not collect: " + ", ".join(unknown[:20]))
    if uncovered:
        raise _invalid(f"{len(uncovered)} pin nodes have no mutation row: " + ", ".join(uncovered[:20]))


# --- mutate -----------------------------------------------------------------

def _copy_source(root: Path, source: str, work: Path) -> Path:
    destination = work / "src" / Path(source).name
    shutil.copytree(root / source, destination, ignore=shutil.ignore_patterns("__pycache__"))
    return work / "src"


def _run_nodes(root: Path, nodes: list[str], pythonpath: Path, work: Path, env: dict, timeout: float) -> dict:
    """Run nodes against the copied source; return {node: 'passed'|'failed'} or {'<timeout>': ...}."""
    outcomes = work / "outcomes.jsonl"
    plugin_dir = work / "plugin"
    plugin_dir.mkdir(exist_ok=True)
    (plugin_dir / "rf1_outcomes.py").write_text(OUTCOME_PLUGIN, encoding="utf-8")
    run_env = dict(env)
    run_env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(pythonpath), str(plugin_dir), env.get("PYTHONPATH", "")]))
    run_env["RF1_OUTCOMES"] = str(outcomes)
    run_env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "rf1_outcomes", *nodes],
            cwd=root, env=run_env, capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"<timeout>": "timed-out"}
    events: dict[str, list[tuple[str, str]]] = {}
    if outcomes.exists():
        for line in outcomes.read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            events.setdefault(event["node"], []).append((event["when"], event["outcome"]))
    result = {}
    for node in nodes:
        seen = events.get(node, [])
        # A kill is a failing assertion: only a call-phase failure counts
        # (review finding RF1-09). A setup or teardown failure is an error,
        # which neither kills a row nor lets the control pass.
        if ("call", "failed") in seen:
            result[node] = "failed"
        elif any(outcome == "failed" for _when, outcome in seen):
            result[node] = "error"
        elif ("call", "passed") in seen:
            result[node] = "passed"
        elif any(outcome == "skipped" for _when, outcome in seen):
            result[node] = "skipped"
        else:
            result[node] = "missing"
    return result


def _probe_env(root: Path) -> dict:
    env = dict(os.environ)
    env.pop("GND_RF1_CAPTURE", None)
    return env


def mutate(args: argparse.Namespace) -> int:
    out = Path(args.out)
    _fresh_out(out)
    root = Path(args.root).resolve()
    table = load_table(root / args.table)
    rows = table["rows"]
    validate_rows(root, args.source, rows)
    env = _probe_env(root)
    collected = collect(root, list(args.tests), env, args.source)
    validate_coverage(rows, table["exempt"], collected)
    if args.only:
        rows = [row for row in rows if row["id"] in set(args.only)]
        if not rows:
            raise _invalid("--only selected no rows")
    out.mkdir(parents=True)
    all_nodes = sorted({node for row in rows for node in row["expect_red"]})
    with tempfile.TemporaryDirectory(prefix="rf1-control-") as temporary:
        work = Path(temporary)
        control = _run_nodes(root, all_nodes, _copy_source(root, args.source, work), work, env, args.timeout * 4)
    red = sorted(node for node, outcome in control.items() if outcome != "passed")
    (out / "control.txt").write_text(
        f"control nodes: {len(all_nodes)}\nnot passing: {len(red)}\n" + "".join(f"  {node}\n" for node in red),
        encoding="utf-8",
    )
    if red:
        print(f"control red: {len(red)} of {len(all_nodes)} nodes do not pass unmutated", file=sys.stderr)
        return 1

    def run_row(row: dict) -> dict:
        with tempfile.TemporaryDirectory(prefix="rf1-mutant-") as temporary:
            work = Path(temporary)
            pythonpath = _copy_source(root, args.source, work)
            target = pythonpath / Path(args.source).name / Path(row["file"]).relative_to(args.source)
            text = target.read_text(encoding="utf-8")
            target.write_text(text.replace(row["old"], row["new"], 1), encoding="utf-8")
            outcomes = _run_nodes(root, row["expect_red"], pythonpath, work, env, args.timeout)
        if "<timeout>" in outcomes:
            return {"id": row["id"], "status": "timed-out", "nodes": {}}
        killed = all(outcomes.get(node) == "failed" for node in row["expect_red"])
        return {"id": row["id"], "status": "killed" if killed else "survived", "nodes": outcomes}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(run_row, rows))
    report = {
        "schema_version": 1,
        "control_nodes": len(all_nodes),
        "rows": {result["id"]: {"status": result["status"], "nodes": result["nodes"]} for result in results},
        "killed": sum(result["status"] == "killed" for result in results),
        "total": len(results),
    }
    (out / "mutation-report.json").write_bytes(_canonical(report))
    failed = [result["id"] for result in results if result["status"] != "killed"]
    print(f"rows: {len(results)}  killed: {report['killed']}  not killed: {len(failed)}")
    for row_id in failed:
        print(f"  {row_id}: {report['rows'][row_id]['status']}")
    return 1 if failed else 0


# --- capture and merge --------------------------------------------------------

def capture(args: argparse.Namespace) -> int:
    out = Path(args.out)
    _fresh_out(out)
    root = Path(args.root).resolve()
    tag = f"py{sys.version_info.major}{sys.version_info.minor}"
    target = out / tag
    target.parent.mkdir(parents=True)
    env = _probe_env(root)
    env["GND_RF1_CAPTURE"] = str(target.resolve())
    completed = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *PIN_FILES],
                               cwd=root, env=env, check=False)
    return 0 if completed.returncode == 0 else 1


def _files(root: Path) -> dict[str, bytes]:
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*.json"))}


def merge(args: argparse.Namespace) -> int:
    out = Path(args.out)
    _fresh_out(out)
    captures = {}
    for raw in args.captures:
        path = Path(raw)
        if path.name not in MINORS or not path.is_dir():
            raise _invalid(f"{path}: a capture directory must be named one of {', '.join(MINORS)}")
        captures[path.name] = _files(path)
    if set(captures) != set(MINORS):
        raise _invalid(f"merge needs exactly the captures {', '.join(MINORS)}")
    keys = set().union(*(set(files) for files in captures.values()))
    missing = sorted(key for key in keys if any(key not in files for files in captures.values()))
    if missing:
        raise _invalid("captures disagree on their key set: " + ", ".join(missing[:20]))
    written: dict[str, bytes] = {}
    for key in sorted(keys):
        variants = {tag: captures[tag][key] for tag in MINORS}
        if len(set(variants.values())) == 1:
            written[key] = variants[MINORS[0]]
        else:
            stem = key.removesuffix(".json")
            for tag, data in variants.items():
                written[f"{stem}.{tag}.json"] = data
    for relative, data in written.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    manifest = "".join(f"{hashlib.sha256(data).hexdigest()}  {relative}\n" for relative, data in sorted(written.items()))
    (out.parent / "goldens.sha256").write_text(manifest, encoding="utf-8")
    keyed = sorted({relative.rsplit(".", 2)[0] for relative in written if relative.endswith(tuple(f".{t}.json" for t in MINORS))})
    print(f"goldens: {len(written)} files; interpreter-keyed keys: {len(keyed)}")
    for key in keyed:
        print(f"  {key}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="rf1_pins.py")
    commands = parser.add_subparsers(dest="command", required=True)
    cap = commands.add_parser("capture")
    cap.add_argument("--out", required=True)
    cap.add_argument("--root", default=str(ROOT))
    mer = commands.add_parser("merge")
    mer.add_argument("--out", required=True)
    mer.add_argument("captures", nargs="+")
    mut = commands.add_parser("mutate")
    mut.add_argument("--out", required=True)
    mut.add_argument("--root", default=str(ROOT))
    mut.add_argument("--table", default=DEFAULT_TABLE)
    mut.add_argument("--source", default=DEFAULT_SOURCE)
    mut.add_argument("--tests", nargs="+", default=list(PIN_FILES))
    mut.add_argument("--only", nargs="+")
    mut.add_argument("--timeout", type=float, default=300.0)
    mut.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        return {"capture": capture, "merge": merge, "mutate": mutate}[args.command](args)
    except ToolError as error:
        print(str(error), file=sys.stderr)
        return error.code


if __name__ == "__main__":
    raise SystemExit(main())
