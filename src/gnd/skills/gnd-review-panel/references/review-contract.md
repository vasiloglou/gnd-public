# The review-panel contract

Every field the panel reads or writes, every status it can report, the exact algebra behind quorum and agreement, both commands with their bounds and exit bands, and everything a panel result does not establish. Read [`../SKILL.md`](../SKILL.md) first; this file is the detail behind it.

## 0. The shipped surface, restated

This section is deliberately duplicated from `SKILL.md`, because progressive disclosure loads `SKILL.md` on every trigger and loads this file only on demand — a correction that lands here and not there is worse than one that never lands, since the stale claim then sits in the file that is always read.

> **The runtime attempts six reviewer IDs over five installed executables and requires three distinct schema-valid successes. Claude and the GLM seat use Claude Code's `--safe-mode`; Codex uses `--ignore-user-config`; Qwen uses `--bare --safe-mode --sandbox --approval-mode plan`, binds OpenAI-compatible auth and the OpenRouter base URL in argv, maps `OPENROUTER_API_KEY` to `OPENAI_API_KEY` for that seat only, excludes the `agent` tool, permits zero tool calls, and carries fixed 600-second and four-turn ceilings; and Gemini uses `--approval-mode plan`. Qwen receives GND's already loaded and digest-checked artifact bytes inline, so it needs no approval-requiring filesystem reader. These are vendor controls, and Qwen's vendor sandbox is not a GND-owned sandbox. Claude, Codex, Qwen, Gemini, and the GLM seat receive prompt bytes on stdin. Kimi receives the UTF-8 prompt as one argv element through its documented `--prompt` mode and emits `stream-json`; the last non-empty assistant message is projected into response validation while the raw JSONL remains evidence. Each reviewer must first return substantive help that word-boundary-matches every long flag in its fixed invocation; any reviewer that cannot is retained as `incompatible` and is never invoked.**

> **GND does not enforce read-only execution.** It asks reviewers not to modify the repository and re-checks reviewed artifact bytes before publication, but it does not sandbox reviewer CLIs, constrain their tools, or prevent their effects. A changed reviewed artifact refuses the run after the fact; that is detection, not containment — and files the request did not name get no digest at all. Run a panel only from a clean working tree or a disposable worktree/clone dedicated to the run, so anything a reviewer touches outside the reviewed set is visible in `git status` rather than silently folded into uncommitted work.

> **A disposable tree must contain the intended panel implementation.** When developing GND itself, run `git diff --quiet -- src/gnd/review src/gnd/skills/gnd-review-panel src/gnd/skills/gnd-review-panel-light` before creating a worktree from `HEAD`. If it exits nonzero, stop, run the required verification ladder, and commit those implementation bytes first; never use a clean checkout to omit pending panel fixes. Record the run tree's `git rev-parse HEAD` and confirm that the imported `gnd` module resolves inside that tree before invoking the panel.

> **A request for all six seats has a credential-name preflight.** Require `OPENROUTER_API_KEY` and `ZAI_API_KEY` in the parent process environment before spending the panel budget, and report missing names without reading values. If either is absent, stop before invoking reviewers. Never read or source a repository `.env`. Runs that seek ordinary advisory quorum rather than six working seats retain missing credentials through their normal seat-level `auth-failure` envelopes.

> **The fixed invocation requests the reviewer model profile.** Claude and Codex request literal `xhigh`; Qwen requests the OpenRouter-only model ID `qwen/qwen3.8-max`; Gemini requests `gemini-3.1-pro-preview`; Kimi requests `kimi-code/kimi-for-coding`; the GLM seat runs the claude executable requesting `glm-5.3` against Z.AI's Anthropic-compatible endpoint through a fixed per-seat environment projection. Qwen, Gemini, Kimi, and the GLM seat expose no supported per-run effort flag. Model or provider access failure never authorizes a silent downgrade. [`../../gnd-update-review-panel/SKILL.md`](../../gnd-update-review-panel/SKILL.md) is the explicit maintainer workflow for refreshing this six-reviewer policy and enforcing Qwen's OpenRouter route; it never runs this panel.

