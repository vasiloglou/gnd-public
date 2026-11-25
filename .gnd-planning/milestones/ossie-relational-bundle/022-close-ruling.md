# Close ruling and follow-ups

**Owner ruling, 2026-11-25.** `auto=false`.

After PR 274 merged, the owner was told what was still open and asked "Do
you rule the ossie-relational-bundle milestone closed, or not yet?" The
owner answered:

> close all the open things

## Reading of the answer

The question asked for the close ruling, and the list before it named the
other open items. The answer is recorded as:

1. **The milestone is ruled closed**, over the
   [close record](021-milestone-close.md) as merged at `e8359685`, with its
   stated residuals.
2. **An instruction to finish the carried items** that can be finished
   inside this repository.

It is **not** recorded as confirmation of any text that leaves the
repository. The plan (D10) requires the owner to confirm each such text, and
"close all" names none.

## What was done on it

| Open item | Outcome |
|---|---|
| The close ruling | Recorded here. |
| OB1-Q1: `guard_yaml` captured its default byte cap at import | **Closed.** The default is read at call time, as `loads` reads it. `test_guard_yaml_reads_its_default_cap_at_call_time`. |
| OB2-Q1: two definitions of "confirmed alethic" | **Closed.** `gnd.rmap.is_confirmed_alethic` is the one definition; the ontology export uses it at both of its sites. The census baselines keep their bytes. |
| OB4-Q4: four private RFC 6901 pointer helpers | **Closed for the three Ossie modules**: `gnd.artifacts.json_pointer`, used by the export, the import and the binding. The helpers in `recovery/inventory.py` and `transition.py` belong to other components and build their pointers in a different shape; they are left alone. |
| OB2-Q2: `refscheme.reference_identity` ignores `preferred` and confirmation | **Not changed.** It would change results for callers outside this milestone. An issue text is drafted in [D10-drafts.md](notes/D10-drafts.md). |
| OB3-Q5: identifiers the ontology export does not declare | **Not changed.** It changes the ontology's bytes for existing models and needs its own spec. An issue text is drafted in the same file. |
| The Codex review comment on PR 274 | **Not posted.** The round is kept in `notes/reviews/pr-274-r1`. The PR is merged and its one finding is fixed. |
| D10: the three issues and the reporter message | **Not sent.** Drafted; each needs the owner's confirmation of its text. Only the owner can reach the reporter. |
| External acceptance | **Open.** It needs the reporter's run. |

## Review state

The three maintenance changes are covered by the focused suites and the
guard block. No reviewer has read them.

## Gates

| Gate | Result |
|---|---|
| `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py tests/test_rmap.py tests/test_ossie_relational.py tests/test_physical_binding.py tests/test_ossie_docs.py tests/test_ossie_formulas.py tests/test_rf1_cli_pins.py tests/test_rf7_input_policy.py "tests/test_documentation_tutorials.py::test_documented_learning_path[ossie]" --tb=line` | `986 passed in 161.86s`, exit 0. The byte baselines of the ontology export and of the relational files are in this lane and did not move. |
| the project guard block (16 files) | first run: 863 passed, 3 failed. Two were the dynamic-query census, which counts annotations: the two shared helpers moved two rows. A chained successor delta (`evidence/close-followups/dynamic-query-successor.json`) records them; `tests/test_rf6_query_policy.py` and the structure tests then pass (73 passed). The third is the known red, `test_reference_closure_and_declared_bootstrap`. |
| `uv run ruff check` | exit 0 |
| `python3 scripts/components_index.py changed --base origin/main --strict` | 0 to fix, 0 to reread |

The oracle lane was not run on these bytes. The changes do not alter a
written byte: the corpora and baselines are unchanged.
