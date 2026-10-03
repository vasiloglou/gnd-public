"""Independent guarded join counts and bounded synthetic example inputs."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

Binding = dict[str, Any]
_WORKSPACES = []
def materialize_example_fixture(tests_root: Path) -> Path:
    fixture = tests_root / "fixtures/public-example-guards/workspace.json.gz"
    assert fixture.is_file() and not fixture.is_symlink()
    with fixture.open("rb") as stream:
        compressed = stream.read(64 * 1024 + 1)
    assert len(compressed) <= 64 * 1024
    assert hashlib.sha256(compressed).hexdigest() == 'ed1dbb213b6fefaf7adf14707ac181570da9388d30a6c83ac44033dd7aaef9fb'
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        expanded = stream.read(256 * 1024 + 1)
    assert len(expanded) <= 256 * 1024
    payload = json.loads(expanded)
    assert payload["schema_version"] == 1
    assert len(payload["members"]) == 16
    workspace = tempfile.TemporaryDirectory(prefix="gnd-public-examples-")
    _WORKSPACES.append(workspace)
    root = Path(workspace.name)
    for value, member in payload["members"].items():
        relative = PurePosixPath(value)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert value == relative.as_posix() and relative.parts
        raw = base64.b64decode(member["data"], validate=True)
        assert len(raw) <= 64 * 1024
        assert hashlib.sha256(raw).hexdigest() == member["sha256"]
        destination = root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    return root

def _identity(value: Any) -> tuple[str, Any]:
    """ORM scalar identity, domain-tagged, written from the semantics directly.

    Python makes ``True == 1`` and hashes them alike; ORM does not. Booleans are
    a separate scalar domain from numbers, while Integer and Float share the
    numeric domain because Float and Number roles accept either JSON spelling.

    This is deliberately NOT ``gnd.checker._identity_key``, even though it must
    agree with it. Importing the checker would make this module a second reading
    of the checker rather than an independent one, and the whole point of
    recomputing a join here is that two independent sources agree. Same
    semantics, different code -- the C1 rule the synth oracle follows for the
    same reason.

    Found by the single-seat diff review: without this, an antecedent binding
    one variable across a Boolean role and an Integer role reported one binding
    where the runtime reports zero.
    """
    if isinstance(value, bool):
        return ('boolean', value)
    if isinstance(value, (int, float)):
        return ('number', value)
    return ('other', value)

def _unify(row: Mapping[str, Any], bind: Mapping[str, Any], seed: Binding) -> Binding | None:
    """Extend ``seed`` so ``row`` satisfies ``bind``, or ``None`` if it cannot.

    A ``bind`` value spelled ``$name`` is a variable: it takes the row's value
    for that role, and must agree -- by ORM identity, not Python equality --
    with any value the variable already carries. Every other value is a literal
    the row must match under the same identity.
    """
    out = dict(seed)
    for role, term in bind.items():
        if role not in row:
            return None
        observed = row[role]
        if isinstance(term, str) and term.startswith('$'):
            if term in out and _identity(out[term]) != _identity(observed):
                return None
            out[term] = observed
        elif _identity(observed) != _identity(term):
            return None
    return out

def antecedent_bindings(antecedent: Iterable[Mapping[str, Any]], facts: Mapping[str, Any]) -> list[Binding]:
    """Every variable binding for which the whole antecedent conjunction holds.

    This is the join the checker computes, computed again from the same bytes by
    different code. The length is the binding count the report does not publish.
    """
    bindings: list[Binding] = [{}]
    for atom in antecedent:
        rows = facts.get(str(atom['fact_type'])) or []
        nxt: list[Binding] = []
        for seed in bindings:
            for row in rows:
                if not isinstance(row, Mapping):
                    continue
                extended = _unify(row, atom.get('bind') or {}, seed)
                if extended is not None:
                    nxt.append(extended)
        bindings = nxt
        if not bindings:
            break
    return bindings

def guarded_binding_counts(model: Mapping[str, Any], population: Mapping[str, Any]) -> dict[str, int]:
    """``constraint id -> independently recomputed binding count``.

    Model-level guarded constraints only; both Phase 4 cases put their guards
    there. Keyed by ``id`` rather than by position, because a report's
    ``constraint_ref`` is positional and the expense conversion moves indices.
    """
    facts = population.get('facts') or {}
    counts: dict[str, int] = {}
    for constraint in model.get('constraints') or []:
        if str(constraint.get('type')) != 'guarded':
            continue
        cid = constraint.get('id')
        if cid is None:
            raise ValueError(f'guarded constraint without an id: {constraint!r}')
        counts[str(cid)] = len(antecedent_bindings(constraint.get('antecedent') or [], facts))
    return counts

def ref_to_id(model: Mapping[str, Any]) -> dict[str, str]:
    """The D-P4.15 resolution: ``constraints[N] -> id`` in document order.

    Every id must appear exactly once; a duplicate or a renamed constraint reds
    here rather than silently matching the wrong verdict downstream.
    """
    mapping: dict[str, str] = {}
    seen: set[str] = set()
    for index, constraint in enumerate(model.get('constraints') or []):
        cid = constraint.get('id')
        if cid is None:
            continue
        if str(cid) in seen:
            raise ValueError(f'duplicate constraint id: {cid}')
        seen.add(str(cid))
        mapping[f'constraints[{index}]'] = str(cid)
    return mapping
