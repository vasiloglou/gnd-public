# OS6 local contribution candidate

The [OS6 spec](024-OS6-spec-gate.md) binds the contribution scope.
The local branch `codex/convert-ontology-requires` starts at the pinned
Apache Ossie Converters commit `83ddc294c8840f5f497a2bdbec2348a128fc2254`.
The initial candidate is
`a39bcc2706857753ea0a92c2fd92b3131f6830a3`. It prepares scoped
requirements through the upstream formula visitor and adds a test for
concept, relationship and ontology scopes. The source and test files
compile. The contribution's emitted behavior awaits the selected gates.

The [replay script](evidence/OS6/replay.py) uses the OS4 instrument against
a named local checkout. It leaves the original report intact, attempts
all 38 eligible exports, and isolates the eight requires expressions
from the reviewed formula corpus. The replay will record the branch
commit, each emitted requirement and each observed limitation.

The upstream pytest and snapshot plugin wheels were checked against
the upstream lockfile and installed in a separate local test directory.
The pinned RelationalAI 1.39.0 SDK and offline test configuration are
available. The suite and replay await the owner's opt-in selection.
The local branch is prepared for testing before its independent review.
