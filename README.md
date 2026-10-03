# GND

GND checks facts against a conceptual model: declare the rules, inspect a failed
check, repair the facts and check again. Use the CLI or Python API. Generic
modeling and checking are included; application-specific products and hosted
commercial services are not implied.

Start with the [no-key dispatch tutorial](docs/quickstart.md), then its software
release example. All inputs ship in the package. See [contributing](CONTRIBUTING.md),
[support](docs/support.md), [compatibility](docs/compatibility.md) and
[advanced workflows](docs/advanced.md).

**Release preparation, not an accepted public release.** Phase 3 regression
acceptance and Phase 4 candidate sign-off remain pending. A passing mechanical
check does not certify source truth, completeness or universal correctness.
Missing/stale assurance remains unavailable. Names remain get-nick-done / gnd;
owned code is Apache-2.0, with third-party attribution in NOTICE.

The bundled [zero-install model validator](src/gnd/skills/gnd-model-from-text/scripts/validate_model.py)
is a limited fallback. It does not implement layer-2 semantic model rules,
population checking of any kind, or model-relative population validation. It
cannot return exit band 4 (indeterminate), provide `--format json`, or emit
`acceptance_ready`. Use the installed GND CLI for those capabilities.
