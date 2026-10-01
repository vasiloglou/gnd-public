---
name: gnd-update-review-panel
description: "Updates the five terminal-agent harnesses used by GND's active review panel (Claude Code, Codex CLI, Qwen Code, Gemini CLI, and Kimi Code), enforces Qwen's OpenRouter route, then refreshes and validates the fixed reviewer model and prompt-transport policy from current official provider documentation. Use when asked to update, upgrade, refresh, or audit the review-panel CLIs, models, provider routing, effort settings, or Kimi non-interactive invocation. This maintainer workflow may update installed packages, select an existing Qwen OpenRouter route, or edit the panel adapters, contract, and tests; it never runs a panel, edits a reviewed artifact, changes credentials, or silently downgrades a model."
---

# Update the GND Review Panel

Refresh two separate surfaces in order: the installed reviewer CLIs, then GND's
Python-owned model policy. Do not treat a newer binary as evidence that the model
profile is current, and do not treat a current model profile as evidence that a
local executable was updated.

## Preconditions

Run this workflow only from the GND repository root. Require
`src/gnd/review/adapters.py`, `src/gnd/skills/gnd-review-panel/SKILL.md`,
`src/gnd/skills/gnd-review-panel-light/SKILL.md`, and `pyproject.toml` to exist.
A request to update the harnesses authorizes the package
updates below; it does not authorize login, credential changes, provider purchases,
or a review-panel run.

Before modifying anything, inspect `git status --short` and preserve unrelated
worktree changes. Stop if a required file overlaps an unexplained user edit.

## 1. Check and update the harness set

Run the bundled updater in check mode first:

```bash
python3 src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py --check
```

It recognizes all five active panel CLIs; Kimi is also used by the separate
legacy `plan-review-panel` shell harness:

| Reviewer | Supported source |
|---|---|
| Claude Code | global npm package `@anthropic-ai/claude-code` |
| Codex CLI | global npm package `@openai/codex` |
| Qwen Code | global npm package `@qwen-code/qwen-code` |
| Gemini CLI | global npm package `@google/gemini-cli` |
| Kimi Code | global npm package `@moonshot-ai/kimi-code` or native `~/.kimi-code/bin/kimi` |

The check is fail closed. If a CLI is missing or its executable comes from another
source, stop before any update and use that vendor's documented updater only after
identifying the source. Never replace an unknown executable with an npm install.

When all five updater-managed sources resolve, apply the update:

```bash
python3 src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py --apply
```

The script queries live npm `latest` tags and Kimi's official native release
endpoint, preserves native-vs-npm Kimi, updates the global npm packages in one npm
transaction, runs Kimi's official installer for native Kimi **only at a digest you have
reviewed and pinned** (see below), and then verifies every resolved command. It also selects the already-configured Qwen
OpenRouter route described below. Retain its complete before/after JSON in the work
log. A partial or unverifiable update is a failure; do not call it current.

### The native-Kimi installer must be pinned before it will run

Native Kimi is installed by piping `https://code.kimi.com/kimi-code/install.sh` into
`bash`. That is remote code executing with your privileges, so the script **refuses to
run it unless its sha256 matches a digest you have reviewed**:

```bash
# 1. See what upstream is serving right now — this fetches and hashes, never executes.
python3 .../update_harnesses.py --check      # read the native_kimi_installer block

# 2. Review the script at that digest, then either pin it permanently ...
#    (set NATIVE_KIMI_INSTALLER_SHA256 in update_harnesses.py)
# 3. ... or authorise a single run:
python3 .../update_harnesses.py --apply --installer-sha256 <hex>
```

With no pin, `--apply` fails closed: nothing is executed and no harness is modified.
When upstream publishes a new installer the digest stops matching and `--apply` halts —
**that is the control working, not a bug.** Re-review and re-pin.

Do not "fix" a mismatch by copying the observed digest into the constant without reading
the script. That is trust-on-first-use wearing a pin's clothes: it records whatever was
served, which is the one thing the pin exists to not do. Transport hardening
(`--proto =https`, host confinement, size cap) proves only *where* the bytes came from;
the same host can serve different code tomorrow over equally good TLS.

