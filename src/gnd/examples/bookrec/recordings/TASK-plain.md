# Task

Recommend books for Ada.

Write `recommendation.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` whose `recommendation`
list contains at least two books for `ada`. Keep every other fact list and the
`population` header exactly as they are. The rules are in `../model.orm.yaml`;
the books, genres, ratings and reader preferences are in the seed facts.

If you can run commands, check your file with
`gnd check ../model.orm.yaml recommendation.population.json` and fix it until
the check exits 0. Edit nothing outside the candidate directory.
