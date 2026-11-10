Retained Claude Fable response; repository/home paths sanitized if present. This is authorship, not an independent review or a claim commands ran.

I've read the expense and bookrec demos, the two tutorial pages, the MC3 spec and the includes section; nothing was run or edited. Below are the choice, the page, and the handoff.

## 1. The demo: expense reports, grown to two teams

I chose the expense demo and extended its story: the company now has two teams, Engineering and Sales, filing on the same form under different policies.

- **Everyone has filed an expense.** "Sales may spend more on a client dinner than Engineering" needs no explanation, and neither does "no receipt, no reimbursement".
- **The stakes are familiar.** Teams copy the policy and change the numbers. Finance then changes what the form means, one copy misses it, and two reports that both say "approved" stop meaning the same thing.
- **The existing demo already splits cleanly.** The shipped `model.orm.json` has 20 rules: 14 say what an expense is, and 6 are limits (four category caps, two approval limits). The 14 become the shared model; the 6 become Engineering's policy, unchanged.
- **The existing fact files give the contrast for free.** The shipped 90 EUR meal and the 800 EUR team-lead approval are blocked today. Under a Sales policy with a 120 EUR meal cap and a 1000 EUR team-lead limit, the same facts should pass.
- **Bookrec is a worse fit.** It is one product with one rulebook, so a second policy over the same books would have to be invented.

One new relationship is needed: **Expense has Receipt**. Each team attaches its own receipt rule to it, and it is the definition Finance later changes. The handoff explains why, and gives a fallback that uses only shipped facts.

## 2. The page

Proposed home: `docs/tutorials/shared-expense-policies.md`. Every result is labelled expected until Codex records the run; Part 2 is labelled planned.

````markdown
# Two teams, one expense form

Engineering and Sales file expenses on the same form. An expense has a
submitter, an amount, a category and an approval, whichever team it comes from.
Their policies differ: Sales takes clients to dinner, so its meal cap is higher
and its team leads may approve more.

The usual fix is to copy the expense model and change the numbers. That works
until Finance changes what the form means. One copy gets the change, the other
does not, and two reports that both say "approved" stop meaning the same thing.

On this page you keep **one shared model** of what an expense is, and give each
team a **small policy of its own** on top of it. Each team checks its expenses
against the whole thing: the shared definitions plus its own rules. You type
requests; GND does the checking. All the data is synthetic.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="One shared expense model, two team policies">

![Finance owns one shared expense model: what an expense, a category, an approval and a receipt are. Engineering's policy and Sales's policy each build on that shared model and add only their own limits. The same three expenses go to both. A 90 EUR dinner is blocked for Engineering and accepted for Sales. A missing receipt is a warning for Engineering and a violation for Sales.](../assets/applications/expense-teams.svg)
</div>

!!! note "Status of the results on this page"

    Part 1 uses what GND does today. Its result tables are marked *expected*
    until the [commands page](../how-to/shared-expense-policies-commands.md)
    records a real run. Part 2 is planned work and is marked that way. No prompt
    on this page is a recording.

## The result in one table

| | Two copies of the model | One shared model, two policies |
|---|---|---|
| What an expense is | written twice, 14 rules in each copy | written once |
| A team's own rules | mixed in with the definitions | a short file of its own: 6 limits and a receipt rule |
| The same 90 EUR dinner | whatever each copy happens to say | blocked for Engineering, accepted for Sales, on purpose |
| Finance changes a definition | edit every copy by hand | each team sees which of its rules break before anything changes *(planned)* |

## Who does what

| Who | Does what |
|---|---|
| Finance | owns the shared model: what an expense is |
| Each team | owns its policy: its limits and its receipt rule |
| You | ask Claude Code, read the answers, decide |
| GND | reads the shared model and a team's policy as one model, and checks expenses against all of it |

A team's policy never copies a shared definition and cannot change one. It says
which edition of the shared model it builds on, the way a contract cites the
2026 edition of a handbook and not just "the handbook".

