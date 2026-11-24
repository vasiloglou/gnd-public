1. **F1 — YAML names are read incorrectly**, `tools/skill_names.py:11–12`. Valid frontmatter containing `name: "demo"` returns the literal string `'"demo"'` instead of `'demo'`, causing directory/name comparisons to fail. Other executed cases:
   - `name: demo # comment` returns `'demo # comment'`.
   - `"name": demo` returns `None`.
   - `name: >-\n  demo` returns `'>-'`.
   - An indented mapping returns `None`.

   Reproduce by passing each form inside `---` frontmatter to `skill_name`. The existing `gnd.exp.frontmatter.read_frontmatter` correctly returns `'demo'` for every case. Reuse that reader.

2. **F2 — Inline dashes truncate frontmatter**, `tools/skill_names.py:9`. This valid document returns `None` instead of `'demo'`:

   ```yaml
   ---
   description: "Use --- to separate sections."
   name: demo
   ---
   ```

   Splitting on every `"---"` mistakes description text for a closing fence. I also reproduced an `IndexError` for a document without frontmatter and a false name extracted after a body horizontal rule. Fence detection should use the existing frontmatter reader.

What I checked and found true:

- All three SHA-256 hashes match the brief.
- Both committed test bodies pass: the packaged test used real files; the temporary-file test used in-memory filesystem operations.
- The packaged inventory contains 18 matching directory/name pairs.
- Exercised the delimiter split/index, `startswith("name:")`, colon split, and line splitting with the inputs above. Findings were reproduced using mocked reads, without creating files.
- The working tree remained unchanged.

What I could not check:

- The full pytest suite and real temporary-directory fixture were not run because the brief prohibits creating files.

VERDICT: CHANGES_REQUESTED