"""Current source-site guard successors; no historical proof execution claim."""
from dataclasses import replace

import pytest
from public_site_census import audit, capture_sites, inventory
from support.repository import REPO_ROOT as ROOT

from gnd import semantic_registry as registry


@pytest.fixture(scope="module")
def static_sites():
    return inventory(ROOT)


def test_static_inventory_excludes_installed_assurance_copies(static_sites):
    assert any(site.path == "src/gnd/report.py" for site in static_sites)
    assert not any(
        site.path.startswith("src/gnd/_assurance_evidence/") for site in static_sites
    )


def test_transition_assurance_delegation_is_an_exact_static_site(static_sites):
    path = "src/gnd/report.py"
    source = (ROOT / path).read_text()
    selector = '_assurance_surface="transition"'
    assert source.count(selector) == 1
    changed = inventory(
        ROOT,
        replacements={path: source.replace(selector, '_assurance_surface="snapshot"')},
    )
    owner = "gnd.report.build_transition_payload"
    assert len([site for site in static_sites if site.owner == owner]) == len(
        [site for site in changed if site.owner == owner]
    ) + 1


def test_a_runtime_producer_cannot_hide_behind_an_alias(static_sites):
    namespace = {"__name__": "gnd.semantic_adapter", "emit": registry.record_branch}
    exec(  # noqa: S102 -- fixed source mutation, no file writes
        'def disguised_producer():\n    emit("applicability:adapter:n-a:non-finite-number")\n',
        namespace,
    )
    with (
        capture_sites(ROOT, static_sites, registry.REGISTRY),
        pytest.raises(AssertionError, match="no producer owner frame"),
    ):
        namespace["disguised_producer"]()


@pytest.fixture(scope="module")
def owned_sites(static_sites):
    """One real current adapter producer; no complete historical census claim."""
    from gnd.semantic_adapter import _refusal

    identity = "applicability:adapter:n-a:non-finite-number"
    with capture_sites(ROOT, static_sites, registry.REGISTRY) as trace:
        refusal = _refusal("owned-current-site", "non-finite-number")
    assert (refusal.location, refusal.reason) == ("owned-current-site", "non-finite-number")
    assert set(trace.observed) == {identity}
    assert len(trace.observed[identity]) == 1
    site = next(iter(trace.observed[identity]))
    assert site.owner == "gnd.semantic_adapter._refusal"
    assert site in static_sites
    return trace.observed


def test_unused_registry_row_is_detected(static_sites, owned_sites):
    extra = replace(registry.REGISTRY[0], scope_id="snapshot:unused:n-a:clean")
    findings = audit(static_sites, owned_sites, (*registry.REGISTRY, extra))
    assert "row-site-count:snapshot:unused:n-a:clean:0" in findings


def test_an_unexecuted_duplicate_site_is_detected(static_sites, owned_sites):
    path = "src/gnd/semantic_adapter.py"
    source = (ROOT / path).read_text()
    before = '    record_branch("applicability:adapter:n-a:" + reason, outcome="refused")'
    assert source.count(before) == 1
    after = before + "\n    if False:\n    " + before
    changed = inventory(ROOT, replacements={path: source.replace(before, after)})
    # Compare static locations with an observation mapped to unchanged source
    # expressions. The inserted branch is deliberately never executed.
    old_adapter = next(
        site for site in static_sites if site.owner == "gnd.semantic_adapter._refusal"
    )
    new_adapter = [site for site in changed if site.owner == old_adapter.owner]
    assert len(new_adapter) == 2
    added = next(site for site in new_adapter if site.line != old_adapter.line)
    findings = audit(changed, owned_sites, registry.REGISTRY)
    assert f"unexecuted-site:{added.path}:{added.line}" in findings


def test_duplicate_execution_of_one_id_at_two_sites_is_detected(static_sites, owned_sites):
    identity, locations = next(iter(owned_sites.items()))
    original = next(iter(locations))
    other = next(site for site in static_sites if site != original)
    changed = {**owned_sites, identity: {original, other}}
    assert f"row-site-count:{identity}:2" in audit(static_sites, changed, registry.REGISTRY)


def test_an_unregistered_producer_owner_is_detected(static_sites, owned_sites):
    path = "src/gnd/semantic_adapter.py"
    source = (
        (ROOT / path).read_text()
        + '\n\ndef unexpected_producer():\n    record_branch("applicability:adapter:n-a:non-finite-number")\n'
    )
    changed = inventory(ROOT, replacements={path: source})
    assert any(
        item.startswith("unregistered-owner:gnd.semantic_adapter.unexpected_producer:")
        for item in audit(changed, owned_sites, registry.REGISTRY)
    )
