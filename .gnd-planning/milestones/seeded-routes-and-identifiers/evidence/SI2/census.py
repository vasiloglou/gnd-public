import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from gnd import model_verbalization, refscheme, vocabulary
from gnd.artifacts import canonical_json_bytes
from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError
from gnd.evolve import shapes
from gnd.extract import guidelines
from gnd.model import load_model
from gnd.model_index import ModelIndex
from gnd.rmap import RmapVariant, _Mapper, is_confirmed_alethic

ORIGINAL = refscheme.reference_identity
paths = subprocess.check_output(["git", "ls-files", "-z", "*.orm.json", "*.orm.yaml"]).decode().split("\0")[:-1]
counts = Counter({"qualifying_competitions": 0, "C": 0})
records = []
identity_digest = hashlib.sha256()

def outputs(model, identities):
    def identity(oid, _model):
        return identities[oid]
    with patch.object(refscheme, "reference_identity", identity), \
         patch.object(vocabulary, "reference_identity", identity), \
         patch.object(model_verbalization, "reference_identity", identity):
        return {
            "model_verbalization": model_verbalization.render_model_verbalization(model),
            "extraction_vocabulary": vocabulary.render_verbalization(model),
            "applicability": refscheme.applicable_set(model),
            "evolve_shape_references": shapes._references(ModelIndex.for_model(model), model, tuple(identities)),
            "extraction_guidelines": guidelines.render_guidelines(model),
        }

for filename in paths:
    try:
        model = load_model(Path(filename))
    except (OSError, ValueError, ModelLoadError, ModelValidationError, ReferenceInputError):
        counts["refused"] += 1
        continue
    counts["loadable"] += 1
    # Direct identities and the legacy fallback use the original implementation.
    ids = [row["id"] for row in model.object_types]
    legacy = {oid: ORIGINAL(oid, model) for oid in ids}
    identity_digest.update(canonical_json_bytes([filename, legacy]))
    counts["legacy_composite"] += sum(v[0] == "composite" for v in legacy.values())
    for oid, identity in legacy.items():
        if identity[0] == "direct":
            continue
        qualifying = sum(1 for c in model.constraints if c.get("type") == "uniqueness"
                         and c.get("scope") == "external" and c.get("preferred")
                         and is_confirmed_alethic(c) and c.get("role_refs")
                         and refscheme.anchors_on(c["role_refs"], oid, model))
        if qualifying > 1:
            counts["qualifying_competitions"] += 1
    preferred_first = model.model_copy(update={"constraints": sorted(
        model.constraints, key=lambda c: not bool(c.get("preferred") and is_confirmed_alethic(c)))})
    preferred = {oid: ORIGINAL(oid, preferred_first) for oid in ids}
    # Reading A delegates composite identification, retaining the direct path.
    mapper = _Mapper(model, RmapVariant.HALPIN)
    rmap = dict(legacy)
    for oid, v in legacy.items():
        if v[0] == "direct":
            continue
        key = mapper.key(oid)
        kind, payload = mapper.identity(oid)
        if kind == "composite" and key is not None and oid not in mapper.fallback:
            rmap[oid] = ("composite", payload)
        elif v[0] == "composite":
            rmap[oid] = ("unmatchable", "Rmap selects no composite identifier.")
    for label, candidate in (("A", rmap), ("C", preferred)):
        changed = [oid for oid in ids if legacy[oid] != candidate[oid]]
        if changed:
            before = outputs(model, legacy)
            after = outputs(model, candidate)
            records.append([label, filename, changed, [key for key in before if before[key] != after[key]]])
            counts[label] += len(changed)

print(json.dumps({"counts": counts, "changes": records, "identity_digest": identity_digest.hexdigest(), "B": "legacy, zero changes by definition"}, indent=2))
