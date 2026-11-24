<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
F1 (P2) — [tools/skill_names.py:11](<repo>/tools/skill_names.py:11): A valid multiline description can hide the declared name.

Reproduce with this `demo/SKILL.md`:

```yaml
---
description: |
  ---
  A demo skill.
name: demo
---
```

`skill_name()` returns `None`; `skill_names()` returns `{"demo": None}`. Expected: `"demo"` and `{"demo": "demo"}`.

The reused reader’s existing fence matcher (`src/gnd/exp/frontmatter.py:102`) strips indentation and mistakes description content for the closing fence. Confirmed by running the real parser with mocked filesystem reads: YAML correctly parses `name: demo`, while `read_frontmatter()` truncates the mapping. Fix the shared fence handling and add a regression test.

What I checked and found true:

- All three SHA-256 hashes match the brief.
- The packaged-skill test passes: all 18 names match their directories.
- Ruff and `git diff --check` pass.
- Quoted names, comments, flow mappings, folded strings, multiline quoting, missing names, and non-string names behave as expected.
- The `*/SKILL.md` glob discovers packaged skills and existing discovery links.
- The fence matcher fails on the indented `---` input above; no new regex was introduced.

What I could not check:

- The temporary-directory test was not run because it creates files, contrary to the read-only brief. Synthetic parsing probes used in-memory mocks. No files were changed.

VERDICT: CHANGES_REQUESTED