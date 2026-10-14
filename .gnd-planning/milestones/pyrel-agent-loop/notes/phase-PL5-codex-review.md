# Independent PL5 review (Codex gpt-6-sol)

Owner explicitly approved this review in chat on 2026-10-14. One reviewer is one reviewer.
Returned text below is verbatim except replacement of the checkout prefix by <checkout>.
The reviewer's hash table contains a malformed dev-session digest; it is retained as returned, not corrected into evidence. Recompute actual file hashes separately.
Raw review SHA-256: 2ab7358ee10adf2f7e4b3b0fabbbb11f721134c4783995c3b03b849de4eb17e1

## Verdict: revise

I reviewed committed diff `1495ba2..2eb91af` at `2eb91afe73400d39225daa4e0bb92ff020fd5052`. **Two findings block PL5 closure:** the Expense page conceals material lines of the recorded task, and its evolution example displays a green conformance result without checking the generated project. The remaining findings are substantive hardening or coverage gaps. This is one independent review; I invoked no other reviewer or provider.

### Findings

1. **High · blocking — the Expense recording shows an incomplete task.** [docs/expense/04-native.md:278](<checkout>/docs/expense/04-native.md:278) prints only four lines of the hash-checked [task](<checkout>/src/gnd/examples/expense/recordings/TASK-conflict.md:5). The hidden lines explicitly require a `team-lead` fact for expense 102, preservation of the seed, and repair until `gnd check` exits 0. A reader sees only “Dana … approved expense 102. Record it,” so the recorded first-try finance candidate appears to answer a materially different task. **Reproduction:** compare the page’s `splitlines()[:4]` with task lines 5–13; the retained desktop and mobile screenshots show the same omission.

2. **High · blocking — `conformance-exit: 0` checks no linked project.** The new [meal-cap helper:58](<checkout>/src/gnd/examples/expense/prepare_meal_cap.py:58) emits `linked_projects: []`, although step 2 created `expense-native` with `gnd codegen`. [Step 7:590](<checkout>/docs/expense/04-native.md:590) then presents `conformance-exit: 0`. Evolution runs conformance only for declared projects; its aggregate defaults to zero for an empty list ([service.py:1841](<checkout>/src/gnd/evolve/service.py:1841), [models.py:1100](<checkout>/src/gnd/evolve/models.py:1100)). A reader can change the model and mistake that zero for evidence that generated files remain aligned. **Reproduction:** static trace of the proposal and aggregate; post-change project conformance was **UNREPRODUCED** under the read-only constraint.

3. **Medium · hardening — opening promises can imply a real refusal.** [Expense’s opening:9](<checkout>/docs/expense/04-native.md:9) says an agent “is refused,” and [the overview:167](<checkout>/docs/pyrel-apps.md:167) likewise says the check refuses the agent’s request. [BookRec:485](<checkout>/docs/bookrec/07-native.md:485) says a real assistant does the feedback reading shown for the stand-in. Later sections correctly disclose the distinction, but these claims blur it at the point a junior reader forms expectations. **Reproduction:** both `results.json` files list all eight Codex runs as `accepted` in one attempt; no Claude run or real feedback repair was recorded.

4. **Medium · hardening — hash checks disappear under optimized Python.** The recorded-task, transcript, candidate and feedback blocks use `assert` for their digest checks; for example [BookRec:289](<checkout>/docs/bookrec/07-native.md:289) and [Expense:279](<checkout>/docs/expense/04-native.md:279). With `python -O` or `PYTHONOPTIMIZE=1`, altered bytes can be printed without a check; the tamper tests use the normal interpreter. **Reproduction:** read-only `.venv/bin/python -O -c 'assert False; print("printed despite failed assertion")'` printed the message.

5. **Medium · hardening — the cap helper can widen a rule while calling it a reduction.** [prepare_meal_cap.py:25](<checkout>/src/gnd/examples/expense/prepare_meal_cap.py:25) accepts any integer; [line 55](<checkout>/src/gnd/examples/expense/prepare_meal_cap.py:55) always records that Finance “lowered” the cap. `--cap 100` proposes raising the shipped 75 EUR limit, contrary to the tutorial’s stated operation; zero and negative values are also admitted by the helper. **UNREPRODUCED runtime:** this follows directly from the argument and proposal construction; I did not write a proposal.

6. **Medium · hardening — evolution command pipelines mask failure exits.** Both chapters pipe `gnd evolve preview` and `apply` through `grep` and `sed` without `pipefail`, for example [Expense:582](<checkout>/docs/expense/04-native.md:582) and [BookRec:603](<checkout>/docs/bookrec/07-native.md:603). A failed evolution command can leave the shell reporting success while showing no expected record. **Reproduction:** the read-only equivalent `false | grep -E 'breaking|affected' | sed -E 's/x/y/'` returned pipeline exit `0`.

7. **Medium · completeness — the promised prose gate omits touched agents pages.** Plan PL-R7 and [the PL5 spec](<checkout>/.gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL5-spec.md:21) apply the readability and claim gate to every touched page. [test_pyrel_learning_path.py:8](<checkout>/tests/test_pyrel_learning_path.py:8) defines `FULL` as only the overview and two chapters; the touched `docs/agents` pages receive none of those paragraph, wording or required-claim checks. **Reproduction:** compare `FULL` with the committed agents-page diff. I did not establish a current prose violation on those pages.

