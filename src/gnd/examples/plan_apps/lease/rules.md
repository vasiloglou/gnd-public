# Lease rules

- No payment is due before the lease starts.
- No payment is due after the lease ends.
- Each payment is the monthly rent.
- A lease has one payment due on a given day.
- A payment should be due at least a week before the lease ends (a guideline:
  the checker warns, it doesn't refuse).

## What the property manager does

- Schedule a payment: an amount due on a day.
- Cancel a payment due on a day.

## The lease

Apartment 4B, from 1 February to 31 July 2025, at 1,450 a month.

The lease itself is a document. Extracting its terms and checking that every
extracted fact points at the sentence it came from is GND's `gnd extract` and
`gnd verify`, which run on GND only. The schedule rules below run on GND and
on PyRel.