**Before you start.** Install GND as the [installation page](../installation.md)
shows and add the Claude Code plugin as the [plugin page](../marketplace-plugins.md)
shows. The [commands page](../how-to/shared-expense-policies-commands.md) has
the copy step and every command behind the requests below.

## The expenses

These are the three expenses from the [expense tutorial](../expense/01-model.md),
each now with a receipt number.

| Expense | Employee | Category | Amount | Approval | Receipt |
|---|---|---|---:|---|---|
| 101 | Ari | Meals | 60 EUR | pending | R-101 |
| 102 | Bea | Travel | 800 EUR | pending | R-102 |
| 103 | Ari | Equipment | 1,400 EUR | finance | R-103 |

## The two policies

| | Engineering | Sales |
|---|---:|---:|
| Meals, at most | 75 EUR | **120 EUR** |
| Training, at most | 1,500 EUR | 1,500 EUR |
| Travel, at most | 2,000 EUR | 2,000 EUR |
| Equipment, at most | 3,000 EUR | 3,000 EUR |
| A team lead approves up to | 100 EUR | **1,000 EUR** |
| Finance approves up to | 3,000 EUR | 3,000 EUR |
| Receipts | an expense **should** have one | an expense **must** have one |

Engineering's numbers are the expense tutorial's, unchanged. Sales's are new.

# Part 1: share the definitions, keep your own rules

## 1. See what is shared and what is yours

**You type**

```text
Read me Engineering's expense policy in plain English. Show which sentences
come from the shared expense model and which are Engineering's own.
```

**Claude Code does** ask GND to read the whole model back. GND follows the
policy to the shared model it builds on and reads both as one.

**GND says** *(expected)*

| Comes from | What it says |
|---|---|
| The shared model | An expense is submitted by one employee, has one amount and is in one category. Categories are meals, training, travel and equipment. An approval names a submitted expense and one chain, team-lead or finance. An expense has at most one receipt. |
| Engineering's policy | The four category caps and the two approval limits above. An expense should have a receipt. |

Engineering's file holds seven rules. The model GND checks holds all of them
plus everything shared.

## 2. Give Sales its own policy

**You type**

```text
Create a Sales expense policy that builds on the same shared expense model.
Meals up to 120 EUR. A team lead approves up to 1000 EUR. Everything else as
in Engineering. Every Sales expense must have a receipt. Do not copy or change
any shared definition. Validate it and read it back to me.
```

**Claude Code does** write a short policy file for Sales and ask GND to
validate it. The example ships the result, so you can skip the writing.

**GND says** *(expected)* the Sales policy is valid. Read back, its team-lead
rule is the sentence from the expense tutorial with one number changed: *if an
expense is approved by team-lead and has an amount, that amount is at most
1000*. The shared sentences are the same ones Engineering sees.

## 3. Same expenses, two verdicts

Two mistakes from the expense tutorial come back here: Ari's dinner claimed at
90 EUR, and Bea's 800 EUR trip approved by a team lead.

**You type**

```text
Check the 90 EUR dinner against Engineering's policy and against Sales's.
Then do the same for the trip approved by a team lead.
```

**GND says** *(expected)*

| The expense | Under Engineering's policy | Under Sales's policy |
|---|---|---|
| 101: a 90 EUR meal | **blocked**: meals are at most 75 EUR | accepted: meals are at most 120 EUR |
| 102: 800 EUR, approved by a team lead | **blocked**: a team lead approves at most 100 EUR | accepted: a team lead approves at most 1,000 EUR |

The Engineering column is what the expense tutorial reports today for the same
facts. Neither verdict is a mistake: each team gets the answer its own policy
gives, and both agree on what an expense, a meal and a team lead are.

## 4. One relationship, two rules about it

The shared model says an expense *may* have a receipt. It does not say whether
one is required. That is each team's call, and each team hangs its own rule on
the same shared relationship.