8. **Low · hardening — excerpt grounding ignores line order.** [test_pyrel_learning_path.py:129](<checkout>/tests/test_pyrel_learning_path.py:129) turns the shipped source into a set of stripped lines and checks each displayed line for membership. Reordering an `if`, `else`, or query line in a tutorial excerpt would still satisfy this guard while teaching invalid code. **Reproduction:** static inspection of the set-membership assertion; a mutation run was **UNREPRODUCED** under the no-edit instruction.

### Claims checked and limits

The shipped model provenance, verbalizer blocks, ORM excerpts and hand-written PyRel snippets align for the illustrated age and team-lead rules. The pages label the hand-written queries as equivalents. BookRec runs both stand-in candidates through the app; Expense reports on the retained accepted stand-in candidate. The pages correctly explain that the generic coverage floors do not require two recommendations for Ada or an approval of expense 102, and do not preserve seed facts. The recorded result files confirm **eight Codex runs, all accepted on attempt 1, and no Claude recording**.

I checked the 007 and 008 records against their cited text and JSON evidence: their listed SHA-256s match; the installed receipts report 61/71 BookRec and 46/57 Expense offline/native passes, 137/137 corpus cases, and 16 successful child commands. These are retained author-run results, **not tests I reran**. I inspected four cited desktop/mobile screenshots and did not run native execution, a docs build, or a broad suite. The seven refactoring failures reported on clean main remain a separately classified inherited issue.

The new helper is RF7-allowlisted, and the fresh-wheel receipt’s 123-resource inventory includes it with a source-matching digest. I found no wheel resource omission or need for a new runtime module home. The evolution finding is an incomplete declared-project check, not a refactoring request.

### SHA-256 identity

All paths below are relative to `<checkout>`.

| File | SHA-256 |
|---|---|
| `docs/pyrel-apps.md` | `832a7bd79f38d8efa1cf5b4156a8e1d714c69d19f0336bfc182254e777f0898e` |
| `docs/bookrec/07-native.md` | `d80b39a4fe5de8c6d79635f93bdd863241518402b8ed7d6014244b4e90bc8ee8` |
| `docs/expense/04-native.md` | `8df41bf5251bef487d20a073516cb41fe30392bb85062b4723d2b831ab9f0d88` |
| `docs/agents/index.md` | `d212257ee6dbde0443bd71328d59f16f6d650eebe9f6706a916f052a72714869` |
| `docs/agents/dev-session.md` | `e266027e1014d90ba17f66fe8bd986ef323773a48b1234ed3d950` |
| `docs/agents/recorded-sessions.md` | `c40ae2b90e55d1e14071cbcef2fff54da1343c0ae331663dcc14b38ebed3d950` |
| `docs/agents/model-from-text.md` | `71e218b372b45be5db4e4debf1d9671be2ea3a216518686d0570168aa932afca` |
| `docs/agents/codegen-conformance.md` | `880376d011149753da5852790b23463c8d26d2a1aad2c52a94451a5f1ab41c8c` |
| `docs/agents/evolve.md` | `6c51cb6d3bef2322242dd131dff7aca7acde86ce157d2652166349aabf0602a7` |
| `src/gnd/examples/expense/prepare_meal_cap.py` | `1200d95bdce81f462a8ea4be8e5cbdfccf99b56d12232f940798490eb05dfba2` |
| `tests/test_pyrel_learning_path.py` | `9bc1fb81c9145023383e8c6a0e0d96d1aba2870a5ff0193fb0592e630e34f296` |
| `tests/test_pyrel_applications_install.py` | `7da32fab177a10982e7ccff69a2dd50b1c85c671828d5b0d824f6ac63a19a08c` |
| `tests/test_rf7_structure.py` | `3d00c3fcaca8548bf932194567b1c4f8089f2bcecacc67c7efbf6866a4ad2a8f` |
| `tools/accept_pyrel_applications_install.py` | `4be1160d1be7109cf4e12070d6f5131fc5ed67c24ed38fa50516704bc942894f` |
| `zensical.toml` | `d501feebf40b6e2e75a1a4fe7d8f1b04f68789661c42f50ededfcef26d59bb4b` |

Planning identities: PL5 spec `6849374ac2befaa195e3ed18a2101103f41d317ca16b818068a897fd9fa23d83`; whole plan `f4e2edcba67675f4b4a2053a918a8275f69940c2ed7326bd383c4e59e51d45fa`; milestone README `84c68513fd4e705115cfeabfa92f24e819fe5133d4b6ed01043037f0625c8853`; records 007 and 008 `97c76c1d5d11462729deb77f612966eacf28981b2c07c50b1fdb821d8bf2a6b4` and `3519710592234ea1b09d92f7e5bba69b15ca77c2837b151cc5ae01f81e585002`. The cited PL5 source-identity and PL6 receipt files hash to `41c35fba179509d0e47cba3608f39105aacc9748f848a4ada8c734ffd96f40ba` and `6823a52ddc23195e71809df92d3edb288cfb4e63f9891f3bd3d2c0d77093fca9`.
