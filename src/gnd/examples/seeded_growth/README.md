# Seeded growth example

An unattended model grown from an owner-reviewed vocabulary, used by
"Starting from a reviewed vocabulary" in
`src/gnd/skills/gnd-model-from-text/references/unattended-growth.md`.

- `seed.orm.yaml`: the reviewed vocabulary. Version 4, not unattended; its one
  constraint is `explicit`, `confirmed` and `alethic`, with `reviewed_in`.
- `root.orm.yaml`: the growth root. Version 5, `source.mode: unattended`,
  `reviewer: none`; it includes the seed by pin and holds nothing of its own,
  so it declares no document yet.
- `round-1.document.txt`, `round-1.proposal.json`: round 1 declares the
  document and adds an Author value type and "Author writes WorkKey", with
  spans and two sample rows.
- `round-2.document.txt`, `round-2.proposal.json`: round 2 binds the root as
  round 1 publishes it, declares its document and attaches a `sample`,
  `proposed`, `deontic` mandatory constraint to the seed's fact type.
- `population.json`, `policy.json`, `receipts.json`: a population of the grown
  root, and a two-judge policy with approving receipts that bind it.

From a copy of this folder (the commands write into it):

```bash
gnd validate root.orm.yaml
gnd evolve preview root.orm.yaml round-1.proposal.json --workspace . --records records --out preview-1.json --policy additive
gnd evolve apply root.orm.yaml round-1.proposal.json --preview preview-1.json --workspace . --records records --policy additive
gnd evolve preview root.orm.yaml round-2.proposal.json --workspace . --records records --out preview-2.json --policy additive
gnd evolve apply root.orm.yaml round-2.proposal.json --preview preview-2.json --workspace . --records records --policy additive
gnd validate root.orm.yaml --document round-1.document.txt --document round-2.document.txt --require-documents
gnd check root.orm.yaml population.json
gnd judgments check root.orm.yaml population.json --policy policy.json --receipts receipts.json --trusted-root .
```

Each command exits 0. `gnd validate` prints one `INCLUDE seed …` line naming
what the seed carries. The proposals and the judgment inputs bind digests; in
the source repository, regenerate them with
`tools/build_seeded_growth_example.py` after any edit to the seed, the root or
a document.

## Retry an unsuccessful search

Run the following in a fresh copy of this example, before applying round 1.
The recorded path is one possible agent decision. A host can offer different
searches and replay the resulting record. The root's pinned seed supplies the
work/version fact. The short phrase alone leaves the relation unresolved.

```python
import hashlib
import json
from pathlib import Path
from unicodedata import normalize

from gnd import api
from gnd.model import load_model_bytes_composed

root = Path("root.orm.yaml")
raw = root.read_bytes()
model = load_model_bytes_composed(raw, source=root, root=root.parent)
view_text = api.verbalize_model(model, for_growth=True)
view = json.loads(view_text)
facts = view["fact_types"]
snapshot = hashlib.sha256(raw).hexdigest()
view_hash = hashlib.sha256(view_text.encode("utf-8")).hexdigest()

by_reading = [f for f in facts if "edition" in f["reading"].casefold()]
by_player = [f for f in facts if any(player == "version" for _, player in f["roles"])]
assert not by_reading
fact, = by_player
assert fact["id"] == "work_has_version"
assert fact["roles"] == [["work", "work"], ["version", "version"]]

document = Path("round-2.document.txt").read_bytes()
source = normalize("NFC", document.decode("utf-8"))
quote = "W-1 has version V-1"
assert source.count(quote) == 1
start = source.index(quote)
# The agent attributes the subject and object of this occurrence to named roles.
# Verify proposed values against those citations before recording reuse.
end = start + len(quote)
role_spans = {"work": [start, start + len("W-1")], "version": [end - len("V-1"), end]}
bindings = {"work": "W-1", "version": "V-1"}

def supports_binding(binding, citations):
    roles = {role for role, player in fact["roles"]}
    return roles == binding.keys() == citations.keys() and all(
        start <= left < right <= end and source[left:right] == binding[role]
        for role, (left, right) in citations.items()
    )

assert supports_binding(bindings, role_spans)
reversed_binding = {"work": bindings["version"], "version": bindings["work"]}
assert not supports_binding(reversed_binding, role_spans)
other_work = source.index("W-2", end)
other_version = source.index("V-2", other_work)
other_citations = {"work": [other_work, other_work + 3], "version": [other_version, other_version + 3]}
assert not supports_binding({"work": "W-2", "version": "V-2"}, other_citations)
# A separate passage mentions both IDs but supplies no directed predicate.
ambiguous = "The catalogue lists W-1 alongside V-1."
ambiguous_hash = hashlib.sha256(ambiguous.encode("utf-8")).hexdigest()
direct = [f for f in facts if "has version" in f["reading"].casefold()]
assert [f["id"] for f in direct] == [fact["id"]]
record = {
    "expected_model_sha256": snapshot,
    "document_sha256": hashlib.sha256(document).hexdigest(),
    "searches": [
        {"query": query, "partial": True, "view_sha256": view_hash, "shown": rows}
        for query, rows in [("reading: edition", by_reading), ("role player: version", by_player)]
    ],
    "inspected_ids": [fact["id"]],
    "reversed_binding_supported": supports_binding(reversed_binding, role_spans),
    "direct_lookup": {"query": "reading: has version", "shown": direct,
                      "partial": True, "view_sha256": view_hash},
    "ambiguous_document": ambiguous,
    "decisions": [
        {"decision": "reuse", "id": fact["id"], "span": [start, start + len(quote)],
         "bindings": bindings, "role_spans": role_spans,
         "reason": "The work is the subject of has version; V-1 fills its version role."},
        {"decision": "defer", "document_sha256": ambiguous_hash, "span": [0, len(ambiguous)],
         "reason": "Listing two identifiers together leaves the relationship and direction unresolved."},
    ],
}
# Check the captured root and authenticate its pinned includes again at handoff.
# The evolution gate repeats its own compare-and-swap check at application time.
current = root.read_bytes()
if hashlib.sha256(current).hexdigest() != record["expected_model_sha256"]:
    raise ValueError("stale growth round: re-open the current model")
load_model_bytes_composed(current, source=root, root=root.parent)
print(json.dumps(record, ensure_ascii=False, indent=2))
```

The same round can find a direct reading match by searching for `has version`.
Round 1's additive proposal illustrates the third disposition: introduce a
new type and fact when the full vocabulary and the source support that decision.
Use the preview/apply commands above against the corresponding round snapshot.
