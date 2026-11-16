# Replay a semantic revision

Run the reading fixture and migrate its evidence into a new, separately
identified release directory.

```sh
python -m gnd.examples.literature.reading run --out reading-run
python -m gnd.examples.literature.revision run reading-run --out revision-run
python -m gnd.examples.literature.revision status revision-run/after
python -m gnd.examples.literature.revision replay revision-run
python -m gnd.examples.literature.revision replay revision-run --snapshot before
```

The whale fixture separates two pairs of methods that share spellings.
Three cross-sense ancestry paths disappear and two unaffected paths remain.
The occurrence map uses the source ID, fact type and source fact index
from the verified composition record. A source-free WHAM mention keeps
both candidate senses on the rereading list. The vocabulary change also
invalidates the selected scoped absence while preserving unrelated coverage.

The original and changed snapshots each carry a `manifest.json` with the
release policy SHA-256, snapshot name and exact artifact path-and-digest
roster. The separately selected policy lists every required artifact kind
and upstream path. The after manifest also pins the prior composition and
population used by migration. `status` validates its policy before reading
the named snapshot, then reports changed files, stale prior inputs and their
transitive dependents. Use
`--policy PATH --policy-sha256 DIGEST` for a separately trusted policy. A
missing artifact, invalid roster or stale dependency exits 3. `replay`
reruns the public routes over captured inputs and compares both outputs
with the retained release. The original snapshot can replay independently.
Each snapshot retains the raw reading sources, vocabulary and saved assertion
review inputs. The workflow independently authenticates those inputs before
use. A saved assertion review applies to its pinned interpretation policy.

Public check confirms the assertions' anchored roles. The check reports
exit 4 because the assertion population contains no declared derivation.
Witness and replay establish the five requested lineage outcomes separately.
The revision also exercises a public evolve transaction. A pinned preview
authorizes the exact non-additive fixture transition. The old assertion
review becomes stale even though its role values and source span stay the
same. A separately captured review binds the revised definition. A small
unchanged-vocabulary fixture exercises rule-edition comparison.

The synthetic corroborating source supplies a second independent witness
for VampNet's ancestry from DMD. Its source, occurrence, review and
witness identities are distinct from the original source. Both support
records bind the rule and verified resolution editions. Either certificate
can replay from its own source when the other source is unavailable.
