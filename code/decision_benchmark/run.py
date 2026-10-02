"""Frozen GPU binary benchmark: dataset, preflight, evaluate, report, compare."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'code')]
os.environ.setdefault('USE_TF','0')
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS','1')
os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
from decision_benchmark.contracts import contract_sha256, input_sha256, routing_contract, timed_prediction
from decision_benchmark.metrics import summarize, paired_accuracy_difference

HERE = Path(__file__).resolve().parent
RESULTS = HERE/'results_conversation_only_gpu'
BASELINE_SOURCE = HERE/'results_binary_gpu'
ARTIFACTS = ROOT/'.cache/decision_sources/artifacts.json'
NAMES = ['baseline','modernjev','laya','qwen_jev']

def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')

def cases():
    from decision_benchmark.dataset import validate
    return validate([json.loads(line) for line in (HERE/'cases.jsonl').read_text(encoding='utf-8').splitlines()])

def adapter(name):
    from decision_benchmark.adapters import BaselineAdapter, LocalAdapter
    if name=='baseline':
        return BaselineAdapter()
    artifacts=json.loads(ARTIFACTS.read_text(encoding='utf-8'))
    return LocalAdapter(name,artifacts[name],device='cuda',dtype='bfloat16')

def gpu_metadata():
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA required; no CPU fallback')
    return {'gpu_name':torch.cuda.get_device_name(), 'cuda_version':torch.version.cuda,
            'peak_allocated_mb':round(torch.cuda.max_memory_allocated()/1024**2,1),
            'peak_reserved_mb':round(torch.cuda.max_memory_reserved()/1024**2,1)}

def dataset_sha():
    return hashlib.sha256((HERE/'cases.jsonl').read_bytes()).hexdigest()

def adapter_sha():
    return hashlib.sha256((HERE/'adapters.py').read_bytes()+(HERE/'contracts.py').read_bytes()).hexdigest()

def payload(row):
    # Expected labels and provenance never reach inference.
    return {'query':row['query'],'history':row['history']}

def preflight(name, engine=None):
    from decision_benchmark.contracts import make_state, serialize_conversation_state
    engine=adapter(name) if engine is None else engine
    rows=cases()
    bad=[r['id'] for r in rows if not engine.fits(make_state(payload(r)))]
    if bad:
        raise ValueError(f'{name} cannot fit complete histories: {bad}')
    serialized=[]
    for row in rows:
        state=make_state(payload(row))
        text=engine.helper.serialize_state(state) if name=='modernjev' else serialize_conversation_state(state)
        if json.loads(text)!=state or 'available_tools' in text:
            raise ValueError('Unexpected tool metadata in decision state')
        serialized.append({'id':row['id'],'state':state,'serialized_state':text,
                           'input_sha256':input_sha256(payload(row))})
    (RESULTS).mkdir(parents=True,exist_ok=True)
    (RESULTS/f'{name}-inputs.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in serialized),encoding='utf-8')
    dump(RESULTS/f'{name}-preflight.json',{'n':len(rows),'complete_histories_fit':True,
         'dataset_sha256':dataset_sha(),'contract_sha256':contract_sha256(),
         'adapter_sha256':adapter_sha(),'state_format':'conversation only; no tool inventory',
         'device':'cuda','dtype':'bfloat16','model':engine.spec,'gpu':gpu_metadata()})
    print(f'{name}: all 100 complete histories fit; CUDA BF16 confirmed',flush=True)

def evaluate(name, engine=None, cold_load_ms=None):
    rows=cases()
    target=RESULTS/f'{name}.jsonl'
    meta_path=RESULTS/f'{name}-runtime.json'
    prior=[json.loads(line) for line in target.read_text(encoding='utf-8').splitlines()] if target.exists() else []
    if prior:
        metadata=json.loads(meta_path.read_text(encoding='utf-8'))
        if metadata['dataset_sha256'] != dataset_sha() or metadata['contract_sha256'] != contract_sha256():
            raise ValueError('Cached predictions use a different dataset or contract')
        if name!='baseline' and metadata.get('adapter_sha256')!=adapter_sha():
            raise ValueError('Cached predictions use different adapter serialization')
    done={r['id'] for r in prior}
    if len(done)==len(rows):
        print(name+': 100 cached',flush=True)
        return
    if name!='baseline':
        proof=json.loads((RESULTS/f'{name}-preflight.json').read_text(encoding='utf-8'))
        if (proof['dataset_sha256'] != dataset_sha() or proof['contract_sha256'] != contract_sha256()
            or proof.get('adapter_sha256') != adapter_sha()):
            raise ValueError('Preflight does not match frozen inputs')
    tick=time.perf_counter()
    engine=adapter(name) if engine is None else engine
    load_ms=round((time.perf_counter()-tick)*1000,3) if cold_load_ms is None else cold_load_ms
    if name!='baseline':
        for _ in range(3):
            timed_prediction(engine,{'query':'What is Article 21?','history':[]})
        import torch
        torch.cuda.reset_peak_memory_stats()
    metadata={'dataset_sha256':dataset_sha(),'contract_sha256':contract_sha256(),
              'device':'remote' if name=='baseline' else 'cuda',
              'dtype':None if name=='baseline' else 'bfloat16', 'load_ms':load_ms,
              'model':engine.settings.generation_model if name=='baseline' else engine.spec,
              'python':sys.version,'python_executable':sys.executable,
              'platform':platform.platform(),'concurrency':1,
              'packages':{p:importlib.metadata.version(p) for p in ('torch','transformers','huggingface-hub')},
              'warmup_calls':0 if name=='baseline' else 3,
              'request_settings':{'think':False,'temperature':'provider default','tools':'always offered'}
                 if name=='baseline' else {'threshold':.5,'candidate_order':['search','no_search']}}
    if name!='baseline':
        metadata.update({'adapter_sha256':adapter_sha(),'state_format':'conversation only; no tool inventory',
                         'serialization_override':'conversation-only renderer' if name=='modernjev' else 'unchanged upstream rendering'})
    dump(meta_path,metadata)
    with target.open('a',encoding='utf-8') as output:
        for row in rows:
            if row['id'] in done:
                continue
            tick=time.perf_counter()
            try:
                value=engine.predict(payload(row)) if name=='baseline' else timed_prediction(engine,payload(row))
                if name=='baseline':
                    value['duration_ms']=round((time.perf_counter()-tick)*1000,3)
                    calls=value['tool_calls']
                    if calls and any(c['name'] != 'search_corpus' for c in calls):
                        raise ValueError('Provider called a tool not offered by the benchmark')
            except Exception as exc:
                value={'error':str(exc),'error_type':type(exc).__name__,
                       'duration_ms':round((time.perf_counter()-tick)*1000,3)}
            value.update({k:row[k] for k in ('id','style','group','expected_route')})
            value['input_sha256']=input_sha256(payload(row))
            if name!='baseline':
                value['adapter_sha256']=adapter_sha()
            output.write(json.dumps(value,ensure_ascii=False)+'\n')
            output.flush()
            done.add(row['id'])
            if len(done)%10==0:
                print(f'{name}: {len(done)}/100',flush=True)
    if name!='baseline':
        metadata['model_parameter_devices']=sorted({str(p.device) for p in engine.engine.model.parameters()})
        metadata['model_parameter_dtypes']=sorted({str(p.dtype) for p in engine.engine.model.parameters()})
        metadata.update(gpu_metadata())
    dump(meta_path,metadata)

def report():
    rows=cases()
    predictions={}
    for name in NAMES:
        runtime=json.loads((RESULTS/f'{name}-runtime.json').read_text(encoding='utf-8'))
        if runtime['dataset_sha256'] != dataset_sha() or runtime['contract_sha256'] != contract_sha256():
            raise ValueError('Runtime metadata differs from frozen inputs for '+name)
        if name!='baseline' and (runtime['device']!='cuda' or runtime['model_parameter_devices']!=['cuda:0']):
            raise ValueError('Local inference was not entirely on the required GPU for '+name)
        if name!='baseline' and runtime.get('adapter_sha256')!=adapter_sha():
            raise ValueError('Runtime used a different state serializer for '+name)
        values=[json.loads(line) for line in (RESULTS/f'{name}.jsonl').read_text(encoding='utf-8').splitlines()]
        indexed={r['id']:r for r in values}
        if len(values)!=100 or len(indexed)!=100 or set(indexed)!={r['id'] for r in rows}:
            raise ValueError('Incomplete or duplicate predictions for '+name)
        for row in rows:
            if indexed[row['id']]['input_sha256'] != input_sha256(payload(row)):
                raise ValueError('Input mismatch for '+name+'/'+row['id'])
            if any(indexed[row['id']][key] != row[key] for key in ('style','group','expected_route')):
                raise ValueError('Gold metadata mismatch for '+name+'/'+row['id'])
        predictions[name]=[indexed[r['id']] for r in rows]
    summary={'protocol':routing_contract(),'dataset_sha256':dataset_sha(),
             'n':100,'model_selection_or_threshold_tuning':False,'models':{},
             'state_format':'conversation only; no available_tools field',
             'baseline_reused_from':str(BASELINE_SOURCE)}
    for name in NAMES:
        values=predictions[name]
        measured={style:summarize([r for r in values if style=='overall' or r['style']==style])
                  for style in ('overall','single','multi')}
        if name!='baseline':
            measured['paired_accuracy_vs_baseline']=paired_accuracy_difference(values,predictions['baseline'])
        summary['models'][name]=measured
    dump(RESULTS/'summary.json',summary)
    dump(RESULTS/'selection.json',{'qualified':False,'selected_model':None,
         'reason':'Fixed comparison only; no independent production qualification.',
         'contract_sha256':contract_sha256()})
    review=['# Binary routing benchmark — all 100 cases','',
      '50 single-turn / 50 multi-turn; each style has 25 search and 25 no-search cases. '
      'Local models run CUDA BF16; the existing LLM provider runs remotely. Search threshold is 0.5.', '',
      'Decision-model state contains only the complete conversation, including the latest question. '
      'The routing policy and two choices are supplied separately. ModernJEV uses a local serializer override '
      'to prevent its upstream helper from inserting an empty available_tools field. '
      'All three decision models were rerun; the original LLM predictions were reused without provider requests.', '',
      'This is a controlled routing comparison with a compact shared policy and real tool calling. '
      'It does not execute retrieval after the scored decision or assess final-answer quality. '
      'Reference answers were generated by the existing LLM using article excerpts selected from the existing corpus. '
      'Reference generation uses deterministic article lookup, not the production hybrid retrieval graph. '
      'Histories are shared replay, not independent model conversations. Full histories fit all models without trimming.', '',
      '| Model | Overall | Single | Multi | Search precision | Search recall | Missed searches | Extra searches | Failures | Median ms | P95 ms |',
      '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name in NAMES:
        measured=summary['models'][name]; m=measured['overall']
        review.append(f"| {name} | {m['accuracy']:.0%} | {measured['single']['accuracy']:.0%} | {measured['multi']['accuracy']:.0%} | {m['search_precision']:.1%} | {m['search_recall']:.1%} | {m['missed_search']} | {m['unnecessary_search']} | {m['failures']} | {m['median_ms']:.1f} | {m['p95_ms']:.1f} |")
    review += ['', 'Labels follow the frozen evidence policy and are independent of model outputs. '
               'Invalid or failed predictions count as incorrect in the accuracy denominator. '
               'Latency excludes local model load and warmup; baseline latency includes network and provider response generation. '
               'All requests run sequentially. A local no-search decision still needs an LLM answer call; these timings do not establish end-to-end savings. '
               'Each checkpoint has one prediction per model, without measuring provider sampling variability. '
               'This small constructed dataset is a diagnostic evaluation, not a production accuracy estimate.', '',
               '## Every case', '', '| Case | Style | Expected | LLM | ModernJEV | Laya | Qwen JEV |',
               '|---|---|---|---|---|---|---|']
    combined=[]
    for i,row in enumerate(rows):
        entry=dict(row)
        entry['predictions']={name:predictions[name][i] for name in NAMES}
        combined.append(entry)
        cells=[]
        for name in NAMES:
            v=predictions[name][i]
            result=v.get('route','ERROR')
            marker='✓' if result==row['expected_route'] else '✗'
            probability=f" ({v['probabilities']['search']:.4f})" if 'probabilities' in v else ''
            cells.append(marker+' '+result+probability)
        review.append('| '+' | '.join([row['id'],row['style'],row['expected_route']]+cells)+' |')
    review += ['', '## Questions, history and gold-label rationale', '']
    for row in rows:
        review += [f"### {row['id']} — {row['expected_route']}", '', '**Latest question:** '+row['query'], '',
                   '**Gold rationale:** '+row['rationale'], '']
        for message in row['history']:
            review += [f"**{message['role']}:** {message['content']}", '']
    (RESULTS/'report.md').write_text('\n'.join(review),encoding='utf-8')
    (RESULTS/'all_cases.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in combined),encoding='utf-8')
    with (RESULTS/'all_cases.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.writer(handle)
        writer.writerow(['id','style','question','expected']+[x for name in NAMES for x in (name+'_route',name+'_correct',name+'_p_search',name+'_ms')])
        for row in combined:
            cells=[row['id'],row['style'],row['query'],row['expected_route']]
            for name in NAMES:
                p=row['predictions'][name]
                cells += [p.get('route','ERROR'),p.get('route')==row['expected_route'],p.get('probabilities',{}).get('search',''),p['duration_ms']]
            writer.writerow(cells)
    print(json.dumps({n:summary['models'][n]['overall'] for n in NAMES},indent=2),flush=True)

def reuse_baseline():
    """Copy the unchanged provider results without constructing a provider."""
    import shutil
    runtime=json.loads((BASELINE_SOURCE/'baseline-runtime.json').read_text(encoding='utf-8'))
    values=[json.loads(line) for line in (BASELINE_SOURCE/'baseline.jsonl').read_text(encoding='utf-8').splitlines()]
    expected={r['id']:r for r in cases()}
    if (runtime['dataset_sha256']!=dataset_sha() or runtime['contract_sha256']!=contract_sha256()
        or len(values)!=100 or len({v['id'] for v in values})!=100):
        raise ValueError('Saved baseline does not match the frozen dataset and policy')
    for value in values:
        row=expected[value['id']]
        if value['input_sha256']!=input_sha256(payload(row)) or value['expected_route']!=row['expected_route']:
            raise ValueError('Saved baseline input/gold mismatch')
    RESULTS.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(BASELINE_SOURCE/'baseline.jsonl',RESULTS/'baseline.jsonl')
    runtime['reused_from']=str(BASELINE_SOURCE/'baseline.jsonl')
    runtime['reused_predictions_sha256']=hashlib.sha256((BASELINE_SOURCE/'baseline.jsonl').read_bytes()).hexdigest()
    dump(RESULTS/'baseline-runtime.json',runtime)
    print('Reused all 100 original LLM results; no provider calls',flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['dataset','preflight','evaluate','report','compare','worker','decision-run','decisions-only'])
    parser.add_argument('--model',choices=NAMES)
    parser.add_argument('--manifest')
    args=parser.parse_args()
    if args.command=='dataset':
        from decision_benchmark.dataset import generate
        generate()
    elif args.command=='preflight': preflight(args.model)
    elif args.command=='evaluate': evaluate(args.model)
    elif args.command=='report': report()
    elif args.command=='decision-run':
        if args.model not in NAMES[1:]:
            raise ValueError('decision-run requires a local decision model')
        tick=time.perf_counter()
        engine=adapter(args.model)
        cold_load_ms=round((time.perf_counter()-tick)*1000,3)
        preflight(args.model,engine)
        evaluate(args.model,engine,cold_load_ms)
    elif args.command=='decisions-only':
        reuse_baseline()
        for name in NAMES[1:]:
            subprocess.run([sys.executable,__file__,'decision-run','--model',name],check=True)
        report()
    elif args.command=='worker':
        raise RuntimeError('Binary production worker is not qualified; observer remains disabled')
    else:
        for name in NAMES[1:]:
            subprocess.run([sys.executable,__file__,'preflight','--model',name],check=True)
        for name in NAMES:
            subprocess.run([sys.executable,__file__,'evaluate','--model',name],check=True)
        report()

if __name__=='__main__': main()
