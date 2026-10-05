"""Reproductions of RF2 independent-review findings."""
from pathlib import Path

import pytest
import test_measure_offline as scans
import test_rf2_helpers as controls
from test_measure_offline import MODEL

from gnd import cli
from gnd.synth import provenance


@pytest.mark.parametrize("consumer", ["synth", "measure"])
def test_cli_uses_new_provenance_lookup(consumer, tmp_path, monkeypatch, capsys):
    corpus = tmp_path / "corpus"
    if consumer == "measure":
        assert cli.main(["synth", str(MODEL), "--out", str(corpus),
                         "--seed", "7", "--seeds", "3", "--format", "json"]) == 0
    marker = RuntimeError("RF2 new provenance lookup reached")
    def refuse(_):
        raise marker
    monkeypatch.setattr(provenance, "validated_model_sha256", refuse)
    args = (["synth", str(MODEL), "--out", str(corpus), "--seed", "7",
             "--seeds", "3", "--format", "json"] if consumer == "synth" else
            ["measure", str(MODEL), "--populations", str(corpus), "--format", "json"])
    if consumer == "synth":
        assert cli.main(args) == 74
        assert "RF2 new provenance lookup reached" in capsys.readouterr().out
    else:
        with pytest.raises(RuntimeError, match="RF2 new provenance lookup reached"):
            cli.main(args)


def test_scan_scope_control_rejects_missing_home(monkeypatch):
    original = scans._module_path
    monkeypatch.setattr(scans, "_module_path", lambda name: None if name == "gnd.artifacts" else original(name))
    with pytest.raises(AssertionError):
        controls.test_affected_scan_scopes_cover_moved_definitions()


@pytest.mark.parametrize("declaration", ["_EXIT_EXTRA: int = 19", "EXIT_EXTRA = 18 + 1",
                                          "NEW_CODE = 19\nEXIT_EXTRA = NEW_CODE"])
def test_exit_guard_rejects_other_assignment_forms(monkeypatch, declaration):
    original = Path.read_text
    def changed(path, *args, **kwargs):
        source = original(path, *args, **kwargs)
        if path == controls.ROOT / "src/gnd/model.py":
            source += "\n" + declaration + "\n"
        return source
    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(AssertionError):
        controls.test_all_exit_allocations_have_one_home_and_old_aliases()


def test_real_closure_guard_rejects_network_import_in_new_home(monkeypatch):
    original = Path.read_text
    def changed(path, *args, **kwargs):
        source = original(path, *args, **kwargs)
        if path == controls.ROOT / "src/gnd/artifacts.py":
            source += "\nimport socket\n"
        return source
    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(AssertionError, match="artifacts.py"):
        scans.test_no_network_library_is_reachable_from_the_measure_lane()
