"""Run reviewed public acceptance lanes; incomplete mapping never passes."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from support.public_migration import (
    MigrationRefusal,
    load_case_map,
    strict_json,
    validate_case_map,
    validate_progress_counts,
    validate_surface_map,
)
from support.public_review_storage import LEAF_PINS, PACK_PINS, migration_view

MIGRATION = Path(".gnd-planning/milestones/public-launch/migration")
IDENTITY_SHA256 = "4d67ea0b0790f9860682267ea63d15c2e490318f14125256807b9e6c877fcaf3"
ORIGINAL_COUNT = 5331
MAX_STREAM_BYTES = 1_048_576
MAX_RECEIPT_BYTES = 8_388_608
REQUIRED_GATES = ("tests/test_public_generated_examples.py", "tests/test_public_optional.py", "tests/test_yaml_comment_neighbor.py", "tests/test_transition_mapping_totality.py", "tests/test_public_alias_schema_guards.py")


def require(condition, reason):
    if not condition:
        raise MigrationRefusal(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_bytes(path, cap=MAX_STREAM_BYTES):
    require(".." not in path.parts, "traversal-input")
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink-input")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "nonregular-input")
            raw = stream.read(cap + 1)
        require(len(raw) <= cap, "oversize-input")
        return raw
    except OSError as error:
        raise MigrationRefusal("unreadable-input") from error


def document(path):
    # Documents are a single strict JSON value; pretty formatting is not JSONL.
    raw = read_bytes(path, cap=MAX_RECEIPT_BYTES)
    try:
        if raw.startswith(b"\x1f\x8b"):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(MAX_RECEIPT_BYTES + 1)
        require(len(raw) <= MAX_RECEIPT_BYTES, "oversize-document")
        value = strict_json(raw.decode("utf-8"))
        require(isinstance(value, dict), "invalid-document-shape")
        return value
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise MigrationRefusal("unreadable-document") from error


def audit(root):
    # Reuse the already tested exact attribution/size auditor.
    from test_public_distribution import audit_tree

    try:
        return audit_tree(root)
    except (AssertionError, OSError, ValueError, KeyError, TypeError) as error:
        raise MigrationRefusal("content-audit-refused") from error


def collection_sets(value):
    require(isinstance(value, dict) and set(value) == {"status", "selected", "deselected"},
            "invalid-collection-shape")
    lanes = {}
    seen = set()
    for lane in ("selected", "deselected"):
        require(isinstance(value[lane], list) and len(value[lane]) <= 50_000,
                "invalid-collection-shape")
        nodes = set()
        for row in value[lane]:
            require(isinstance(row, dict) and set(row) == {"node", "markers"},
                    "invalid-collection-shape")
            node = row["node"]
            require(isinstance(node, str) and node.startswith("tests/") and "::" in node,
                    "invalid-collected-node")
            path = Path(node.split("::", 1)[0])
            require(".." not in path.parts and "\\" not in str(path), "invalid-collected-node")
            require(node not in seen, "duplicate-collected-node")
            require(isinstance(row["markers"], list) and
                    all(isinstance(m, str) for m in row["markers"]) and
                    row["markers"] == sorted(set(row["markers"])), "invalid-markers")
            seen.add(node)
            nodes.add(node)
        lanes[lane] = nodes
    require(len(seen) <= 50_000, "invalid-collection-shape")
    return lanes["selected"], lanes["deselected"]


def plan(rows, *, originals, collection, private, surfaces, expected_surfaces):
    """Pure planning instrument; CLI supplies byte-pinned production inputs."""
    selected, deselected = collection_sets(collection)
    validate_case_map(rows, originals=originals, collected=selected | deselected,
                      retained_private=private)
    validate_surface_map(surfaces, surfaces=expected_surfaces, collected=selected | deselected)
    nodes = set()
    for row in rows:
        if row["selection"] == "default":
            require(set(row["target_nodes"]) <= selected, "default-node-deselected")
            nodes.update(row["target_nodes"])
        elif row["selection"] == "optional-unverified":
            require(set(row["target_nodes"]) <= deselected, "optional-node-selected")
    for row in surfaces["surfaces"]:
        if row["execution"] == "current":
            require(bool(set(row["target_nodes"]) & nodes), "surface-outside-default")
    require(bool(nodes), "empty-default-selection")
    return tuple(sorted(nodes))


def preflight(root, mapping):
    manifest = audit(root)
    by_path = {row["path"]: row for row in manifest["files"]}
    migration = root / MIGRATION
    raw = read_bytes(migration / "original-identities.json")
    require(digest(raw) == IDENTITY_SHA256, "original-identities-digest-mismatch")
    originals = strict_json(raw.decode("utf-8"))
    require(isinstance(originals, dict) and len(originals) == ORIGINAL_COUNT,
            "original-identities-count-mismatch")
    require(set(originals) == {f"source-case-{i:05d}" for i in range(ORIGINAL_COUNT)},
            "original-identities-roster-mismatch")
    if mapping.exists() or (mapping.name in LEAF_PINS and mapping.name.endswith("-case-map.jsonl.gz")):
        require(mapping.parent == migration, "mapping-outside-migration")
        selected_names = [mapping.name]
    else:
        require(mapping == migration / "b3-case-map.jsonl.gz", "missing-mapping")
        selected_names = None
    rows = []
    with migration_view(migration) as logical:
        paths = ([logical / name for name in selected_names] if selected_names is not None
                 else sorted(logical.glob("*-case-map.jsonl.gz")))
        require(bool(paths), "missing-mapping")
        for path in paths:
            require(path.parent == logical, "mapping-outside-migration")
            rel = (migration / path.name).relative_to(root).as_posix()
            if rel not in by_path:
                # Packed leaves remain independently byte-pinned and physically attributed
                # by the approved bounded pack; unreviewed physical shards cannot use it.
                require(not (migration / path.name).exists() and path.name in LEAF_PINS,
                        "unattributed-mapping")
                require(all((migration / name).relative_to(root).as_posix() in by_path
                            for name in PACK_PINS), "unattributed-mapping")
                require(digest(read_bytes(path)) == LEAF_PINS[path.name], "mapping-digest-mismatch")
            require(len(read_bytes(path)) < MAX_STREAM_BYTES, "oversize-shard")
            rows.extend(load_case_map(path))
            require(len(rows) <= 10_000, "too-many-rows")
    collection = document(migration / "collection.json.gz")
    selected, deselected = collection_sets(collection)
    policy = document(migration / "retained-private-policy.json.gz")
    require(isinstance(policy.get("originals"), dict), "invalid-private-policy")
    validate_progress_counts(document(migration / "progress.json"), tuple(rows),
                             original_count=ORIGINAL_COUNT)
    # Missing originals refuse before any wheel build, test or optional invocation.
    validate_case_map(tuple(rows), originals=originals, collected=selected | deselected,
                      retained_private=policy["originals"])
    inventory = document(migration / "b3-surface-inventory.json")
    require(set(inventory) == {"surfaces"} and isinstance(inventory["surfaces"], list) and
            all(isinstance(s, str) and s for s in inventory["surfaces"]) and
            len(inventory["surfaces"]) == len(set(inventory["surfaces"])), "invalid-surfaces")
    nodes = set(plan(tuple(rows), originals=originals, collection=collection,
                     private=policy["originals"], surfaces=document(migration / "b3-surfaces.json"),
                     expected_surfaces=set(inventory["surfaces"])))
    for module in REQUIRED_GATES:
        require((root / module).is_file() and module in by_path, "missing-required-gate")
        gate_nodes = {n for n in selected if n.split("::", 1)[0] == module}
        require(bool(gate_nodes), "uncollected-required-gate")
        nodes.update(gate_nodes)
    return manifest, tuple(sorted(nodes))


def clean_environment(home=None, executable_dir=None):
    env = {key: os.environ[key] for key in
           ("LANG", "LC_ALL", "TZ", "SYSTEMROOT", "SSL_CERT_FILE", "SSL_CERT_DIR")
           if key in os.environ}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
               PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    env["PATH"] = os.pathsep.join(filter(None, [str(executable_dir) if executable_dir else None,
                                              str(Path(shutil.which("uv")).parent)
                                              if shutil.which("uv") else None, os.defpath]))
    if home is not None:
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
    return env


def command(argv, *, cwd, env, timeout=1800):
    """Bound reads and the complete process group, including inherited pipes."""
    print(json.dumps({"command": list(map(str, argv))}), flush=True)
    proc = subprocess.Popen(list(map(str, argv)), cwd=cwd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + timeout
    refusal = None
    with selectors.DefaultSelector() as selector:
        for label, stream in (("stdout", proc.stdout), ("stderr", proc.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, label)
        while selector.get_map():
            if time.monotonic() >= deadline:
                refusal = "stage-timeout"
                break
            for key, _ in selector.select(min(0.1, max(0, deadline - time.monotonic()))):
                remaining = MAX_STREAM_BYTES - len(streams[key.data])
                chunk = os.read(key.fd, min(4096, remaining + 1))
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                elif len(chunk) > remaining:
                    refusal = "stage-output-cap"
                    break
                else:
                    streams[key.data].extend(chunk)
            if refusal:
                break
    if refusal or proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=5)
    for stream in (proc.stdout, proc.stderr):
        if not stream.closed:
            stream.close()
    for label, raw in streams.items():
        text = bytes(raw).decode("utf-8", "replace")
        if text:
            print(json.dumps({label: text}), flush=True)
    if refusal:
        raise MigrationRefusal(refusal)
    result = {"exit": proc.returncode,
              "argv_sha256": digest(json.dumps(list(map(str, argv)), separators=(",", ":")).encode()),
              **{label + "_sha256": digest(bytes(raw)) for label, raw in streams.items()}}
    require(proc.returncode == 0, "stage-failed")
    return result


WORKER = r'''
import importlib.metadata, json, pathlib, sys, pytest, gnd
root, request, output, origin, metadata_origin = map(pathlib.Path, sys.argv[1:6])
nodes = json.loads(request.read_text())
class Selection:
    def __init__(self): self.passed=set(); self.skipped=set(); self.selected=[]
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, session, config, items):
        chosen=[item for item in items if item.nodeid in nodes]
        rejected=[item for item in items if item.nodeid not in nodes]
        if rejected: config.hook.pytest_deselected(items=rejected)
        items[:]=chosen
        self.selected=[item.nodeid for item in items]
        if any(not pathlib.Path(item.path).resolve().is_relative_to(root.resolve()/'tests') for item in items):
            raise pytest.UsageError('test origin refused')
        if len(self.selected)!=len(set(self.selected)) or set(self.selected)!=set(nodes):
            raise pytest.UsageError('exact requested selection was not collected')
    def pytest_runtest_logreport(self, report):
        if report.skipped: self.skipped.add(report.nodeid)
        if report.when=='call' and report.passed: self.passed.add(report.nodeid)
plugin=Selection()
modules=sorted({n.split('::',1)[0] for n in nodes})
code=pytest.main(['-q','-c',str(root/'pyproject.toml'),'--rootdir',str(root),
 '--confcutdir',str(root/'tests'),'-o','pythonpath=','--tb=short',*modules],plugins=[plugin])
for name,module in tuple(sys.modules.items()):
    if name=='gnd' or name.startswith('gnd.'):
        path=getattr(module,'__file__',None)
        if path and not pathlib.Path(path).resolve().is_relative_to(origin.resolve()):
            raise SystemExit('runtime import origin refused')
metadata=importlib.metadata.distribution('get-nick-done')
if not pathlib.Path(metadata.locate_file('')).resolve().is_relative_to(metadata_origin.resolve()):
    raise SystemExit('distribution metadata origin refused')
if code==0 and (plugin.skipped or plugin.passed!=set(nodes)): code=1
output.write_text(json.dumps({'exit':int(code),'selected':plugin.selected,
 'passed':sorted(plugin.passed),'skipped':sorted(plugin.skipped),
 'runtime_origin_checked':True,'metadata_origin_checked':True}))
raise SystemExit(code)
'''


def execute_nodes(root, nodes, *, python, origin, metadata_origin, scratch, env, prefix=()):
    require(bool(nodes) and len(nodes) <= 50_000 and len(nodes) == len(set(nodes)),
            "invalid-execution-selection")
    request = scratch / "requested.json"
    output = scratch / "observed.json"
    request.write_text(json.dumps(nodes))
    result = command([*prefix, python, "-c", WORKER, root, request, output, origin, metadata_origin],
                     cwd=root, env=env)
    observed = document(output)
    require(observed.get("exit") == 0 and set(observed.get("passed", [])) == set(nodes) and
            not observed.get("skipped") and set(observed.get("selected", [])) == set(nodes),
            "execution-selection-mismatch")
    return {"stage": result, "observation": observed}


def isolation_prefix(forbidden):
    """Hide the checkout workspace parent; the export and venv live outside it."""
    if sys.platform == "darwin":
        executable = shutil.which("sandbox-exec")
        require(bool(executable), "installed-isolation-unavailable")
        profile = '(version 1)(allow default)(deny file-read* (subpath ' + json.dumps(str(forbidden)) + '))'
        return [executable, "-p", profile]
    executable = shutil.which("bwrap")
    require(bool(executable), "installed-isolation-unavailable")
    return [executable, "--ro-bind", "/", "/", "--tmpfs", str(forbidden),
            "--dev-bind", "/dev", "/dev", "--proc", "/proc", "--"]


def installed(root, manifest, nodes, scratch):
    export = scratch / "export"
    export.mkdir()
    for row in manifest["files"]:
        source, target = root / row["path"], export / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if row["kind"] == "installer-link":
            target.symlink_to(row["link_value"])
        else:
            target.write_bytes(read_bytes(source))
            target.chmod(row["mode"])
    shutil.copy2(root / MIGRATION / "b3-files.json", export / MIGRATION / "b3-files.json")
    require(not (export / ".git").exists(), "export-has-git-history")
    home = scratch / "home"
    home.mkdir()
    env = clean_environment(home)
    stages = []
    stages.append(command(["uv", "--version"], cwd=scratch, env=env, timeout=60))
    # The scoped source protocol pins the executable build profile.
    version = subprocess.run(["uv", "--version"], cwd=scratch, env=env,
                             capture_output=True, text=True, check=False, timeout=60)
    require(version.returncode == 0 and version.stdout.split()[:2] == ["uv", "0.10.10"],
            "unsupported-build-profile")
    artifacts = scratch / "artifacts"
    stages.append(command(["uv", "build", "--wheel", "--out-dir", artifacts], cwd=export, env=env))
    wheels = list(artifacts.glob("*.whl"))
    require(len(wheels) == 1, "unexpected-wheel-set")
    venv = scratch / "venv"
    stages.append(command(["uv", "venv", "--python", Path(sys.executable).resolve(), venv],
                          cwd=scratch, env=env))
    python = venv / "bin/python"
    stages.append(command(["uv", "pip", "install", "--python", python, wheels[0]],
                          cwd=scratch, env=env))
    env = clean_environment(home, venv / "bin")
    prefix = isolation_prefix(root.parent.resolve())
    base_probe = """import importlib.util
