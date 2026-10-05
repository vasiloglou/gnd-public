# Model a domain by dialogue

The `gnd-model-from-text` skill turns a conversation into an executable ontology. It
follows Halpin's **Conceptual Schema Design Procedure (CSDP)**. Your agent asks for
concrete examples, verbalizes each elementary fact back to you, and then asks about
constraints one at a time, using your sample data. You answer in plain language; the
agent writes `model.orm.yaml` and a readable verbalization, then runs `gnd validate`.

Every constraint it writes records **why** it exists (`provenance`: the step, the turn,
your words) and **how hard** it is (`modality`: alethic or deontic). Its source is one
of *explicit*, *sample*, *common-sense*, *llm-inferred* or *user-supplied*, so you can
tell what you said from what the model guessed.

## Ask for a model

```text
Use gnd-model-from-text in Guided mode to model our movie catalog. Ask me for example
movies first, confirm each fact with me, then ask about uniqueness and mandatory roles.
Write model.orm.yaml and model.verbalization.txt and validate the model.
```

Modes: **Guided** walks every CSDP step in conversation, one confirmation at a time.
**MVP-fast** runs the same steps in batches, covers only the slice you are building now,
and ends with one compact review; it is the default for prototypes. **One-shot** drafts
the whole model from a rich description for you to review.

## What the dialogue looks like

The skill ships a complete illustrative dialogue for a small movie catalog
(`gnd-model-from-text/examples/movie_catalog.dialogue.md`). An excerpt from step 1,
elementary facts:

> **Agent:** Let me decompose into elementary facts and verbalize each. Please confirm,
> correct, or reject: *"Movie #1 has title 'The Departed'." Is this an atomic fact?*
>
> **User:** All four are atomic. We treat title, director, release year, and rating as
> independent facts per movie.

From step 4, uniqueness:

> **Agent:** *Movie directed-by Director: each Movie has one Director in your sample.
> Always true, or are co-directors allowed?*
>
> **User:** We pick one director for co-directed films. So yes, one Director per Movie.

Each answer becomes a constraint that carries your words:

```yaml
- id: movie_directed_by_director
  reading: "{Movie} directed by {Director}"
  constraints:
    - type: uniqueness
      roles: [movie]
      source: explicit
      status: confirmed
      modality: alethic
      provenance:
        csdp_step: 4
        dialogue_turn: 20
        user_quote: "We pick one director for co-directed films. So yes, one Director per Movie."
```

## Check the model the agent wrote

The finished model ships with the skill, so you can check it directly:

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from shutil import copyfile
copyfile(str(files("gnd") / "skills" / "gnd-model-from-text" / "examples" / "movie_catalog.orm.yaml"),
         "model.orm.yaml")
```

<!-- gnd-run expect=0 -->
```sh
gnd validate model.orm.yaml
```

Every constraint carries its modality and provenance; the skill does not leave either
implicit:

<!-- gnd-run expect=0 -->
```python
from ruamel.yaml import YAML

model = YAML(typ="safe").load(open("model.orm.yaml"))
constraints = [c for ft in model["fact_types"] for c in ft.get("constraints", [])]
constraints += model.get("constraints", [])
for c in constraints:
    assert c["modality"] in {"alethic", "deontic"} and c["source"] and c.get("provenance") is not None
print(len(constraints), "constraints, each with a modality, a source and provenance")
```

## Now the model checks the agent

Once you accept the model, it judges every later output. Write the sample catalog from
the dialogue, plus a draft an agent might produce, with a second title for *Parasite*
and a rating that does not exist:

<!-- gnd-run expect=0 -->
```python
import copy, json

facts = {
    "movie_has_title": [{"movie": 1, "title": "The Departed"}, {"movie": 2, "title": "Inception"},
                        {"movie": 3, "title": "Parasite"}],
    "movie_directed_by_director": [{"movie": 1, "director": "Martin Scorsese"},
                                   {"movie": 2, "director": "Christopher Nolan"},
                                   {"movie": 3, "director": "Bong Joon-ho"}],
    "movie_released_in_year": [{"movie": 1, "year": 2006}, {"movie": 2, "year": 2010},
                               {"movie": 3, "year": 2019}],
    "movie_has_rating": [{"movie": 1, "rating": "R"}, {"movie": 2, "rating": "PG-13"},
                         {"movie": 3, "rating": "R"}],
}
header = {"model": "model.orm.yaml", "source": "synthetic", "covers": list(facts)}
json.dump({"population": header, "facts": facts}, open("catalog.population.json", "w"), indent=1)

draft = copy.deepcopy(facts)
draft["movie_has_title"].append({"movie": 3, "title": "Gisaengchung"})
draft["movie_has_rating"][1] = {"movie": 2, "rating": "PG-14"}
json.dump({"population": header, "facts": draft}, open("agent-draft.population.json", "w"), indent=1)
```

<!-- gnd-run expect=0 -->
```sh
gnd check model.orm.yaml catalog.population.json
```

<!-- gnd-run expect=1 -->
```sh
gnd check model.orm.yaml agent-draft.population.json
```

The draft fails with two findings, each traceable to a sentence the user said:

```text
BLOCKING (alethic)
  [fail] fact_types[movie_has_title].constraints[0]: Each movie plays 'movie_has_title' with at most
         one combination of the other roles — violated: movie '3' has 2 facts.
  [fail] constraints[0]: Each rating value must be one of ['G', 'PG', 'PG-13', 'R', 'NC-17'] —
         violated: 'PG-14'.
```

GND can also read any population back as sentences, which is useful for a reviewer or
as context for the next agent turn:

<!-- gnd-run expect=0 -->
```sh
gnd verbalize population model.orm.yaml catalog.population.json
```

## Starting from something else

- **An existing codebase:** `gnd-model-from-code` runs a bounded static recovery pass
  and records evidence for every claimed element
  ([evolution and recovery](../guides/evolution-and-recovery.md#recover-a-model-from-an-existing-repository)).
- **A GSD project:** `gnd-adopt` maps every requirement into the recovered model
  ([adopt a GSD project](../guides/evolution-and-recovery.md#adopt-a-gsd-project)).
- **An existing ORM model in the RelationalAI ORM-skill dialect:**
  `gnd import rai-orm MODEL --out DIR` converts it once and writes an alias map.

The format itself is documented in the `gnd-orm-core` reference library, and
[ORM: the executable ontology](../concepts.md) explains the notation.
