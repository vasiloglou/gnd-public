# Adopt rules on a project that already breaks them

A team wants its CI to check the project's architecture rules on every
change: no import loops, nothing in the legacy area, an owner for every
component. A scanner already turns the code into facts, and `gnd check`
judges them. The trouble is the first run. The project has broken some of
these rules for years, so a plain check fails on every change, and a gate
that always fails gets switched off.

This how-to sets the gate up so that violations a change adds fail it and
old ones do not. GND judges the change and the saved state of `main` under
the same rules, marks each violation **new** or **standing**, and counts the
ones the change fixed. A rule with nothing to judge, or one GND could not
decide, still stops the run, as described below.

Along the way you will see each rule named by the id its author wrote, with
the author's advice on what to do, every edge of every import loop, and a
rule accepted while the data it will judge does not exist yet.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="The change under review, against main">

![Part of the component graph of the change under review (cache, admin and four imports that break no rule are left out). The import loop between api and auth was already on main: its two rows are standing. The change adds a loop between search and util: its two rows are new. The loop between reports and billing on main is gone, because billing no longer imports reports; reports still imports billing, but no longer inside a loop, so both rows the loop gave on main are resolved. The component legacy_ui, in the legacy area, and metrics, which has no owner, were already like this on main: standing.](../assets/applications/rule-check-baseline.svg)
</div>

*Source: `catalog/head.population.yaml` against `catalog/base.population.yaml` of the shipped example; a selected view of the graph.*

