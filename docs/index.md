---
hide:
  - toc
---

<div class="hero" markdown>
<p class="eyebrow">GND · Get Nick Done · agent skills + Python</p>

# Build agentic data apps that check themselves.

<p class="lineage">Inspired by the success of <a href="https://github.com/gsd-build/get-shit-done">GSD (Get Shit Done)</a> for traditional software development, GND is its lighter sibling, built specifically for agentic data apps.</p>

<p class="lead">Describe your domain once as an executable ontology: an ORM model of facts, rules and constraints. Your agent answers with structured plans and facts instead of prose, and GND verifies them against the model and reports exactly which rule failed.</p>

[Build with your agent](agents/index.md){ .md-button .md-button--primary }
[Run a check in 60 seconds](quickstart.md){ .md-button }

</div>

<figure class="hero-media">
--8<-- "docs/assets/hero.svg"
<figcaption class="caption">You ask for a payment. The agent answers with a plan: operations over the model, not prose. GND checks the plan, names the precondition that failed, and the agent resubmits a plan that passes. <a href="agents/plans.md">Run this example yourself →</a></figcaption>
</figure>

## How it works

<div class="steps" markdown>
<div markdown>
<p class="number">01 / ONTOLOGY</p>

**State the rules once.** Write them as an ORM model, `model.orm.yaml`. An agent
drafts it with you through Halpin's conceptual schema design procedure, and every
rule reads back as a sentence you can confirm.
</div>
<div markdown>
<p class="number">02 / STRUCTURED OUTPUT</p>

**The agent answers in facts.** It replies with populations and operation plans,
such as `approve_expense(41, alice)` or `recommendation(ada, river)`, never paragraphs
you have to trust.
</div>
<div markdown>
<p class="number">03 / VERIFY AND FEED BACK</p>

**GND decides.** `gnd check` evaluates every constraint: pass, a failed rule with the
offending facts, a warning, or *cannot decide*. Closed feedback goes back to the agent;
no answer key leaks.
</div>
</div>

Because the checker is deterministic and its feedback names the exact rule and
binding that failed, a failed attempt is not the end of the task. The agent repairs
and retries inside a bounded session, so **smaller, cheaper models can finish work**
that a single unchecked prompt would hand to a frontier model. Any OpenAI-compatible
endpoint or local command can be the agent ([sessions](agents/dev-session.md)).

## One model in the middle

<div class="orm-teaser" markdown>
<div class="orm-teaser__figure">
--8<-- "docs/assets/orm-d2-exclusion.svg"
</div>
<div markdown>

GND's intermediate representation is **Object-Role Modeling (ORM 2)**, Terry Halpin's
fact-based conceptual modeling method. Every requirement becomes an elementary fact
type with explicit constraints, and each constraint reads back as a plain sentence a
domain expert can confirm. The diagram says *no reader is recommended a book they
already rated*. GND's checker, synthetic data, code generation and exports all read
that same model.

