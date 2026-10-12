# Install GND

Install the Python runtime from PyPI, then choose how your coding agent receives
GND's skills. Python 3.11 or newer is required. The package is **get-nick-done**;
the command and Python import are **gnd**.

## 1. Install the Python runtime from PyPI

With [uv](https://docs.astral.sh/uv/getting-started/installation/), install GND as
a command-line tool:

```sh
uv tool install get-nick-done==0.1.0
uv tool update-shell
```

Open a new shell, then run `gnd --help`. This makes the command available to
Claude Code and Codex without activating a project environment.

Alternatively, use pip in a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install get-nick-done==0.1.0
gnd --help
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. If you use
this route, start your coding agent from the activated shell so it can find
`gnd`. Python integrations can use the same environment to `import gnd`.

## 2. Install the skills for your agent

Choose one of the following methods for each agent. A marketplace plugin
supplies the skills and references; it still needs the Python runtime above.

### Claude Code marketplace plugin

Run these commands **inside Claude Code**:

```text
/plugin marketplace add vasiloglou/gnd-public
/plugin install gnd@gnd-marketplace
```

Start a new session. Invoke `/gnd:gnd-model-from-text` or ask Claude to use that
skill to model your expense approval policy and validate the result.

### Codex marketplace plugin

Run these commands **in your terminal** with a Codex CLI that supports `plugin`:

```sh
codex plugin marketplace add vasiloglou/gnd-public --ref main
codex plugin add gnd@gnd-marketplace
codex plugin list --marketplace gnd-marketplace --json
```

Start a new Codex chat, then ask it to use `gnd-model-from-text` to model your
expense approval policy and validate the result. Desktop clients with marketplace
support can also install GND from the configured marketplace.

The marketplace entries need to be present on repository `main`. While the
repository is private, access requires GitHub authentication. The `v0.1.0` tag
contains the Python release and predates plugin packaging, so the plugin commands
use `main`. See [plugin installation and updates](marketplace-plugins.md) for
switching from existing skill copies and managing plugin updates.

### Install skill files directly from the Python package

This route works with the PyPI package without a marketplace. Run it in the
project where Claude Code or Codex will work:

```sh
gnd install --claude --project
gnd doctor --claude --project
```

For Codex instead:

```sh
gnd install --codex --project
gnd doctor --codex --project
```

To target both agents, use `gnd install --project` and `gnd doctor --project`.
Replace `--project` with `--global` for user-level installation. Start a new agent
session after installation. See [skill installation details](agents/install.md)
for scope, upgrade, and uninstall behavior. `gnd doctor` inspects these copied
skills; it does not inspect marketplace plugins.

## Upgrade

For a uv tool installation:

```sh
uv tool upgrade get-nick-done
```

For a pip installation, activate its environment and run:

```sh
python -m pip install --upgrade get-nick-done
```

If you installed skill files directly, run `gnd install --sync` after upgrading.
Plugin users update through their agent's plugin manager. Keep the plugin and
runtime versions aligned.

## Install a release artifact

You can instead download the wheel and checksums from the
[v0.1.0 release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.1.0).
Install it in an activated virtual environment:

```sh
python -m pip install /path/to/get_nick_done-0.1.0-py3-none-any.whl
```

## Contributor checkout

Contributors use the repository and locked environment:

```sh
git clone https://github.com/vasiloglou/gnd-public.git
cd gnd-public
uv sync --locked --group dev
```

Follow [CONTRIBUTING](https://github.com/vasiloglou/gnd-public/blob/main/CONTRIBUTING.md)
for development skill setup. Tutorials copy inputs from the installed package,
so application users do not need a repository checkout.

## Optional tools

The base checker needs no provider key, native compiler, or database. Synthetic
population generation uses the `synth` extra. Native exports and live agent
sessions have additional tools described in their guides.

[Continue to your first check →](quickstart.md)
