"""Bounded supervisor for the approved, isolated Phase 6 start replay.

The context file is machine-local setup data, not certification evidence. The
retained binding records exact commits, argv, exits and stream identities. A
failed command stops the ordered walk and cannot be retried by this driver.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import selectors
import signal
import stat
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def within_deadline(elapsed_ms: float, limit_ms: float) -> bool:
    """Use the supervisor's inclusive deadline rule at execution and in controls."""
    return elapsed_ms <= limit_ms


def process_family(root_pid: int, known: set[int]) -> set[int]:
    if os.environ.get("GND_PHASE7_BACKEND") == "macos-host-venv":
        # macOS refuses exec of ps inside sandbox-exec even with allow default;
        # pgrep -P remains available and can walk the same observed family.
        pending = [root_pid, *sorted(known)]
        found: set[int] = set()
        while pending:
            parent = pending.pop()
            if parent in found:
                continue
            found.add(parent)
            result = subprocess.run(
                ["/usr/bin/pgrep", "-P", str(parent)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode not in (0, 1):
                raise OSError(f"pgrep family scan failed: {result.returncode}")
            if result.returncode == 0:
                pending.extend(int(pid) for pid in result.stdout.split())
        # Exited parents are not survivors; kill(pid, 0) is read-only liveness.
        live = set()
        for pid in found:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                continue
            live.add(pid)
        return live
    output = subprocess.check_output(["ps", "-axo", "pid=,ppid="], text=True)
    parents = {int(p): int(parent) for p, parent in (line.split() for line in output.splitlines())}
    found = {root_pid} | (set(parents) & known)
    while True:
        expanded = found | {pid for pid, parent in parents.items() if parent in found}
        if expanded == found:
            return found & set(parents)
        found = expanded


def artifact_inventory(root: Path) -> dict[str, tuple[int, int, int]]:
    """Inspect only the command-owned output tree, without following links."""
    rows = {}
    pending = [root]
    entries = 0
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            entries += 1
            if entries > 10000:
                raise ValueError("artifact file count limit")
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode):
                pending.append(path)
            elif stat.S_ISREG(info.st_mode):
                rows[path.relative_to(root).as_posix()] = (
                    info.st_size,
                    info.st_mtime_ns,
                    info.st_ino,
                )
            else:
                raise ValueError("nonregular command artifact")
    return rows


def command(
    argv: list[str],
    cwd: Path,
    out: Path,
    limits: dict,
    neutral_roots: list[Path],
    *,
    artifact_root: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    artifact_root = out if artifact_root is None else artifact_root
    artifact_root.mkdir(parents=True, exist_ok=True)
    baseline = artifact_inventory(artifact_root)
    observed = {}
    env = dict(os.environ if environment is None else environment)
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONPATH", None)
    started = time.monotonic()
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    selector = selectors.DefaultSelector()
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    assert process.stdout is not None and process.stderr is not None
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    known: set[int] = set()
    failure = None
    last_scan = 0.0
    try:
        while selector.get_map():
            now = time.monotonic()
            if now - last_scan >= 0.5:
                known |= process_family(process.pid, known)
                try:
                    observed = {
                        path: info
                        for path, info in artifact_inventory(artifact_root).items()
                        if baseline.get(path) != info
                    }
                except (OSError, ValueError):
                    failure = "artifact-inventory"
                last_scan = now
            if not within_deadline((now - started) * 1000, limits["seconds"] * 1000):
                failure = "timeout"
            if failure:
                break
            for key, _ in selector.select(0.1):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                target = captured[key.data]
                if len(target) + len(chunk) > limits[f"{key.data}_bytes"]:
                    failure = "stream-limit"
                    break
                target.extend(chunk)
            if (
                sum(len(value) for value in captured.values())
                + sum(info[0] for info in observed.values())
                > limits["retained_bytes"]
            ):
                failure = "retained-limit"
    finally:
        selector.close()
        survivors = process_family(process.pid, known)
        # Retain nested new-session descendants too; killpg alone misses them.
        if failure or any(pid != process.pid for pid in survivors):
            for pid in sorted(survivors - {process.pid}, reverse=True):
                with contextlib.suppress(ProcessLookupError):
                    os.kill(pid, signal.SIGKILL)
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except PermissionError:
                    # Darwin can return EPERM after the final group member
                    # exits. Reap it; a still-live process is never excused.
                    if process.poll() is None:
                        raise
        code = process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()
    remaining = process_family(process.pid, known)
    # A short-lived child can finish between periodic scans. Recheck after all
    # descendants have been reaped and before any success may be recorded.
    try:
        observed = {
            path: info
            for path, info in artifact_inventory(artifact_root).items()
            if baseline.get(path) != info
        }
    except (OSError, ValueError):
        failure = failure or "artifact-inventory"
    raw_stream_bytes = sum(len(value) for value in captured.values())
    artifact_bytes = sum(info[0] for info in observed.values())
    if artifact_bytes + raw_stream_bytes > limits["retained_bytes"]:
        failure = failure or "retained-limit"
    artifact_retention = []
    remaining_bytes = max(0, limits["retained_bytes"] - raw_stream_bytes)
    for path, info in sorted(observed.items()):
        retained = min(info[0], remaining_bytes)
        if retained != info[0]:
            # This is a failed command's own generated output. Retain a bounded
            # prefix and explicitly record the loss; never accept a truncation.
            with (artifact_root / path).open("r+b") as stream:
                stream.truncate(retained)
        remaining_bytes -= retained
        artifact_retention.append(
            {"path": path, "observed_bytes": info[0], "retained_bytes": retained}
        )
    streams = {}
    for name, value in captured.items():
        raw = bytes(value)
        data = raw
        for index, root in enumerate(neutral_roots):
            data = data.replace(str(root).encode(), f"<root-{index}>".encode())
        target = out / name
        target.write_bytes(data)
        streams[name] = {
            "path": name,
            "sha256": digest(target),
            "bytes": len(data),
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "raw_bytes": len(raw),
        }
    retained_argv = list(argv)
    for index, root in enumerate(neutral_roots):
        retained_argv = [value.replace(str(root), f"<root-{index}>") for value in retained_argv]
    row = {
        "argv": retained_argv,
        "argv_sha256": hashlib.sha256(
            json.dumps(argv, ensure_ascii=False, separators=(",", ":")).encode()
        ).hexdigest(),
        "exit": code,
        "seconds": time.monotonic() - started,
        "failure": failure,
        "cleanup_remaining": sorted(remaining),
        "artifacts": artifact_retention,
        "retention": "literal context/repository roots in argv and streams replaced by numbered tokens; argv_sha256 binds the original UTF-8 JSON argument vector",
        "status": "passed" if code == 0 and not failure and not remaining else "failed",
        **streams,
    }
    write(out / "result.json", row)
    return row


def stage_formal(work: Path, context: str, outputs: Path) -> list[tuple[Path, bytes]]:
    """Only the disposable publication input copy receives relocated fresh results."""
    if context not in {"phase4", "phase5"}:
        return []
    family = {"phase4": "transition", "phase5": "derivation"}[context]
    target = work / f"proof/v6/{family}/evidence/formal"
    originals = []
    for source in sorted((outputs / "formal").iterdir()):
        destination = target / source.name
        if not destination.is_file():
            raise ValueError(f"unapproved publication input: {destination.name}")
        originals.append((destination, destination.read_bytes()))
        if source.suffix == ".json":
            value = json.loads(source.read_text())
            for stream in ("stdout", "stderr"):
                value[stream]["path"] = (
                    (target / Path(value[stream]["path"]).name).relative_to(work).as_posix()
                )
            write(destination, value)
        else:
            destination.write_bytes(source.read_bytes())
    return originals


def clean_context(work: Path, commit: str, *, env: dict[str, str] | None = None) -> None:
    """Reject both index and working-tree drift outside generated output/cache."""
    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=work, text=True, env=env
    ).strip()
    if actual != commit:
        raise ValueError("replay context commit differs from its binding")
    tracked = subprocess.check_output(
        ["git", "diff", "HEAD", "--name-only", "-z"], cwd=work, env=env
    )
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=work, env=env
    )
    unexpected = []
    for raw in untracked.split(b"\0"):
        if not raw:
            continue
        path = raw.decode("utf-8", errors="strict")
        # These are the supervisor's dedicated output directory and ordinary
        # interpreter/test caches, never source or a caller-selected exception.
        if path.startswith(".gnd-planning/phase6-replay-output/"):
            continue
        if "__pycache__" in Path(path).parts or path.startswith(".pytest_cache/"):
            continue
        unexpected.append(path)
    if tracked or unexpected:
        raise ValueError("replay context is not clean at the bound commit")


