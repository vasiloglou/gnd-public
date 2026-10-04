# Measurement receipt example

This independently synthetic movie/title example has two constraints and one conforming population per pool. The Faker pool uses seed 42. The other pool was authored by Codex as a synthetic fixture; generating its populations calls no external provider.

## Coverage

Both receipts cover 2 of 8 applicable cells: 25% coverage, six missing cells and two not-applicable cells. The example demonstrates portable receipts; its single conforming specimen does not exercise every case kind.

Open the [Faker corpus](02-corpus/movie/faker/index.json), [authored pool corpus](02-corpus/movie/llm-proposed/index.json), [Faker receipt](measurements/movie.faker.json), and [authored pool receipt](measurements/movie.llm-proposed.json).

## The per-constraint rates

Each constraint has n = 1 and no expected nonpass observation. The false-fail rate is 0.0 and the conditional false-pass rate is null. There is no blended "verifier accuracy".

This excerpt comes from each receipt's value constraint:

```json
{"constraint_ref":"constraints[0]","n":1,"expected_nonpass":0,"false_pass_rate":null,"false_fail_rate":0.0,"undecided_rate":0.0}
```

The two pool labels and digests differ. Joining their compatible constraint references gives matching rates for these two specimens. This observation belongs to this toy pair.
