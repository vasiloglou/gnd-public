# Inputs for the 0.3.0 installed-wheel probes

`tests/test_release_acceptance.py` copies these into a directory outside the
checkout and runs the installed `gnd` on them (release-0.3.0 phase RN2, probes
Q4 and Q5). The wheel does not carry them. Each is a byte copy of a tracked
file, or was written once by the named harness; the digests below are of the
files here.

| File | Origin | sha256 |
|---|---|---|
| `q4/model.orm.yaml` | `tests/fixtures/unattended-model-growth/ug2/base.orm.yaml` | `1a8db33084817e9e418b4fb06d9ac08bfc6876d460fb1b9e908639cdaecae314` |
| `q4/model.verbalization.txt` | the one line the UG2 harness writes beside the model | `38709c1ba3e7a2ce5295e87314ca4a1674a6458a077298b344c966331a8148f3` |
| `q4/proposal.json` | corpus case C01, written by `_workspace` in `tests/test_evolve_population_check.py` | `115bd3703e652464dcf3bfb364bf212ec1e8dbebcaf82c35c226e08441bd8cf0` |
| `q4/populations/clean.json` | `tests/fixtures/unattended-model-growth/ug2/populations/clean.json` | `ba4fe6073f2004422b509be1c555c1c4dbc50298392c0fc6d7039d303a895f3b` |
| `q4/populations/violating.json` | `tests/fixtures/unattended-model-growth/ug2/populations/violating.json` | `6266d50573c46e8269526c18c0ef6401478a68efce647bc4535f7919a6f5f8db` |
| `q5/model.orm.yaml` | `tests/fixtures/unattended-model-growth/ug3/models/span-element.orm.yaml` | `56213db71bb18914d8825a76613ba363355cdc3232277f0af9e318fea1a5370e` |
| `q5/ledger.txt` | `tests/fixtures/unattended-model-growth/ug3/documents/ledger.txt` | `6cec7fe354bc7c620fccfeece167c43dec11096669d934a54ce5ef8fffd155e8` |
| `q5/annex.txt` | `tests/fixtures/unattended-model-growth/ug3/documents/annex.txt` | `69897fa97fa34393398757221b81b99c4fad230ffc46c28cd1dd8d088061d5e4` |
