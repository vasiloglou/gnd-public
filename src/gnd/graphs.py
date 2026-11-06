"""Graph algorithms shared across layers; imports nothing from gnd."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import TypeVar

N = TypeVar("N", bound=Hashable)


def strongly_connected_components(
    nodes: Iterable[N], successors: Mapping[N, Sequence[N]]
) -> list[list[N]]:
    """Every strongly connected component, in Tarjan completion order.

    Iterative, so a long chain cannot exhaust the Python stack. Roots are
    tried in ``nodes`` order and each node's successors in the order given, so
    the result is deterministic for deterministic inputs. A component is
    emitted before any component that reaches it (dependencies first), and its
    members are in stack-pop order. Singletons are included; callers filter.
    A successor missing from ``successors`` is treated as having none.
    """
    index: dict[N, int] = {}
    low: dict[N, int] = {}
    on_stack: set[N] = set()
    stack: list[N] = []
    components: list[list[N]] = []
    for root in nodes:
        if root in index:
            continue
        work: list[tuple[N, int]] = [(root, 0)]
        while work:
            node, position = work[-1]
            if position == 0:
                index[node] = low[node] = len(index)
                stack.append(node)
                on_stack.add(node)
            children = successors.get(node, ())
            descended = False
            while position < len(children):
                child = children[position]
                position += 1
                if child not in index:
                    work[-1] = (node, position)
                    work.append((child, 0))
                    descended = True
                    break
                if child in on_stack:
                    low[node] = min(low[node], index[child])
            if descended:
                continue
            if low[node] == index[node]:
                component: list[N] = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                components.append(component)
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
    return components
