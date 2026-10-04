---
hide:
  - toc
---

<div class="hero" markdown>
<p class="eyebrow">GND · Get Nick Done</p>

# Build applications with rules you can check.

<p class="lead">Turn domain requirements into explicit models. Build with a coding agent or Python. Check the facts your application produces, understand failures, and evolve the rules.</p>

[Build BookRec](bookrec/01-model.md){ .md-button .md-button--primary }
[Try a first check](quickstart.md){ .md-button }

</div>

## The gap between “it runs” and “it follows the rules”

A recommender returns a book someone already read. An expense is approved without
a recorded submission. A shipment takes longer than its deadline. The program ran,
but its output broke a rule you care about.

GND lets you state those rules in a **conceptual model** and check a
**population of facts** against them. The resulting report identifies failing
constraints and advisory warnings. Your application decides what to do next:
reject an output, explain it to a person, or ask an agent to propose a repair.

![The model and candidate facts feed GND; findings guide a repair and another check.](assets/check-loop.svg){ .mechanism }

## More than the first check

Use the same model through a development cycle: author it with an agent, examine
examples, generate a Python project, implement the application, test its output,
and evolve the model when the requirements change. GND provides commands and
agent skills for these steps. You select the handoffs; the checker does not
silently change your model or application.

<div class="gallery" markdown>
<article markdown>
<p class="number">01 / BUILD AN APPLICATION</p>

### A recommender with explicit rules

Build **BookRec**, a working Python library and CLI. Prevent recommendations of
already-read books, enforce age restrictions, inspect genre warnings and learn
why a rule change can reject yesterday's output.

[Follow the six-chapter tutorial →](bookrec/01-model.md)
</article>
<article markdown>
<p class="number">02 / MODEL A WORKFLOW</p>

### Expense approvals you can inspect

Build an expense approval/reporting CLI. Check submissions and approval policy,
reject an invalid state and add a currency requirement through model evolution.

[Build the expense application →](expense/01-model.md)
</article>
</div>

## Choose the level you need

| You want to… | Start here |
|---|---|
| Understand models, facts and constraints | [Core concepts](concepts.md) |
| See a useful failure in a few commands | [Check and repair a shipping request](quickstart.md) |
| Build with a coding agent | [Agent skills and explicit handoffs](guides/agent-skills.md) |
| Add checks to existing Python code | [Stable Python API](reference/python-api.md) |
| Find out whether a feature fits your problem | [Supported capabilities](reference/capabilities.md) |
| Improve GND itself | [Contributor guide](development/index.md) |

The core checker runs locally. The introductory applications use synthetic data
and need no model-provider API key after installation. Optional synthesis,
provider and native-tool workflows have their own prerequisites. A passing check
means the supplied facts satisfy the modeled rules; you still choose the right
rules and establish whether the facts describe the world accurately.
