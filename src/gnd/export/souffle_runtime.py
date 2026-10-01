"""Explicit bounded foreign execution and independent positive-proof replay."""

import json
import os
import re
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from dataclasses import replace
from pathlib import Path

from gnd import artifacts
from gnd.model import iter_derivation_clauses
from gnd.witness import io as witness_io
from gnd.witness.kernel import replay_witness
from gnd.witness.types import DEFAULT_LIMITS as PROOF_LIMITS
from gnd.witness.types import WitnessResult

from . import souffle
from .souffle_io import verify_souffle_bundle
from .souffle_types import DEFAULT_LIMITS, checked_limits


class NativeFailure(ValueError):
    def __init__(self, reason):
        self.reason = reason


def command(
    argv,
    root,
    deadline,
    cap,
    *,
    stdin=None,
    prior=0,
    output=None,
    cwd=None,
    env=None,
    output_baseline=None,
):
    # Never accumulate child pipes in memory. Poll a bounded private job and
    # kill its process group on time/volume exhaustion, including descendants.
    if time.monotonic() >= deadline:
        raise NativeFailure("tool-timeout")
    stdout, stderr = root / "stdout", root / "stderr"
    input_path = root / "stdin"
    input_path.write_bytes(stdin or b"")
    with input_path.open("rb") as inp, stdout.open("wb") as out, stderr.open("wb") as err:
        try:
            child = subprocess.Popen(
                argv, stdin=inp, stdout=out, stderr=err, start_new_session=True, cwd=cwd, env=env
            )
        except OSError:
            raise NativeFailure("tool-error") from None

        def size():
            total = prior + stdout.stat().st_size + stderr.stat().st_size
            visits = 0
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW

            def walk(fd, depth, prefix=""):
                nonlocal total, visits
                with os.scandir(fd) as entries:
                    for entry in entries:
                        visits += 1
                        if visits > 4096 or depth > 64:
                            raise NativeFailure("output-limit")
                        info = entry.stat(follow_symlinks=False)
                        relative = prefix + entry.name
                        if stat.S_ISREG(info.st_mode):
                            path = Path(output) / relative
                            if path in (stdout, stderr, input_path):
                                continue
                            baseline = (output_baseline or {}).get(relative, 0)
                            total += max(0, info.st_size - baseline)
                        elif stat.S_ISDIR(info.st_mode):
                            child_fd = os.open(entry.name, flags, dir_fd=fd)
                            try:
                                walk(child_fd, depth + 1, relative + "/")
                            finally:
                                os.close(child_fd)
                        else:
                            raise NativeFailure("output-invalid")
                        if total > cap:
                            raise NativeFailure("output-limit")

            if output:
                fd = os.open(output, flags)
                try:
                    walk(fd, 0)
                finally:
                    os.close(fd)
            return total

        try:
            while child.poll() is None:
                if time.monotonic() >= deadline:
                    raise NativeFailure("tool-timeout")
                if size() > cap:
                    raise NativeFailure("output-limit")
                time.sleep(0.01)
            if time.monotonic() >= deadline:
                raise NativeFailure("tool-timeout")
            if size() > cap:
                raise NativeFailure("output-limit")
        finally:
            # A successfully exited parent may still have live children.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                # macOS may report EPERM for an already exited group; cleanup
                # must not replace a previously established refusal.
                pass
            child.wait()
    return child.returncode, stdout.read_bytes(), stderr.read_bytes()


def prepare(bundle, executable, limits):
    verified = verify_souffle_bundle(bundle, limits=limits)
    if verified.exit_code:
        return verified, None
    if os.name != "posix":
        raise NativeFailure("tool-platform-unsupported")
    tool = shutil.which(str(executable))
    if tool is None:
        raise NativeFailure("tool-absent")
    return verified, Path(tool).resolve()


