import json, sys, copy, hashlib
sys.path.insert(0, sys.argv[2])
import build_growth_example as b
from pathlib import Path
from gnd.evolve import ConstraintLocator, EvolutionOperation, EvolutionOperationKind
root = Path(sys.argv[1]); text = (root/"model.orm.yaml").read_text()
p = b.proposal(text, "round-3", EvolutionOperation(operation_id="add-mand2", kind=EvolutionOperationKind.ADD,
    locator=ConstraintLocator(host="fact_type", host_id="order_arrives_via_channel", family="mandatory"), after=b.MANDATORY))
(root/"round-3.proposal.json").write_text(json.dumps(p.model_dump(mode="json"), indent=2, sort_keys=True))