Bea loses the receipt for the trip.

**You type**

```text
Expense 102 has no receipt. Check it against both policies and tell me what
each team is asking for.
```

**GND says** *(expected)*

| | Engineering | Sales |
|---|---|---|
| The team's words | "An expense should have a receipt." | "No receipt, no reimbursement." |
| Kind of rule | **advisory** | **must** |
| What GND reports for expense 102 | a **warning**; the check still passes | a **violation**; the check fails |
| What the team wants done | attach the receipt if it turns up | add the receipt, then check again |

A warning tells you something is off and lets the work continue. A violation
stops it. The same missing receipt is one or the other because each team said
so in its own policy, not because the checker guessed.

## 5. The shared model cannot change under you

Each policy records the exact edition of the shared model it was written
against. Suppose someone edits the shared file in place, say to add a fifth
category, without publishing a new edition.

**You type**

```text
Someone edited the shared expense model directly. Check the seed expenses
against Sales's policy again.
```

**GND says** *(expected)* no. The shared file no longer matches the edition
Sales's policy names, so GND refuses to load the model and checks nothing. A
definition both teams rely on can only change as a new edition, in the open.

# Part 2: Finance changes a shared definition

!!! warning "Planned, not yet available"

    This half describes work in progress. Nothing below has been run; it is the
    demonstration this page will show once the feature is released.

Finance starts accepting e-invoices as well as paper receipts. It publishes a
second edition of the shared model: "Expense has Receipt" is replaced by
"Expense is supported by Document". The first edition stays where it is.

## 6. Ask what the update would break

**You will type**

```text
Finance published edition 2 of the shared expense model. Preview moving
Sales's policy to it. Do not change anything yet.
```

**GND will say** the move, on its own, does not work, and name why: Sales's
rule *every expense must have a receipt* hangs on a relationship edition 2 no
longer has. The six limits are not named, because nothing they use changed.
Nothing is published; Sales's policy is exactly as it was.

| Sales's rule | In edition 2 |
|---|---|
| The four category caps | unaffected |
| The two approval limits | unaffected |
| Every expense must have a receipt | **broken**: "Expense has Receipt" is gone |

## 7. Repair it in one reviewed change

**You will type**

```text
Move Sales's policy to edition 2 and, in the same change, restate the receipt
rule as: every expense must be supported by a document. Preview it, show me
what it affects, and wait for my go-ahead.
```

**GND will say** the combined change is valid, and will mark it as one that
needs your explicit acceptance. After you accept, only Sales's policy file
changes. The shared model is never written by a team's change.

**You will get** a Sales policy on edition 2. An expense with a document passes;
an expense without one is blocked, as the missing receipt was in step 4.

## 8. What stays put

- **Engineering has not moved.** Its policy still names edition 1 and checks
  as before. It makes the same move when it is ready, with its own preview.
- **A team cannot edit a shared definition.** If Sales asks to add a category
  to the shared list from inside its own policy, GND refuses and says the
  definition belongs to the shared model. That request goes to Finance.

## What you did

| Step | What happened | Who checked it |
|---|---|---|
| 1 | read one policy back, shared and own sentences together | GND |
| 2 | Sales got a policy without copying a definition | GND validated it |
| 3 | one dinner and one trip, two correct verdicts | GND, once per policy |
| 4 | one missing receipt: a warning for one team, a violation for the other | GND |
| 5 | an in-place edit to the shared model was refused | GND |
| 6–8 *(planned)* | a new edition named the one rule it breaks; one change repaired it | GND, before anything was published |

## What this does not establish

- **That either policy is wise.** GND checks expenses against the rules each
  team wrote. It does not judge the rules.
- **That the shared model is right.** Naming an edition proves which
  definitions you built on, not that Finance got them right.
- **Anything about a generated application.** The expense tutorial's generated
  project does not yet accept a policy built on a shared model. This page
  checks facts directly.
