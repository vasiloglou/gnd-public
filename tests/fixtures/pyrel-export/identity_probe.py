"""Test instrument, injected into an emitted program before its main guard.

Membership counts, not global equality of backend surrogate IDs. The control
probe deliberately aliases the two concepts to prove this assertion can fail.
"""


def assert_identity_memberships(pairs):
    assert len(pairs) == 2, "expected two declared domain entity concepts"
    assert pairs[0][1] is not pairs[1][1], "unrelated types share one concept"
    counts = []
    for model, concept in pairs:
        assert concept._identify_by, "entity has no identify_by reference"
        frame = model.select(concept).to_df()
        counts.append(len(frame.index))
    assert sorted(counts) == [1, 2], f"wrong concept memberships: {counts}"


def install_identity_probe(entry_point):
    from relationalai.semantics import Model

    concepts = []
    original = Model.Concept

    def capture(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        # Lazy backend imports also declare concepts on Library subclasses.
        # Observe user Models only; their identify_by requirement remains below.
        if type(self) is Model:
            concepts.append((self, result))
        return result

    Model.Concept = capture

    def checked(argv=None):
        result = entry_point(argv)
        assert result == 0, f"program failed before identity observation: {result}"
        assert_identity_memberships(concepts)
        return result

    return checked