def selected_nodes(argv: list[str], work: Path, out: Path, spec: dict, expected: list[str]) -> dict:
    """Collect the exact command selection before executing any selected test."""
    if "pytest" not in argv or any(arg in {"--collect-only", "--co"} for arg in argv):
        raise ValueError("node inventory requires an executable pytest command")
    collection = command(
        [*argv, "--collect-only"], work, out, spec, [work, work.resolve(), Path.home()]
    )
    if collection["status"] != "passed":
        raise ValueError("node collection did not pass")
    # The repository's frozen pytest commands all use -q, whose collection
    # format emits one literal node ID per line before its count summary.
    raw = (out / "stdout").read_text()
    actual = [line for line in raw.splitlines() if re.match(r"[^\s]+\.py::", line)]

    def normalized(node: str) -> str:
        return (
            node.replace("<root-0>", "<context-root>")
            .replace("<root-1>", "<context-root>")
            .replace(str(work), "<context-root>")
        )

    actual = [normalized(node) for node in actual]
    bound = [normalized(node) for node in expected]
    passed = actual == bound and len(actual) == len(set(actual))
    value = {
        "status": "passed" if passed else "failed",
        "expected": bound,
        "actual": actual,
        "missing": sorted(set(bound) - set(actual)),
        "added": sorted(set(actual) - set(bound)),
        "collection": collection,
    }
    write(out / "node-comparison.json", value)
    if not passed:
        raise ValueError("actual selected nodes differ from the literal node binding")
    return value


