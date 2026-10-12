# Install GND

You need Python 3.11 or newer. The distribution is **get-nick-done**; the command
and Python import are both **gnd**. The package name and internal milestone
numbers are separate from the published release version.

## Install from PyPI

```sh
pip install get-nick-done==0.1.0
gnd --help
```

For agent skills, choose [the marketplace plugin](marketplace-plugins.md) or the
`gnd install` commands below. The marketplace route uses a separate Python
runtime installation and does not need `gnd install`.

## Install a release artifact

You can instead download the wheel from the
[v0.1.0 release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.1.0).
Create a fresh environment and install that exact file:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install /path/to/get_nick_done-0.1.0-py3-none-any.whl
source .venv/bin/activate
gnd --help
```

The wheel path is the one installation placeholder. The tutorials below use the
active environment's `python` and `gnd` commands. On Windows, activation uses
`.venv\Scripts\activate`; the documented shell walkthroughs are verified on the
profiles listed under [support](support.md).

## Work from the public repository

For a contributor checkout, use the repository and the locked environment:

```sh
git clone https://github.com/vasiloglou/gnd-public.git
cd gnd-public
uv sync --locked --group dev
source .venv/bin/activate
gnd --help
```

Repository access is required while staging remains private. After activating,
create a separate empty working directory for a tutorial. Its inputs are copied
from package resources, so it does not depend on repository fixtures.

## Install the skills into your agent

GND is skills plus Python code. The package you just installed also carries the agent
skills. Place them in the project where your coding agent works:

```sh
gnd install --project
gnd doctor --project
```

By default this targets both Claude Code (`.claude/skills/`) and Codex (`.codex/skills/`);
`--claude` or `--codex` selects one, and `--global` installs at user level. `doctor`
reports what is placed and flags stale, modified or colliding copies. See
[Install the skills](agents/install.md) for the details, and
[Work with an agent](agents/index.md) for what each skill produces.

## Optional tools

The base checker needs no provider key, native compiler or database. Synthetic
population generation uses the `synth` extra. Native exports and live agent
sessions have additional tools, described in their task guides. A docs preview
uses the separate `docs` development group; installing GND does not install a
site generator.

[Continue to your first check →](quickstart.md)