- **Anything in Part 2.** It is a plan until its results are recorded.

The exact rules for building one model on another are in the
[model includes reference](../reference/model-includes.md).
````

**Diagram specification (`expense-teams.svg`)**

- **Top:** one wide box, "Shared expense model · owned by Finance", listing Expense, Employee, Amount, Category, Chain, Receipt.
- **Middle:** two boxes side by side, "Engineering's policy" (meals 75, team lead 100, receipt: should) and "Sales's policy" (meals 120, team lead 1000, receipt: must). Each has an arrow up to the shared box labelled "builds on edition 1".
- **Bottom:** one strip of three expense cards (101, 102, 103) feeding both policies. Two verdict chips sit under each policy: "90 EUR dinner", red for Engineering and green for Sales; "no receipt on 102", amber "warning" for Engineering and red "violation" for Sales.
- **Second figure for Part 2, optional (`expense-teams-update.svg`):** editions 1 and 2 side by side with the Receipt line struck through and replaced by Document. Sales's arrow moves from 1 to 2, with one rule highlighted "broken, then restated". Engineering's arrow stays on edition 1.
- **Style:** same colours and narrow-screen scroll note as `expense-limits.svg`. No hashes, file names or exit codes in the art.

## 3. Implementer handoff

**Reuse exactly, from `src/gnd/examples/expense/`**

- **Definitions:** from `model.orm.json`, all six object types, all five fact types with their eight inline uniqueness and mandatory rules, and `known_categories`, `known_chains`, `positive_amount`, `approval_needs_submission`, `approval_needs_chain`, `chain_needs_approval`. These 14 rules move to the shared model with their provenance unchanged.
- **Limits:** `policy_meals`, `policy_training`, `policy_travel`, `policy_equipment`, `approval_limit_team_lead`, `approval_limit_finance`. These 6 become Engineering's own rules, unchanged.
- **Facts:** `seed.population.json`, `invalid-meal.population.json` (101 = 90 EUR) and `invalid-chain.population.json` (102 approved by team-lead).
- **Documented single-file verdicts:** `policy_meals {"$e": 101, "$a": 90}` and `approval_limit_team_lead {"$a": 800, "$e": 102}`.

**Smallest split (proposed: `src/gnd/examples/expense/teams/`)**

| File | Contents |
|---|---|
| `shared/expense-v1.orm.json` | Version 1, standalone-valid. The 14 rules above, plus the new `Receipt` value type and `expense_has_receipt` ("{Expense} has {Receipt}") with one uniqueness rule on `expense`. No mandatory rule on it. |
| `engineering.orm.json` | Version 5. One include (`id: expense`, `path: shared/expense-v1.orm.json`, real digest). Own top-level `constraints`: the six limits verbatim. One `fact_type_constraints` entry on `expense_has_receipt`: `receipt_expected`, mandatory on `expense`, `modality: deontic`. |
| `sales.orm.json` | Same include. The six limits with `policy_meals` at 120 and `approval_limit_team_lead` at 1000. Attached `receipt_required`, mandatory on `expense`, `modality: alethic`. |

- **Layout:** include paths may not contain `..`, so both policies sit directly above `shared/`. Say on the commands page that real projects each carry their own pinned copy.
- **Rule metadata:** new rules use `source: user-supplied`, `status: confirmed`, with the team's sentence from step 4 as `provenance.user_quote`.
- **The team's remedy:** use the existing repair annotation `allowed_fixes: [add-fact]`. The format says it does not change evaluation. Check how it surfaces in reports before the page claims GND prints it; if it doesn't, the step 4 row "What the team wants done" stays policy text.

**Why a new fact type**

The five shipped relationships carry only definitional inline rules, so nothing team-specific can be attached to them. `expense_has_receipt` gives each team one inline rule to attach, and gives Finance a definition to change in Part 2. It does not exist today.