def invoke(verified, executable, limits, *, commands=None):
    start = time.monotonic()
    deadline = start + limits.native_seconds
    with tempfile.TemporaryDirectory(prefix="gnd-souffle-") as directory:
        root = Path(directory)
        bundle = root / "bundle"
        bundle.mkdir()
        for name, data in verified.files.items():
            p = bundle / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        output = root / "output"
        output.mkdir()
        import hashlib

        def identity(info):
            return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns

        h = hashlib.sha256()
        descriptor = os.open(executable, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode & (stat.S_ISUID | stat.S_ISGID):
                raise NativeFailure("tool-error")
            expected_identity = identity(info)
            for chunk in iter(lambda: stream.read(65536), b""):
                if time.monotonic() >= deadline:
                    raise NativeFailure("tool-timeout")
                h.update(chunk)
            if identity(os.fstat(stream.fileno())) != expected_identity:
                raise NativeFailure("tool-error")

        def same_executable():
            if identity(executable.lstat()) != expected_identity:
                raise NativeFailure("tool-error")

        same_executable()
        code, out, err = command(
            [str(executable), "--version"], root, deadline, limits.native_output_bytes
        )
        same_executable()
        try:
            text = (out + err).decode("utf-8")
        except UnicodeError:
            raise NativeFailure("tool-version-unsupported") from None
        if (
            code
            or not re.search(r"^Version:\s*2\.5\s*$", text, re.MULTILINE)
            or not re.search(r"^Word size:\s*64 bits\s*$", text, re.MULTILINE)
        ):
            raise NativeFailure("tool-version-unsupported")
        tool = {
            "path": str(executable),
            "sha256": h.hexdigest(),
            "version": "2.5",
            "word_size": 64,
            "native_exit": None,
        }
        argv = [
            str(executable),
            "--no-preprocessor",
            "-F",
            str(bundle / "facts"),
            "-D",
            str(output),
        ]
        if commands is not None:
            argv += ["-t", "explain"]
        argv += [str(bundle / "program.dl")]
        code, stdout, _stderr = command(
            argv,
            root,
            deadline,
            limits.native_output_bytes,
            prior=len(out) + len(err),
            stdin=commands,
            output=output,
        )
        same_executable()
        tool["native_exit"] = code
        if code:
            raise NativeFailure("tool-error")
        symbols = souffle.parse(verified.files["symbols.json"], "json")
        expected = {r["symbol"] + ".csv": r for r in symbols["relations"] if r["derived"]}
        actual = {p.name for p in output.iterdir()}
        if set(expected) - actual:
            raise NativeFailure("output-partial")
        if actual - set(expected):
            raise NativeFailure("output-invalid")
        files = {
            n: artifacts.read_regular_bounded(output, n, max_bytes=limits.native_output_bytes)[0]
            for n in expected
        }
        return files, stdout, tool, time.monotonic() - start


def decode(text, primitive):
    try:
        if primitive == "String" and re.fullmatch(r"s:(?:[0-9a-f]{2})*", text):
            value = bytes.fromhex(text[2:]).decode("utf-8")
        elif primitive == "Boolean" and text in {"b:0", "b:1"}:
            value = text == "b:1"
        elif primitive in {"Integer", "Number"} and re.fullmatch(r"n:(?:0|-?[1-9][0-9]*):1", text):
            value = int(text[2:-2])
        elif primitive == "Duration" and re.fullmatch(r"u:(?:0|[1-9][0-9]*)", text):
            value = int(text[2:])
        elif primitive == "Date":
            value = text[2:]
        else:
            raise ValueError("token")
        if souffle.token(value, primitive) != text:
            raise ValueError("canonical token")
        return {"primitive": primitive, "value": value}
    except (ValueError, UnicodeError):
        raise NativeFailure("output-invalid") from None


def context(verified):
    manifest = souffle.parse(verified.files["manifest.json"], "json")
    refs = tuple(
        (r["id"], verified.files[f"inputs/reference-{n}.json"])
        for n, r in enumerate(manifest["binding"]["references"])
    )
    args = [
        verified.files["inputs/model.json"],
        verified.files["inputs/candidate.json"],
        manifest["input_formats"]["model"],
        manifest["input_formats"]["candidate"],
        refs,
        DEFAULT_LIMITS,
    ]
    model, candidate, pops, rows, origins, roles, _charge, _counts = souffle.admit(*args)
    return manifest, refs, model, candidate, pops, rows, origins, roles


def extensions(verified, outputs, limits):
    _manifest, _refs, model, _candidate, _pops, rows, _origins, roles = context(verified)
    symbols = souffle.parse(verified.files["symbols.json"], "json")["relations"]
    registry = {
        souffle.token(row[r], p) for fid, rs in rows.items() for row in rs for r, p in roles[fid]
    }
    count_allowed = set()
    for f in model.fact_types:
        for c in iter_derivation_clauses(f.get("derivation_rule")):
            for fid, terms in [(f["id"], c["head"])] + [
                (a["fact_type"], a["bind"]) for a in c["body"] + c.get("negate", [])
            ]:
                for r, p in roles[fid]:
                    t = terms[r]
                    if not (type(t) is str and t.startswith("$")):
                        registry.add(souffle.token(t, p))
            if c.get("aggregate"):
                count_allowed.update(
                    (f["id"], role)
                    for role, term in c["head"].items()
                    if term == c["aggregate"]["as"]
                )
    # Propagate count-valued columns through relational copies/joins only.
    # Merely containing a count elsewhere cannot authorize invented numbers.
    pending = [
        (f["id"], c)
        for f in model.fact_types
        for c in iter_derivation_clauses(f.get("derivation_rule"))
    ]
    changed = True
    while changed:
        changed = False
        for fid, c in pending:
            variables = {
                term
                for a in c["body"]
                for role, term in a["bind"].items()
                if (a["fact_type"], role) in count_allowed
            }
            for role, term in c["head"].items():
                if term in variables and (fid, role) not in count_allowed:
                    count_allowed.add((fid, role))
                    changed = True
    result = {}
    n = 0
    for relation in symbols:
        if not relation["derived"]:
            continue
        values = []
        seen = set()
        for line in outputs[relation["symbol"] + ".csv"].decode("utf-8").splitlines():
            n += 1
            if n > limits.native_rows:
                raise NativeFailure("output-limit")
            cells = line.split("\t")
            if len(cells) != len(relation["roles"]):
                raise NativeFailure("output-invalid")
            typed = []
            for t, role in zip(cells, relation["roles"], strict=True):
                cell = decode(t, role["primitive"])
                if t not in registry and not (
                    (relation["fact_type"], role["name"]) in count_allowed
                    and role["primitive"] in {"Integer", "Number"}
                    and 0 <= cell["value"] <= 2**63 - 1
                ):
                    raise NativeFailure("output-invalid")
                typed.append(cell)
            key = json.dumps(typed, sort_keys=True)
            if key not in seen:
                seen.add(key)
                values.append(typed)
        result[relation["fact_type"]] = values
    return result


def run_souffle(bundle_path, *, executable="souffle", limits=DEFAULT_LIMITS):
    result = {
        "version": 1,
        "kind": "souffle-run-result",
        "exit_code": 4,
        "status": "failed",
        "reason": None,
        "assurance": "none",
        "counts": dict.fromkeys(
            ("fact_types", "clauses", "input_rows", "encoded_cells", "emission_visits"), 0
        ),
        "tool": None,
        "elapsed_seconds": 0,
        "extensions": None,
    }
    try:
        checked_limits(limits)
        verified, tool = prepare(bundle_path, executable, limits)
        result["counts"] = verified.counts
        if verified.exit_code:
            result.update(exit_code=verified.exit_code, reason=verified.reason)
            return result
        outputs, _, identity, elapsed = invoke(verified, tool, limits)
        try:
            values = extensions(verified, outputs, limits)
        except UnicodeError:
            raise NativeFailure("output-invalid") from None
        result.update(
            exit_code=0,
            status="completed",
            tool=identity,
            elapsed_seconds=elapsed,
            extensions=values,
        )
    except NativeFailure as e:
        result["reason"] = e.reason
    except (artifacts.ArtifactError, *souffle.INPUT_ERRORS):
        result.update(exit_code=3, reason="input-invalid")
    return result


class FalseProof(ValueError):
    pass


class UnknownProof(ValueError):
    pass


def map_proof(document, target, verified):
    manifest, refs, model, _candidate, _pops, _rows, origins, roles = context(verified)
    if (
        type(document) is not dict
        or set(document) != {"proof", "rules"}
        or type(document["rules"]) is not list
    ):
        raise ValueError("unknown tree wire")
    symbols = souffle.parse(verified.files["symbols.json"], "json")
    rels = {r["symbol"]: r for r in symbols["relations"]}
    inputs = {r["input"]: r for r in symbols["relations"] if r["input"]}
    rule_map = {(r["symbol"], r["native_rule"]): r for r in symbols["rules"]}
    facts = {f["id"]: f for f in model.fact_types}
    nodes = []

    def tuple_text(text):
        if type(text) is not str:
            raise ValueError("native tuple")
        match = re.fullmatch(r"([ri][0-9]+)\((.*)\)", text)
        if match is None:
            raise UnknownProof("unknown axiom")
        try:
            values = json.loads("[" + match[2] + "]")
        except ValueError:
            raise ValueError("tuple syntax") from None
        return match[1], values

    def visit(branch, depth):
        if depth > PROOF_LIMITS.proof_depth or len(nodes) >= PROOF_LIMITS.nodes:
            raise NativeFailure("work-limit")
        if type(branch) is not dict:
            raise ValueError("tree shape")
        if set(branch) == {"axiom"}:
            symbol, values = tuple_text(branch["axiom"])
            if symbol not in inputs:
                raise UnknownProof("unknown base")
            relation = inputs[symbol]
            fid = relation["fact_type"]
            if len(values) != len(relation["roles"]) + 1 or type(values[-1]) is not int:
                raise ValueError("base shape")
            ordinal = values[-1]
            origin = next(
                (
                    o["origin"]
                    for o in origins
                    if o["input"] == symbol and o["source_ordinal"] == ordinal
                ),
                None,
            )
            if origin is None:
                raise FalseProof("forged ordinal")
            typed = [
                decode(t, r["primitive"])
                for t, r in zip(values[:-1], relation["roles"], strict=True)
            ]
            node = {
                "id": len(nodes),
                "kind": "base",
                "fact_type": fid,
                "tuple": typed,
                "origin": origin,
            }
        elif set(branch) == {"premises", "rule-number", "children"}:
            symbol, values = tuple_text(branch["premises"])
            if symbol not in rels or type(branch["children"]) is not list:
                raise ValueError("relation/children")
            relation = rels[symbol]
            fid = relation["fact_type"]
            if len(values) != len(relation["roles"]):
                raise ValueError("arity")
            match = re.fullmatch(r"\(R([1-9][0-9]*)\)", str(branch["rule-number"]))
            if not match:
                raise ValueError("rule syntax")
            rule = rule_map.get((symbol, int(match[1])))
            if rule is None:
                raise FalseProof("unknown rule")
            premises = [visit(child, depth + 1) for child in branch["children"]]
            typed = [
                decode(t, r["primitive"]) for t, r in zip(values, relation["roles"], strict=True)
            ]
            if rule["kind"] == "input":
                if len(premises) != 1 or nodes[premises[0]]["tuple"] != typed:
                    raise FalseProof("input projection")
                return premises[0]
            if rule["kind"] != "derivation":
                raise UnknownProof("count helper")
            c = list(iter_derivation_clauses(facts[fid]["derivation_rule"]))[rule["clause_index"]]
            if len(premises) != len(c["body"]):
                raise FalseProof("premise roster")
            bindings = {}
            for a, premise in zip(c["body"], premises, strict=True):
                node = nodes[premise]
                if node["fact_type"] != a["fact_type"]:
                    raise FalseProof("premise relation")
                for (role, p), cell in zip(roles[a["fact_type"]], node["tuple"], strict=True):
                    term = a["bind"][role]
                    if type(term) is str and term.startswith("$"):
                        key = term[1:]
                        if key in bindings and bindings[key] != cell:
                            raise FalseProof("unification")
                        bindings[key] = cell
            node = {
                "id": len(nodes),
                "kind": "rule",
                "fact_type": fid,
                "clause_index": rule["clause_index"],
                "tuple": typed,
                "bindings": bindings,
                "premises": premises,
            }
        else:
            raise ValueError("unknown native branch")
        nodes.append(node)
        return node["id"]

    root = visit(document["proof"], 1)
    if nodes[root]["tuple"] != target["tuple"] or nodes[root]["fact_type"] != target["fact_type"]:
        raise FalseProof("root mismatch")
    binding = {
        k: manifest["binding"][k] for k in ("model_digest", "candidate_digest", "references")
    }
    cert = {
        "version": 1,
        "kind": "derivation-witness",
        "binding": binding,
        "results": [
            {"request_index": 0, "target": target, "status": "proved", "reason": None, "root": root}
        ],
        "nodes": nodes,
    }
    md = souffle.parse(verified.files["inputs/model.json"], manifest["input_formats"]["model"])
    pd = souffle.parse(
        verified.files["inputs/candidate.json"], manifest["input_formats"]["candidate"]
    )
    result = replay_witness(md, pd, cert, reference_inputs=refs)
    return (
        WitnessResult(0, result.results, cert, work=result.work)
        if result.exit_code == 0
        else result
    )


def native_witness(bundle_path, targets_document, *, executable="souffle", limits=DEFAULT_LIMITS):
    try:
        checked_limits(limits)
        verified = verify_souffle_bundle(bundle_path, limits=limits)
        if verified.exit_code:
            return WitnessResult(verified.exit_code, reason=verified.reason)
        manifest, refs, model, _candidate, _pops, _rows, _origins, _roles = context(verified)
        witness_io.record(targets_document, "version targets")
        if type(targets_document["version"]) is not int or targets_document["version"] != 1:
            raise ValueError("targets version")
        targets = targets_document["targets"]
        if not isinstance(targets, list) or not 1 <= len(targets) <= PROOF_LIMITS.targets:
            raise ValueError("targets")
        # Conservative closure support before P3 target typing (Duration is an
        # explicit unsupported proof scalar, despite being a valid export scalar).
        from gnd.witness.io import support_closure

        if not support_closure(model, targets)[0]:
            return WitnessResult(2, reason="fragment-unsupported")
        witness_io.validate_targets(targets, model)
        verified, tool = prepare(bundle_path, executable, limits)
        symbols = souffle.parse(verified.files["symbols.json"], "json")["relations"]
        names = {r["fact_type"]: r["symbol"] for r in symbols}
        commands = (
            "format json\nsetdepth 128\n"
            + "".join(
                "explain "
                + names[t["fact_type"]]
                + "("
                + ", ".join(
                    json.dumps(souffle.token(c["value"], c["primitive"])) for c in t["tuple"]
                )
                + ")\n"
                for t in targets
            )
            + "exit\n"
        )
        _, stdout, _, _ = invoke(verified, tool, limits, commands=commands.encode())
        # Native emits one JSON document per explain request, without a wrapper.
        proof_limits = replace(
            PROOF_LIMITS,
            bytes=limits.document_bytes,
            container_depth=limits.container_depth,
            scalar_bytes=limits.scalar_bytes,
            numeric_digits=limits.numeric_digits,
        )
        text = stdout.decode()
        decoder = json.JSONDecoder(
            object_pairs_hook=witness_io._pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
        )
        documents = []
        while text.strip():
            doc, end = decoder.raw_decode(text.lstrip())
            witness_io.validate_witness_structure(doc, limits=proof_limits)
            documents.append(doc)
            text = text.lstrip()[end:]
        if len(documents) != len(targets):
            raise UnknownProof("missing explanation")
        results = []
        nodes = []
        for i, (doc, target) in enumerate(zip(documents, targets, strict=True)):
            # Reparse with duplicate-key/nonfinite/depth checks.
            # Both decoding paths reject duplicate keys; single documents also
            # retain their exact raw byte ceiling.
            if len(targets) == 1:
                doc = witness_io.parse_wire(stdout, limits=proof_limits)
            mapped = map_proof(doc, target, verified)
            if mapped.exit_code:
                return WitnessResult(
                    mapped.exit_code,
                    reason="proof-invalid" if mapped.exit_code == 1 else mapped.reason,
                )
            cert = mapped.certificate
            offset = len(nodes)
            for node in cert["nodes"]:
                node["id"] += offset
                if "premises" in node:
                    node["premises"] = [p + offset for p in node["premises"]]
                nodes.append(node)
            row = cert["results"][0]
            row.update(request_index=i, root=row["root"] + offset)
            results.append(row)
        certificate = {
            "version": 1,
            "kind": "derivation-witness",
            "binding": cert["binding"],
            "results": results,
            "nodes": nodes,
        }
        md = souffle.parse(verified.files["inputs/model.json"], manifest["input_formats"]["model"])
        pd = souffle.parse(
            verified.files["inputs/candidate.json"], manifest["input_formats"]["candidate"]
        )
        replayed = replay_witness(md, pd, certificate, reference_inputs=refs)
        if replayed.exit_code:
            return replayed
        return WitnessResult(0, tuple(results), certificate, work=replayed.work)

    except FalseProof:
        return WitnessResult(1, reason="proof-invalid")
    except UnknownProof:
        return WitnessResult(2, reason="fragment-unsupported")
    except NativeFailure as e:
        return WitnessResult(4, reason=e.reason)
    except (artifacts.ArtifactError, *souffle.INPUT_ERRORS):
        return WitnessResult(3, reason="input-invalid")
