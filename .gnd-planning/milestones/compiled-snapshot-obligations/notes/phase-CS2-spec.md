# CS2 — Trace and public contract

Delegated approval (auto=true), 2026-10-13, before implementation.

## Obligations and scope

Read the full plan and CS0/CS1. CS2-C1 requires trace eligibility versus runtime
activation and retained transition-only reasons. CS2-C2 requires a bounded
normalized single/batch agreement matrix with its actual denominator. CS2-C3
requires explicit walk-only counterexamples/boundaries. CS2-C4 requires a public
recipe and exact candidate identity; no external app gate is claimed run.
CS-R1–R6 and the six named standing rules in CS0 remain binding.

## Design and tests

Update output._print_trace to say ordinary snapshots exclude operations and
--compiled-operations opts into eligible standing subsets. Keep digest output
and retained-reason text. Canonical semantics live in the packaged ORM reference;
schema descriptions and public API/transition docs point to that boundary.
Snapshot-ignores-operations sentences gain explicit default-mode qualification.
The compiler's provenance caveat states why opt-in is a caller assertion.

Run issue public API/single/batch cases, trace controls and schema synchronization
with default exclusions. Pin a transition-only obligation that is still checked
per step and absent from activated snapshots. State that intermediate states,
dynamic step rules and frames cannot be inferred from these snapshots. The
finite local agreement claim covers the compiled verdict inventory in the two
fixture populations only; it does not assert the app's M3 gate or all walks.

## Approval, size and boundary

This is delegated agent approval before writes, not human reading of these bytes.
Estimate under 80 documentation/source lines plus trace assertions. No packaged
skill discovery link or real development twin is edited manually. No release,
certificate, external app edit or full replay. Record actual results and open
questions, including separately supported occurrence admission, at close.
