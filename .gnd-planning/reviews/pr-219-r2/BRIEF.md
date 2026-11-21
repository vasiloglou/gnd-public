# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Is each change in this pull request correct and complete for what it sets out to do, and is anything in it wrong, unsupported by the code it cites, or missing?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every code location, line number and quoted message cited in the four new planning files and the PROJECT.md roadmap section matches the code at 0f39c392.
- C2. Together the planned phases cover every request in issues #214, #215, #216, #217 and #218, and the partition of #214 between include-root-routes and pyrel-rules-coverage leaves no item unowned or owned twice.
- C3. Issue #179 was already delivered before this change, so closing it as completed is supported by the repository's records and code.
- C4. The synced skill files are byte-identical to dev-tools c9648dd for the paths .devtools.toml names, the .claude and .codex twins are identical, and .devtools-receipt.json describes them.
- C5. The test_doctor_uninstall.py change pins exactly the new tracked files and nothing that weakens its guard.
- C6. The order and dependencies stated between the milestones are consistent across PROJECT.md, the three READMEs and the three plan outlines.

## The change under review

Pull request #219, https://github.com/vasiloglou/gnd-public/pull/219, at head `73e0d16ff5c978cbba69af391dcd921f57d6b9f8` (base `0f39c3929285876829e24a9aece33b3d3dd410da`). Its diff is `.gnd-planning/reviews/pr-219-r2/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/reviews/pr-219-r2/diff.patch` | `8d802724e3e6a8e52d9fa1c96e56dfbb1e0015b3554f62b82c18ee052d949bec` |

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
