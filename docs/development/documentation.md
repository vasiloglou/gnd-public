# Write and preview documentation

Documentation is Markdown in `docs/`, with navigation and presentation in
`zensical.toml`. Application inputs and checkpoints live in the installed package
under `src/gnd/examples/`; a tutorial must not require the old source repository.

## Preview and build

From a contributor checkout:

```sh
uv sync --locked --group docs --group dev
uv run --group docs zensical serve --dev-addr 127.0.0.1:8000
```

For a strict production build and internal-link check:

```sh
uv run --group docs zensical build --strict
uv run python tools/check_docs.py site
```

The site uses local assets and system fonts. The docs dependency group stays
separate from the base package. CI builds a preview artifact; the deployment job
is gated by the `GND_DOCS_PUBLISH` repository variable and a manual request. The
release operator enables that variable only at Phase 5 publication.

## Keep runnable instructions honest

Place an HTML comment `<!-- gnd-run expect=0 -->` immediately before a
normal `sh` or `python` fenced block. Set the expected exit explicitly for an
intentional failure. Each block runs in a fresh process, and a tutorial shares
one temporary working directory. Use `python` and `gnd` from the active environment;
put directory changes inside the same block as the command that needs them.

The parser consumes the comments for tests; the site renders ordinary
code fences normally. Unmarked snippets are illustrative or setup instructions; label
placeholders and optional provider/native prerequisites in adjacent prose.

Use `<!-- gnd-run expect=0 lane=souffle -->` (or `pyrel` / `lean`) for a native
step. The default lane is offline; a selected native lane runs its offline
prerequisites and refuses absent or wrong-version tools. PyRel uses a separate
locked interpreter because its Pydantic pin conflicts with GND: the runner takes
it from `GND_TUTORIAL_PYREL_PYTHON` and exports it to pyrel-lane blocks as
`GND_PYREL_PYTHON`, the variable the applications read. Bare `python` and `gnd`
keep meaning the GND environment in every block, as they do in a reader's shell.
A `python` fence in the pyrel lane still runs under the PyRel interpreter. See
[runtime setup](../runtimes/scenario.md). Never count skipped native steps as
successful execution.

Full native source is rendered with `pymdownx.snippets` from the packaged file;
documented commands execute that same file. The site rejects missing includes
and leaked include directives. Packaged runtime-environment files are byte-pinned
copies of the separate locked tutorial project, not an independently maintained lock.

```sh
uv run pytest -q tests/test_documentation_tutorials.py tests/test_release_docs.py --tb=short
```

The runner also accepts an explicitly selected installed Python executable via
`GND_TUTORIAL_PYTHON`. Release validation installs each wheel origin in a fresh
venv, copies docs/tools/README outside the checkout, and runs the same examples.
Assertions in executable blocks check actual output facts as well as command
exits. Negative controls prove that wrong exits and broken links fail the gates.

## Writing style

Start with the reader's goal. Explain the model before asking them to copy it.
Show the meaningful part of a report, a reasoned repair and the next action.
Put a prompt beside the checkpoint it can produce and name the explicitly
selected skill. Distinguish a historical observation, a supplied checkpoint and
a new live run. Update capabilities from the code and authoritative references.

The bounded installed-wheel check builds both origins and retains artifacts:

```sh
uv run python tools/check_installed_docs.py --out /tmp/gnd-docs-candidate
```

Choose a new output directory for each candidate; the command refuses to reuse
an existing directory so wheel identities and results cannot be overwritten.
