# Temporary conditional bootstrap

Source repository: `vasiloglou/gnd` (private). Tool baseline:
`ac4be67afdddde0b2b2095a6cd383bc13852758c` (accepted v7.2).
This exact source-pinned local GND development environment is the temporary
conditional dependency for optional maintained panel execution. It is not
bundled or distributed here. An outsider without source access cannot run the
panel from this P1 scaffold. No public review-execution claim is made.

Use the owner-configured source environment only after explicit review selection;
record resolved `gnd` executable/module path and source identity for that run.
The scaffold contains reference documents, not a complete importable GND runtime.
Do not run the launcher in the target pretending `uv run gnd` already resolves.
Ordinary Python/pytest scaffold tests and the sample protocol exercise need no
source checkout, provider key or private document. No provider is invoked by CI.

P2 supplies coherent package targets and installer-produced links. P3 accepts
current test/fixture successors. P4-C5 must remove this bootstrap, install the
target-built candidate wheel in a fresh target-only environment, inspect actual
executable/module/link paths and verify both agent roots and contributor exercise.
Only that later check can establish source-free contributor readiness.

## Owner-only source bootstrap preparation

An owner with source access may prepare a separate source checkout; never reset
the active development tree. The following commands are instructions, not P1
executed provider gates. Replace SOURCE_DIR and TARGET_DIR with absolute paths.

```bash
git clone --no-checkout https://github.com/vasiloglou/gnd.git SOURCE_DIR
git -C SOURCE_DIR checkout --detach ac4be67afdddde0b2b2095a6cd383bc13852758c
cd SOURCE_DIR
uv sync
uv run gnd review --help
```

Only after explicit artifact/recipient approval, from that source directory:
`uv run python TARGET_DIR/tools/run_gnd_review_panel.py REQUEST --out OUTPUT`.
Record the resolved tool/module paths and source pin. Terminal-agent CLIs and
required credentials remain explicitly selected optional panel prerequisites;
this sequence installs no public target runtime and invokes no provider by itself.
An outsider without access cannot prepare this conditional tool. P4 removes it.
