# 09: a unary fact type

**Model.** A Person is identified by a PersonId. A Person may smoke.

**Semantic model.** One dataset, `person`, with `person_id` (Integer) and
the flag `person_smokes` (Boolean). The flag is never NULL: false means the
person does not smoke.

**Mapping.**
- **Objects.** A Person comes from `person.person_id`.
- **Links.** "Person smokes" has one role, so its tree is a single root node
  that names the relationship (a unary is named at level 1). Not every row
  is a link, so the expression is
  `CASE WHEN "PERSON"."PERSON_SMOKES" THEN "PERSON"."PERSON_ID" END`. It
  gives the person where the flag is true and NULL otherwise, and a NULL
  gives no link.

**Open point.** Ossie does not define what a NULL in a mapping expression
means. "No link" is GND's reading (decision E8), recorded as a known risk.

**Extension.** The fact type is carried as the column `person_smokes`.
