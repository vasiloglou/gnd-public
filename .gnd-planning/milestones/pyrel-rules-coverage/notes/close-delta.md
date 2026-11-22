# pyrel-rules-coverage — delta from the plan

What the milestone delivered beyond, or differently from, plan r4 as
written. The canonical statement of each is plan §11.

1. **Single-fact-type external uniqueness** (A1). The plan named anchors by
   object type only. One fact type is a projection in GND, so its anchors
   are its roles.
2. **Disconnected vacuity** (A2). Vacuous only when every list is empty,
   and read from the computed view of semiderived types. The LQP version
   always lists the rule.
3. **Input refusals widened** (A3). Numerically equal rows count as repeats.
   Non-finite numbers are refused everywhere. LQP returns 3 for an
   unreadable population. The last two predate the milestone and are
   repaired by it.
4. **D6 widened** (A4). From cells and constants to reference facts, nested
   constants, arithmetic, aggregates and head roles: every route a value
   PyRel would round could take.
5. **Ossie** (A5). One Ossie line keeps fact-scoped value rules as
   extensions, so the Ossie export is unchanged, as plan §0 requires.
6. **Generated names** (A6). Universes are recorded where they arise. This
   also closes a pre-existing gap for plan create effects.
7. **Runtime page** (A7). Older statements narrowed to match the code.
8. **Comparator** (RP3). The shared comparator compares witness numbers by
   GND's identity (`1` = `1.0`), because the programs print Float values
   as floats.
9. **RF6 inventory**. Three authenticated successor deltas
   (`evidence/RP1`, `RP3`, `RP4`) record the new counted reads; no
   historical evidence was rewritten.
10. **Process**. RP1's code and RP5's tests were drafted before their gates
    were written, and the records disclose it. Each gate was committed
    before its phase commit.
