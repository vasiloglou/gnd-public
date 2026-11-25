"""For each RF0 identical-candidate group that was not promoted, compare the RF1 helper goldens' observed values across its sites."""
import json, sys
from pathlib import Path
G = Path("tests/fixtures/rf1-pins/goldens/helpers")
groups = {
    "ccbb68bd _rate": ["identical_candidate_gnd.fidelity.match__rate", "identical_candidate_gnd.measure.score__rate"],
    "c4e1c0f8 sorted_set/_canonical": ["canonical_json_gnd.assurance__sorted_set", "canonical_json_gnd.proof_bridge__canonical"],
    "0f1cc1a7 safe coordinate": ["safe_filesystem_gnd.artifacts__safe_fs_coordinate", "safe_filesystem_gnd.conformance.structural__safe_coordinate"],
    "22614c42 object_types_by_id": ["identical_candidate_gnd.popvalidate__object_types_by_id", "identical_candidate_gnd.synth.assemble__object_types_by_id", "identical_candidate_gnd.synth.poolfile__object_types_by_id"],
    "c9b00e5d role object": ["identical_candidate_gnd.popvalidate__role_object_types", "identical_candidate_gnd.synth.assemble__role_object"],
}
for name, stems in groups.items():
    obs = []
    for stem in stems:
        p = G / f"{stem}.json"
        if not p.exists():
            obs.append(None); print(f"{name}: missing golden {p.name}"); continue
        obs.append(json.loads(p.read_text())["observed"])
    present = [o for o in obs if o is not None]
    agree = len(present) == len(stems) and all(o == present[0] for o in present)
    print(f"{name}: {len(present)}/{len(stems)} goldens; observed values {'AGREE' if agree else 'DIFFER'}")
    if not agree and len(present) >= 2:
        a, b = json.dumps(present[0], sort_keys=True), json.dumps(present[1], sort_keys=True)
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        print("   first difference near:", a[max(0,i-80):i+80], "|||", b[max(0,i-80):i+80])
for stem in ("safe_filesystem_gnd.conformance.structural__directory_identity",):
    print("3d106ff9 directory identity: structural golden only (artifacts.directory_identity was nested; owed to RF4):", (G / f"{stem}.json").exists())
print("73ae047d, 5153de62: pinned through tests/test_rf1_session_pins.py::test_session, not per site; no per-site agreement exists")
