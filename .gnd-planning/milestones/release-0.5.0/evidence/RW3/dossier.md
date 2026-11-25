# GND 0.5.0 publication hand-over

Prepared on 2026-11-25. This page hands the accepted candidate to the owner.
It publishes nothing, and no command on it was run except where it says so.
The procedure is [docs/releasing.md](../../../../../docs/releasing.md); this
page adds no rule to it.

## The candidate

The [RW2 record](../../004-phase-RW2.md) binds the accepted candidate to main
commit `85d076ba384e67b1f992cfd6b9a596ca01b3d4e7`. The retained directory, on
the planning machine and on beast-3, is
`~/gnd-release/0.5.0/85d076ba/candidate/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `release/get_nick_done-0.5.0-py3-none-any.whl` | 3,578,846 | `c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49` |
| `release/get_nick_done-0.5.0.tar.gz` | 2,673,541 | `9576a57d735d54aa7cd565b52670f11feb6bf659dd75da40a868942168e8a8c0` |
| `comparison/get_nick_done-0.5.0-py3-none-any.whl` | 3,578,846 | `c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49` |

The comparison wheel was built from the sdist and has the wheel's digest. It
stays in the receipt and is not uploaded.

## Results

- **Two builds, one result.** The first build ran on macOS 26.6.2 arm64 with
  Python 3.11.15 and uv 0.10.10; an independent build on beast-3 (macOS
  27.0.1 arm64, Python 3.11.18, uv 0.10.10) gave the same three digests.
- **Installed acceptance** on beast-3: 33 passed, for the release wheel and
  the comparison wheel, with the source checkout denied. `uvx` printed
  `gnd 0.5.0`.
- **Default lane** at the candidate commit, six shards on beast-3 with
  Python 3.13.18 and uv 0.13.7: 22,020 passed, no failure, and the two known
  `tests/test_public_optional.py` setup errors.
- **Opt-in lanes** at the candidate commit, on the owner's selections:
  `pyrel_oracle` 345 passed; `ossie_oracle` 91 passed with its consumer test
  deselected.
- **Main since the candidate.** At the [snapshot](pre-publication-state.txt)
  main was `44d866df`; `src`, `PYPI.md`, `pyproject.toml`, `LICENSE` and
  `NOTICE`, the only paths the sdist holds, do not differ from `85d076ba`.
  RW3 changes `docs/releasing.md`, `tools/release_text.py` and one test file,
  none of which is in the package.

## What was not measured

- Any profile but macOS 27.0.1 arm64 with Python 3.11.18 and uv 0.10.10.
  Ubuntu, Windows, the workflow's prepare job, Trusted Publishing and
  TestPyPI were outside the run.
- The files PyPI will serve, and a fresh install from the index. Both are
  act 3 below.
- A RelationalAI engine: no exported `--rules lqp` program was run on one,
  and the Ossie oracle's consumer test was not run.
- Whether the Ossie oracle root used at the freeze is the one the Ossie
  milestone used. It held both upstream repositories at the pinned commits
  and passed the lane's own pin check.
- From an installed wheel, by the RW2 spec's coverage table:
  - the PyRel exactness refusals, beyond the models the probe exports;
  - an include path that cannot be encoded;
  - the checker's speed on large vocabularies, one parse per load, CRLF
    block scalars and the model index's key order;
  - `narrow_proposal` and `gnd evolve summary`;
  - a live producer run of the reading example;
  - the frontmatter reader, and every documentation page;
  - the Ossie size options beyond one refusal, and binding refusals by rule.
  The default lane covers each of these from the source tree.
- The notes' completeness beyond the reconciliation table of RW1 and its
  one reviewer.
- External acceptance of the Ossie relational files by the reporter, and a
  review of the repairs made after that milestone's close review. Both are
  that milestone's stated residuals.

## The remote state

The [snapshot](pre-publication-state.txt) was taken on 2026-11-25 at
17:27 UTC with read-only commands. Against the plan's baseline (W4):

| Item | Baseline | Snapshot |
|---|---|---|
| Visibility, default branch | public, `main` | the same |
| Tags | `v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.3.1`, `v0.4.0` with the peeled commits W4 lists | the same five, the same commits; no `v0.5.0` |
| GitHub releases | four; 0.3.1 has none | the same four |
| Environments | `github-pages` only | the same |
| `release.yml` runs | none | none |
| PyPI | 0.1.0 to 0.4.0 | the same; the 0.5.0 endpoint answers 404 |
| `.github` since `v0.4.0` | -- | no change |

Take it again immediately before the upload.

## Owner acts

Each act runs only on the owner's explicit request at that time. The order
is the plan's (§11): the tag and the GitHub release come after the served
files are compared, so a failed comparison stops before anything is
announced.

1. **Before anything: the owner's own checks (RC-07).** Confirm that the
   PyPI account that will upload owns `get-nick-done`, and review the
   repository's content and history for anything that should not be public.
   No tool here can do either. Say that both are done, with the date; the
   publication record quotes that statement. Then verify the files and that
   the version is still free:

   ```sh
   cd ~/gnd-release/0.5.0/85d076ba/candidate
   shasum -a 256 -c SHA256SUMS
   test "$(cat SOURCE_COMMIT)" = 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7
   curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/get-nick-done/0.5.0/json
   ```

   Expected: three `OK` lines and `404`. Also check that main has not changed
   a shipped file since the candidate:

   ```sh
   git fetch origin main
   git diff --stat 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7 origin/main -- src PYPI.md pyproject.toml LICENSE NOTICE
   ```

   Expected: no output. If it prints a file, the candidate is stale: stop,
   and RW2 builds a new one.

2. **Upload** the wheel and the sdist with the owner's PyPI token. The token
   is the owner's; it is typed by the owner and is not given to an agent.
   Receipt: the upload output with its date.

   ```sh
   cd ~/gnd-release/0.5.0/85d076ba/candidate
   uvx twine upload release/get_nick_done-0.5.0-py3-none-any.whl release/get_nick_done-0.5.0.tar.gz
   ```

3. **Compare the served files and install from the index.** These are the
   commands of the workflow step "Compare served PyPI files and exercise a
   fresh index install", run by hand as `docs/releasing.md` says. Receipt:
   their output. On a mismatch or a failure, stop: no tag, no release, and
   the incident procedure of `docs/releasing.md` applies.

   ```sh
   cd ~/gnd-release/0.5.0/85d076ba
   python3 - <<'PYTHON'
   import hashlib, json, pathlib, urllib.request
   release = pathlib.Path('candidate/release')
   with urllib.request.urlopen('https://pypi.org/pypi/get-nick-done/0.5.0/json', timeout=60) as response:
       served = {item['filename']: item for item in json.load(response)['urls']}
   for artifact in sorted(release.iterdir()):
       expected = hashlib.sha256(artifact.read_bytes()).hexdigest()
       item = served[artifact.name]
       assert item['digests']['sha256'] == expected, artifact.name
       with urllib.request.urlopen(item['url'], timeout=60) as response:
           assert hashlib.sha256(response.read()).hexdigest() == expected, artifact.name
       print('served file matches:', artifact.name, expected)
   PYTHON
   scratch=$(mktemp -d) && cd "$scratch"
   uv venv installed
   uv pip install --python installed/bin/python --index-url https://pypi.org/simple "get-nick-done==0.5.0"
   installed/bin/gnd --version
   installed/bin/python -I - <<'PYTHON'
   from importlib.resources import files
   from gnd import api
   root = files('gnd') / 'examples' / 'dispatch'
   for name, expected in [('seed.pop.json', 1), ('repaired.pop.json', 0)]:
       result = api.check(root / 'model.orm.json', root / name, admission=True)
       assert result['exit_code'] == expected, result
   print('Fresh PyPI install rejected the invalid plan and accepted its repair.')
   PYTHON
   ```

4. **Tag** the accepted source, from a repository checkout. Receipt: the
   peeled remote ref.

   ```sh
   (
   set -e
   git fetch origin main
   git tag -a v0.5.0 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7 -m 'get-nick-done 0.5.0'
   git push origin refs/tags/v0.5.0
   peeled=$(git ls-remote --tags origin 'refs/tags/v0.5.0^{}' | awk '{print $1}')
   test "$peeled" = 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7
   printf '%s\n' "$peeled"
   )
   ```

5. **GitHub release** with the two files and their checksums (RW-D9). The
   [release body](github-release-notes.md) is a draft for the owner to edit.
   Receipt: the release URL and the downloaded attachment check.

   ```sh
   (
   set -e
   repo=$(git rev-parse --show-toplevel)
   release_notes_file="$repo/.gnd-planning/milestones/release-0.5.0/evidence/RW3/github-release-notes.md"
   test -r "$release_notes_file"
   cd ~/gnd-release/0.5.0/85d076ba/candidate
   (cd release && shasum -a 256 get_nick_done-0.5.0-py3-none-any.whl get_nick_done-0.5.0.tar.gz) > SHA256SUMS.txt
   gh release create v0.5.0 --verify-tag --repo vasiloglou/gnd-public --title 'GND v0.5.0' --notes-file "$release_notes_file" release/get_nick_done-0.5.0-py3-none-any.whl release/get_nick_done-0.5.0.tar.gz SHA256SUMS.txt
   attachments=$(mktemp -d)
   gh release download v0.5.0 --repo vasiloglou/gnd-public --dir "$attachments"
   cmp SHA256SUMS.txt "$attachments/SHA256SUMS.txt"
   (cd "$attachments" && shasum -a 256 -c SHA256SUMS.txt)
   )
   ```

6. **The pages pull request**, on a topic branch of a checkout that holds
   this folder. The date is the one on the upload receipt.

   ```sh
   (
   set -e
   cd "$(git rev-parse --show-toplevel)"
   supplemental_patch="$PWD/.gnd-planning/milestones/release-0.5.0/evidence/RW3/post-publication-supplement.patch"
   test -r "$supplemental_patch"
   printf 'Publication date from the upload receipt (YYYY-MM-DD): '
   IFS= read -r publication_date
   publish_exit=0
   uv run python tools/release_text.py publish --date "$publication_date" --built 85d076ba --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10' || publish_exit=$?
   test "$publish_exit" = 1
   git apply --check "$supplemental_patch"
   git apply "$supplemental_patch"
   uv run python tools/release_text.py check
   uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py --tb=short
   uv run --group docs zensical build --strict
   uv run python tools/check_docs.py site
   )
   ```

   The helper exits 1 at first because it leaves seven lines for a person;
   the [tool-only preview](tool-only-preview.txt) lists them and the
   [supplemental patch](post-publication-supplement.patch) rewrites them.
   The [rehearsal](scratch-verification.txt) ran exactly this, with the
   rehearsal date 2026-11-25, in a disposable clone of the RW3 commit: the
   patch applied, `check` exited 0, the four release test files had 97
   passed, and the docs build and link check exited 0. If main's pages have
   changed by then, `git apply --check` fails; reconcile the patch by hand
   against the list.

   One of the seven lines is a choice (RW3 spec D3). The literature page
   says its results come from "the packaged literature example in GND 0.4.0".
   The patch drops the version, because the page now holds results 0.4.0
   does not ship and this phase did not check that every result comes from
   0.5.0. Name 0.5.0 instead if that is checked.

7. **Issue comments**, if the owner wants them (RW-D10). The plan names
   issues 214 and 217. The 0.5.0 notes also link 193, 215, 216, 218, 221,
   222, 226, 227 and 228, and the Ossie milestone filed 276 to 278 for its
   three requests. No text is drafted here.

A numbered publication record then binds the receipts of acts 1 to 7.