Fallback with no new fact type: use `expense_has_currency` from `currency.orm.json`, attaching the shipped `required_expense_has_currency` as the team rule. `currency-missing.population.json` and `currency.population.json` then supply the facts, with the documented findings `[101]` and `[102]`. It is a weaker human story.

**Facts and expected findings (all pending a real run)**

| Facts (proposed file) | Engineering | Sales |
|---|---|---|
| Seed plus receipts R-101, R-102, R-103 | pass | pass |
| 101 = 90 EUR, plus receipts | fail `policy_meals`, 101/90 | pass |
| 102 by team-lead, plus receipts | fail `approval_limit_team_lead`, 102/800 | pass |
| Seed, receipts for 101 and 103 only | warning `receipt_expected` on 102, exit 0 | fail `receipt_required` on 102 |
| Seed after an in-place edit of the shared file | not run here | refused, `include:hash-mismatch` |

- Every population must list `expense_has_receipt` in `covers`; otherwise the receipt rule is vacuous, not failed.
- Population headers name one model. If that binding is enforced, ship per-team copies and have the commands page assert their `facts` sections are equal.
- Prediction to measure, not to print unverified: a clean check evaluates 22 rules (15 shared plus 7 own).

**Part 2 scenario (MC3; do not present as observed)**

1. Add `shared/expense-v2.orm.json`: remove `Receipt` and `expense_has_receipt`; add `Document` and `expense_supported_by_document` with the same uniqueness rule. Leave v1 untouched.
2. Re-pin only: expect analysis-only, exit 3. It should name `receipt_required`, not name the six limits, and stage nothing.
3. Combined proposal on `sales.orm.json`: `repin-include` for `expense`, DELETE `receipt_required` on the old host, ADD it on `expense_supported_by_document`. Expect preview 0 with breaking true, exact radius acceptance required, apply and finalize 0, only `sales.orm.json` replaced.
4. Check a v2-shaped population: pass with all documents; fail when 102 has none.
5. Controls: `engineering.orm.json` still validates and checks on v1 with v2 present. A Sales proposal that adds a category to `known_categories` is refused with `evolve:included-element`, exit 3.

The MC3 corpus exercises this shape with a ring rule. A mandatory rule moving hosts is the same operation pair but must be measured, not assumed.

**Commands page (`docs/how-to/shared-expense-policies-commands.md`)**

- **Part 1, run and record with `gnd-run` markers:** the copy step; `gnd validate` on the shared model and both policies; `gnd check` for each row of the facts table; the whole-model read-back for both policies; the tamper check on a scratch copy.
- **Part 2, add only after MC3 lands:** `gnd evolve preview` and `gnd evolve apply` with the existing `--workspace`, `--records`, `--preview` and `--out` flags, using the existing breaking-acceptance mechanism.
- **After Part 1 is verified:** replace the status note and each *(expected)* tag with the learn-rules sentence: "Every number on this page comes from a real run of the commands behind it."

**Verify first; stop and report if any fails**

- A version-5 policy may carry its own top-level guarded `constraints` over included fact types. The format's example shows only the attachment.
- A deontic mandatory rule reports `warning` with exit 0.
- The read-back resolves includes, and whether it can show which file each sentence comes from. If it cannot, step 1's "comes from" column is the author's grouping and the prompt must be reworded.
- `docs/reference/model-includes.md` is a placeholder link. Point it at the existing public page that cites the format's "Model includes (version 5)" section; do not restate the rules.
- Do not run `gnd codegen`, conformance or a linked project on these models, and check that `gnd export pyrel` accepts them before showing any PyRel line. The spec keeps codegen and conformance refused for include-bearing models.

**Wording rules for the page**

Use "shared model", "policy", "edition", "builds on", "advisory", "must", "warning", "violation". Keep "scanner", "vocabulary", "include", "pin", "digest", "composition" and file suffixes out of the narrative; they belong on the commands page.
