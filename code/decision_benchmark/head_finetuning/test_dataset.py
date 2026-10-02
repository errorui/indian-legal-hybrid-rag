import json
from pathlib import Path
import pytest
from build_dataset import build, validate, input_text


def test_balanced_groups_and_evaluation_exclusion():
    rows,sources,evaluation=build()
    assert len(rows)==200 and len(sources)==60
    assert sum(r['split']=='train' for r in rows)==160
    assert sum(r['split']=='validation' for r in rows)==40
    assert validate(rows,evaluation) is rows


def test_counterfactual_pairs_share_query_and_depth_but_not_evidence():
    rows,_,_=build()
    for offset in range(0,200,4):
        positive,negative=rows[offset+2:offset+4]
        assert positive['query']==negative['query']
        assert positive['expected_route']=='search'
        assert negative['expected_route']=='no_search'
        assert positive['history']!=negative['history']
        assert len(positive['history'])==len(negative['history'])


def test_validator_rejects_gold_leaking_into_inference_state():
    rows,_,evaluation=build()
    rows[0]['request']['state']['expected_route']='search'
    with pytest.raises(ValueError,match='contract mismatch'):
        validate(rows,evaluation)


def test_required_source_passages_agree_with_labels():
    rows,sources,_=build()
    for row in rows:
        required=row['source_articles']
        if not required:
            continue
        supplied=[sources[article]['opening'] in input_text(row) for article in required]
        if row['expected_route']=='no_search':
            assert all(supplied), row['id']
        else:
            assert not all(supplied), row['id']


def test_saved_files_and_evaluation_fingerprint():
    here=Path(__file__).with_name('data')
    manifest=json.loads((here/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['evaluation_sha256_before']==manifest['evaluation_sha256_after']
    assert manifest['candidate_tokens']['max']<=512
    assert manifest['candidate_tokens']['truncations']==0