def approved_resume(root: Path, amendment: Path, replay: dict) -> tuple[dict, list[dict]]:
    overlay = json.loads(amendment.read_text())
    if overlay.get("schema_version") == 4:
        return approved_default_resume(root, replay, overlay)
    if overlay.get("schema_version") == 3:
        return approved_containment_resume(root, replay, overlay)
    if overlay.get("schema_version") == 2:
        return approved_toolchain_resume(root, amendment, replay, overlay)
    for field in ("approval", "original_manifest", "prior_results"):
        binding = overlay[field]
        if digest(root / binding["path"]) != binding["sha256"]:
            raise ValueError(f"stale resume {field}")
    approval = json.loads((root / overlay["approval"]["path"]).read_text())
    if approval["status"] != "approved":
        raise ValueError("resume requires approved amendment")
    previous = json.loads((root / overlay["prior_results"]["path"]).read_text())["results"]
    if [(row["id"], row["status"]) for row in previous] != [
        ("phase3-formal", "passed"),
        ("phase3-correspondence", "passed"),
        ("phase3-focused", "failed"),
    ]:
        raise ValueError("unexpected previous attempts")
    for row in previous:
        for stream in ("stdout", "stderr"):
            path = amendment.parent / row["id"] / row[stream]["path"]
            if digest(path) != row[stream]["sha256"]:
                raise ValueError("stale previous stream")
    if overlay["additional_start_attempt"] != {
        "id": "phase3-focused",
        "attempt": 2,
        "seconds": 900,
    } or overlay["reuse_start"] != ["phase3-formal", "phase3-correspondence"]:
        raise ValueError("unexpected retry authorization")
    if overlay["start_ceiling_seconds"] != replay["start_ceiling_seconds"] + 900:
        raise ValueError("unexpected start budget")
    return overlay, previous