---

## 1. The request

One JSON object, closed (`extra="forbid"`) and strictly typed at every level.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `1` | literal |
| `kind` | `plan` \| `experiment-outcome` \| `spec-results-delta` | the discriminator |
| `plan` | artifact | present only for `plan` |
| `outcome` | artifact | present only for `experiment-outcome` |
| `spec`, `results`, `delta` | artifact | all three present only for `spec-results-delta`; the three paths must be distinct under case-folded Unicode normalization |
| `rubric` | object | `name` plus `criteria`, at least one, all unique |

An **artifact** is `path`, `sha256`, `media_type`. `path` is a normalized repository-relative POSIX path — no absolute form, no drive letter, no backslash, no `.` or `..` component, no NUL, no non-normal spelling. `sha256` is 64 lowercase hex characters. `media_type` matches a conservative `type/subtype` grammar.

**Loading is fail-closed and bounded.** The request itself is read under a 1 MiB cap; each artifact under a 10 MiB per-file cap and a 30 MiB aggregate cap; every read goes through the descriptor-bound no-follow primitive against one retained repository-root identity, which is re-asserted after the last artifact is read. A digest that disagrees with the bytes on disk is refused before any process starts.

**Artifact transport is seat-specific and recorded by run schema 6.** Qwen receives the exact bytes GND already loaded and digest-checked, framed as UTF-8 when possible and base64 otherwise, so its zero-tool `plan` invocation never needs the shell command its CLI uses to read a named path. The other five seats receive one reference block per artifact — `path`, `media_type`, `bytes`, `sha256` — and read each path themselves. Kimi therefore retains the small by-reference prompt its argv transport needs to stay below `ARG_MAX`. Every prompt requires one focused pass: no delegation, web browsing, tests, builds, history inspection, or recursive repository inventory. The panel still reads and digest-checks every artifact before and after the run under the same caps.

**What that costs, and it is not small.** The panel can prove what it *offered* and that the files did not change during the window. It cannot prove what any reviewer read. A reviewer that ignored an artifact is indistinguishable from one that read it whole, cited evidence is evidence of engagement only, and a disagreement between two reviewers may mean they read different things rather than that they judged differently. `PANEL-REVIEW.md` states this in its own advisory boundary.

## 2. The reviewer response

The requested transport is **JSON Lines**: line 1 is the head, and every following line is exactly one concern. Claude, Codex, Qwen, Gemini, and the GLM seat emit those bytes directly on stdout. Kimi's raw stdout is its own `stream-json`: every non-empty line must be one strict JSON object, and the last non-empty assistant `content` is the response candidate. The complete Kimi stream remains the retained raw stdout. Duplicate keys and non-finite constants are refused before validation. The single-object transport — the whole response as one JSON object with its concerns inside — remains fully readable, and so do legacy direct Kimi response objects.

```
{"schema_version":2,"reviewer_id":"claude","disposition":"revise","summary":"…","concern_count":2}
{"concern_id":"…","severity":"high","relevance":"blocking","title":"…","evidence":[…],"recommendation":"…"}
{"concern_id":"…","severity":"medium","relevance":"completeness","title":"…","evidence":[…],"recommendation":"…"}
```

The head carries `schema_version`, `reviewer_id`, `disposition`, `summary`, an optional `concern_count`, and an optional `artifact_reads`. Identity, disposition, and summary are authoritative and strict. The two self-report fields are read best-effort and may never cost a seat, because a cross-check that can fail a seat is the trivial-loss defect this parser exists to remove:

