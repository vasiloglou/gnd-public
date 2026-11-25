"""Exercise standalone intake with an untrusted claimed include origin."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import vg3_cases
from test_si1_seeded_routes import MODEL_ROUTES, _run

with TemporaryDirectory() as folder:
    base = Path(folder)
    rooted = json.loads(vg3_cases.write(base).read_bytes())
    authored = vg3_cases.spanned_seed()
    authored.update(version=5, model_id=rooted["model_id"], source=rooted["source"])
    authored["source"]["origins"] = [
        {"origin": "includes[seed]", "composed_address": "$.object_types[0]"},
    ]
    candidate = base / "standalone.orm.json"
    population = base / "population.json"
    population.write_text(json.dumps({
        "population": {"model": candidate.name, "model_id": authored["model_id"], "source": "fixture",
                       "covers": ["work_has_version"]},
        "facts": {"work_has_version": [{"work": "w", "version": "v"}]},
    }))
    for owning_spans in (True, False):
        if not owning_spans:
            authored["object_types"][0].pop("provenance")
        candidate.write_text(json.dumps(authored))
        for route in MODEL_ROUTES:
            code, output = _run(route, candidate, base / f"{route}-{owning_spans}", population)
            observed = [
                label for label in ("unattended:flat-without-root", "semantic:unattended-u4", "include:declaration")
                if label in output
            ]
            if not owning_spans:
                expected = (3, ["unattended:flat-without-root", "semantic:unattended-u4"])
            elif route == "flatten":
                expected = (3, ["include:declaration"])
            else:
                expected = (0, [])
            assert (code, observed) == expected, output
            print(route, "valid spans" if owning_spans else "missing owned span", code, observed)