def approved_toolchain_resume(root: Path, amendment: Path, replay: dict, overlay: dict):
    """One separately approved setup-failure retry, preserving both prior walks."""
    for field in (
        "approval",
        "original_manifest",
        "prior_results",
        "previous_amendment",
        "readiness",
    ):
        binding = overlay[field]
        if digest(root / binding["path"]) != binding["sha256"]:
            raise ValueError(f"stale toolchain resume {field}")
    approval = json.loads((root / overlay["approval"]["path"]).read_text())
    if approval.get("status") != "approved":
        raise ValueError("toolchain retry requires approved amendment")
    earlier_path = root / overlay["previous_amendment"]["path"]
    if json.loads(earlier_path.read_text()).get("schema_version") != 1:
        raise ValueError("toolchain retry must follow the original context amendment")
    earlier, original_attempts = approved_resume(root, earlier_path, replay)
    previous = json.loads((root / overlay["prior_results"]["path"]).read_text())
    if previous["amendment_sha256"] != digest(earlier_path) or previous["status"] != "failed":
        raise ValueError("toolchain retry has no matching failed predecessor")
    rows = previous["results"]
    expected = [
        ("phase3-focused", 2, "passed"),
        ("phase3-distribution", 1, "passed"),
        ("phase3-default", 1, "passed"),
        ("phase4-formal", 1, "failed"),
    ]
    if [(r["id"], r["attempt"], r["status"]) for r in rows] != expected:
        raise ValueError("unexpected toolchain predecessor attempts")
    for row in rows:
        name = row["id"] + ("-attempt2" if row["attempt"] == 2 else "")
        for stream in ("stdout", "stderr"):
            path = (root / overlay["prior_results"]["path"]).parent / name / row[stream]["path"]
            if digest(path) != row[stream]["sha256"]:
                raise ValueError("stale toolchain predecessor stream")
    if overlay["additional_start_attempt"] != {"id": "phase4-formal", "attempt": 2, "seconds": 600}:
        raise ValueError("unexpected toolchain retry authorization")
    if overlay["reuse_start"] != [
        "phase3-formal",
        "phase3-correspondence",
        "phase3-focused",
        "phase3-distribution",
        "phase3-default",
    ]:
        raise ValueError("unexpected successful-result reuse")
    for field in (
        "phase3_test_commit",
        "current_start_commit",
        "current_close_commit",
        "close_ceiling_seconds",
    ):
        if overlay[field] != earlier[field]:
            raise ValueError(f"toolchain repair changed {field}")
    if overlay["start_ceiling_seconds"] != earlier["start_ceiling_seconds"] + 600:
        raise ValueError("unexpected toolchain retry budget")
    if overlay["total_start_and_close_ceiling_seconds"] != (
        overlay["start_ceiling_seconds"] + overlay["close_ceiling_seconds"]
    ):
        raise ValueError("inconsistent combined replay ceiling")
    return overlay, original_attempts + rows