Note this is the one network egress under `src/gnd/` that the repository's no-network
gates cannot observe — it leaves via `subprocess` → `curl`, so the banned-import test
sees no banned import and the in-process socket patch has no subprocess to watch. The
digest refusal is the compensating control.

## 2. Resolve the current quality-first model profile

The table below is a checked baseline, not a timeless registry. On every invocation,
open the current official pages and confirm both the model and the installed CLI
flag before editing code:

| Reviewer | Quality-first baseline | Per-run effort |
|---|---|---|
| Claude | `opus` (latest Opus alias) | `--effort xhigh` |
| Codex | `gpt-6-sol` | `-c model_reasoning_effort=\"xhigh\"` |
| Qwen | `qwen/qwen3.8-max` | model supports tiered reasoning; no per-run effort flag |
| Gemini | `gemini-3.1-pro-preview` | model thinking; no CLI effort flag |
| Kimi | `kimi-code/kimi-for-coding` | no CLI effort flag; `--prompt` non-interactive mode |
| GLM | `glm-5.3` via the Claude Code CLI against `https://api.z.ai/api/anthropic` | no effort flag — Z.AI documents no effort control on the Anthropic-compatible endpoint |

The GLM seat installs no sixth binary: it runs the Claude Code executable under a
fixed per-seat environment projection (remove the real Anthropic credentials, map
`ZAI_API_KEY` to `ANTHROPIC_AUTH_TOKEN`, set `ANTHROPIC_BASE_URL`). Updating the
`@anthropic-ai/claude-code` package therefore updates both seats at once, and any
claude argv change must be re-verified against the glm policy too.

Use only primary vendor sources:

- Claude: <https://code.claude.com/docs/en/model-config>
- Codex/OpenAI: <https://developers.openai.com/api/docs/guides/latest-model>
- Qwen: <https://github.com/QwenLM/qwen-code/blob/main/docs/users/configuration/model-providers.md>
- Gemini: <https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/gemini-3.md>
- Kimi: <https://moonshotai.github.io/kimi-code/en/reference/kimi-command>
- GLM/Z.AI: <https://docs.z.ai/devpack/tool/claude>

For Qwen, also inspect the just-installed package's bundled model-provider schema
and preset for the current Max family. OpenRouter is mandatory: the user's
`~/.qwen/settings.json` must contain exactly one `modelProviders.openai` entry whose
`id` is `qwen/qwen3.8-max`, whose `baseUrl` is
`https://openrouter.ai/api/v1`, and whose `envKey` is
`OPENROUTER_API_KEY`. The updater checks that route before changing any package,
then atomically sets `model.name` and `model.baseUrl` to that entry and verifies it
again after the update. It never reads the key's value, creates a provider entry,
or changes credentials. A missing, duplicate, or non-OpenRouter route is a blocker;
DashScope and every other fallback are forbidden.

Select the provider's explicitly documented strongest flagship, Opus, Sol, Max,
or Pro model for difficult review work. For Kimi, retain the documented managed
coding alias unless the provider explicitly ranks a replacement. Prefer a documented rolling alias when it
means “latest strongest”; otherwise pin the current concrete model ID so evidence
records what was requested. Do not infer availability from marketing prose.

`xhigh` is a literal requirement where the CLI exposes it. Do not translate it to
`max`: they are distinct settings. Qwen 0.21.12 supports `xhigh` only through its
persistent `model.reasoningEffort` setting; do not mutate that global preference or
pretend it was bound by argv. Do not invent an effort flag for Gemini or Kimi. If
a provider later exposes a documented per-invocation `xhigh`, add it
only after the installed `--help` surface proves the flag exists.

Account access is not a reason to weaken the profile. If the strongest configured
model is unavailable, retain the reviewer's ordinary failed envelope; never silently
fall back to a weaker model and count that result toward the intended profile.

The light panel retains these exact models and changes only supported per-run
effort: Claude and Codex use `high` by default or user-selected `medium`. Qwen,
Gemini, and Kimi remain byte-identical to the quality-first policy because they
expose no supported per-run effort control that this command may bind. Re-check
that `high` and `medium` remain documented values whenever the Claude or Codex
CLI changes.

## 3. Update the fixed panel policy

