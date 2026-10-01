# Contributing during staging

Only the reviewed scaffold and development workflow are present. For credential-free
checks use Python >=3.11 in an isolated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q tests/test_development_scaffold.py tests/test_review_credential_launcher.py
```

Tests use synthetic temporary credentials and mock all network/provider calls;
no API keys, source checkout or private documents are needed for these checks.
Read [bootstrap limits](docs/development/bootstrap.md) before optional review.

Agents discover `process-phase` and the owned `plan-review-panel` compatibility
entry in both `.codex/skills/` and `.claude/skills/`. These are real twin directories.
All GND installer-managed links and fresh-clone receipt adoption are deferred to
P2; there is no P1 `gnd doctor` success claim. Ordinary changes use focused tests.
A numbered phase requires a spec, explicit owner gate, implementation, adversarial
review, refactoring review and a record. Begin with the non-authoritative
[spec](docs/development/examples/phase-spec.md) and [record](docs/development/examples/phase-record.md)
exercise; they demonstrate fields, not executed work or owner approval.

All units remain source-owned during this staging batch. New authoritative public
work requires a recorded handoff; migration questions keep their IDs and triggers.
Do not enable a package publisher or run broad/provider/certification lanes without
their named selection. Open issues for proposed changes; security reports use the
private route in [SECURITY](SECURITY.md).