def approved_containment_resume(root: Path, replay: dict, overlay: dict):
    """Reuse the completed proofs; retry only the separately approved consumer."""
    for field in (
        "approval",
        "original_manifest",
        "prior_results",
        "previous_amendment",
        "readiness",
    ):
        binding = overlay[field]
        if digest(root / binding["path"]) != binding["sha256"]:
            raise ValueError(f"stale containment resume {field}")
    approval = json.loads((root / overlay["approval"]["path"]).read_text())
    if approval.get("status") != "approved":
        raise ValueError("containment retry requires approved amendment")
    earlier_path = root / overlay["previous_amendment"]["path"]
    if json.loads(earlier_path.read_text()).get("schema_version") != 2:
        raise ValueError("containment retry must follow the toolchain amendment")
    earlier, original_attempts = approved_resume(root, earlier_path, replay)
    previous_path = root / overlay["prior_results"]["path"]
    previous = json.loads(previous_path.read_text())
    if previous["amendment_sha256"] != digest(earlier_path) or previous["status"] != "failed":
        raise ValueError("containment retry has no matching failed predecessor")
    rows = previous["results"]
    if [(r["id"], r["attempt"], r["status"]) for r in rows] != [
        ("phase4-formal", 2, "passed"),
        ("phase4-correspondence", 1, "failed"),
    ]:
        raise ValueError("unexpected containment predecessor attempts")
    for row in rows:
        name = row["id"] + ("-attempt2" if row["attempt"] == 2 else "")
        for stream in ("stdout", "stderr"):
            if digest(previous_path.parent / name / row[stream]["path"]) != row[stream]["sha256"]:
                raise ValueError("stale containment predecessor stream")
    if overlay["additional_start_attempt"] != {
        "id": "phase4-correspondence",
        "attempt": 2,
        "seconds": 900,
    }:
        raise ValueError("unexpected containment retry authorization")
    if overlay["reuse_start"] != earlier["reuse_start"] + ["phase4-formal"]:
        raise ValueError("unexpected completed-proof reuse")
    for field in (
        "phase3_test_commit",
        "current_start_commit",
        "current_close_commit",
        "close_ceiling_seconds",
    ):
        if overlay[field] != earlier[field]:
            raise ValueError(f"containment repair changed {field}")
    if overlay["start_ceiling_seconds"] != earlier["start_ceiling_seconds"] + 900:
        raise ValueError("unexpected containment retry budget")
    if overlay["total_start_and_close_ceiling_seconds"] != (
        overlay["start_ceiling_seconds"] + overlay["close_ceiling_seconds"]
    ):
        raise ValueError("inconsistent combined containment ceiling")
    return overlay, original_attempts + rows


