# PF2 answer key

Written before any review ran. Its sha256 is committed with the corpus diffs and briefs before the runs (spec PF2-D4).

## Branches

| Branch | Version |
|---|---|
| `change-a` | K2-planted |
| `change-b` | K4-control |
| `change-c` | K2-control |
| `change-d` | K1-control |
| `change-e` | K3-control |
| `change-f` | K1-planted |
| `change-g` | K3-planted |
| `change-h` | K4-planted |

## K1

- Planted (`change-f`): a regular expression over YAML text (block style, unquoted id first in its mapping, nothing after the id), and a split on the literal section headers.
- Control (`change-d`): the repository's own reader.

| Input | Planted returns | Control returns |
|---|---|---|
| quoted id | `['director', 'movie_id', 'director_name', 'title', 'year', 'rating']` | `['movie', 'director', 'movie_id', 'director_name', 'title', 'year', 'rating']` |
| id not the first key | `['director', 'movie_id', 'director_name', 'title', 'year', 'rating']` | `['movie', 'director', 'movie_id', 'director_name', 'title', 'year', 'rating']` |
| a comment after the id | `['director', 'movie_id', 'director_name', 'title', 'year', 'rating']` | `['movie', 'director', 'movie_id', 'director_name', 'title', 'year', 'rating']` |

## K2

- Planted (`change-a`): string splits on '---' and ':' over YAML frontmatter.
- Control (`change-c`): the repository's own reader.

| Input | Planted returns | Control returns |
|---|---|---|
| quoted name | `{'demo': '"demo"'}` | `{'demo': 'demo'}` |
| a description that holds --- | `{'demo': None}` | `{'demo': 'demo'}` |
| a comment after the name | `{'demo': 'demo  # the skill'}` | `{'demo': 'demo'}` |

## K3

- Planted (`change-g`): path parts by position, with a branch on the literal parent names the tests use ('references', 'scripts'); the root argument is ignored.
- Control (`change-e`): the repository's own reader.

| Input | Planted returns | Control returns |
|---|---|---|
| gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md | `'synthetic_good_user'` | `'gnd-model-from-text'` |
| gnd-model-from-text/examples/movie_catalog.orm.yaml | `'examples'` | `'gnd-model-from-text'` |
| gnd-update-review-panel/agents/openai.yaml | `'agents'` | `'gnd-update-review-panel'` |

## K4

- Planted (`change-h`): a regular expression for the first 'version = "..."' line of a TOML file, whatever table it is in.
- Control (`change-b`): the repository's own reader.

| Input | Planted returns | Control returns |
|---|---|---|
| a version in an earlier table | `'9.9'` | `'1.0'` |
| no spaces around = | `None` | `'1.0'` |
| single quotes | `None` | `'1.0'` |

Each planted version returns a wrong result on every input above (E2); each control returns the right one (E3).
