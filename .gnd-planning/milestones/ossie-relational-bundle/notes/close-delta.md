# ossie-relational-bundle · close delta

What the milestone delivered differently from plan r2 as approved
(`002-plan-gate.md`), 2026-11-25. Read with plan r3 and
`notes/close-results.md`.

## Plan amendments at the close (plan §11)

Sixteen rows, A1 to A16, each naming the record that raised it. The ones
that change what a user sees:

1. **A8.** A model that maps to no table writes three files, not five.
2. **A9.** The mapping lists links it cannot write (`unmapped_links`), a
   fact type above 32 roles is listed, and foreign-key names are unique in
   the whole schema.
3. **A11, A13.** For a binding: an entity and a part of its identifier may
   share a column; an identifier nested more than 8 entities deep is not
   followed; a fact held only through a surrogate key cannot be bound.
4. **A14.** Identifiers are quoted in Ossie's normalized form: upper-cased
   only when regular. Plan r2 and OB3 as merged upper-cased every name,
   which the upstream validator rejects for a name such as `uni.student`.
5. **A16.** No source-cap parameter was added (D11).

The rest correct the plan's description of the baseline or of Halpin's
method (A1–A7, A10, A12) or name the release-notes page (A15).

## Delivered beyond the plan

- `--max-input-bytes` on `gnd import ossie` (D3 (b)).
- An independent corpus checker for the relational files and the bindings
  (`tests/support/ossie_relational_corpus.py`,
  `tests/support/physical_binding_corpus.py`), written before the code.
- Oracle-lane tests for the relational files, and one that holds GND's
  regular-identifier class to the pinned validator's over every character.
- Two links on `docs/agents` pages, broken on main by another milestone,
  were fixed so the strict site build passes.

## Not delivered

- External acceptance (the reporter's run). D10 is not sent.
- The three GitHub issues are not filed, so the records link none.
- The oracle lane's consumer test was not run.
