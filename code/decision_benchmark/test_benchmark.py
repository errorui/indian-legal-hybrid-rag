import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from decision_benchmark.contracts import (fit_history, input_sha256, validate_prediction,
                                         make_state, serialize_conversation_state)
from decision_benchmark.dataset import validate
from decision_benchmark.metrics import summarize

def test_history_is_never_silently_dropped():
    payload={'query':'Explain that','history':[{'role':'user','content':'old'},{'role':'assistant','content':'answer'}]}
    with pytest.raises(ValueError,match='truncation is forbidden'):
        fit_history(payload,lambda s:len(s['conversation'])<=2)
    state,removed=fit_history(payload,lambda s:True)
    assert removed==0 and len(state['conversation'])==3

def test_labels_and_provenance_do_not_enter_inference_hash():
    a={'query':'Hi','history':[],'expected_route':'search'}
    b=dict(a,expected_route='no_search',rationale='secret gold')
    assert input_sha256(a)==input_sha256(b)

def test_threshold_and_invalid_probabilities():
    assert validate_prediction({'route':'search','probabilities':{'search':.5,'no_search':.5}})
    with pytest.raises(ValueError):
        validate_prediction({'route':'search','probabilities':{'search':.49,'no_search':.51}})
    with pytest.raises(ValueError):
        validate_prediction({'route':'search','probabilities':{'search':float('nan'),'no_search':0}})

def test_failures_count_in_accuracy_and_recall():
    rows=[{'expected_route':'search','route':'search','duration_ms':1},
          {'expected_route':'search','error':'timeout','duration_ms':10},
          {'expected_route':'no_search','route':'search','duration_ms':2},
          {'expected_route':'no_search','route':'no_search','duration_ms':1}]
    m=summarize(rows)
    assert m['accuracy']==.5 and m['search_recall']==.5
    assert m['failures']==1 and m['unnecessary_search']==1

def test_saved_dataset_balance_real_history_and_shared_pairing():
    path=Path(__file__).with_name('cases.jsonl')
    rows=validate([json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()])
    assert len(rows)==100
    for i in range(50,100,2):
        assert rows[i]['history']==rows[i+1]['history']
        assert rows[i]['expected_route']!=rows[i+1]['expected_route']

def test_conversation_only_renderer_never_adds_an_empty_tool_inventory():
    state=make_state({'query':'Explain Article 14','history':[{'role':'assistant','content':'Earlier answer'}]})
    text=serialize_conversation_state(state)
    assert 'available_tools' not in text and json.loads(text)==state
    assert list(json.loads(text))==['conversation']
    with pytest.raises(ValueError):
        serialize_conversation_state(dict(state,available_tools=[]))

def test_modernjev_preflight_and_prediction_use_the_overridden_renderer(monkeypatch):
    """Verify the adapter's serializer override using a fake engine and tokenizer."""
    import types
    from decision_benchmark.adapters import LocalAdapter
    calls=[]
    class Engine:
        def __init__(self, *args, **kwargs):
            self.tokenizer=lambda *args,**kwargs: {'input_ids':[1]}
            self.model=types.SimpleNamespace(to=lambda **kwargs:None,config=types.SimpleNamespace())
        def decide(self, *, state, question, criteria):
            calls.append(helper.serialize_state(state))
            return {'predicted_label':'search','candidates':[{'label':'search','score':.7},{'label':'no_search','score':.3}]}
    helper=types.SimpleNamespace(DecisionModel=Engine,serialize_state=lambda s:json.dumps(dict(s,available_tools=[])))
    monkeypatch.setattr('decision_benchmark.adapters.load_module',lambda *args:helper)
    adapter=LocalAdapter('modernjev',{'path':'.','repo':'fixture','revision':'fixture'},device='cpu',dtype='float32')
    payload={'query':'Explain Article 14','history':[]}
    assert adapter.fits(make_state(payload))
    assert adapter.predict(payload)['route']=='search'
    assert 'available_tools' not in calls[0]
