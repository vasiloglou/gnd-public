# Growth round outcomes · plan r1 (outline)

**Status: outline draft, 2026-11-22. Not reviewed and not approved.** This
plan covers [#227](https://github.com/vasiloglou/gnd-public/issues/227) and
[#228](https://github.com/vasiloglou/gnd-public/issues/228). Phases are
outlines; none has a spec yet. `start-milestone` turns this outline into the
full plan and the GO1 draft spec, and the plan review runs then. Code
references were read at `17ab99d2` on 2026-11-22.

## Goal and completion predicates

A host that grows one model over many documents with no reviewer gets more out
of each round, and each round costs less.

- **GO1.** One `gnd evolve preview` or `apply` parses each distinct model text
  once. Today `apply` calls `model._parsing.parse_model_document` 22 times and
  `preview` 6 times (#228, profile at 604 object types), and the round's time
  is those parses.
- **GO2.** `gnd evolve preview` names an outcome for every operation of the
  proposal. Today the additive policy already does this (`policy_issues`, one
  row per refused operation, exit 3, `evolve/cli_service.py:367`), but a
  refusal outside the policy raises one `EvolutionError` for the whole proposal
  (`evolve/service.py:295`, `:346`, and rule D-12 at `:430-477`), tied to no
  operation.
- **GO3.** A host can keep the admitted operations of a proposal and drop the
  others without writing the candidate model by hand. The result is a new
  proposal with its own preview; `apply` still applies a reviewed preview
  whole.
- **GO4.** `unattended-growth.md` states what a reply carries for a fact type
  the model already has. Today "The reply shape" says "ids that already exist
  are reused" (`:286`) and nothing about whether the reply repeats the element
  or its rows.
- **GO5.** A round ends with a summary a host can log and compare across
  rounds and growers: operations proposed, operations mapped onto existing
  elements, operations dropped and why, elements added.

## 0. Binding design rules

- **`apply` stays whole.** A preview is applied exactly as reviewed. No phase
  adds partial application to `apply`.
- **No check is relaxed.** New constraints stay `proposed` and `deontic`; #227
  says that suits the reporter. Revalidation in `apply` stays (#228 "Not
  requested").
- **Records keep their bytes.** A proposal and preview that are admitted today
  produce the same records after GO1. GO2 and GO5 add fields; the preview
  schema version moves if a field is added (D2).
- **Previews stay value-free.** A per-operation outcome names ids, key names
  and a verdict word, as `PolicyIssue.detail` does today
  (`evolve/models.py:890`).

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #228 "Measured" | A round that adds one fact type and one constraint: 6.6 s at 304 object types, 11.3 s at 604, 21.0 s at 1,204, 42.6 s at 2,404; `apply` is two thirds of it. Measured at `4ad0d216` | GO1 |
| #228 "Where" | `evolve/service.py:241` `_load_model_document` runs 7 times in one `apply` and parses the text in `guard_bytes` (`model/_includes.py:300`), in `load_model_bytes` (`model/__init__.py:287`), in `parse_model_document` and in `guard_yaml` (`input_policy.py:113`); `apply` (`:2110`) runs `preview` (`:1520`) and `finalize` (`:2377`) again, and each loads both models from bytes | GO1 |
| #227 cause 1 | One fact type with neither a constraint nor an open question sinks the round. The rule that rejects it is the reporter's host rule, not a GND refusal. GND's part: the proposal is one candidate model plus its operations, so dropping one operation means rebuilding both | GO2, GO3 |
| #227 cause 2 | Replies restate reused fact types with their rows: 12,000 to 16,000 output tokens a round against 4,700 for a reply that does not | GO4 |
| #227 request 3 | A diagnostic per round: proposed, mapped onto existing, dropped, added | GO5 |
| `unattended-growth.md:61-73` | The shape report already lists, for each added fact type, the existing fact types over the same role players; the host decides and logs | GO5 reuses it |
| `discover/output.py:90`, `:102` | `candidate_document` replays operations over a model and `candidate_text` writes the candidate; the growth tests build proposals with them | GO3 reuses them |

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #228: parse each model text once per invocation | GO1 |
| #228: a bound a test can hold on the number of parses | GO1 |
| #227: a per-element outcome from `evolve preview` | GO2 |
| #227: or a documented way to apply part of a proposal | GO3 |
| #227: reply guidance for reused fact types | GO4 |
| #227: a growth diagnostic per round | GO5 |

Not in this milestone: a round that validates only what changed (#228 names
it as a larger request), and the Sonnet empty-reply cause, which the reporter
has not confirmed.

## 2–3. Contract sketch and dependencies

- **GO1** is internal to `evolve/service.py` and the model loader's call
  sites. It changes no record, flag or exit code. It needs no ruling.
- **GO2** adds per-operation outcomes to the preview. It needs D1 and D2.
- **GO3** needs GO2, because the host picks what to keep from the outcomes.
- **GO4** is a document change with a guard test, in the shape of
  `tests/test_unattended_growth_guidance.py`. It needs D3 and is independent
  of GO1 to GO3.
- **GO5** needs GO2 and D4.
- **One writer at a time on `evolve/service.py` and on
  `unattended-growth.md`.** The reviewed-vocabulary-growth plan being written
  in another session changes both: its VG2 edits rule D-12 in
  `evolve/service.py` and the growth document, and its VG4 runs rounds on an
  include root. GO1 runs before VG2 starts or after it merges; GO4 runs after
  VG2's document change or carries it.
- Start condition: none for GO1.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| GO1 | The number of `parse_model_document` calls in one `apply` and in one `preview` is a small constant, the same at 100 and at 1,000 object types (the #228 bound). Every evolve fixture produces byte-identical records. A model text changed between two loads in one invocation is still refused, as today. The measured round at 2,404 object types is recorded before and after |
| GO2 | A proposal with one operation the candidate validation refuses and three it admits: the preview names all four, each with its outcome, and exits 3. A proposal admitted today has every operation marked admitted and its other fields unchanged |
| GO3 | From that preview the host produces a proposal of the three admitted operations with one call; it previews and applies with exit 0. An operation that depends on a dropped one (a constraint on a dropped fact type) is dropped with it and named |
| GO4 | The reply shape states the rule for a reused fact type and shows it in the example. A guard test fails when the rule is removed. The packaged growth example's replies follow it |
| GO5 | Three rounds of the unattended acceptance replay each produce a summary whose four counts add up to the operations proposed. A round that proposes nothing and a round whose proposals all map onto existing elements give different summaries |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | GO2: how far "an outcome for every operation" goes. (a) Policy issues plus the candidate-validation and D-12 refusals, each tied to its operation where the refusal names an element. (b) Policy issues only, as today, with the first other refusal named | (a). A refusal that names no element stays a whole-proposal refusal and says so |
| D2 | GO2: where the outcomes live. (a) A new `operation_outcomes` list in the preview, under a new preview schema version. (b) Reuse `policy_issues` with new cells | (a). `policy_issues` keeps its meaning and its consumers |
| D3 | GO4: what a reply carries for a reused fact type. (a) Its id only; rows for it go in `rows` against the existing id when the document has new ones. (b) The full element, as replies do today | (a). It is the two-thirds cut #227 measured |
| D4 | GO5: who computes the summary. (a) GND, from the proposal and the preview: operations by kind and collection, shape matches, refused operations. The host adds what it dropped before the proposal. (b) A log format in the document that the host fills alone | (a), with the host's own drops as an input file |
| D5 | GO3: the surface. (a) A library function beside `candidate_document`. (b) A `gnd evolve` subcommand that writes the narrowed proposal | (a) until a host asks for the command |
| D6 | Whether GO1 ships alone as a maintenance pass before the rest | Yes if the rulings for GO2 to GO5 take longer than GO1 |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** `unattended-growth.md`, the evolution contract's preview
  section, the growth example and its page.
- **Risks.**
  - A parse cache could hide a file changed between two reads. Control: the
    cache is keyed by the sha256 of the bytes already admitted through the
    trusted descriptor, and lives for one invocation.
  - Per-operation outcomes could leak a value into the preview. Control: the
    value-free rule of §0, with the disclosure tests in the gate.
  - A narrowed proposal could be mistaken for the reviewed one. Control: it
    has its own `proposal_id` and names the proposal it came from.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- **Verification.** Each spec names its focused lane from
  `test_evolve_additive_policy.py`, `test_evolve_source_document.py`,
  `test_unattended_model_growth_acceptance.py` and
  `test_unattended_growth_guidance.py`, plus the structure and inventory
  guards.
