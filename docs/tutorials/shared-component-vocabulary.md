# Share the scanner, keep your own rules

Two teams use the same component scanner. Checkout needs to stop import loops.
Platform wants every component to have an owner. They agree on what a component
and an import mean; they make different decisions about what is acceptable.

With GND, the scanner can ship that shared vocabulary once. Each project keeps
a small model containing its own rules and a pin to the vocabulary it uses.
Updating the scanner's vocabulary does not replace the project's policy.

This example expands the [component catalog](../how-to/adopt-rules-with-a-baseline.md)
already shipped with GND. Its twelve components include `api`, `auth`, `search`,
`util` and `metrics`. The facts are example scanner output; GND checks those
facts and does not run the scanner itself.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="One vocabulary and two project policies">

![One component vocabulary supplies both projects. Checkout owns a blocking no-import-loops rule: api and auth form one loop, search and util another. Removing the two return imports makes the rule pass. Platform owns an advisory ownership rule: metrics has no owner, so GND warns; assigning it to the platform team removes the warning. Both projects keep identical vocabulary bytes, and both repairs leave the vocabulary and project rules unchanged.](../assets/applications/shared-vocabulary-teams.svg)
</div>

*Source: the shipped `model_composition/checkout/` and `model_composition/platform/`
models and before/after catalogs, adapted from `rule_check`. The
[commands page](../how-to/share-a-vocabulary.md) reproduces every result.*

!!! info "Files on GitHub"

    These review-copy files are on the draft branch:

    - [Checkout's project rules](https://github.com/vasiloglou/gnd-public/blob/codex/model-composition-docs-draft/src/gnd/examples/model_composition/checkout/project.orm.yaml)
    - [Platform's project rules](https://github.com/vasiloglou/gnd-public/blob/codex/model-composition-docs-draft/src/gnd/examples/model_composition/platform/project.orm.yaml)
    - [The component vocabulary](https://github.com/vasiloglou/gnd-public/blob/codex/model-composition-docs-draft/src/gnd/examples/model_composition/checkout/vocabulary/components-v1.orm.yaml)
    - [All example files](https://github.com/vasiloglou/gnd-public/tree/codex/model-composition-docs-draft/src/gnd/examples/model_composition)

## The result

| Project | Its own rule | First check | After the repair |
|---|---|---|---|
| Checkout | No import loops | Two loops fail the rule: `api` ↔ `auth`, `search` ↔ `util` | Both loops are broken; the rule passes |
| Platform | Every component should have an owner | A warning: `metrics` has no owner | `metrics` has an owner; the warning is gone |

Both projects use identical vocabulary bytes. Their project files contain their
own rules without copying the component and fact declarations. Platform's
ownership rule is advisory, so its first check warns without blocking the run.
Checkout's no-loops rule is blocking.

The [commands and example files](../how-to/share-a-vocabulary.md) reproduce
these results. Prompts below are requests you can give your coding assistant;
they are not recordings of an agent conversation.

## 1. Give the teams the same words

**You ask**

```text
Use the shipped component vocabulary for both projects. Keep checkout's
no-import-loops rule and platform's ownership rule in their own project files.
Show me which parts belong to the tool and which belong to each project.
```

The tool owns the meaning and shape of the exported facts: a component imports
another component, belongs to an area, has an owning team, or ships in a release.
Those declarations live in a versioned vocabulary file.

Each project keeps a local copy of that vocabulary and pins its exact bytes.
Its own file adds the policy:

| Shared by the tool | Owned by checkout | Owned by platform |
|---|---|---|
| Components, areas, teams, releases and the facts connecting them | No component may import itself, directly or through other components | Every component should have an owning team |

GND reads the vocabulary and the project's additions as one model. The team
can check the scanner's facts against its own policy without maintaining a
second copy of the vocabulary's declarations.

## 2. Ask for findings the team can act on

**You ask**

```text
Check both catalogs. Name the rule behind each finding and show the advice
its author supplied for fixing it.
```

Checkout's no-import-loops rule finds two groups: `api` with `auth`, and
`search` with `util`. The project supplied this remedy:

> Break the loop: move the shared code into a lower component both can import.

Platform's ownership rule points to `metrics`. Its advice is:

> Add the owning team to the component's catalog entry.

These remedies come from the project's rule files. GND reports them alongside
the findings; it does not choose or carry out the code change.

## 3. Repair the facts and check again

**You ask**

```text
Compare each catalog with its repaired version. Did checkout remove both
loops? Did platform add an owner for metrics? Did either project have to
change the shared vocabulary?
```

In checkout's repaired catalog, `auth` no longer imports `api`, and `util` no
longer imports `search`. Both loops disappear. In platform's repaired catalog,
`metrics` belongs to the `platform` team. Its ownership warning disappears.

Neither repair changes the vocabulary or the project rules. The scanner facts
change; the same rules judge them again.

## When the tool's vocabulary changes

A new vocabulary is a separate project decision. A pin keeps a tool update
from silently changing the model a project's rules depend on. If the file's
bytes no longer match the pin, GND refuses the model before checking facts.

The next part of this example will show a vocabulary update that changes a
fact used by a project rule, the review that names what breaks, and the combined
change that updates the pin and repairs the rule. That walkthrough is still in
progress; the current runnable example covers sharing, findings and repairs.
