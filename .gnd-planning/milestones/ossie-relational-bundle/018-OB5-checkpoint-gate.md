# OB5 checkpoint gate

**Owner ruling, 2026-11-25.** `auto=false`.

At the viewable checkpoint (H1) the owner was shown the three pages at
commit `4cacaf8d` and asked three questions:

1. Are the pages good to go to the Codex review, or do you have changes?
2. Should I fix the two broken links in this phase so the strict build passes?
3. Do you want Ossie's own validator run now (H7)?

The owner answered:

> yes to all

## Rulings

| Item | Ruling |
|---|---|
| Checkpoint (H1) | **Passed.** The pages go to the review as written. |
| The two broken links | **Fix in this phase.** `docs/agents/model-from-text.md` and `docs/agents/evolve.md` link to a file outside the site. Both are broken on main (from `b36b446d`). This widens OB5 by those two lines. |
| H7, OB3-Q3 | **Requested.** The opt-in oracle lane runs now, for the semantic model and mapping of the export census (OB3 T11) and of the valid binding corpus (OB4 T13), on the code at this branch. The root is prepared from the OS0 receipt. |
