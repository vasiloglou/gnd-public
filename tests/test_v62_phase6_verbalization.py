from gnd.model_verbalization import render_model_verbalization


def test_exists_consequent_verbalizes_joint_assignment_and_exact_terms(tmp_path):
    from support.v62_phase6_corpus import loaded_case
    model, *_ = loaded_case(tmp_path)
    text = render_model_verbalization(model)
    assert 'there exists a joint assignment such that' in text
    assert 'neighbor_seen(neighbor = $neighbor, sample = $sample) holds' in text
    assert 'mod($pci, 30) equals mod($neighbor_pci, $modulus)' in text
