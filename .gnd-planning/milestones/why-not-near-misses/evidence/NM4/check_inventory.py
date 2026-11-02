"""NM4 T9: every file the plan's inventory command finds has a row in the spec's disposition table."""
import pathlib, re, subprocess, sys
spec = (pathlib.Path(__file__).parents[2] / "notes/phase-NM4-spec.md").read_text()
table = spec.split("### Inventory and dispositions (NM4-C1)", 1)[1].split("\nNew files:", 1)[0]
rows = [line for line in table.splitlines() if line.startswith("| `")]
named = set()
for row in rows:
    cell = row.split("|")[1]
    paths = re.findall(r"`([^`]+)`", cell)
    base = paths[0].rsplit("/", 1)[0] if paths else ""
    for p in paths:
        named.add(p if "/" in p else f"{base}/{p}")
        if "/" in p and p.count("/") == 2 and p.startswith("gnd-"):
            named.add(f"src/gnd/skills/{p}")
    # "a/b/x.md, `c/y.md`" rows: relative names after the first take the first's directory or the skills root
    for p in paths[1:]:
        named.add(f"src/gnd/skills/{p}")
inventory = subprocess.run(["git", "grep", "-li", r"redact\|--raw\|unredacted\|why-not\|disclos", "HEAD", "--",
                            "docs", "src/gnd/skills"], capture_output=True, text=True, check=True).stdout.split()
inventory = [line.split(":", 1)[1] for line in inventory]
new = {"docs/reference/disclosure.md", "docs/how-to/disclosure-mode.md"}
missing = [f for f in inventory if f not in named and f not in new]
print("\n".join(missing) or f"{len(inventory)} inventory files, each with a disposition")
sys.exit(bool(missing))
