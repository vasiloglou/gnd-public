---
name: gnd-consolidate
description: Review one grown ORM model for consolidation candidates, prepare a located group decision, and resume the reviewed evolution until the selected budget or threshold is reached.
---

# Consolidate a grown model

Use a terminal in the model's workspace. Run `gnd consolidate candidates MODEL` to inspect all six signals and their evidence. Use `python -m gnd.evolve.consolidation MODEL --minimum-score 85 --max-decisions 20` to get the next eligible group. Keep the same score and work budgets across the run. For each member, search the authored model for role and constraint references, then read the cited documents at their normalized character offsets and verify their excerpt digests.

When the answer is `needs-decision`, copy the exact `model_sha256`, `group.group_id` and `group.evidence_sha256` into a JSON decision with a named `actor`. Choose one action.

- `leave` records the reviewed evidence. It becomes eligible again if its evidence changes.
- `merge` removes a duplicate and keeps a selected survivor. Repoint all referencing roles and rewrite their readings. For each removed fact, append its observations to the surviving fact with their original spans, remapping row indices. Include every required operation in one proposal.
- `demote-to-row` replaces a type with a located observation in a surviving fact. Preserve its original support and review the references and constraints affected by the removal.
- `link-subtype` adds a subtype relationship between selected members. Supply the model's inheritance declaration and check both reference schemes.

For a mutation, prepare one proposal and run the ordinary evolution preview. Inspect the complete candidate, verbalization and blast radius. Include the reviewed preview object in the decision's `preview` field. For a breaking change it must contain acceptance of the exact blast-radius digest. The proposal's audit actor must match the decision. For each deleted sampled fact add a `moves` entry with `source`, `target` and a total `roles` mapping from each old role name to its surviving role. The transfer check compares typed rows and their original spans as multisets.

The terminal can create the accepted preview with the installed Python API. After inspecting the preview, provide its exact report digest in `accepted_digest`. Use the same workspace, model and linked-project paths used to produce the reviewed preview.

```python
from gnd.evolve import EvolutionService, read_evolution_proposal_document

proposal = read_evolution_proposal_document(proposal_json)
service = EvolutionService(model_path=model_path, evidence_root=records_dir, allowed_project_root=workspace)
reviewed = service.preview(proposal, accepted_blast_radius_sha256=accepted_digest)
decision["preview"] = reviewed.model_dump(mode="json")
```

Run `python -m gnd.evolve.consolidation MODEL --decision decision.json` with the same budget options. On `completed`, check the conformance exit and load the next group. The model directory holds the durable journal under `.gnd-consolidation`. Keep it together with the model. After interruption rerun the command without a decision to finish the pending action. Repeating the same completed decision returns its ID. Stop on `decision-limit`, `items-limit`, `pairs-limit`, `no-eligible-group`, a refusal, or a group for which the reviewer needs more evidence. The workflow never touches git.

## Installed example

Save the following model as `codes.json` in an empty directory.

```json
{"version":1,"object_types":[{"id":"code","kind":"value","primitive":"Integer"}],"fact_types":[{"id":"shown","reading":"{Code} is visible","roles":[{"object_type":"code","role_name":"code"}]},{"id":"listed","reading":"{Code} is visible","roles":[{"object_type":"code","role_name":"code"}]}]}
```

Run the following in that directory. It reviews one group and records a leave. The final command asks for a different unresolved group.

```sh
python -m gnd.evolve.consolidation codes.json > next.json
python -c 'import json; r=json.load(open("next.json")); g=r["group"]; print(json.dumps(dict(actor="example-reviewer",action="leave",model_sha256=r["model_sha256"],group_id=g["group_id"],evidence_sha256=g["evidence_sha256"])))' > decision.json
python -m gnd.evolve.consolidation codes.json --decision decision.json
python -m gnd.evolve.consolidation codes.json
```