Edit the Python-owned baseline `invocation_argv` tuples and the closed
`reviewer_policies` effort projection in `src/gnd/review/adapters.py`. Include
every model and supported effort flag, preserve `xhigh` for the quality-first
command plus `high`/`medium` for the light command, and verify every long flag
against the installed CLI's substantive help. Keep stdin prompt transport for
Claude, Codex, Qwen, and Gemini. Kimi is
the sole argv transport: append the UTF-8 prompt as one exec argument after
`--prompt`, request `stream-json`, retain raw JSONL, and validate only the last
non-empty assistant message. Never route Kimi through a shell. Keep the timeout,
executable-identity, environment-allowlist, and no-session-persistence controls.

Preserve the explicit disclosure that Kimi prompt mode cannot combine with
`--plan`, uses automatic permissions, exposes the live prompt in argv, and may
hit the OS argv-size ceiling.

Do not make models, flags, executables, prompt transport, or effort selectable from
the review request or repository content. The command-line selection belongs only
to `gnd review panel-light`, is closed to `high` and `medium`, and never changes
models or persistent settings. Do not weaken a policy merely to make a new CLI
version pass. A CLI whose help does not document every fixed invocation
flag remains `incompatible`. GND does not sandbox reviewer CLIs or claim that
vendor permission flags enforce a GND-owned read-only boundary.

The policy has **one code-owned source** — the baseline tuples and closed effort
projection in `src/gnd/review/adapters.py` — and three deliberately duplicated
prose surfaces (progressive disclosure loads an entry point on every trigger,
the full contract on demand):

- `src/gnd/skills/gnd-review-panel/SKILL.md`
- `src/gnd/skills/gnd-review-panel/references/review-contract.md`
- `src/gnd/skills/gnd-review-panel-light/SKILL.md`

Update both, then rely on the drift gate for exactly what it checks:
`tests/test_skill_prose_sync.py` asserts every model ID against both prose
surfaces, every long invocation flag against `review-contract.md` only, the
`xhigh` literal against both surfaces, and Kimi's argv transport in the entry
point and contract.

Update tests to assert each exact model, every supported `xhigh` flag, both light
efforts, and that Qwen/Gemini/Kimi do not change between profiles. Any argv change
must update the retained-help conformance test; fake reviewers emit realistic help
and must never manufacture a GND-authored capability record.

## 4. Validate

Run, in order:

```bash
uv run --with PyYAML python /path/to/skill-creator/scripts/quick_validate.py src/gnd/skills/gnd-update-review-panel
uv run --with PyYAML python /path/to/skill-creator/scripts/quick_validate.py src/gnd/skills/gnd-review-panel-light
uv run pytest tests/test_review_runner.py tests/test_review_e2e.py tests/test_review_bands.py tests/test_skill_prose_sync.py
uv run pytest tests/test_packaged_skills.py tests/test_install.py tests/test_doctor_uninstall.py
uv run pytest
uv run gnd doctor --project
```

Use the actual discovered `skill-creator` path for the first command. If the new
packaged skill changed the inventory, regenerate GND's project discovery links with
`uv run gnd install --symlink --project`; do not hand-author a divergent link value.

## Report

Report every CLI's before version, after version, latest observed version, install
source, and executable path. Report Qwen's sanitized route fields and confirm that
the selected model and base URL are OpenRouter-bound. Then report the six requested
models (the glm seat's model and Z.AI base URL included), which reviewers carry
literal `xhigh`, how the `high` and `medium` light
profiles differ, every reviewer left incompatible and why, the exact tests run,
and whether `gnd doctor --project` passed. State that no
panel was run and no credentials or reviewed artifacts were changed.

## Record and commit

This is a GND-maintainer workflow: its commits target the GND repository itself, not a consuming project, so there is no milestone record file -- the GND repo's own planning tree is its record. Commit as `chore(review-panel): ...` (or `fix(review-panel): ...` when repairing a broken route), staging exactly the files this workflow declares it may modify, with a body listing before/after harness versions and the step-4 validation ladder results with exit codes verbatim. Grammar only -- wrapping, `--` for dashes, no backticks -- follows [`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md). `gnd` itself never touches git.
