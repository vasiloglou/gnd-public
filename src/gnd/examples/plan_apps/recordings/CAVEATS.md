## Caveats

- **Two launches before this one were stopped and discarded.** The cause was a
  recorder defect, not the outcomes: both passed the PyRel interpreter in a way
  that failed inside each run's temporary directory, so every PyRel check
  crashed.
  - The first launch made 132 model calls over 86 runs.
  - The second made 143 calls over 49 runs.
  - Neither recording is kept here. The recorder now refuses to start unless
    each app's documented first plan gets its documented verdict.
- **Rebound once after recording.** A refusal message printed the app's
  temporary plan path, which is now replaced by `<tmp>`. `manifest.json`
  (`rebound`) lists the files changed and their digests. No outcome changed.
- **Reindexed once after recording.** `results.json`'s per-attempt index was
  rebuilt from the recorded `session.txt` and reply files, which were not
  changed:
  - each reported (check, status) pair is kept, including warnings and rules
    reported as not checked;
  - exit-3 refusal codes are kept;
  - "repaired" is split into repaired-rule and repaired-format.
- **Claude Code saw context the OpenRouter models did not.**
  - Claude Code adds its own environment context, about 1.5k tokens, including
    the host's date. Four Claude Haiku clinic runs mention the system date
    2026-10-14; the clinic state's "today" is 2024-03-10.
  - Claude also reasons before it answers (extended thinking); the small models
    do not.
  - Claude Code cannot drop that context without an API key (`--bare`), and the
    owner's login was used.
- **The answer template quoted every value.** The adapter's system prompt showed
  bindings as `"<value>"`. Every Claude lease repair was a repaired-format run:
  `amount` was first written as the string `"1450"`. The template is now
  type-neutral for later recordings.
- **OpenRouter chose the upstream host per call:**
  - Llama 3.1 8B: Novita 26, DeepInfra 34;
  - Gemma 3 4B: Parasail 68, DeepInfra 3;
  - Llama 3.2 3B: Parasail 69.

  The reply files' `provider` field holds that host, not "openrouter".
- **The access rules the models read said Frank's wiki access was "approved by
  Erin"**, while the state says Dana. The text was corrected after the
  recording (PL16 review, C1). No run's verdict depends on Frank's approval.
- **Small models are nondeterministic.** These are 5 runs each, at the
  provider's default temperature; another 5 runs would differ.
