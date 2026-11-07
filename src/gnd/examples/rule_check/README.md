# rule_check

The worked example of the how-to "Adopt rules on a project that already
breaks them" (`docs/how-to/adopt-rules-with-a-baseline.md`).

- `model.orm.yaml`: a component catalog and four rules, each with an id and
  a remedy: no import loops, no component in the legacy area, every
  component should have an owner, and nothing ships in a draft release.
- `base.population.yaml`: the catalog on main, with the violations the
  project already has.
- `head.population.yaml`: the catalog of a change under review, which fixes
  one old loop and adds a new one.
- `fixed.population.yaml`: the same change after the new loop is broken.

All three are labelled `source: tool-output`, with the scanner and revision
that produced them.
