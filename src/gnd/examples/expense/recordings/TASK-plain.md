# Task

Record an approval of expense 102.

Write `approvals.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` with expense `102` added
to `expense_is_approved` and to `expense_approved_by_chain`, naming the chain
that approves it. Keep every other fact and the `population` header exactly as
they are. The rules, including who may approve how much, are in
`../model.orm.json`.

If you can run commands, check your file with
`gnd check ../model.orm.json approvals.population.json` and fix it until the
check exits 0. Edit nothing outside the candidate directory.
