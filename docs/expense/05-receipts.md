# 5. Check one claim across three documents

A travel claim rarely arrives as one clean record. A. Martin's trip to Paris
comes as three documents: the **travel approval**, the **hotel folio** and the
**corporate card statement**. Each one prints names its own way. The card says
`HTL LUMIERE PARIS` and the folio says `Hotel Lumière`. Both list a
`Café Central`, but the two are different cafés.

On this page you have GND read each document on its own, combine the three
into one claim, and check that claim against Finance's policy. A reviewer
decides which names mean the same vendor. GND never guesses. It refuses to
combine the documents until every name that could be joined has a decision.
All the data is synthetic.

*Source: a real run of the `gnd` commands behind each step. Every result
below comes from that run. The requests are suggestions, not recordings of
an agent conversation.*

!!! note "Where this ships"

    Identity decisions, fixed reference lists and separate reading and checking
    models are on `main` after 0.3.1. They are not in a published package yet.
    Install GND from a checkout of the repository to run this chapter.

!!! info "Files on GitHub"

    - [`receipts/`](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/expense/receipts): the whole example
    - [`vocabulary/expense-travel.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/expense/receipts/vocabulary/expense-travel.orm.json): the shared vocabulary both models build on
    - [`reading.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/expense/receipts/reading.orm.json) and [`checking.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/expense/receipts/checking.orm.json): the reading model and Finance's checking model
    - [`reference/approved-vendors.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/expense/receipts/reference/approved-vendors.json): the approved vendor list
    - [`claim/resolution.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/expense/receipts/claim/resolution.json): the reviewer's four decisions
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/expense/05-receipts.md)

## The result in one table

| Card line | Joined by printed name | Joined by the reviewer's decisions |
|---|---|---|
| C1 `HTL LUMIERE PARIS`, 612 EUR | **wrongly flagged:** no receipt, vendor not approved | accepted |
| C2 `SPA LUMIERE`, 95 EUR | **wrongly flagged:** no receipt. Also flagged, rightly, as not approved | flagged only because the spa is not an approved vendor |
| C3 `TAXI G7`, 42 EUR | flagged: no receipt | flagged: the reviewer could not match it to the folio's taxi, so it goes to a person |
| C4 `Café Central`, Vienna, 23 EUR, 9 March | **wrongly passed** the receipt and approved-vendor rules | flagged: no receipt, vendor not approved, after the trip ended |

Joining names exactly as printed gets it wrong both ways. It flags real hotel
charges and lets a café in another city borrow the hotel café's receipt. Once
the reviewer's decisions are applied, each flag on the right has a reason a
finance clerk would accept.

## Who does what

| Who | Does what |
|---|---|
| Finance | owns the policy and the approved vendor list |
| A reviewer | decides, for each pair of similar names, whether they are the same vendor, different vendors, or unknown |
| You | ask Claude Code, read the answers, decide |
| GND | reads each document, checks every decision against the documents, combines them, and checks the claim |

## The three documents

| Document | What it says |
|---|---|
| Travel approval | Trip T-114, Paris, approved from 2 to 6 March 2026 |
| Hotel folio | R1 Hotel Lumière, room. R2 Spa Lumière, massage. R3 Café Central, the lobby café. R4 a taxi booked by the concierge |
| Card statement | C1 HTL LUMIERE PARIS, 612 EUR. C2 SPA LUMIERE, 95 EUR. C3 TAXI G7, 42 EUR. C4 Café Central, Vienna, 23 EUR on 9 March |

## The policy

Finance's checking model adds four rules to the shared vocabulary:

| Rule | In plain English |
|---|---|
| Receipt | every card charge needs a receipt from the same vendor |
| Approved vendor | only vendors on the approved list can be claimed |
| Not before the trip | a claimed expense is on or after the trip's first day |
| Not after the trip | a claimed expense is on or before the trip's last day |

The **approved vendor list** is a fixed reference list owned by Finance:
Hotel Lumière, TAXI G7 and Café Central. It is not read from any document.
GND fingerprints it, so a check always says exactly which version of the list
it used.

## 1. Read each document with the reading model

**You type**

```text
Use /gnd:gnd-extract to read the travel approval, the hotel folio and the card
statement with receipts/reading.orm.json. One population per document.
For every vendor, record exactly where in the document you found it. Then
verify each one.
```

**Claude Code does** run the extraction skill once per document and asks GND
to verify each result.

**GND says** each reading is bound to its document. Every vendor name points
at the exact characters it came from. The reading model has no policy rules,
so nothing is judged yet.

| Document | Facts read | Vendor names located in the text |
|---|---:|---:|
| Travel approval | 2 | none on this document |
| Hotel folio | 4 | 4 of 4 |
| Card statement | 16 | 4 of 4 |

!!! info "Why two models?"

    The **reading model** describes what a document can say. The **checking
    model** adds what Finance requires of a whole claim. Both build on the same
    shared vocabulary and the same approved vendor list. A clerk reading a
    folio should not have to know the trip-date rule, and one folio can feed
    many claims.

## 2. Combine the documents by printed name

To see why decisions matter, first combine the three readings with no
decisions at all.

**You type**

```text
Combine the three readings into one claim, joining vendors only where the
names are printed identically. Check the claim against
receipts/checking.orm.json.
```

**GND says** the claim breaks three rules. Two of the verdicts are wrong:

| Rule | Lines GND flags |
|---|---|
| Receipt | `HTL LUMIERE PARIS`, `SPA LUMIERE`, `TAXI G7` |
| Approved vendor | `HTL LUMIERE PARIS`, `SPA LUMIERE` |
| Not after the trip | C4, on 9 March, after the trip ended on 6 March |

The hotel room is flagged because the card spells its name differently. The
Vienna café is *not* flagged for a receipt, because its name happens to match
the hotel's lobby café. Only the date rule catches it.

## 3. Record the reviewer's decisions

**You type**

```text
For each card vendor whose name resembles a folio vendor, record a decision
with its evidence: same vendor, different vendor, or unresolved. HTL LUMIERE
PARIS is Hotel Lumière. SPA LUMIERE is Spa Lumière. TAXI G7 might be the
concierge's taxi, but we cannot tell, so leave it unresolved. The card's Café
Central is in Vienna, so it is a different vendor from the lobby café.
```

**Claude Code does** write one decision per pair. Each decision cites the line
on the card and the line on the folio that it is about.

| Card name | Folio name | Decision | In the combined claim |
|---|---|---|---|
| HTL LUMIERE PARIS | Hotel Lumière | same | Hotel Lumière |
| SPA LUMIERE | Spa Lumière | same | Spa Lumière |
| TAXI G7 | Taxi | unresolved | each keeps its own placeholder, so neither can satisfy a rule by accident |
| Café Central | Café Central | different | Café Central, Vienna |

## 4. Combine and check again

**You type**

```text
Combine the three readings using those decisions, and check the claim.
```

**GND says** the claim still breaks three rules, and now every flag is right:

| Rule | Lines GND flags |
|---|---|
| Receipt | `Café Central, Vienna`, and the unresolved `TAXI G7` |
| Approved vendor | `Café Central, Vienna`, `Spa Lumière`, and the unresolved `TAXI G7` |
| Not after the trip | C4, on 9 March |
| Not before the trip | passes |

The hotel room passes every rule. The spa has a receipt but is not an approved
vendor. The taxi waits for a person, because nobody could say whose taxi it
was. The Vienna café fails three ways, and each failure is real.

GND also records which decision touched each combined fact, and which version
of the approved vendor list the check used. A finance auditor can trace the
hotel room back to line C1 on the card, the decision that matched it to the
folio, and line R1 on the folio.

## 5. Forget a decision, and GND stops

Suppose the reviewer had recorded only the first three decisions and skipped
the two Café Centrals.

**You type**

```text
Combine the readings with only the first three decisions.
```

**GND says** no, and names the pair it needs a decision for:

```text
ERROR: composition:invalid: keys at card expense_paid_to_vendor#3.vendor and
folio receipt_issued_by_vendor#2.vendor (object type vendor) are joined without
a same decision
```

That is card line C4 and folio line R3. Two names that look identical are not
joined just because they match. Someone has to say whether they are the same
vendor. GND writes nothing until they do.

## What you have now

| Before | Now |
|---|---|
| A claim was one population | a claim combines several documents, each read on its own and bound to its own text |
| Matching names was invisible | every match is a reviewed decision with evidence, and an unmatched look-alike is refused |
| Reference data was mixed into the facts | the approved vendor list is a fixed, fingerprinted input owned by Finance |
| One model did everything | a reading model for documents, a checking model for the claim, both on one shared vocabulary |

??? note "Under the hood: the gnd commands behind each step"

    Run these inside `src/gnd/examples/expense/receipts` of a checkout.
    `claim-flat/` holds the readings with no decisions, and `claim-missing/`
    holds the readings without the Café Central decision.

    ```sh
    gnd extract reading.orm.json --out artifacts
    gnd verify reading.orm.json extracted/card/population.json --artifacts artifacts
    gnd compose checking.orm.json claim-flat --out flat.population.json --record flat.composition.json
    gnd check checking.orm.json flat.population.json --composition flat.composition.json --sources claim-flat
    gnd compose checking.orm.json claim --out claim.population.json --record claim.composition.json
    gnd check checking.orm.json claim.population.json --composition claim.composition.json --sources claim
    gnd compose checking.orm.json claim-missing --out missing.population.json --record missing.composition.json
    ```

    `tools/build_expense_receipts_example.py` rebuilds every input, and
    `tests/test_expense_receipts_example.py` checks that the commands give the
    results on this page.

To see the same machinery on a harder domain, where two research papers name
the same method differently and identical names mean different methods, read
[Literature lineage](../literature/01-lineage.md).