- **`concern_count`** is a cross-check on a number the panel counts for itself. A bare integer, an integral float, and a decimal string are all read as the number they name; anything else is recorded as `declared_concern_count_unreadable`. Measured: a live Kimi seat returned `"4"` and lost a complete review backed by eleven file reads.
- **`artifact_reads`** is the reviewer's read report — one `{path, digest_matched}` entry per referenced artifact it read. It is the design's proof-of-read, restored to a structured home after one round suppressed it as prose and the next round then had two seats with no observable evidence of reading at all. Entries that are garbage, duplicated, or name a path outside the request are counted in `artifact_reads_dropped`; a field that is not a list is `artifact_reads_unreadable`. **`digest_matched: false` is an integrity signal about the review itself**, not a critique of the artifact: the reviewer is told to stop and `block` on a mismatch, an `approve` carrying one is self-contradictory and `malformed`, and the rendered report surfaces it apart from ordinary concerns. It remains a self-report — the panel's own on-disk verification is the arbiter of what the bytes were. The prompt asks for **at most 24 concerns, most severe first**; that cap is advisory and is never enforced at parse, because the panel discarding a valid concern to satisfy its own request would contradict the rule that every failure and dissent is retained. The 512 KiB response cap is the only hard bound on size.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `1` | literal |
| `reviewer_id` | `claude` \| `codex` \| `qwen` \| `gemini` \| `kimi` \| `glm` | must equal the reviewer that was invoked |
| `disposition` | `approve` \| `revise` \| `block` | `approve` must carry no concerns; the other two must carry at least one |
| `summary` | non-empty text | |
| `concerns[]` | concern | concern IDs unique within the response |

A **concern** is `concern_id` (stable ID grammar), `severity` (`low` \| `medium` \| `high` \| `critical`), `relevance` (`blocking` \| `hardening` \| `completeness`), `title`, `evidence` (at least one, no duplicates), `recommendation`.

**`relevance` is a second axis, and it is required.** `severity` rates how bad the flaw is; `relevance` rates whether repairing it moves the product toward doing something it demonstrably could not do before. They are independent — a `critical` naming a documentation inconsistency and a `critical` meaning the command exits 0 on invalid input arrive identically on the severity axis, and the panel had no way to tell them apart. `blocking` means that left unfixed, the software does not demonstrably do what it claims. `hardening` means a real defect whose consequence does not stop the demonstration. `completeness` means the artifact becomes more complete or consistent and no observable behaviour changes. Like `severity`, the value is the reviewer's claim about its own concern and carries no authority over the disposition; whoever dispositions the panel assigns the class that governs the repair.

**Every rubric carries the standing MVP triage criterion** (`MVP_TRIAGE_CRITERION`), and a request whose rubric omits it is refused before any reviewer is spawned. The criterion tells reviewers to classify, to report blocking concerns first, and that a review reporting no completeness concerns is not a worse review. This does not repeal the structural pressure the other way — a non-approve verdict is refused unless it carries a concern, and across nineteen measured seat-runs no seat ever returned empty, so a reviewer with nothing blocking to say must still produce something. Requiring the class to be named is what lets the panel measure how much of a round was worth running.

An **evidence** entry is `artifact_path`, `location`, `observation`. `artifact_path` must name an artifact the request itself requested. Reviewers may read anything in the repository for context, but a concern is retained only when its evidence cites the subject under review; a citation elsewhere contributes no finding, and drops the concern rather than the seat. **The prompt says this in as many words**, because for two panels running it did not, and reviewers lost whole seats to a rule they had never been told.

### Salvage: the head is strict, each concern stands alone

The **head is never salvaged**. A response with no readable head, a mismatched `reviewer_id`, a head over the 512 KiB cap, or more than 32 non-JSON lines in front of it is `malformed` and contributes nothing to quorum. An `approve` head that carries any concern line at all is likewise `malformed` — dropping the concern would launder a self-contradictory response into a clean approval.

**Every concern is validated on its own.** One that is unparseable, schema-invalid, a repeat of an earlier `concern_id`, or citing an unrequested path is dropped; the rest of the review is retained. A verdict of `revise` or `block` whose every concern was dropped is still `malformed`, because a verdict with no readable reason is not an opinion.

**Any concern at all means `revise` or `block`.** The prompt says so in those words, because two of four reviewers in `panel-run-by-reference` labelled a response `approve` while carrying concerns and lost their seats to it. The panel does not reinterpret the verdict: inventing a `revise` the reviewer did not give would be as wrong as dropping the concerns to make the approval clean.

