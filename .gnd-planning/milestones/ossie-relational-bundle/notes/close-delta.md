# ossie-relational-bundle · close delta

What the milestone delivered differently from plan r2 as approved
(`002-plan-gate.md`), 2026-11-25. Read with plan r3 and
`notes/close-results.md`.

## Plan amendments at the close (plan §11)

Eighteen rows, A1 to A18, each naming the record that raised it; A17 and A18
came from the close review `(c2)`. The ones
that change what a user sees:

1. **A8.** A model that maps to no table writes three files, not five.
2. **A9.** The mapping lists links it cannot write (`unmapped_links`), a
   fact type above 32 roles is listed, and foreign-key names are unique in
   the whole schema.
3. **A11, A13.** For a binding: an entity and a part of its identifier may
   share a column; an identifier nested more than 8 entities deep is not
   followed; a fact held only through a surrogate key cannot be bound.
4. **A14.** Identifiers are quoted in Ossie's normalized form: upper-cased
   only when regular. OB3's spec (E5) and normative text, as merged,
   upper-cased every name; plan r2 states no quoting rule `(c3)`. The
   upstream validator rejects that for a name such as `uni.student`.
5. **A16.** No source-cap parameter was added (D11).
6. **A17** `(c2)`. A default run has a second new failure: the size bound
   covers the two new files, so it can stop with `ossie:output-size` where
   the three-file run succeeded.
7. **A18** `(c2)`. The normative home is two sections, "Relational mapping
   (Rmap)" and "Ossie interchange".

The rest correct the plan's description of the baseline or of Halpin's
method (A1–A7, A10, A12) or name the release-notes page (A15).

## Delivered beyond the plan

- An independent corpus checker for the relational files and the bindings
  (`tests/support/ossie_relational_corpus.py`,
  `tests/support/physical_binding_corpus.py`), written before the code.
- Oracle-lane tests for the relational files, and one that holds GND's
  regular-identifier class to the pinned validator's over every character.
- Two links on `docs/agents` pages, broken on main by another milestone,
  were fixed so the strict site build passes.

## In the plan, as ruled `(c2)`

- `--max-input-bytes` on `gnd import ossie`: plan D3 (b), approved at the
  plan gate. It was listed above as beyond the plan in error.

## Not delivered

- External acceptance (the reporter's run). D10 is not sent.
- The three GitHub issues are not filed, so the records link none.
- The oracle lane's consumer test was not run.
