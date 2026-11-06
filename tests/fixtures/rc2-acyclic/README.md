# RC2 corpus: the full extent of an `acyclic` violation (report version 15)

This corpus is the approval instrument for phase RC2 of the
`rule-check-adoption` milestone (spec:
`.gnd-planning/milestones/rule-check-adoption/notes/phase-RC2-spec.md`, §11).
It is committed before any implementation and fails until RC2 lands.
`tests/test_rc2_acyclic_extent.py` runs every case from this directory and
compares the result with the answer key in `expected/`. This README tells
each case's story only; the expected bytes and exit codes are in
`expected/`.

Every command runs with this directory as the working directory.

## Why

Today an `acyclic` rule that fails names one cycle. When the graph holds
several loops, the one named depends on the whole graph: adding a loop in
one place can change which loop is reported somewhere else. A CI gate that
compares runs then sees a "new" violation where nothing changed. Under
`--rule-ids` (report version 15), a failing `acyclic` rule instead lists
every edge that lies inside a loop, so each loop's edges stay put whatever
happens elsewhere, and its message says how many separate loops there are
and how many components each one has. Without `--rule-ids` nothing changes.

## The models

- `models/graph.orm.yaml`: components use other components. One rule,
  `no_import_loops`: the uses relation is `acyclic`, with a remedy.
- `models/graph-composite.orm.yaml`: the same graph with the rule
  `layered_imports`, variant `acyclic-intransitive`: no loops, and no edge
  `a -> c` when `a -> b -> c` already exists.

## The cases

1. **two-groups.** `gnd check models/graph.orm.yaml
   populations/two-groups.pop.yaml --rule-ids --format json`. `a` and `b`
   use each other, `c` and `d` use each other, `b` uses `c`, and `e` uses
   `a`. There are two separate loops. The rule fails and lists the four
   edges inside them; `b -> c` and `e -> a` are not inside any loop and are
   not listed. The message says two loops of two components each hold four
   edges.
2. **add-disjoint.** The same graph plus a new loop `A -> B -> C -> A`
   that touches nothing else. Today's report names only the new loop and
   drops the old one. Under RC2 the edges of the two old loops are listed
   exactly as in case 1, and the new loop's three edges are added.
3. **self-loop.** `a` uses itself, and `a -> b -> c` is a chain. The one
   self-use is listed as its own edge, a loop of one component; the chain is
   not listed.
4. **clean.** A chain with a shortcut, `a -> b -> c` and `a -> c`. No loop:
   the rule passes, and the report is what RC1 already gives.
5. **composite.** `models/graph-composite.orm.yaml` with `p` and `q` using
   each other, and `r -> s -> t` plus the shortcut `r -> t`. The loop's two
   edges are listed, then the shortcut's witness `(r, s, t)` exactly as
   today; the message names the loop and then the shortcut as today's
   message does.
6. **text-two-groups.** Case 1 without `--format json`: the text report
   prints the same message as the JSON report.
7. **Without `--rule-ids`.** Every case above run without the flag gives
   today's version-7 bytes (`expected/<case>.v7.json`, recorded before any
   RC2 change).

## The large fixture

`generate.py` builds the plan's synthetic graph: 209 components, 2,047
edges, loops of 90, 19, 13, 7, 3, 3, 2 and 2 components. The tests build it
in memory; it is not committed as a population file.

## Also changed by RC2

RC1's corpus (`../rc1-rule-ids/`) has one failing `acyclic` rule under
`--rule-ids`. Its answers `expected/declared-fail.json` and
`expected/declared-fail.txt` are updated to the RC2 form (owner ruling D5,
2026-11-06): the two edges of its one loop, and the loop count in the
message.
