# Commands and origins

All exits were 0 except the declared Lean false-proof block (1), unsupported
export/witness controls (2), altered-bundle control (3), and retained observed red
controls. The exact documented command blocks live in the implementation manifest.

- Focused pytest command: the phase record header, 143 passed.
- Ruff: tools/run_tutorials.py tools/check_docs.py tools/check_installed_docs.py tests/test_documentation_tutorials.py tests/test_external_runtime_tutorials.py src/gnd/examples/release_governance.
- Site: NO_COLOR=1 .venv/bin/zensical build --strict; .venv/bin/python tools/check_docs.py site.
- Build/install: .venv/bin/python tools/check_installed_docs.py --out <candidate-validation>.
- Offline origins: <candidate-validation>/venv-{release,comparison}/bin/python <candidate-validation>/tutorial-source/tools/run_tutorials.py --root <candidate-validation>/tutorial-source --python <candidate-validation>/venv-{release,comparison}/bin/python --lane offline.
- Native: the same release-origin runner, one --group runtime-pyrel --lane pyrel, one --group runtime-souffle --lane souffle, one --group runtime-lean --lane all. GND_TUTORIAL_PYREL_PYTHON selected the isolated locked environment; GND_TUTORIAL_LAKE selected the measured cached toolchain.

The native runs used the identical direct candidate wheel, outside the checkout.
The copied tutorial-source runner/guides were refreshed after the gate repair;
package resources and wheel identities did not change. Both offline origins were
then executed with the final runner/guides. This is no paid provider execution.
