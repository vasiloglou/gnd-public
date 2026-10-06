# RF9 reviewer B: architecture

Native Codex gpt-6-sol/xhigh, one read-only run, exit0. Fixed source:d440b2e37449ef46647d18c491c46d9bb8d3e851; base:f5a83186f7c2215ac2b2afb0a010c2294eaa433a.
Prompt SHA-256:b895e1b9efb09dcddd2959fb1320cdd56d2c4888930d53f644cc93d33eff0e4e.
The return below is verbatim except absolute worktree/home paths replaced by <worktree>/<home>. Primary verification and disposition are separate.

## Area B finding

**P2 · Hardening · Introduced in RF5:** Seven lane services eagerly import `gnd.commands._output`, including [codegen/service.py](<worktree>/src/gnd/codegen/service.py:7). Importing that child also executes its parent package, `gnd.commands`, which [the layer map](<worktree>/tools/gnd_layers.json:194) assigns to `entry`. The services therefore have a runtime lane-to-entry dependency despite the reported zero wrong-way edges. [gnd_arch.py](<worktree>/tools/gnd_arch.py:324) records the explicit child import but omits the parent package execution.

Minimal read-only reproduction:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -c 'import sys; import gnd.codegen.service; print("gnd.commands" in sys.modules)'
# True
```

Expected: the architecture measurement exposes that entry-package dependency. Observed: `wrong_way=[]`; adding Python’s implicit parent imports to the measured graph exposes **seven** lane-to-entry edges. The parent initializer currently contains only a docstring, and sampled import orders succeeded. I found an invalid architecture guarantee and current coupling, not a demonstrated command failure. The package did not exist at the fixed base.

**Potential test masking:** The RF5 entry-point controls in [test_rf5_commands.py](<worktree>/tests/test_rf5_commands.py:119) exercise forbidden imports *from command groups*. They do not exercise this service-to-parent route.

## Measurement and limits

Using the current AST visitor on the fixed base gave 148 modules, five explicit runtime SCCs, and 27 wrong-way edges. The final tree gave 227 modules, zero explicit runtime SCCs, zero recorded wrong-way edges, and zero allowances. I did not confirm a harmful hidden cycle or import-order failure. All 16 current family hooks resolved, and the current implemented-family sets matched.

This was an advisory, read-only Area B review. I did not review Area A compatibility and CLI behavior, Area C state and input semantics, or Area D test and evidence integrity. I ran no broad suite, provider tool, or installed-package check.
