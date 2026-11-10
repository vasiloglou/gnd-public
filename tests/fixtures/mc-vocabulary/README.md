# Model-composition evolution source corpus

A tool ships vocabulary-v1.orm.json. The project owns project_no_loops and project_owner_required as inline attachments. The clean population satisfies both; the cyclic population breaks the ring.

Vocabulary v2 is a new file. It removes component_uses_component and supplies component_depends_on_component with dependent/dependency roles. The project continues loading against v1 until it explicitly changes its pin. A re-pin alone loses the ring's host while the ownership rule stays applicable. The combined proposal changes the pin, deletes the old ring attachment and appends the same ring on the replacement host. Its candidate retains the owner attachment first, matching the declared prune/append order. The updated facts satisfy both rules.

flattened-negative.orm.json is independently standalone-valid. Its proposal deliberately fails authored replay equality; it must not be rejected merely as an invalid model. Future source removal, fallback, dependency-race, linked-project and writer branches are separately narrated in answers.json. The answer key is separate from this entry point so a blind reader can receive inputs without expected results.

The three proposal files are manually authored new-grammar inputs, using the existing canonical JSON producer only for content identities. They have not been accepted by new product code: MC3 does not exist at authorship. Source-state validation/check controls use the existing MC1/MC2 loader to establish reachability, not to derive future evolution answers. Later hostile/implementation successors may add data without changing the gated meanings.
