from __future__ import annotations

from support.v62_phase2_corpus import population, write_model

from gnd import transition as transition_module
from gnd.model import load_model
from gnd.population import load_population


def test_operation_scoped_ids_do_not_hide_another_operations_pre_failure(tmp_path) -> None:

    def mutate(doc):
        annotate = next(row for row in doc['operations'] if row['id'] == 'annotate')
        annotate['preconditions'] = [{'id': 'must_be_ready', 'require': [{'fact_type': 'evidence', 'bind': {'ticket': '$ticket'}}], 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'provenance': {'user_quote': 'Annotation requires evidence.'}}]
    model_path = write_model(tmp_path, mutate)
    model = load_model(model_path)
    pre_doc = population('pre_open').read_text(encoding='utf-8').replace('  note: []', '  note:\n    - { ticket: "SECRET-TICKET-314159" }')
    pre_path = tmp_path / 'pre.pop.yaml'
    pre_path.write_text(pre_doc, encoding='utf-8')
    pre = load_population(pre_path, model=model)
    verdicts = transition_module._compiled_verdicts_for_dynamic_walk(model, pre)
    assert any(row.verdict == 'fail' and 'operations[id=annotate]' in row.locator for row in verdicts)