**An `approve` response must be a clean document** — no preamble, no trailing run, no concern candidate, parseable or not. Approval is the one disposition where anything the panel could not read makes the verdict *more permissive* than what the reviewer wrote, so approval is never salvaged and never surrounded.

**Prose around the response is tolerated; a line that opens JSON and then fails is not prose.** Lines that do not open a JSON value are counted as `preamble_lines` before the head and `trailing_lines` after the last concern. A line opening with `{` before the head is `malformed`; a line opening with `{` or `[` after it is a dropped concern. The asymmetry is deliberate: before the head a match is fatal, so only the rarer prefix counts — ordinary prose opens with a bracket, and measured reviewer prose mentions braces. This is a heuristic and prose is not separable from broken JSON by inspection; what makes it safe is the approval rule above, which holds however a line was classified. A second complete JSON document after an object-transport response is `malformed`.

Nothing is dropped in silence. A retained response carries a `response_salvage` record on its envelope — `transport` (`object` or `jsonl`), `preamble_lines`, `trailing_lines`, `declared_concern_count`, `retained_concern_count`, `dropped[]` (each with `position`, `reason`, `byte_count`), `dropped_overflow`, and a derived `complete` — and `PANEL-REVIEW.md` states it under **Response Completeness**. Only the first 64 drops are recorded individually; the rest are counted in `dropped_overflow`, so a flood of junk lines cannot make the record grow with the reviewer's output. `byte_count` is transport-relative and says so rather than overstating its precision: for `jsonl` it is the exact source line, for `object` the compact re-serialization of an element whose original spelling the whole-document parse did not keep.

The parser is **total over its input**: every reachable failure, including hostile nesting and unencodable text, is a refusal, never a raised Python error. One reviewer's output can never abort another reviewer's seat.

## 3. The six active reviewer policies

Python-owned data. Repository content never selects an executable, a flag, a model, an environment value, or a working directory.

| Reviewer | Executable | Quality profile | Complete invocation argv | Prompt transport |
|---|---|---|---|---|
| claude | `claude` | `opus`, `xhigh` | `--print --safe-mode --model opus --effort xhigh --permission-mode plan --output-format text --no-session-persistence` | stdin |
| codex | `codex` | `gpt-6-sol`, `xhigh` | `exec --ephemeral --ignore-user-config --model gpt-6-sol --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check -` | stdin |
| qwen | `qwen` | OpenRouter-only `qwen/qwen3.8-max`; no per-run effort flag | `--bare --safe-mode --sandbox --auth-type openai --openai-base-url https://openrouter.ai/api/v1 --model qwen/qwen3.8-max --approval-mode plan --max-wall-time 600s --max-session-turns 4 --max-tool-calls 0 --max-subagent-depth 1 --exclude-tools agent --output-format text --prompt -`; per-seat `OPENROUTER_API_KEY` → `OPENAI_API_KEY` | stdin, with digest-checked artifact bytes inline |
| gemini | `gemini` | `gemini-3.1-pro-preview`; no per-run effort flag | `--model gemini-3.1-pro-preview --approval-mode plan --skip-trust --output-format text --prompt -` | stdin |
| kimi | `kimi` | managed `kimi-code/kimi-for-coding`; no per-run effort flag | `--model kimi-code/kimi-for-coding --output-format stream-json --prompt <UTF-8 prompt>` | argv |
| glm | `claude` | `glm-5.3` via Z.AI's Anthropic-compatible endpoint; no per-run effort flag | `--print --safe-mode --model glm-5.3 --permission-mode plan --output-format text --no-session-persistence` | stdin |

