# IL5 provider terms (IL-R5, IL5-D8 (o)), recorded 2026-10-27, before the run

**Status:** recorded; **awaiting the owner's confirmation.** `run_llm.py`
refuses to run until `provider-terms-confirmed.json`, beside this file, holds
the owner's words.

## Which terms apply

- **The agent:** the `claude` CLI, `2.1.300 (Claude Code)`, as
  `gnd.agents.AgentAdapterId.claude` invokes it.
- **The sign-in, observed with `claude auth status --json`:** only the fields
  below were read. The identity fields were neither printed nor recorded.
  - `loggedIn` true;
  - `authMethod` `claude.ai`;
  - `apiProvider` `firstParty`;
  - `subscriptionType` `max`.
- **No credential variable is set:** `ANTHROPIC_API_KEY`,
  `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` and `CLAUDE_CONFIG_DIR`
  are all unset (checked by name only). The run therefore uses the CLI's own
  claude.ai sign-in, and the script reads no credential.
- **Claude Code's legal page**
  (<https://code.claude.com/docs/en/legal-and-compliance>, read 2026-10-27):
  - it names the Consumer Terms for Free, Pro and Max users, and the
    Commercial Terms for Team, Enterprise and API users;
  - it says subscription sign-in supports ordinary use of the unmodified
    binary by its own subscriber;
  - its acceptable-use section points to the Usage Policy.
- **This run, by those rules:** the **Consumer Terms of Service** apply.

## What the Consumer Terms say (<https://www.anthropic.com/legal/consumer-terms>, effective 2025-10-08, read 2026-10-27)

Paraphrased; the page itself governs.

- **§4, Inputs and Outputs:**
  - the user keeps their rights in Inputs;
  - Anthropic assigns to the user whatever rights it has in Outputs, subject to
    the user's compliance with the Terms;
  - Outputs may be inaccurate and are to be verified before reliance. GND's
    re-check does that here.
- **§4, Anthropic's use of Materials:** Anthropic may use Inputs and Outputs to
  provide and improve its services, including model training, unless the
  account has opted out. Feedback and safety-flagged material are used either
  way. The prompt holds only the synthetic IK6 refunds example (IL-R8).
- **§3, use restrictions:** the Services may not be used to develop competing
  products, including AI or machine-learning models. The page does not say
  whether that clause reaches Outputs.

## What the owner is asked to confirm

1. **The account:** the run uses this machine's `claude` sign-in (a Max
   subscription, under the Consumer Terms). It is one ordinary invocation by
   the subscriber, not a service offered to others.
2. **The training notice:** the synthetic refunds prompt and the agent's
   answer may be used by Anthropic under §4 unless the account has opted out.
3. **The §3 reading:** using one answer as a rule proposal that GND re-checks,
   inside this repository's evaluation, is not developing a competing product
   or model. **This is your reading to make, not the author's.**
4. **The publication:** the answer is committed to this repository as
   evidence, under §4's assignment.

**What GND does not establish:** that these terms permit this use. That is the
owner's ruling. The text above is a paraphrase made on the date given, and it
may have changed since.