from random import Random
from gnd import api
from gnd.synth.values import make_value, SynthDependencyError
assert importlib.util.find_spec('faker') is None
assert importlib.util.find_spec('pytest') is None
assert api.__all__ == ('validate','check','transition','verbalize','diff','witness','replay','check_with_receipt','CheckReceipt','ReceiptRefused','EvaluationSession')
try:
    make_value('String', Random(0))
except SynthDependencyError as error:
    assert str(error) == SynthDependencyError.REMEDIATION
else:
    raise SystemExit('base-only synth dependency refusal was absent')
"""
    stages.append(command([*prefix, python, "-c", base_probe], cwd=scratch, env=env, timeout=60))
    # Prove the actual denial before treating cwd/import isolation as filesystem isolation.
    denial_probe = "import pathlib,sys; p=pathlib.Path(sys.argv[1]);\ntry: p.read_bytes()\nexcept (OSError,PermissionError): pass\nelse: raise SystemExit('checkout remained readable')"
    stages.append(command([*prefix, python, "-c", denial_probe, root / "pyproject.toml"],
                          cwd=scratch, env=env, timeout=60))
    config = tomllib.loads(read_bytes(export / "pyproject.toml").decode())
    requirements = config["dependency-groups"]["dev"] + config["project"]["optional-dependencies"]["synth"]
    require(isinstance(requirements, list) and all(isinstance(r, str) and r for r in requirements),
            "invalid-declared-test-dependencies")
    stages.append(command(["uv", "pip", "install", "--python", python, *requirements],
                          cwd=scratch, env=env))
    execution = execute_nodes(export, nodes, python=python, origin=venv, metadata_origin=venv,
                              scratch=scratch, env=env, prefix=prefix)
    return {"build_stages": stages, "execution": execution,
            "filesystem_isolation_checked": True, "noneditable_wheel": True,
            "private_history_exported": False}


def static(root):
    manifest = audit(root)
    paths = sorted(row["path"] for row in manifest["files"] if row["path"].endswith(".py") and
                   row["kind"] in {"authored", "adaptation"})
    require(bool(paths), "empty-static-selection")
    env = clean_environment()
    lint = command([sys.executable, "-m", "ruff", "check", *paths], cwd=root, env=env)
    diff = command(["git", "diff", "--check"], cwd=root, env=env, timeout=60)
    staged_diff = command(["git", "diff", "--cached", "--check"], cwd=root, env=env, timeout=60)
    return {"paths": paths, "lint": lint, "diff": diff, "staged_diff": staged_diff,
            "content_scope": "Exact attributed bytes and existing caps; manual content review remains separate."}


def publish_receipt(out, receipt):
    require(".." not in out.parts and not any(p.is_symlink() for p in (out, *out.parents)),
            "unsafe-output-path")
    raw = (json.dumps(receipt, separators=(",", ":")) + "\n").encode()
    require(len(raw) <= MAX_RECEIPT_BYTES, "oversize-receipt")
    packed = gzip.compress(raw, mtime=0)
    require(len(packed) <= MAX_STREAM_BYTES, "oversize-receipt")
    out.mkdir(parents=True, exist_ok=True)
    for number in range(1, 10_001):
        path = out / f"run-{number:04d}.json.gz"
        try:
            with path.open("xb") as stream:
                stream.write(packed)
            return path.name
        except FileExistsError:
            continue
    raise MigrationRefusal("receipt-roster-full")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", type=Path)
    parser.add_argument("--lane", choices=("default", "installed", "static"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="gnd-public-acceptance-") as temporary:
            scratch = Path(temporary).resolve()
            require(not scratch.is_relative_to(ROOT.parent), "scratch-inside-workspace")
            if args.lane == "static":
                observation = static(ROOT)
            else:
                require(args.mapping is not None, "missing-mapping-argument")
                mapping = args.mapping if args.mapping.is_absolute() else ROOT / args.mapping
                manifest, nodes = preflight(ROOT, mapping)
                if args.lane == "installed":
                    observation = installed(ROOT, manifest, nodes, scratch)
                else:
                    observation = execute_nodes(ROOT, nodes, python=sys.executable,
                                                origin=ROOT / "src/gnd", metadata_origin=Path(sys.prefix),
                                                scratch=scratch, env=clean_environment(executable_dir=Path(sys.executable).parent))
            receipt = {"lane": args.lane, "status": "selected-lane-passed", "observation": observation,
                       "limit": "One lane's current-byte observation only; no phase completion, assurance or ownership transfer."}
            name = publish_receipt(args.out, receipt)
            print(json.dumps({"status": receipt["status"], "lane": args.lane, "receipt": name}))
        return 0
    except (MigrationRefusal, OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        reason = error.reason if isinstance(error, MigrationRefusal) else "runner-input-or-stage-refused"
        print(json.dumps({"status": "refused", "lane": args.lane, "reason": reason}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
