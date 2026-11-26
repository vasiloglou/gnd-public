

from __future__ import annotations


def test_every_version_dispatcher_in_this_lane_covers_both_entry_points() -> None:













    import inspect

    from gnd.exp import session_contract, session_eval, session_records, session_store

    shared_json_dispatcher = vars(session_eval.SessionEvidenceJson)["model_validate_json"]
    unpaired: list[str] = []
    for module in (session_contract, session_eval, session_store, session_records):
        for name, obj in vars(module).items():
            if not inspect.isclass(obj) or getattr(obj, "__module__", "") != module.__name__:
                continue
            own = vars(obj)
            if "model_validate" not in own:
                continue
            json_dispatcher = inspect.getattr_static(obj, "model_validate_json", None)
            if "model_validate_json" not in own and json_dispatcher is not shared_json_dispatcher:
                unpaired.append(f"{module.__name__}.{name}")
    assert unpaired == [], (
        "these classes dispatch on schema_version in model_validate but have neither a "
        f"local JSON dispatcher nor the shared evidence JSON dispatcher: {unpaired}"
    )
































