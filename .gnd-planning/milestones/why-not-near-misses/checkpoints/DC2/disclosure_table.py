"""Generate the disclosure table of docs/reference/disclosure.md from gnd.disclosure.SURFACES.

DC2 draft of the generator NM4 ships; every row of the table comes from the code.
"""
from gnd.disclosure import SURFACES

CLASS = {
    ("site", "declared"): "declared roles: shown under `internal`, redacted under `customer`; `--unredacted` / `unredacted=True` refused under `customer`",
    ("site", "view"): "every value: raw under `internal`, value-free under `customer`; `--raw` / `raw=True` refused under `customer`",
    ("every-mode", None): "the same in every mode (see [outputs the same in every mode](#outputs-that-are-the-same-in-every-mode))",
    ("value-free", None): "emits no population values",
}
GROUP = {"gnd": "Command", "api": "`gnd.api`", "export.service": "`gnd.export.service`", "kind": "Output kind"}


def name(key):
    if key.startswith("gnd "):
        return "gnd", f"`{key}`"
    prefix, _, rest = key.partition(":")
    return prefix, f"`{rest}`"


def table():
    rows = {}
    for key, surface in SURFACES.items():
        if surface.note == "a library binding, not an output":
            continue
        prefix, label = name(key)
        rows.setdefault((surface.kind, surface.convention), {}).setdefault(prefix, []).append(
            label + (" (starts processes)" if surface.spawns else ""))
    lines = ["| Surfaces | What they disclose |", "|---|---|"]
    for cls in CLASS:
        for prefix in GROUP:
            names = rows.get(cls, {}).get(prefix)
            if names:
                lines.append(f"| {GROUP[prefix]}: {', '.join(names)} | {CLASS[cls]} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(table())
