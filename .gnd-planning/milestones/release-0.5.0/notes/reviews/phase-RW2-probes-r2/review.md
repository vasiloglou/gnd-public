<!-- Edited by review_tool.py sanitize: 3 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 15 SHA-256 values match the brief. Three gaps remain.

**F1 (medium)** — [tests/test_release_acceptance.py:911](<repo>/tests/test_release_acceptance.py:911): `shlex` treats an unquoted `#` inside a word as a comment, unlike the shell.

Replace the COUNT README’s first command with:

```sh
gnd check model.orm.yaml population.json#BROKEN
```

The helper accepts it. Executing a harmless shell function confirmed that the shell passes `population.json#BROKEN` as the argument. P4 still runs its hardcoded `population.json` command, hiding the documentation regression. Reproduced for all 13 probed commands across both READMEs.

**F2 (medium)** — [tests/test_release_acceptance.py:913](<repo>/tests/test_release_acceptance.py:913): Independent line tokenization counts here-document contents as commands.

Replace the first command, inside its existing shell fence, with:

```sh
cat <<END_COMMAND_TEXT
gnd check model.orm.yaml population.json
END_COMMAND_TEXT
```

The helper accepts it, although the shell supplies that text to `cat`. Reproduced for all 13 commands. `/bin/sh -n` accepts the syntax; execution was prevented by the read-only environment’s restriction on shell temporary files.

**F3 (medium)** — [tests/test_release_acceptance.py:910](<repo>/tests/test_release_acceptance.py:910): The Markdown reader’s `splitlines()` recognizes separators that the shell treats as literal characters.

Prefix a command with `other` followed by U+2028, producing `other\u2028gnd check model.orm.yaml population.json` with an actual U+2028 character. The helper accepts it. `/bin/sh` instead attempts to execute `other\u2028gnd` and exits 127. Reproduced for all 13 commands.

What I checked and found true:

- **C1, ordinary cases:** All 13 commands reject seven mutations each: another executable, shell comment, HTML comment, placement outside a fence, another fence language, changed token boundaries, and removal.
- **C2:** The ten shipped negative controls pass with the repair. Substituting the exact round-1 substring implementation makes eight fail.
- **C3:** Reconstructing the round-1 source and comparing ASTs shows that `readme_commands` is the only changed function. All 16 test functions, including their assertions, are identical.
- Both packaged READMEs pass because their commands match shell-fence token lists.
- Additional matcher checks accept quoted arguments, tabs, trailing comments, tilde fences, fence info strings, CRLF and three-space fence indentation.
- The shipped `program_constants` control passes in memory.

I ran these checks with in-memory file substitutes and bytecode writing disabled. I could not rerun retained-wheel acceptance or the installed families lane because they create environments and scratch files.

VERDICT: CHANGES_REQUESTED