**The GLM seat's per-seat environment projection.** Six seats resolve five executables: the glm policy names the same `claude` binary and is redirected entirely by a fixed, Python-owned projection applied after allowlist sanitization, in order — remove `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `CLAUDE_CODE_OAUTH_TOKEN`; copy `ZAI_API_KEY` to `ANTHROPIC_AUTH_TOKEN` when present; set `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`. The removals mean the seat can never spend a real Anthropic credential against the redirected endpoint, and the model ID is the reverse guard — the Anthropic API would reject `glm-5.3`. A missing `ZAI_API_KEY` produces the seat's ordinary `auth-failure` envelope, never a fallback. No other seat has any projection, so the redirect and the Z.AI credential are invisible to the claude seat. The claude and glm seats read different models from different providers but share one CLI codebase, so agreement between them is weaker independence evidence than agreement between unrelated CLIs.

The capability probe is a syntax compatibility check, not an execution boundary. It requires a clean, complete help process and word-boundary-matches every `--flag` token from the fixed invocation. A help surface missing even one flag is `incompatible` and is never invoked. The probe does not establish model access, flag semantics, or read-only behavior.

**Customization isolation is requested explicitly.** Claude and the GLM seat use `--safe-mode`, Codex uses `--ignore-user-config`, and Qwen uses both `--bare` and `--safe-mode`. Qwen and Gemini request their documented `plan` approval modes. Qwen additionally permits zero tool calls and receives the reviewed bytes inline, so a filesystem-read attempt fails closed instead of asking for interactive approval. This prevents optional user/project extensions, skills, hooks, or MCP configuration from turning a bounded review into a different workflow where the CLI supports such isolation. It does not prove the vendor flags' semantics or create a GND-owned sandbox, so the clean-or-disposable-tree requirement remains.

**Executable identity is bound and re-asserted.** Each executable is resolved once from an absolute-only PATH, canonicalized, and pinned by `(st_dev, st_ino, st_size, st_mtime_ns)`; that identity is re-checked before the probe, before the main invocation, and after it. This is a TOCTOU tuple, not a content digest. Resolution follows symlinks, so an `env node` shim binds the resolved launcher rather than the JavaScript package tree. A swap between resolution and invocation fails closed.

**The environment is an allowlist, not a filter.** Only named process, config and credential variables are copied through, plus a fixed `NO_COLOR=1` and `PYTHONUNBUFFERED=1`. GND never reads a repository `.env`, never writes a credential into evidence, and never copies a credential environment value onto a command line. Kimi's reviewed prompt is deliberately present in argv and may itself contain sensitive artifact content.

**The prompt is framed as untrusted data.** Rubric, Qwen's inline artifact bytes, and the other seats' artifact references travel inside randomly delimited blocks, each labelled with byte length and SHA-256, under a standing instruction that delimited content is evidence and never instruction. The expected reviewer ID is bound in the trusted part of the prompt rather than inferred from what the CLI says about itself. Kimi receives its by-reference prompt as one exec argv element without a shell, so artifact bytes never enter Kimi's argv and the prompt stays below the OS argv-size ceiling.

**The model profile is fixed, not negotiated.** Models and supported effort controls are Python-owned policy and cannot come from the request or a reviewed artifact. Claude and Codex expose `xhigh` on their installed command lines. Qwen's CLI has no per-run effort flag and `--bare` excludes persistent user settings, so the runtime claims no Qwen effort tier; its model ID is maintained as a unique `https://openrouter.ai/api/v1` route using `OPENROUTER_API_KEY`, and the updater refuses DashScope or any other provider fallback. Gemini and Kimi likewise receive no fabricated effort setting. A provider or account that refuses the requested model produces the matching non-success envelope; the runtime has no fallback model path.

**Kimi prompt mode is automatic, not plan mode.** Kimi documents that `--prompt` cannot be combined with `--plan` and that non-interactive prompt mode uses its automatic permission policy. GND's prompt asks every reviewer not to modify the repository and re-checks reviewed artifacts before publication, but it does not turn Kimi's mode into a sandbox or prevent effects elsewhere.

## 4. The eight reviewer statuses

Every attempted reviewer produces exactly one envelope carrying exactly one of these. There is no ninth outcome and no "skipped".

