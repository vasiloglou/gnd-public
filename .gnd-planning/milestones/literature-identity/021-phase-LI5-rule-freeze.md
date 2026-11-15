---
milestone: literature-identity
station: phase-LI5-rule-freeze
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-rule-freeze
date: 2026-11-15
gate:
  command: "ruling: delegated approval (auto=true) of the frozen LI5 model and path policy for reserved scoring"
  exit: "n/a -- ruling"
evidence:
  - path: src/gnd/examples/literature/lineage/model.orm.yaml
    sha256: a63b64293edbed71c74d1ded8423c133c328aa4ea02f550bad4fb03c91591279
  - path: src/gnd/examples/literature/lineage/path-policy.json
    sha256: cc27412b17b7cc1ca4f6d5da940b74b80528e45d2aa9d5a78dbee4986274c0b7
  - path: src/gnd/examples/literature/lineage_run.py
    sha256: 1fbc286b4ba16f81bb606c59d643ed966c655dd7806a1225109fb8af56f7eaff
  - path: tools/build_literature_lineage_model.py
    sha256: 2a6a2b8ea283bbcac5114167f6ee9ce3c48293ff38c60db64c662a8d39e5eb29
  - path: src/gnd/examples/literature/answers/heldout.sha256
    sha256: 00453b06687807e81048144e56608208dc2c28f1f7856ed4604c8406ce9f6af7
---

# Claim

**Delegated approval (auto=true), 2026-11-15.** The milestone chat delegates
the LI5 measurements and rulings within the previously approved corpus
procedure. This record freezes the structured model and policy, generated
model builder and example scoring source before opening the reserved key.
Model validation exited 0 and byte-identical regeneration was measured.

The reserved input digest is pinned in the earlier approved corpus.
Build its input annotations from the public source passages, without
the answer labels, after this freeze. Verify the key digest before
scoring. The authorized report keeps only aggregate results and binds
these rule, policy and input digests. The key remains in its local ref.

The approval instrument is this exact rule and policy pair, with its
implementation and premeasurement checks. Existing approved outcomes
remain the scoring conditions.
