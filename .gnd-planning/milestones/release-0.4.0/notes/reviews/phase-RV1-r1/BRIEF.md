# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Where does the RV1 implementation fail to satisfy the approved and measured criteria?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Version, lock, manifests, prepared pages and retained publication pins agree.
- C2. Recorded example byte comparisons stay exact outside the named version and existing harness hash bindings.
- C3. The publication tests still exercise the expected stale-page controls and the notes cover both tag ranges.

## The change under review

The work from `67f2c0ae` to the working tree at `67f2c0aee200` with uncommitted changes. Its diff is `.gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV1-r1/diff.patch` | `9ededa2ee6266b8439a02eb444ce134015199932493c18633d6cf6733680ceab` |
| `.claude-plugin/marketplace.json` | `a6afa7ab1ca9c719f9bf01e0661769a1d33bf21f4d00bb73854b8e70659924b9` |
| `.claude-plugin/plugin.json` | `761aa27c3ec42d52a38de9327bd552650ceff0ae6fc053e5af30e707d7ca9873` |
| `.codex-plugin/plugin.json` | `d7139825790389ea946d9dd92c7c4cb4cf1da8efc33f2b08f98a1f7f047ce2d7` |
| `docs/compatibility.md` | `a95355246f43ffa81da3edbf8ad2018e4ab5942b54c247efc32939f2b802bd03` |
| `docs/marketplace-plugins.md` | `237b5b14487dbc0242fe465bb36d042a83c9315c15cc89597e4dbcd8fee75519` |
| `docs/release-notes.md` | `823fed9616b3cb6f6562a88bc28a1c09547430540b88f498fb39200b41616928` |
| `docs/support.md` | `04965c5b9a70c9c1dd84a22360c85f5cd0bfae8cd1be4a123f23de0ef32dec1d` |
| `pyproject.toml` | `9e89d2fd7f4eb1e1c9ca2691ab341c5a357d38a109465021e9c611bf5878113f` |
| `tests/test_expense_receipts_example.py` | `640e89f61e03f98429453fcee7449fb633e30182ea0dc9194e517dff594059c1` |
| `tests/test_li1_assurance_report.py` | `edcca4ed768dbdc55e07c7ce7ada03611ac71090ad477eecacecfa144c08f19d` |
| `tests/test_li1_literature_corpus.py` | `0ddb1df764042861caa8ff8a88a60a0692246654e2474361d054f15f8f098f71` |
| `tests/test_release_text.py` | `9f2a5bb6c667a62abdc0f08a244debf5dd9996d0c75948a8e167085185392d93` |
| `tests/test_release_version.py` | `ca526b11a1ea4a3e14ffa79f30f64a8f70114b2ab21302fb0e69168ff4996438` |
| `uv.lock` | `6587a325699ee5711ab287be1e4fc932463a0d957c102f5c0e25fa5e7f0910a1` |
| `.gnd-planning/milestones/release-0.4.0/notes/phase-RV1-spec.md` | `05ea75eb23cd937bea22ba861c4c03178e3cb52b1096cddf274f7a871bad3049` |
| `.gnd-planning/milestones/release-0.4.0/004-RV1-verification.md` | `a2ed98501a186a920907ec93a5be632fe2d5f390ac8b4d1a318d62e4ed56d9b3` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV1/notes-reconciliation.md` | `c2c58ddd08f76e2b9193280727eba7cd05ef132044027b5a8b8ad94679068fe5` |

You may read anything else in the repository that helps you answer.

## Rules

- Read only. Do not edit, create, stage, commit, push or post anything.
- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do
  not print environment variables. If you need one, name it and go on without it.
- A finding names its file and line and the consequence someone would observe. Run what
  you can to show it; where you only read, say so.

## What to return

1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable
   consequence, and how to reproduce it. A finding with no observable consequence is
   style: label it so.
2. What you checked and found true.
3. What you could not check, and why.
4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.
