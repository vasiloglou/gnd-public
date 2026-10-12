# Install GND as an agent plugin

The GND plugin exposes the same 16 workflow skills as the Python package to
Claude Code and Codex. Install the Python runtime first, then choose your agent's
marketplace commands below. Python 3.11 or newer is required.
See [installation from PyPI](installation.md#1-install-the-python-runtime-from-pypi)
for the pip virtual-environment alternative.

```sh
uv tool install get-nick-done==0.1.0
uv tool update-shell
```

Open a new shell and check `gnd --help`. The plugin supplies instructions and
references; the installed `gnd` command performs validation and runs workflows.
Plugin installation does not install Python packages or configure provider keys.

## Claude Code

Run these commands inside Claude Code:

```text
/plugin marketplace add vasiloglou/gnd-public
/plugin install gnd@gnd-marketplace
```

Start a new session, then ask: "Use gnd-model-from-text to model our expense
approval policy, then validate it." Plugin skills are namespaced under `gnd`;
use `/gnd:gnd-model-from-text` to invoke that workflow explicitly.

## Codex

Run these commands in a terminal with a Codex CLI that supports `plugin`:

```sh
codex plugin marketplace add vasiloglou/gnd-public --ref main
codex plugin add gnd@gnd-marketplace
codex plugin list --marketplace gnd-marketplace --json
```

Start a new Codex chat so it picks up the installed skills. Ask it to use
`gnd-model-from-text` for the same expense-policy prompt. In a desktop client
with marketplace support, select GND from the configured marketplace and install
it there if that client does not share the CLI installation.

These commands use GND's repository marketplace. They do not submit GND to an
Anthropic or OpenAI curated directory. Until the repository is public, GitHub
access is required. The marketplace files must be merged into `main` before the
commands above work. The `v0.1.0` tag predates plugin packaging; it contains the
Python release, not these marketplace entries.

## Existing skill installations

Choose either the plugin or `gnd install` to supply skills to each agent. The
plugin has its own cache and lifecycle; `gnd doctor` and `gnd uninstall` inspect
only the roots managed by the Python installer. If you already used
`gnd install --project` or `--global`, use `gnd uninstall` with the matching scope
and runtime before switching, and inspect any modified files it retains.
Do not delete skill files by hand or assume installing a plugin supersedes them.

## Updates

Update the marketplace and plugin through your agent's plugin manager, and update
the Python runtime with `uv tool upgrade get-nick-done`. Keep the plugin version
and runtime version aligned. Plugin users do not need `gnd install --sync`.

## Maintainers

The repository root is the plugin root. `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json` both declare `./src/gnd/skills/`, so every sibling
reference resolves inside the single packaged skill tree. There is no copied
skill bundle to regenerate. LICENSE and NOTICE remain at the plugin root.
The marketplaces contain only GND's packaged workflows; repository development
skills such as `process-phase` are not plugin components.

Validate a change with:

```sh
uv run pytest -q tests/test_marketplace_plugins.py tests/test_release_docs.py
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate .claude-plugin/marketplace.json --strict
codex -c 'marketplaces.gnd-marketplace.source_type="local"' \
  -c "marketplaces.gnd-marketplace.source=\"$PWD\"" \
  plugin list --marketplace gnd-marketplace --available --json
```

The Codex command uses a temporary command-line configuration override; it does
not register the development checkout in the user's marketplace configuration.

Format references: [Claude marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces)
and [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).