def approved_default_resume(root: Path, replay: dict, overlay: dict):
    """One default-suite repair attempt; preserve every predecessor's identity."""
    for field in (
        "approval",
        "original_manifest",
        "prior_results",
        "previous_amendment",
        "readiness",
        "repair_patch",
        "node_inventory",
        "scope_audit",
    ):
        binding = overlay[field]
        if digest(root / binding["path"]) != binding["sha256"]:
            raise ValueError(f"stale default resume {field}")
    approval = json.loads((root / overlay["approval"]["path"]).read_text())
    if approval.get("status") != "approved":
        raise ValueError("default retry requires approved amendment")
    earlier_path = root / overlay["previous_amendment"]["path"]
    if json.loads(earlier_path.read_text()).get("schema_version") != 3:
        raise ValueError("default retry must follow the containment amendment")
    earlier, original_attempts = approved_resume(root, earlier_path, replay)
    previous_path = root / overlay["prior_results"]["path"]
    previous = json.loads(previous_path.read_text())
    if previous["amendment_sha256"] != digest(earlier_path) or previous["status"] != "failed":
        raise ValueError("default retry has no matching failed predecessor")
    rows = previous["results"]
    ordered = [
        spec["id"]
        for spec in replay["commands"]
        if "start" in spec["run_at"] and spec["id"] not in earlier["reuse_start"]
    ]
    expected_ids = ordered[: ordered.index("current-default") + 1]
    expected = [
        (
            name,
            2 if name == "phase4-correspondence" else 1,
            "failed" if name == "current-default" else "passed",
        )
        for name in expected_ids
    ]
    if [(r["id"], r["attempt"], r["status"]) for r in rows] != expected:
        raise ValueError("unexpected default predecessor attempts")
    for row in rows:
        name = row["id"] + ("-attempt2" if row["attempt"] == 2 else "")
        for stream in ("stdout", "stderr"):
            if digest(previous_path.parent / name / row[stream]["path"]) != row[stream]["sha256"]:
                raise ValueError("stale default predecessor stream")
    if overlay["additional_start_attempt"] != {
        "id": "current-default",
        "attempt": 2,
        "seconds": 3600,
    }:
        raise ValueError("unexpected default retry authorization")
    if overlay["reuse_start"] != earlier["reuse_start"] + expected_ids[:-1]:
        raise ValueError("unexpected baseline result reuse")
    for field in (
        "phase3_test_commit",
        "current_close_commit",
        "close_ceiling_seconds",
        "start_ceiling_seconds",
        "total_start_and_close_ceiling_seconds",
    ):
        if overlay[field] != earlier[field]:
            raise ValueError(f"default repair changed {field}")
    readiness = json.loads((root / overlay["readiness"]["path"]).read_text())
    if (
        readiness["base_commit"] != earlier["current_start_commit"]
        or readiness["repair_commit"] != overlay["current_start_commit"]
        or readiness["patch_sha256"] != overlay["repair_patch"]["sha256"]
        or digest(root / readiness["supervisor"]["path"]) != readiness["supervisor"]["sha256"]
        or digest(root / readiness["focused_check"]["path"]) != readiness["focused_check"]["sha256"]
        or digest(root / readiness["lint_check"]["path"]) != readiness["lint_check"]["sha256"]
        or digest(root / readiness["amendment_check"]["path"])
        != readiness["amendment_check"]["sha256"]
    ):
        raise ValueError("default repair context does not match readiness")
    if overlay["node_inventory"].get("selector") != "current-default":
        raise ValueError("default repair changed another node selection")
    audit = json.loads((root / overlay["scope_audit"]["path"]).read_text())
    declaration = root / audit["declaration"]["path"]
    if (
        overlay.get("known_red_start") != {"id": "current-scope", "expected_exit": 1}
        or audit.get("context_commit") != overlay["current_start_commit"]
        or audit.get("registry_rows") != 318
        or audit.get("missing_rows") != []
        or len(audit.get("findings", [])) != 638
        or digest(declaration) != audit["declaration"].get("sha256")
    ):
        raise ValueError("default repair changed the bounded scope disposition")
    return overlay, original_attempts + rows


def admit_known_red(row: dict, stdout: Path, audit: dict, expected_exit: int) -> None:
    """Admit only the exact precomputed findings authorized by an amendment."""
    observed = json.loads(stdout.read_text())
    if (
        row["exit"] != expected_exit
        or row["failure"] is not None
        or row["cleanup_remaining"]
        or observed != audit["findings"]
    ):
        raise ValueError("scope command differs from the approved known-red disposition")
    row["disposition"] = "approved-known-red"


