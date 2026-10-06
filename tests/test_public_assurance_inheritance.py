from gnd.assurance import inheritance as assurance_inheritance


def test_phase3_runtime_input_rebinding_is_metadata_but_input_name_is_semantic():
    row = {'case_id': 'P3-0055', 'consumer': 'build_check_payload', 'scope_id': 'scope'}

    def output(root, model='P2-001.model.orm.yaml'):
        return {**row, 'consumer_output': {'outcome': 'accepted'}, 'semantic_observation': {'model': f'{root}/runtime-inputs/{model}', 'population': f'{root}/runtime-inputs/P2-001.population.json', 'semantic_decision': 'accept'}}
    historical = assurance_inheritance._phase3_output(lambda _: output('historical-evidence'), {**row, 'output_path': 'old', 'output_sha256': '0'})
    rebound = assurance_inheritance._phase3_output(lambda _: output('fresh-corpus-work'), {**row, 'output_path': 'new', 'output_sha256': '1'})
    changed_input = assurance_inheritance._phase3_output(lambda _: output('fresh-corpus-work', 'P2-999.model.orm.yaml'), {**row, 'output_path': 'changed', 'output_sha256': '2'})
    assert rebound == historical
    assert changed_input != historical
