# BookRec tutorial resources

These are independently authored synthetic tutorial inputs for the public GND
package. No real reader, customer catalogue, historical agent session or private
application is included. Start at the documentation's BookRec chapter 1.

- `model.orm.yaml`: version-1 domain with unread/age rules and advisory genre fit.
- `seed.population.json`: accepted baseline; the other named populations isolate
  already-read, adult-for-minor and genre-warning outcomes.
- `extension/bookrec/`: human-authored deterministic library and CLI. GND's
  scaffold does not generate this application algorithm.
- `architecture.contract.yaml`: bounded static structure and executable smoke
  declarations for the generated project.
- `strict.orm.yaml` / `genre-proposal.json`: exact modify-only evolution from the
  baseline model to mandatory genre fit. The fixed audit date identifies a
  prepared tutorial request, not a claim that a reader performed a past run.
- `complete.orm.yaml` / `complete.population.json`: version-2 checkpoint adding
  derived blocked/eligible facts and all-eligible completeness.

The same model identifier is retained to let a population be evaluated under
changed rules. Model byte digests distinguish the rules used by each check.
The complete checkpoint is a separately supplied exercise model, not a claim
that the genre proposal also added its derivations.

The evolution proposal declares no linked projects. Chapter 6 checks generated
project conformance explicitly after publication. A real workflow should declare
all selected linked projects and their tracked rosters when authoring a proposal.

The default GND backend publishes only output with checker exit 0 and
`acceptance_ready: true`.
It preserves any existing output and removes rejected temporary candidates.
Its API report uses `unredacted=True` because all tutorial values are synthetic;
use an explicit disclosure policy for an application's real data. A checker pass
means conformity to the supplied rules. It does not measure ranking quality.

The optional native backend uses `--backend pyrel --pyrel-python
/absolute/pinned/python`, with the isolated PyRel 1.30.1/DuckDB 1.5.5 interpreter.
It runs the developer-owned `bookrec/native_query.py` to propose native eligible
pairs, then checks the exact candidate in a separate exported PyRel process.
Only a complete, bound `applications-v1` accepted report publishes output.
The GND interpreter remains separate; missing native dependencies do not fall
back to the default backend. Native limits are 1 through 100.

For `recommend`, the application owns recommendation rows and preserves other
asserted source facts. `complete` uses the complete model's native computed
blocked/eligible relations to generate claims and all preferred recommendations.
Supplied derived claims are refreshed in the proposed candidate. Query and
checker processes have separate temporary/build directories; checked captured
bytes publish only to a fresh output. These are finite synthetic snapshot checks,
not ranking-quality or actor-permission claims.
