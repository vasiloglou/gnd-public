# Disclosure example

A two-column model whose `email` role is declared `redact: true`, and a
population in which customer `c-1` has two email addresses, which violates
`one_email_per_customer`.

```sh
gnd check model.orm.yaml population.json --format json
GND_DISCLOSURE=customer gnd check model.orm.yaml population.json --format json
gnd --disclosure internal check model.orm.yaml population.json --format json
```

With the mode unset or `customer`, the report names the violation but not the
addresses. Under `internal` it shows them. Under `customer`, `--unredacted` is
refused with exit 3. See `docs/reference/disclosure.md`.