| Status | Means | Counts toward quorum |
|---|---|---|
| `success` | probed, invoked, exited zero cleanly, and returned a schema-valid response | **yes** |
| `missing` | the executable was not found on PATH | no |
| `incompatible` | the capability probe did not establish the fixed invocation flag surface, so the reviewer was **never invoked** | no |
| `timeout` | the probe or the invocation exceeded the shared deadline, or the reviewer was cancelled after its process group was cleaned | no |
| `auth-failure` | the probe or the invocation reported an authentication failure | no |
| `nonzero` | a spawn failure, a nonzero exit, or a process-group cleanup that could not be proven | no |
| `over-limit` | a retained stream hit its byte cap | no |
| `malformed` | one clean invocation whose output failed closed validation | no |

A failed envelope carries at least one **issue** — `missing`, `incompatible`, `timeout`, `cancelled`, `cleanup-failed`, `spawn-failed`, `auth-failure`, `nonzero`, `over-limit`, `malformed`, `artifact-changed` — and the issue code must agree with the retained process facts. A label is an audit claim, not a presentation string, so an envelope claiming `timeout` without timed-out process evidence, or `over-limit` without a truncated stream, is refused at load.

## 5. The envelope and its process evidence

| Field | Notes |
|---|---|
| `schema_version` | `1` |
| `reviewer_id`, `executable_name` | must agree with each other |
| `status` | one of the eight above |
| `capability` | process evidence for the probe, or null when nothing was spawned |
| `invocation` | process evidence for the main call, or null when the reviewer was never invoked |
| `response` | the validated response on `success`, null otherwise — a failed envelope may never carry one |
| `response_salvage` | what the response cost to read; present only on `success`, absent entirely on pre-salvage evidence, and its `retained_concern_count` must equal the retained concerns |
| `evidence_resolution` | panel-measured engagement, present on every schema-version-4 `success`: for each retained concern, whether any evidence entry carries a verbatim quotation (15+ characters, whitespace-normalized) found in the cited artifact's bytes — `anchored_concerns`, `total_concerns`, `unanchored_concern_ids`. Measurement, never enforcement: nothing is dropped over it, and it is conservative in the safe direction — a fabricated quotation cannot match, a real one can only fail to, so it understates engagement and never overstates it |
| `issues[]` | `code`, `message`, optional `location`; empty exactly when `status` is `success` |

**Process evidence** records `status`, `spawned`, `timed_out`, `termination` (`not-started` \| `exited` \| `terminated` \| `killed`), `return_code`, `signal`, `spawn_error`, `started_monotonic`, `ended_monotonic`, `elapsed_seconds`, `argv_sha256`, `argv_count`, `stdin_sha256`, `stdout`, `stderr`, `environment`, `termination_steps`, and `process_group_cleaned`. The schema-v1 field historically named `stdin_sha256` binds the prompt bytes for every invocation: actual stdin for Claude, Codex, Qwen, and Gemini, and Kimi's final argv element. Kimi's `argv_sha256` independently binds the complete argv without retaining it. Raw bytes live out of band; each stream carries `path`, `sha256`, `observed_bytes`, `retained_bytes`, and `truncated`, so a truncation is always visible as a gap between observed and retained.

The internal consistency rules are enforced at validation, not by convention — timing must be finite and monotonic, elapsed must match the endpoints, a forced termination must carry its SIGTERM or SIGKILL step, an unstarted process may not claim an exit or carry streams, and a `succeeded` process must have exited zero with its process group proven clean.

## 6. The run