[Learn the notation](concepts.md) · [ORM Foundation](https://www.orm.net/) ·
[ORM 2 graphical notation](https://www.orm.net/pdf/ORM2.pdf)
</div>
</div>

<figure class="wide-figure">
--8<-- "docs/assets/orm-d7-intermediate-representation.svg"
</figure>

!!! tip "Coming from GSD?"

    GND keeps [GSD](https://github.com/gsd-build/get-shit-done)'s discipline (plan,
    execute, verify, record) and its skills-in-your-agent packaging. It replaces the
    requirements document with an executable model, so a phase is done when the
    model's checker says so. Already have a GSD project? The `gnd-adopt` skill migrates
    your `.planning/` requirements into a GND model, with every requirement accounted
    for. [Adopt a GSD project →](guides/evolution-and-recovery.md#adopt-a-gsd-project)

## GND is skills plus Python code

The **skills** tell a coding agent what to produce: a model, a population, a plan, a
session contract, an evolution proposal. The **Python runtime** checks what it
produced. The skills follow the [Agent Skills](https://agentskills.io/) format and
install into both agents:

<p class="pills"><span>Claude Code</span><span>Codex</span><span>Agent Skills format</span><span>Python ≥ 3.11</span></p>

```sh
pip install get-nick-done
gnd install --project
gnd doctor --project
```

| Ask your agent to… | Skill | It produces | GND checks it with |
|---|---|---|---|
| [Model a domain by dialogue](agents/model-from-text.md) | `gnd-model-from-text` | `model.orm.yaml` + verbalization | `gnd validate` |
| [Propose a plan](agents/plans.md) | your application's skill | `steps.json` | `gnd check --pre --steps` |
| [Work until the checker accepts](agents/dev-session.md) | `gnd-dev-session` | attempts under a session contract | `gnd exp run` |
| [Generate the project](agents/codegen-conformance.md) | `gnd-codegen` | derived tools + your extension | `gnd conformance` |
| [Change a rule](agents/evolve.md) | `gnd-model-evolve` | a reviewed proposal | `gnd evolve preview` / `apply` |
| [Read or write documents](agents/documents.md) | `gnd-extract`, `gnd-render-doc` | facts with a digest-bound sidecar | `gnd verify`, `gnd doccheck` |
| [Export or get a review](agents/export-and-review.md) | `gnd-export`, `gnd-review-panel` | Soufflé, Lean, witnesses, a panel review | `gnd replay`, `gnd review finalize` |

## What GND catches

<div class="gallery gallery--3" markdown>
<article markdown>
<p class="number">PLANS</p>

### A step was skipped

The agent tries to pay a draft expense. `reimburse_expense` fails its precondition
`pre_submitted`; the agent adds the missing steps.

[Check an agent's plan →](agents/plans.md)
</article>
<article markdown>
<p class="number">SIDE EFFECTS</p>

### Every fact legal, the walk is not

An approval also flipped a bystander expense to *rejected*. No snapshot check can see
it; the frame check fails the walk.

[The frame check →](guides/data-and-transitions.md#check-a-plan-and-its-side-effects)
</article>
<article markdown>
<p class="number">HARD RULES AND ADVICE</p>

### Already read

A recommender suggests a book Ada rated. `unread_only` fails and names the pair; a
genre mismatch is only a warning.

[BookRec, chapter 2 →](bookrec/02-facts.md)
</article>
<article markdown>
<p class="number">THE LOOP</p>

### Attempt 1 red, attempt 2 accepted

A session contract, closed answer-free feedback, and explicit outcomes: accepted,
stagnation, oscillation, budget exhausted.

[Drive an agent →](agents/dev-session.md)
</article>
<article markdown>
<p class="number">RULE CHANGES</p>

### Legal yesterday, illegal today

The same output, two model versions: an advisory rule promoted to a hard one rejects
yesterday's recommendations, with a blast-radius preview first.

[BookRec, chapter 6 →](bookrec/06-evolution.md)
</article>
<article markdown>
<p class="number">DERIVATIONS</p>

### Did it recommend everything eligible?

Derived fact types with stratified negation. GND names the eligible pair the
application missed, and the claimed pair it should not have made.

[Derivations →](guides/data-and-transitions.md)
</article>
<article markdown>
<p class="number">TEST THE TESTER</p>

### Measure the verifier itself

`gnd synth` generates conforming, boundary and violating populations; `gnd measure`
reports false-pass and false-fail rates per constraint.

[Synthetic data →](guides/synthetic-data.md)
</article>
<article markdown>
<p class="number">DOCUMENTS</p>

### Facts in, facts out

Render a document from facts with planted distractors, one of them instruction-shaped,
then extract the facts back and check both directions.

[Documents →](agents/documents.md)
</article>
<article markdown>
<p class="number">ENGINES</p>

### Three engines, one model

Trace vulnerable dependencies in Soufflé, prove a finite policy in Lean, and audit
approvals with PyRel.

[Verify at scale →](runtimes/scenario.md)
</article>
</div>

[See every capability in the tour →](tour.md)

## Verify at the scale you need

<div class="runtimes" markdown>
<div markdown>
**GND engine** *(default)*

Lightweight, portable native Python. No database, no service, and three-valued
verdicts: *unknown* never becomes *yes* or *no*.
</div>
<div markdown>
**Soufflé**

`gnd export souffle` writes a standalone Datalog program for recursive impact
analysis at scale. [Tutorial](runtimes/souffle.md)
</div>
<div markdown>
**Lean**

`gnd export lean` writes finite definitions and explicitly unproved obligations;
prove them, or find a counterexample. [Tutorial](runtimes/lean.md)
</div>
<div markdown>
**PyRel** *(optional)*

`gnd export pyrel` writes a standalone program that runs locally on DuckDB, or on
Snowflake when your business logic and data live in enterprise systems.
[Tutorial](runtimes/pyrel.md)
</div>
</div>

## Choose your path

| You want to… | Start here |
|---|---|
| Understand the ontology, facts and constraints | [ORM: the executable ontology](concepts.md) |
| See a useful failure in a few commands | [Run a check in 60 seconds](quickstart.md) |
| Build with Claude Code or Codex | [Work with an agent](agents/index.md) |
| See every feature with an example | [Capabilities tour](tour.md) |
| Add checks to existing Python code | [Python API](reference/python-api.md) |
| Find out whether a feature fits your problem | [Supported capabilities](reference/capabilities.md) |
| Improve GND itself | [Contributor guide](development/index.md) |

<p class="caption">A passing check means the supplied facts satisfy the modeled rules. GND verifies the output, never the producer; you still choose the rules and establish that the facts describe the world. Public builds report assurance as <code>unavailable</code>. The core checker runs locally and the tutorials need no model-provider key. Native Soufflé, Lean and PyRel execution, and Snowflake deployment, are optional and have their own prerequisites.</p>