!!! info "Files on GitHub"

    - [`rule_check/model.orm.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/rule_check/model.orm.yaml): the component catalog and its four rules, each with an `id` and a `remedy`
    - [`rule_check/base.population.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/rule_check/base.population.yaml): the catalog on `main`
    - [`rule_check/head.population.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/rule_check/head.population.yaml): the catalog of the change under review
    - [`rule_check/fixed.population.yaml`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/rule_check/fixed.population.yaml): the same change once its new loop is broken
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/how-to/adopt-rules-with-a-baseline.md)

Copy the example into a working folder:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/rule_check', 'catalog', dirs_exist_ok=True)"
```

## The rules and the facts

The model declares components and four facts about them: which component
imports which, the area it lives in, its owning team, and the release it
ships in. Its four rules each carry an `id` and a `remedy`, the author's
advice on what to do when the rule fails:

| Rule id | Says | Kind |
|---|---|---|
| `no_import_loops` | no component imports itself, directly or through others | must hold |
| `no_legacy_components` | no component lives in the `legacy` area | must hold |
| `every_component_has_an_owner` | every component should have an owning team | advisory |
| `no_draft_releases` | nothing ships in a draft release | must hold |

In this scenario the facts come from a scanner that reads the code, not from
a person or an agent, and the population files say so in their header:

<!-- gnd-run expect=0 output=stdout -->
```sh
head -7 catalog/head.population.yaml
```

```text
# The catalog on the change under review: breaks the reports/billing loop, adds a search/util loop.
population:
  model: model.orm.yaml
  model_id: urn:gnd-example:rule-check@1
  source: tool-output
  producer: "components-scan 1.4.0 @ 9b72c55"
  covers: [component_imports_component, component_is_in_area, component_has_owner, component_ships_in_release]
```

`source: tool-output` labels facts a deterministic program produced, and
`producer` names the program and the revision it read. Both are labels the
writer states; GND does not run or verify the scanner.

## One run is not enough

Check the change on its own, with `--rule-ids` so each verdict names the
rule's own id and prints its remedy:

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check catalog/model.orm.yaml catalog/head.population.yaml --rule-ids
```

```text
BLOCKING (alethic)
  [fail] constraint:no_import_loops (fact_types[component_imports_component].constraints[0]): The relation 'component_imports_component' is acyclic — violated: 2 strongly connected groups (sizes 2, 2) hold 4 edges.
    remedy: Break the loop: move the shared code into a lower component both can import.
  [fail] constraint:no_legacy_components (constraints[0]): Guarded comparison consequent evaluated over bindings=12 — violated by bindings: {'$c': 'legacy_ui', '$a': 'legacy'}.
    remedy: Move the component out of the legacy area, or retire it.
  [vacuous] constraint:no_draft_releases (constraints[1]): Fact type(s) 'component_ships_in_release' contain no facts in this population — constraint is vacuous, not evaluated.
    remedy: Ship the component in a numbered release, not a draft.
ADVISORY (deontic)
  [warning] constraint:every_component_has_an_owner (fact_types[component_has_owner].constraints[0]): Each component must play the 'component' role in 'component_has_owner' — violated: 'metrics' plays no such fact.
    remedy: Add the owning team to the component's catalog entry.
pass=0 fail=2 warning=1 unchecked=0 vacuous=1
COVERAGE
  component_imports_component: declared, facts=14
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
```

The check fails, and rightly: the change adds a loop between `search` and
`util`. But it would fail just as hard if the change touched nothing, because
`api` and `auth` have imported each other for a long time and `legacy_ui`
still lives in the legacy area. The loop rule's message says how many loops
there are and how big each one is; the JSON report lists every edge inside
them, one row per edge, as the next section shows.

The release rule says `vacuous`: no component has a release recorded yet, so
the rule has nothing to judge.

## Compare with main

Give the check the saved state of `main` as a baseline:

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check catalog/model.orm.yaml catalog/head.population.yaml --baseline catalog/base.population.yaml
```

```text
BLOCKING (alethic)
  [fail, new] constraint:no_import_loops (fact_types[component_imports_component].constraints[0]): The relation 'component_imports_component' is acyclic — violated: 2 strongly connected groups (sizes 2, 2) hold 4 edges.
    remedy: Break the loop: move the shared code into a lower component both can import.
  [fail, standing] constraint:no_legacy_components (constraints[0]): Guarded comparison consequent evaluated over bindings=12 — violated by bindings: {'$c': 'legacy_ui', '$a': 'legacy'}.
    remedy: Move the component out of the legacy area, or retire it.
  [vacuous] constraint:no_draft_releases (constraints[1]): Fact type(s) 'component_ships_in_release' contain no facts in this population — constraint is vacuous, not evaluated.
    remedy: Ship the component in a numbered release, not a draft.
ADVISORY (deontic)
  [warning, standing] constraint:every_component_has_an_owner (fact_types[component_has_owner].constraints[0]): Each component must play the 'component' role in 'component_has_owner' — violated: 'metrics' plays no such fact.
    remedy: Add the owning team to the component's catalog entry.
pass=0 fail=2 warning=1 unchecked=0 vacuous=1
COVERAGE
  component_imports_component: declared, facts=14
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
BASELINE catalog/base.population.yaml
  new=2 standing=4 resolved=2 positional_keyed=0 undecided=0
```

Each failing line now says whether it is new. The loop rule is `new`
because one of its loops is; the legacy component and the missing owner are
`standing`. The `BASELINE` lines count offending rows: two new (the
`search`/`util` loop), four standing, and two resolved (the
`reports`/`billing` loop, which the change broke). The run still fails, but
now only because of what the change added.

In JSON, the same counts are a `baseline` block, and each verdict marks its
rows one by one (the pipeline keeps `gnd`'s exit code, 1):

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check catalog/model.orm.yaml catalog/head.population.yaml --baseline catalog/base.population.yaml --format json \
  | python -c "import json, sys; report = json.load(sys.stdin); print(json.dumps(report['baseline'], indent=2)); [print(v['address'], row, mark) for v in report['verdicts'] if v['row_novelty'] for row, mark in zip(v['offending_facts'], v['row_novelty'])]"
```

```text
{
  "population": "catalog/base.population.yaml",
  "population_sha256": "d816aea7caf713a67837f1361c4a2676a91a5aac82ba7167bf1ef88106fd5fcd",
  "new": 2,
  "standing": 4,
  "resolved": 2,
  "positional_keyed": 0,
  "undecided": 0
}
constraint:no_import_loops ['api', 'auth'] standing
constraint:no_import_loops ['auth', 'api'] standing
constraint:no_import_loops ['search', 'util'] new
constraint:no_import_loops ['util', 'search'] new
constraint:every_component_has_an_owner metrics standing
constraint:no_legacy_components {'$c': 'legacy_ui', '$a': 'legacy'} standing
```

A violation is matched across the two runs by its rule's address and its
offending row, so the match does not depend on the order of the facts.

## Fix the new loop

The author breaks the loop by having `util` stop importing `search`:

<!-- gnd-run expect=2 output=stdout -->
```sh
gnd check catalog/model.orm.yaml catalog/fixed.population.yaml --baseline catalog/base.population.yaml
```

```text
BLOCKING (alethic)
  [fail, standing] constraint:no_import_loops (fact_types[component_imports_component].constraints[0]): The relation 'component_imports_component' is acyclic — violated: 1 strongly connected group (size 2) holds 2 edges.
    remedy: Break the loop: move the shared code into a lower component both can import.
  [fail, standing] constraint:no_legacy_components (constraints[0]): Guarded comparison consequent evaluated over bindings=12 — violated by bindings: {'$c': 'legacy_ui', '$a': 'legacy'}.
    remedy: Move the component out of the legacy area, or retire it.
  [vacuous] constraint:no_draft_releases (constraints[1]): Fact type(s) 'component_ships_in_release' contain no facts in this population — constraint is vacuous, not evaluated.
    remedy: Ship the component in a numbered release, not a draft.
ADVISORY (deontic)
  [warning, standing] constraint:every_component_has_an_owner (fact_types[component_has_owner].constraints[0]): Each component must play the 'component' role in 'component_has_owner' — violated: 'metrics' plays no such fact.
    remedy: Add the owning team to the component's catalog entry.
pass=0 fail=2 warning=1 unchecked=0 vacuous=1
COVERAGE
  component_imports_component: declared, facts=13
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
BASELINE catalog/base.population.yaml
  new=0 standing=4 resolved=2 positional_keyed=0 undecided=0
```

Nothing is new any more, so no rule fails the run. It exits 2 instead of 0
for a different reason: the release rule is still vacuous, and a check that
could not judge one of its rules does not call the data acceptable.

## Accept a rule that has nothing to judge yet

The release rule was shipped before the scanner records releases, on
purpose. Say so for the whole run with `--allow-vacuous`:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check catalog/model.orm.yaml catalog/fixed.population.yaml --baseline catalog/base.population.yaml --allow-vacuous
```

```text
BLOCKING (alethic)
  [fail, standing] constraint:no_import_loops (fact_types[component_imports_component].constraints[0]): The relation 'component_imports_component' is acyclic — violated: 1 strongly connected group (size 2) holds 2 edges.
    remedy: Break the loop: move the shared code into a lower component both can import.
  [fail, standing] constraint:no_legacy_components (constraints[0]): Guarded comparison consequent evaluated over bindings=12 — violated by bindings: {'$c': 'legacy_ui', '$a': 'legacy'}.
    remedy: Move the component out of the legacy area, or retire it.
  [vacuous] constraint:no_draft_releases (constraints[1]): Fact type(s) 'component_ships_in_release' contain no facts in this population — constraint is vacuous, not evaluated.
    remedy: Ship the component in a numbered release, not a draft.
ADVISORY (deontic)
  [warning, standing] constraint:every_component_has_an_owner (fact_types[component_has_owner].constraints[0]): Each component must play the 'component' role in 'component_has_owner' — violated: 'metrics' plays no such fact.
    remedy: Add the owning team to the component's catalog entry.
pass=0 fail=2 warning=1 unchecked=0 vacuous=1
COVERAGE
  component_imports_component: declared, facts=13
  component_is_in_area: declared, facts=12
  component_has_owner: declared, facts=11
  component_ships_in_release: declared, facts=0
BASELINE catalog/base.population.yaml
  new=0 standing=4 resolved=2 positional_keyed=0 undecided=0
vacuous accepted: 1 rules have nothing to judge yet (--allow-vacuous).
```

The run passes, and the vacuous rule is still listed. The last line counts
the vacuous rules the option covers; it is printed whenever the option is on
and a rule is vacuous, so read the exit code for the verdict. With the option
on, a new violation of a must-hold rule, or a must-hold rule that could not
be decided, still stops the run.

## What CI runs

One command per change, with the population of `main` saved as an artifact
of the last merge. The paths below are placeholders for your pipeline's own
files, not the example's:

```text
gnd check MODEL.orm.yaml HEAD.population.yaml --baseline MAIN.population.yaml --allow-vacuous --format json
```

| Exit | Meaning under `--baseline` |
|---|---|
| 0 | no new violation; standing ones are counted, not failed |
| 1 | at least one new violation of a must-hold rule |
| 2 | a rule had nothing to judge in the change, and `--allow-vacuous` is absent |
| 3 | the model or either population is ill-formed, or the model is not supported (below) |
| 4 | a must-hold rule could not be decided in either run, so "no new violations" cannot be claimed |
| 64 | a usage error, such as conflicting flags |
| 70 | an internal error |

## Limits

- `--rule-ids`, `--baseline` and `--allow-vacuous` produce report version
  15, for one plain snapshot check. Models with temporal terms, an active
  redaction policy or reference populations are refused with
  `check:rule-ids-unsupported`; under `--baseline`, models with structured
  derivations are refused with `check:baseline-unsupported`. Both refusals
  come before either population is read.
- A rule without an `id` is matched by its position, which moves if a rule
  is inserted above it. The check says how many such keys it used and warns
  when there are any; give rules ids before relying on a baseline.
- The report fields are listed in the [rule-check report reference](../reference/rule-check-report.md).