| Field | Notes |
|---|---|
| `schema_version` | `1` \| `2` \| `3` \| `4` \| `5` \| `6`, naming which writer produced the evidence so a reader never infers it from an absence. **1**: published before the salvage record existed. **2**: successful envelopes carry salvage and every prompt carried artifact bytes. **3**: as 2, with every artifact passed by reference. **4**: as 3, with measured evidence engagement. **5**: as 4, with the selected reviewer effort recorded. **6**: as 5, with `artifact_transport=qwen-inline` recording exact inline bytes for Qwen and references for the other five seats. Every earlier run loads byte-identically at its own version |
| `request` | the normalized request |
| `request_sha256` | digest of its canonical form |
| `envelopes[]` | current runs: exactly six, in the fixed order claude, codex, qwen, gemini, kimi, glm; committed runs from the prior rosters may contain the first four or the first five |
| `successful_reviewer_ids[]` | derived from the success envelopes; a forged list is refused |
| `quorum_met` | derived — true exactly when there are three or more distinct successes |
| `reviewed_artifacts_before_sha256` | the artifact set digest taken before the panel ran, over the path, digest and length each artifact was found to have **on disk** |
| `reviewed_artifacts_after_sha256` | the same digest taken after. A run you can load always shows the two equal, because a difference stops the run before publication — the guard is that refusal, not this comparison. The digests say what was verified; they are not themselves the verification |

Successful reviewer evidence must cite only requested artifacts. `run.json` is written **last**, after every stream, response and envelope, and the whole directory is published once — so a directory holding a run marker is a directory holding complete evidence.

### The evidence directory

```
panel-run/
  request.json                      normalized request, canonical bytes
  reviewers/<id>/capability.stdout  raw probe stdout
  reviewers/<id>/capability.stderr  raw probe stderr
  reviewers/<id>/stdout             raw invocation stdout
  reviewers/<id>/stderr             raw invocation stderr
  reviewers/<id>/envelope.json      the closed envelope
  reviewers/<id>/response.json      present only on success
  run.json                          the manifest, written last
```

All six active reviewers get all four stream files, including a reviewer that was never spawned — an empty file is the record that nothing was captured, and an absent one would be indistinguishable from a lost one. Prior four-envelope and five-envelope directories remain readable. Re-reading the directory re-checks every digest, every byte length, and the complete file inventory; a missing or unexpected member is a load failure.

## 7. The synthesis, and the algebra

The synthesis is the one document a reviewing agent authors. It is a *proposal*; finalization is what makes it a claim.

| Field | Notes |
|---|---|
| `schema_version` | `1` |
| `run_sha256` | must equal the digest of this exact run's canonical bytes |
| `summary` | non-empty text |
| `agreed_concerns[]` | `group_id`, `severity`, `title`, `summary`, `concerns[]`, `supporting_reviewers[]` |
| `divergent_concerns[]` | concern references |
| `prioritized_fixes[]` | `fix_id`, `rank`, `title`, `action`, `concerns[]`, `evidence[]`, `supporting_reviewers[]` |

A **concern reference** is `reviewer_id` plus `concern_id`; IDs are local to a reviewer, so the pair is the identity. An **evidence reference** adds `evidence_index` into that concern's evidence list.

**The algebra, exactly:**

| Rule | Threshold |
|---|---|
| panel quorum | **3** distinct reviewers with `status: success` |
| concern agreement | **2** distinct successful reviewers within one group |
| accounting | every retained concern of every successful reviewer appears **exactly once**, agreed or divergent |
| group closure | a fix touching any member of an agreed group must carry **every** concern, **every** supporter, and evidence for each |
| fix ranks | unique and contiguous from 1 |
| evidence locality | every cited evidence entry must point into a requested artifact |

Three and two are different numbers over different populations and neither implies the other. Three reviewers can succeed with no concern reaching two supporters — that is a real panel with no agreed concerns, and it is reported as such. Two reviewers can agree completely and still be below quorum — that is not a panel result at all.

Supporting reviewer lists are **derived and compared**, never trusted: a list naming a reviewer that raised nothing, omitting one that did, or naming a reviewer that failed is refused.

## 8. The result and the report

`gnd review finalize` returns a `PanelResult` — `schema_version`, `run_sha256`, `synthesis_sha256`, `advisory` (always `true`), `successful_reviewer_ids`, `agreed_concern_count`, `divergent_concern_count`, `prioritized_fix_count`. It is a separate, digest-linked claim over immutable run evidence, and it carries no verdict, no rate, and no conformance field, because those belong to other claim families and blending them is what the separation exists to prevent.

