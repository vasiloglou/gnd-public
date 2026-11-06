"""The plan's synthetic component graph (rule-check-adoption plan §9).

209 components and 2,047 distinct `uses` edges. Eight groups of mutually
reachable components, of sizes 90, 19, 13, 7, 3, 3, 2 and 2, each closed by a
ring; every other edge runs forward in one fixed order of the components, so
it closes no cycle. Seeded (209), so every run yields the same edges.
"""

from __future__ import annotations

import random

SEED = 209
COMPONENTS = 209
EDGES = 2047
GROUP_SIZES = (90, 19, 13, 7, 3, 3, 2, 2)


def edges() -> list[tuple[str, str]]:
    """The fixture's edges, sorted."""
    names = [f"c{index:03d}" for index in range(COMPONENTS)]
    block: dict[str, int] = {}
    start = 0
    rings: set[tuple[str, str]] = set()
    for number, size in enumerate(GROUP_SIZES):
        members = names[start : start + size]
        for position, name in enumerate(members):
            block[name] = number
            rings.add((name, members[(position + 1) % size]))
        start += size
    for offset, name in enumerate(names[start:]):
        block[name] = len(GROUP_SIZES) + offset
    candidates = sorted(
        (user, used)
        for user in names
        for used in names
        if user != used
        and (user, used) not in rings
        and (block[user] < block[used] or (block[user] == block[used] and block[user] < len(GROUP_SIZES)))
    )
    extra = random.Random(SEED).sample(candidates, EDGES - len(rings))
    return sorted(rings | set(extra))


def population_yaml(model: str) -> str:
    """A population document over `uses` for the model at ``model``."""
    lines = [
        f"population: {{ model: {model}, model_id: urn:gnd-fixture:rc2-graph@1, source: fixture, covers: [uses] }}",
        "facts:",
        "  uses:",
    ]
    lines += [f"    - {{ user: {user}, used: {used} }}" for user, used in edges()]
    return "\n".join(lines) + "\n"
