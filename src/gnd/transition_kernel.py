"""Pure transition decisions shared by production and the Phase 4 proof.

This module deliberately contains only total, side-effect-free functions over
primitive values.  Production owns the extraction of those values from the
validated model/populations; the formal lane verifies a contract-carrying copy
whose executable AST must erase back to this whole module.
"""


def modality_verdict(alethic: bool) -> str:
    return "fail" if alethic else "warning"


def transition_band(has_fail: bool, has_unchecked: bool, has_vacuous: bool) -> int:
    if has_fail:
        return 1
    if has_unchecked:
        return 4
    if has_vacuous:
        return 2
    return 0


def effect_membership(was_present: bool, retracted: bool, asserted: bool) -> bool:
    return (was_present and not retracted) or asserted


def required_fact_verdict(holds: bool, alethic: bool) -> str:
    if holds:
        return "pass"
    return modality_verdict(alethic)


def precondition_verdict(holds: bool, alethic: bool) -> str:
    return required_fact_verdict(holds, alethic)


def retract_target_verdict(has_target: bool) -> str:
    return required_fact_verdict(has_target, True)


def assert_redundant_verdict(was_present: bool) -> str:
    return required_fact_verdict(not was_present, False)


def freshness_verdict(preexisting: bool, created_earlier: bool) -> str:
    if preexisting or created_earlier:
        return "fail"
    return "pass"


def comparison_dispatch(operator: str, new_value: int, old_value: int) -> bool:
    if operator == "<":
        return new_value < old_value
    if operator == "<=":
        return new_value <= old_value
    if operator == "=":
        return new_value == old_value
    if operator == ">=":
        return new_value >= old_value
    if operator == ">":
        return new_value > old_value
    return new_value != old_value


def fact_type_touched(asserted: bool, retracted: bool) -> bool:
    return asserted or retracted


def dynamic_verdict(
    touched: bool,
    functional: bool,
    old_present: bool,
    new_present: bool,
    comparison_holds: bool,
    alethic: bool,
) -> str:
    if not touched:
        return "pass"
    if not functional:
        return "unchecked"
    if not old_present or not new_present:
        return "vacuous"
    if comparison_holds:
        return "pass"
    return modality_verdict(alethic)


def frame_modality(any_deontic_toucher: bool) -> str:
    return "deontic" if any_deontic_toucher else "alethic"


def frame_verdict(has_delta: bool, alethic: bool) -> str:
    if not has_delta:
        return "pass"
    return modality_verdict(alethic)


def frame_assert_verdict(has_delta: bool, alethic: bool) -> str:
    return frame_verdict(has_delta, alethic)


def frame_retract_verdict(has_delta: bool, alethic: bool) -> str:
    return frame_verdict(has_delta, alethic)


def intermediate_verdict(loadable: bool) -> str:
    return "pass" if loadable else "unchecked"


def compiled_subset_verdict(compiled: bool, covered: bool, violated: bool, alethic: bool) -> str:
    if not compiled or not covered or not violated:
        return "pass"
    return modality_verdict(alethic)


def report_evaluated(evaluated: bool) -> bool:
    return evaluated


def report_family_presence(evaluated: bool, supplied: bool) -> bool:
    return evaluated and supplied


def report_steps_present(evaluated: bool, supplied: bool) -> bool:
    return evaluated and supplied
