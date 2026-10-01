# Contributing during runtime staging

The coherent package is staged; complete behavior/workflow acceptance is P3.
All units remain source-owned until an explicit handoff. No target publisher exists.
Use Python >=3.11 and uv 0.10.10 for this staged build profile. CI pins the
same version; P4 will decide the final release tool profile. Credential-free
development:

```bash
uv sync --locked --group dev
uv run gnd install --symlink --project --force
uv run gnd doctor --project
uv run pytest -q tests/test_development_scaffold.py tests/test_review_credential_launcher.py
```

Fresh tracked links have no machine-local receipt. The one-time --force adoption
is safe for these installer-produced links; it does not authorize overwriting
modified files. Never edit links by hand; regenerate using the own installer.
The unmanaged process-phase and owned plan-review-panel roots are real twins.

The selected P2 build/install gate, invoked explicitly, is:

```bash
uv run pytest -q -o addopts='' tests/test_public_runtime.py tests/test_public_distribution.py
```

It builds an sdist, rebuilds a wheel, installs only the base wheel in a temporary
venv outside this checkout, and checks CLI/API/resources/assurance. No provider
credentials, private source checkout or historical Git objects are required.
The distribution gate may fetch pinned build/base dependencies. It is bounded
migration coverage, not the whole advertised framework test suite or certification.
See [bootstrap limits](docs/development/bootstrap.md); P4-C5 remains pending.

Numbered work uses a spec, owner gate, implementation, adversarial review,
refactoring review and record. Begin with the non-authoritative
[spec](docs/development/examples/phase-spec.md) and
[record](docs/development/examples/phase-record.md) exercises.
Do not run broad/provider/native/certification lanes without named selection.
Never source repository .env files. Report security through [SECURITY](SECURITY.md).
