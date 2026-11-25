"""Observed-call guard shared by the two witness fixture families."""

def no_evaluator(monkeypatch) -> None:
    from gnd import checker, extensions, terms

    def forbidden(*args, **kwargs):
        raise AssertionError("replay invoked a production evaluator/comparison primitive")

    for name in (
        "check",
        "structured_extension_view",
        "structured_extension_facts",
        "_python_extension_calculator",
        "_exact_extension_calculator",
        "_evaluate_stratified_extensions",
        "evaluate_derivations_legacy",
        "_PHASE3_LEGACY_EVALUATE_DERIVATIONS",
        "_evaluate_derivations",
        "_evaluate_derivations_dispatch",
        "_compare",
        "_typed_comparison_values",
    ):
        if hasattr(checker, name):
            monkeypatch.setattr(checker, name, forbidden)
        for target in (name, name.removeprefix("_")):
            if hasattr(extensions, target):
                monkeypatch.setattr(extensions, target, forbidden)
    for name in ("evaluate_term", "guarded_operand_evaluator", "materialize_scalar"):
        if hasattr(terms, name):
            monkeypatch.setattr(terms, name, forbidden)
        if hasattr(extensions, name):
            monkeypatch.setattr(extensions, name, forbidden)
