# Check release dependencies and a deadline

A release request depends on approved components. This short example transfers
the dispatch pattern into software delivery: the fixed catalogue supplies allowed
dependency nodes and edges, and the model checks claimed reachable dependencies
and a release deadline. It checks readiness facts; it does not deploy software.

Use an activated [GND environment](installation.md) in an empty directory:

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from shutil import copytree
copytree(str(files("gnd") / "examples" / "release"), "release-demo")
```

<!-- gnd-run expect=0 -->
```sh
gnd validate release-demo/model.orm.json --format json
```

The first request misses its modeled deadline:

<!-- gnd-run expect=1 -->
```sh
gnd check release-demo/model.orm.json release-demo/seed.pop.json --admission --format json
```

The supplied repair satisfies the same model:

<!-- gnd-run expect=0 -->
```sh
gnd check release-demo/model.orm.json release-demo/repaired.pop.json --admission --format json
```

<!-- gnd-run expect=0 -->
```python
from gnd import api
result = api.check("release-demo/model.orm.json", "release-demo/seed.pop.json", admission=True)
failed = [v for v in result["report"]["verdicts"] if v["verdict"] == "fail"]
assert result["exit_code"] == 1
assert len(failed) == 1 and failed[0]["constraint_ref"] == "constraints[1]"
print("Release deadline finding:", failed[0]["message"])
```

Compare the model's domain vocabulary with [dispatch](quickstart.md). The two
examples intentionally use similar mechanics so that you can see which pieces
belong to GND and which describe your domain. For a different development
workflow, continue with [expense approvals](expense/01-model.md).