def run(context_file: Path, amendment: Path | None = None) -> int:
    setup = json.loads(context_file.read_text())
    root, out = Path(setup["root"]), Path(setup["out"])
    manifest = root / "proof/v6/assurance/replay.json"
    replay = json.loads(manifest.read_text())
    overlay, previous = approved_resume(root, amendment, replay) if amendment else ({}, [])
    results = []
    prior_seconds = sum(row["seconds"] for row in previous)
    ceiling = overlay.get("start_ceiling_seconds", replay["start_ceiling_seconds"])
    expected_contexts = dict(replay["contexts"])
    if overlay:
        expected_contexts.update(
            phase3=overlay["phase3_test_commit"], current=overlay["current_start_commit"]
        )
    if any(
        setup["contexts"][name]["commit"] != commit for name, commit in expected_contexts.items()
    ):
        raise ValueError("setup disagrees with approved context bindings")
    started = time.monotonic()
    for spec in replay["commands"]:
        if "start" not in spec["run_at"]:
            continue
        identifier, context = spec["id"], spec["context"]
        if identifier in overlay.get("reuse_start", []):
            continue
        retry = overlay.get("additional_start_attempt", {})
        attempt = retry["attempt"] if identifier == retry.get("id") else 1
        output_id = identifier + ("-attempt2" if attempt == 2 else "")
        if (
            time.monotonic() - started + prior_seconds + setup["setup_seconds"] + spec["seconds"]
            > ceiling
        ):
            raise TimeoutError("insufficient aggregate replay budget before command")
        work = Path(setup["contexts"][context]["path"])
        command_started = time.monotonic()
        clean_context(work, setup["contexts"][context]["commit"])
        outputs = work / ".gnd-planning/phase6-replay-output"
        outputs.mkdir(parents=True, exist_ok=True)
        argv = [item.replace("RUN_OUTPUT", str(outputs.relative_to(work))) for item in spec["argv"]]
        if "node_inventory" in spec:
            binding = (
                overlay["node_inventory"]
                if overlay.get("schema_version") == 4 and identifier == "current-default"
                else spec["node_inventory"]
            )
            inventory = root / binding["path"]
            if digest(inventory) != binding["sha256"]:
                raise ValueError("stale selected node inventory")
            nodes = json.loads(inventory.read_text())["commands"][binding["selector"]]
            selected_nodes(argv, work, out / f"{output_id}-collection", spec, nodes)
            clean_context(work, setup["contexts"][context]["commit"])
            write(
                out / f"{output_id}-selected-nodes.json",
                {
                    "inventory_sha256": binding["sha256"],
                    "selector": binding["selector"],
                    "context_commit": setup["contexts"][context]["commit"],
                    "nodes": nodes,
                    "context_root_substitution": "bound to this command's isolated worktree",
                },
            )
        print(f"START {output_id}", flush=True)
        restored = (
            stage_formal(work, context, outputs) if identifier.endswith("-correspondence") else []
        )
        try:
            limits = dict(spec)
            limits["seconds"] -= time.monotonic() - command_started
            if limits["seconds"] <= 0:
                raise TimeoutError("command admission exhausted its fixed replay bound")
            row = command(
                argv,
                work,
                out / output_id,
                limits,
                [Path(setup["scratch"]), root, Path.home()],
                artifact_root=outputs,
            )
        finally:
            for path, original in restored:
                path.write_bytes(original)
        clean_context(work, setup["contexts"][context]["commit"])
        row.update(
            id=identifier,
            attempt=attempt,
            context=context,
            commit=setup["contexts"][context]["commit"],
            admission_and_command_seconds=time.monotonic() - command_started,
        )
        accepted = row["status"] == "passed"
        if overlay.get("schema_version") == 4 and identifier == "current-scope":
            audit = json.loads((root / overlay["scope_audit"]["path"]).read_text())
            admit_known_red(
                row,
                out / output_id / "stdout",
                audit,
                overlay["known_red_start"]["expected_exit"],
            )
            accepted = True
        results.append(row)
        write(
            out / "replay-result.json",
            {
                "schema_version": 1,
                "manifest_sha256": digest(manifest),
                "stage": "start",
                "amendment_sha256": digest(amendment) if amendment else None,
                "prior_results": overlay.get("prior_results"),
                "results": results,
                "elapsed_seconds": time.monotonic() - started,
                "status": "running" if accepted else "failed",
            },
        )
        print(
            f"END {identifier}: {row['status']} exit={row['exit']} seconds={row['seconds']:.2f}",
            flush=True,
        )
        if not accepted:
            return 1
        if time.monotonic() - started + setup["setup_seconds"] > ceiling:
            raise TimeoutError("aggregate start replay ceiling")
    result = json.loads((out / "replay-result.json").read_text())
    result["status"] = (
        "completed-with-approved-known-red"
        if any(row.get("disposition") == "approved-known-red" for row in results)
        else "passed"
    )
    write(out / "replay-result.json", result)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("contexts", type=Path)
    parser.add_argument("--amendment", type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.contexts, args.amendment))