The Markdown report has fixed headings — `# Panel Review`, `## Summary`, `## MVP Triage`, `## Agreed Concerns`, `## Divergent Views`, `## Prioritized Fix Plan`, `## Advisory Boundary` — renders every group with its evidence locations, counts the retained concerns by relevance under `## MVP Triage` (computed from the retained concerns themselves, never from reviewer prose, and a measurement rather than a gate), lists every divergent view without exception, and neutralizes control characters, HTML and Markdown punctuation in every untrusted string. There is no writer for reviewed artifacts anywhere in this path. An existing report is refused rather than replaced.

## 9. The commands

### `gnd review panel REQUEST --out DIR`

| Bound | Default | Rule |
|---|---|---|
| `--reviewer-timeout` | 600 | positive, finite, seconds |
| `--overall-timeout` | 900 | positive, finite, seconds |
| `--max-output-bytes` | 536870912 | positive; the whole-panel aggregate is twice this and may not exceed 1 GiB. The default is effectively uncapped — a high-effort reviewer's stderr can exceed 1 MiB, and a completed review discarded for output volume costs more than the bytes it retains; pass a smaller value to bound a run |

Each reviewer's deadline is the earlier of its own timeout and the remaining overall budget. Bounds are validated **before** any process is spawned; a non-positive or over-ceiling bound is a usage error and no reviewer runs. The process-group termination grace is Python-owned and not tunable from the command line — a tunable grace is a way to make cleanup unprovable, and cleanup provenance is what the failure envelopes assert.

`REQUEST` and every artifact it names are repository-relative paths resolved against the directory you are standing in.

### `gnd review finalize RUN SYNTHESIS --out REPORT`

Loads and re-verifies the run directory, validates the synthesis closed, refuses a below-quorum run, proves the algebra above, renders, and writes the report exclusively — an existing path is never replaced.

### Exit bands

| Code | Meaning |
|---|---|
| 0 | quorum established, or the report was rendered |
| 3 | the request, the run evidence, or the synthesis failed closed validation |
| 11 | the output directory or the report path already exists; nothing was written |
| 16 | a structurally complete six-attempt run had fewer than three distinct successes |
| 64 | usage error, including a non-positive bound or an unsafe request path |
| 66 | the request, a reviewed artifact, the run directory, or the synthesis is missing |
| 70 | internal defect |
| 74 | a path or an I/O operation was refused or failed |

**16 has exactly one meaning** and covers both commands, because a below-quorum panel and a below-quorum finalization are the same fact about the same run. Per-reviewer detail lives in `run.json`, where a consumer branches on `status` rather than on a proliferation of exit codes.

## 10. Published limits

**A panel result is advisory.** It establishes that three or more reviewers returned validated responses and that a stated grouping did not overclaim against them. It establishes nothing about whether the reviewed artifact is correct.

**Quorum counts successes, not quality.** Three shallow reviews are three successes.

**Semantic equivalence is not proven.** Finalization proves the supporters named really raised the concerns grouped and that nothing was dropped or double-counted. Whether two concerns are *the same issue* stays a human or agent judgment.

**Reviewer independence is assumed, not enforced.** Six seats may sit in front of related models, and two of them share one CLI codebase. Agreement between two of them is weaker evidence than it looks.

**A clean run says nothing about a reviewer's honesty.** The runtime proves what was executed, under what argv, with what output, within what bounds, and that nothing under review changed. It cannot prove a reviewer read carefully.

**The active roster is six.** A current run may resolve zero through six reviewers; three schema-valid successes remain the fixed quorum.

**“Quality-first” names a requested profile, not a measured superiority claim.** Provider documentation establishes which model is currently positioned as flagship, Opus, Sol, Max, or Pro and which effort flags exist. It does not prove that model will review every artifact better. The explicit [`gnd-update-review-panel`](../../gnd-update-review-panel/SKILL.md) maintenance workflow re-checks those current claims and the installed help surfaces before changing this contract.
