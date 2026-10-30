# Interpret the release evidence

After repairing the approvals, all five requests pass the supplied approval-audit
rules. **Three releases still depend on vulnerable components:** checkout,
payments and ledger. Inventory and reporting are unaffected by this particular
catalogue. Approval validity and vulnerability impact answer different questions.

| Evidence | Result | What a release manager can learn |
|---|---|---|
| PyRel policy audit | Three satisfied constraints after repair | Required approval coverage, one approval and reviewer allowlist hold |
| Developer-owned PyRel report | No self-approval or conflicting reviewers; Maya 3 / Noah 2 | Joins explain business details beyond the exported policy model |
| Soufflé dependency analysis | REL-101, REL-104, REL-105 affected | A vulnerable dependency several hops away can block a candidate |
| Positive witness and replay | checkout → payments → ledger → ledger-db | One concrete dependency has a finite replayed explanation |
| Lean completed proofs | Valid witness, satisfiability and subset redundancy; converse refuted | Approval implies requested under the finite policy; review alone does not imply approval |

## Use the supplied checkpoints honestly

The installed `checkpoints/` directory retains real local native outputs. Its
manifest identifies every input, program and output by SHA256 and records PyRel
1.30.1, DuckDB 1.5.5, Soufflé 2.5 (64-bit) and Lean 4.34.0. Absolute tool paths are
replaced by declared placeholders; semantic values and verdicts are preserved.
The manifest detects drift in these supplied bytes; it is not an authentication
service or an independent certificate.

The following offline block verifies those identities before interpreting them:

<!-- gnd-run expect=0 -->
```python
import hashlib, json
from pathlib import Path
root = Path("release-governance")
manifest = json.loads((root / "checkpoints/manifest.json").read_text())
for relative, digest in manifest["inputs"].items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
for relative, digest in manifest["outputs"].items():
    assert hashlib.sha256((root / "checkpoints" / relative).read_bytes()).hexdigest() == digest
assert manifest["tools"]["lean"] == "4.34.0"
print("Supplied checkpoint identities match. This block has not executed a native runtime.")
```

## Produce a small release summary

This reads the **supplied** repaired audit and graph checkpoints. If you ran the
native guides, compare with your fresh `repaired-audit.json` and `gnd-repaired.json`.
It summarizes the two relevant findings without upgrading their claim families.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
root = Path("release-governance")
audit = json.loads((root / "checkpoints/pyrel-repaired.json").read_text())
graph = json.loads((root / "checkpoints/souffle-repaired.json").read_text())
scenario = json.loads((root / "scenario-repaired.json").read_text())
assert [r["status"] for r in audit["verdicts"]] == ["satisfied"] * 3
affected = {row[0]["value"] for row in graph["extensions"]["affected"]}
summary = {
    "input_kind": "supplied native checkpoints",
    "approval_audit": "all three supported constraints satisfied",
    "affected_releases": sorted(r for r, s, _ in scenario["requests"] if s in affected),
    "unaffected_candidates": sorted(r for r, s, _ in scenario["requests"] if s not in affected),
}
assert summary["affected_releases"] == ["REL-101", "REL-104", "REL-105"]
assert summary["unaffected_candidates"] == ["REL-102", "REL-103"]
with Path("release-summary.json").open("x") as handle:
    json.dump(summary, handle, indent=2)
print(json.dumps(summary, indent=2))
```

This is a working reporting application over a bounded synthetic scenario. A real
publication decision would also need your actual release policies and catalogue
coverage. In these examples, an unaffected candidate simply has no reachable
component in the supplied vulnerability set.

## Why keep the tools distinct?

**PyRel** makes relationships and report queries explicit. It is useful for
business-data audits and application queries. GND's exporter supplies a selected
local constraint translation; your native program can ask additional questions.

**Soufflé** expresses a recursive graph computation compactly. Set semantics,
stratified negation, grouping, native execution and provenance give useful—but
different—results. GND's selected witness profile covers positive explanations,
not every native Datalog result.

**Lean** checks the authored proof of a statement, including universal implications
within the generated finite interpretation. A concrete passing snapshot does not
prove redundancy, and compiling a `sorry` template does not complete a theorem.
The tutorial proofs import the actual verified definitions; their dependency
audits retain the ordinary foundational axioms reported by Lean.

The existing [export contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-export/references/export-contract.md)
remains authoritative for supported GND fragments. The stable Python functions
remain documented in the [API reference](../reference/python-api.md).
External-runtime commands and developer-owned programs are separate surfaces.

## Extend the application

Exercise: authorize Ben as a reviewer, then let Ben approve his own inventory
release. Predict why the exported allowlist audit can pass while the native
self-approval report still identifies a problem. Add a policy to the appropriate
model only through an explicitly reviewed model change, then test the same facts
again. Do not silently treat a native query as a newly added GND constraint.

> Review the three evidence families and propose a release summary. Keep the
> verified exporter bundles unchanged. Explain which inputs each conclusion
> depends on and which policies each view omits; do not merge checking, native
> execution, witness replay and completed tutorial proofs into certification.

Return to the [application gallery](../applications.md) or
[task guides](../guides/modeling.md) to apply the workflow in your own project.
