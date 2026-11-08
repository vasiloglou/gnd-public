# FU3 corpus: an `acyclic` ring over a derived fact type (issue 119)

This corpus is the approval instrument for phase FU3 of the
`rule-check-followups` milestone (spec:
`.gnd-planning/milestones/rule-check-followups/notes/phase-FU3-spec.md`).
`tests/test_fu3_derived_ring.py` runs every case from this directory and
compares the result with the answer key in `expected/`. This README tells
each case's story; the expected bytes and exit codes are in `expected/`.

## Why

Under `--rule-ids` (report version 15) a failing `acyclic` rule lists every
edge that lies inside a loop. That listing is computed by a second pass over
the population, not read from the checker's own result. For a ring over a
fact type that is derived through an arithmetic term, the checker takes a
different route, and nothing showed that the two passes read the same edges.
This corpus pins that they do.

## The model

`models/ring.orm.yaml`: a node hops by a number modulo another number, and
"node leads to node" is derived from that: `from` leads to `a mod b`. The
`mod` term makes this an exact-term derivation. One rule, `no_loops`: the
leads relation is `acyclic`.

The checker judges the `leads` facts the population states. Whether those
facts match what the rule derives is a separate verdict, on the derivation.
In every case the hops derive the same six edges: `1 -> 2`, `2 -> 1`,
`3 -> 4`, `4 -> 3`, `2 -> 3` and `5 -> 1` (only `mod-zero` differs).

## The cases

1. **agree.** The population states exactly the six derived edges. The
   derivation passes. The rule fails: two loops, `1 <-> 2` and `3 <-> 4`,
   and their four edges are listed; `2 -> 3` and `5 -> 1` are in no loop and
   are not listed. Without `--rule-ids` the report names one cycle,
   `1 -> 2 -> 1`, as it always has.
2. **add-disjoint.** As `agree`, plus a new loop `20 <-> 21` that is both
   derived and stated and touches nothing else. The four edges of case 1 are
   listed unchanged and in the same order, then the two new ones.
3. **asserted-only.** The population states `1 -> 2`, `3 -> 4`, `2 -> 3`,
   `5 -> 1` and a loop `7 <-> 8` the rule does not derive. The derivation
   fails (edges missing, and edges that should not be there). The rule fails
   on the stated loop: `7 -> 8` and `8 -> 7` are listed, and nothing from
   the derived-only loops.
4. **derived-only.** The population states only `1 -> 2` and `2 -> 3`. The
   derived edges hold two loops, but the stated ones hold none. The
   derivation fails (incomplete); the rule passes, and nothing is listed.
5. **mod-zero.** One hop is modulo zero, so the derivation cannot be
   computed. The population states the loop `1 <-> 2`. The rule is unchecked
   with reason `term:mod-zero` on both versions, and nothing is listed; exit
   4.
6. **Without `--rule-ids`.** Every case above without the flag gives the
   version-7 report in `expected/<case>.v7.json`.
