"""Isolated CUDA Laya decision-layer/scorer training with a frozen-feature cache."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'laya_run'
sys.path[:0] = [str(ROOT / 'code'), str(HERE)]
os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

import numpy as np
import torch
import torch.nn.functional as F
from safetensors.torch import load_file, save_file
from decision_benchmark.adapters import LocalAdapter
from decision_benchmark.contracts import make_state, record, input_sha256, contract_sha256
from build_dataset import validate

CONFIG = dict(seed=20261002, epochs=20, patience=4, learning_rate=1e-4,
              weight_decay=0.01, micro_batch=4, accumulation=2, clip_norm=1.0,
              threshold=0.5, device='cuda', precision='bfloat16',
              checkpoint_selection='minimum validation raw cross-entropy',
              option_order_augmentation=True, feature_dtype='preserve encoder output')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def frozen_hash(model):
    digest = hashlib.sha256()
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            digest.update(name.encode())
            digest.update(parameter.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def trainable_state(model):
    return {name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
            if name.startswith(('head.', 'scorer.'))}


def apply_head(model, state):
    if set(state) != set(trainable_state(model)):
        raise ValueError('Head checkpoint keys differ from the existing decision layers/scorer')
    model.load_state_dict(state, strict=False)


def configure_model(model):
    model.requires_grad_(False)
    model.head.float().requires_grad_(True)
    model.scorer.float().requires_grad_(True)
    model.encoder.to(dtype=torch.bfloat16).eval()
    model.type_emb.to(dtype=torch.bfloat16)
    model.act_head.to(dtype=torch.bfloat16)
    assert all(not p.requires_grad for p in model.encoder.parameters())
    assert all(not p.requires_grad for p in model.act_head.parameters())
    names = [n for n, p in model.named_parameters() if p.requires_grad]
    assert names and all(n.startswith(('head.', 'scorer.')) for n in names)


def encode(engine, row, order):
    from rl_common import build_sequence, serialize_state
    request = record(make_state(row))
    q = engine._to_internal(request['questions']['route'])
    # Audit full lengths before the upstream serializer has any chance to trim.
    header, _ = build_sequence(engine.tok, '', q, 512, engine.cfg['head_max_len'], option_order=order)
    state_tokens = len(engine.tok(serialize_state(request['state']), add_special_tokens=False)['input_ids'])
    complete_length = len(header) + state_tokens
    if complete_length > engine.cfg['max_len']:
        raise ValueError(f"{row['id']}: full Laya input needs {complete_length} tokens; trimming forbidden")
    ins_tokens = len(engine.tok(f"choice question: {q['ins']}", add_special_tokens=False)['input_ids'])
    option_tokens = sum(1 + len(engine.tok(' ' + text, add_special_tokens=False)['input_ids'])
                        for text in __import__('rl_common').render_options(q))
    if ins_tokens + option_tokens > engine.cfg['head_max_len']:
        raise ValueError('Question/option header would be truncated')
    ids, markers = build_sequence(engine.tok, request['state'], q, 512,
                                  engine.cfg['head_max_len'], option_order=order)
    assert len(ids) == complete_length and len(markers) == 2
    label = order.index(0 if row['expected_route'] == 'search' else 1)
    return dict(id=row['id'], ids=ids, markers=markers, label=label, order=order,
                style=row['style'], expected_route=row['expected_route'])


def cache_features(engine, rows, augment=False):
    items = [encode(engine, row, order) for row in rows
             for order in ([[0, 1], [1, 0]] if augment else [[0, 1]])]
    engine.model.encoder.to('cuda').eval()
    for index, item in enumerate(items):
        ids = torch.tensor([item['ids']], device='cuda')
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
            h = engine.model.encoder(input_ids=ids, attention_mask=torch.ones_like(ids)).last_hidden_state
            h = h + engine.model.type_emb(torch.zeros(1, dtype=torch.long, device='cuda'))[:, None, :]
        item['features'] = h[0].detach().cpu().clone()
        if (index + 1) % 40 == 0 or index + 1 == len(items):
            print(f'Frozen GPU features: {index + 1}/{len(items)}', flush=True)
    engine.model.encoder.cpu()
    torch.cuda.empty_cache()
    return items


def batch(items):
    width = max(len(it['ids']) for it in items)
    h = torch.zeros(len(items), width, items[0]['features'].shape[-1], dtype=items[0]['features'].dtype)
    mask = torch.zeros(len(items), width, dtype=torch.bool)
    for i, item in enumerate(items):
        h[i, :len(item['ids'])] = item['features']
        mask[i, :len(item['ids'])] = True
    markers = torch.tensor([it['markers'] for it in items])
    targets = torch.tensor([it['label'] for it in items])
    return [x.to('cuda') for x in (h, mask, markers, targets)]


def head_logits(model, h, mask, markers):
    # Identical to upstream DecisionModel.forward after encoder + fixed type embedding.
    for layer in model.head.layers:
        h = layer(h, src_key_padding_mask=~mask)
    selected = torch.gather(h, 1, markers[:, :, None].expand(-1, -1, h.size(-1)))
    return model.scorer(selected).squeeze(-1).float()


@torch.no_grad()
def evaluate_features(model, items, batch_size=None):
    model.head.eval()
    model.scorer.eval()
    logits = []
    batch_size = batch_size or CONFIG['micro_batch']
    for offset in range(0, len(items), batch_size):
        h, mask, markers, _ = batch(items[offset:offset + batch_size])
        with torch.autocast('cuda', dtype=torch.bfloat16):
            logits.append(head_logits(model, h, mask, markers).cpu())
    z = torch.cat(logits)
    target = torch.tensor([it['label'] for it in items])
    return z, dict(loss=float(F.cross_entropy(z, target)), accuracy=float((z.argmax(-1) == target).float().mean()))


def metrics(predictions):
    def score(rows):
        tp = sum(r['route'] == 'search' and r['expected_route'] == 'search' for r in rows)
        tn = sum(r['route'] == 'no_search' and r['expected_route'] == 'no_search' for r in rows)
        fn = sum(r['route'] == 'no_search' and r['expected_route'] == 'search' for r in rows)
        fp = sum(r['route'] == 'search' and r['expected_route'] == 'no_search' for r in rows)
        return dict(n=len(rows), accuracy=(tp + tn) / len(rows), true_search=tp, true_no_search=tn,
                    missed_search=fn, extra_search=fp, search_recall=tp / max(1, tp + fn),
                    search_precision=tp / max(1, tp + fp),
                    median_ms=float(np.median([r['duration_ms'] for r in rows])))
    return {name: score(predictions if name == 'overall' else [r for r in predictions if r['style'] == name])
            for name in ('overall', 'single', 'multi')}


@torch.no_grad()
def evaluate_full(adapter, rows, output, head_checkpoint=None):
    adapter.engine.model.eval()
    adapter.engine.model.encoder.to('cuda')
    for row in rows[:3]:
        adapter.predict({'query': row['query'], 'history': row['history']})
    values = []
    identity = dict(model_variant='fine_tuned' if head_checkpoint else 'original',
                    head_checkpoint=head_checkpoint.name if head_checkpoint else None,
                    head_sha256=sha(head_checkpoint) if head_checkpoint else None)
    for row in rows:
        torch.cuda.synchronize()
        started = time.perf_counter()
        prediction = adapter.predict({'query': row['query'], 'history': row['history']})
        torch.cuda.synchronize()
        values.append(dict(id=row['id'], style=row['style'], expected_route=row['expected_route'],
                           input_sha256=input_sha256(row), **prediction,
                           **identity,
                           duration_ms=round((time.perf_counter() - started) * 1000, 3)))
    output.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in values), encoding='utf-8')
    return metrics(values)


def train(model, train_items, validation_items, hashes, resume):
    parameters = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(parameters, lr=CONFIG['learning_rate'], weight_decay=CONFIG['weight_decay'])
    updates_per_epoch = math.ceil(160 / (CONFIG['micro_batch'] * CONFIG['accumulation']))
    total_updates = CONFIG['epochs'] * updates_per_epoch
    warmup = max(1, total_updates // 10)
    def schedule(step):
        if step < warmup:
            return (step + 1) / warmup
        return 0.5 * (1 + math.cos(math.pi * (step - warmup) / max(1, total_updates - warmup)))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, schedule)
    rng = random.Random(CONFIG['seed'])
    history = []
    best_loss, stale, start_epoch = float('inf'), 0, 1
    if resume:
        state = torch.load(OUT / 'last.pt', map_location='cpu', weights_only=False)
        if state['config'] != CONFIG or state['hashes'] != hashes:
            raise ValueError('Resume data/config differs from saved run')
        apply_head(model, state['model'])
        optimizer.load_state_dict(state['optimizer'])
        scheduler.load_state_dict(state['scheduler'])
        rng.setstate(state['sampler_rng'])
        torch.set_rng_state(state['torch_rng'])
        torch.cuda.set_rng_state_all(state['cuda_rng'])
        random.setstate(state['python_rng'])
        np.random.set_state(state['numpy_rng'])
        history, best_loss, stale = state['history'], state['best_loss'], state['stale']
        start_epoch = state['epoch'] + 1
    for epoch in range(start_epoch, CONFIG['epochs'] + 1):
        if stale >= CONFIG['patience']:
            break
        model.head.train()
        model.scorer.train()
        indices = list(range(160))
        rng.shuffle(indices)
        # Use one randomly chosen candidate order per sample per epoch.
        items = [train_items[2 * i + rng.randrange(2)] for i in indices]
        optimizer.zero_grad(set_to_none=True)
        loss_sum, norm_sum, correct, updates = 0.0, 0.0, 0, 0
        for offset in range(0, 160, CONFIG['micro_batch']):
            selected = items[offset:offset + CONFIG['micro_batch']]
            h, mask, markers, target = batch(selected)
            with torch.autocast('cuda', dtype=torch.bfloat16):
                z = head_logits(model, h, mask, markers)
                loss = F.cross_entropy(z, target)
            if not torch.isfinite(loss):
                raise RuntimeError('Non-finite training loss; stopping')
            (loss / CONFIG['accumulation']).backward()
            loss_sum += float(loss.detach()) * len(selected)
            correct += int((z.detach().argmax(-1) == target).sum())
            if ((offset // CONFIG['micro_batch']) + 1) % CONFIG['accumulation'] == 0:
                norm = torch.nn.utils.clip_grad_norm_(parameters, CONFIG['clip_norm'])
                if not torch.isfinite(norm):
                    raise RuntimeError('Non-finite gradients; stopping')
                norm_sum += float(norm)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                updates += 1
        _, validation = evaluate_features(model, validation_items)
        entry = dict(epoch=epoch, train_loss=loss_sum / 160, train_accuracy=correct / 160,
                     validation_loss=validation['loss'], validation_accuracy=validation['accuracy'],
                     lr=scheduler.get_last_lr()[0], gradient_norm=norm_sum / updates,
                     peak_allocated_mb=round(torch.cuda.max_memory_allocated() / 1024**2, 1))
        history.append(entry)
        if validation['loss'] < best_loss - 1e-4:
            best_loss, stale = validation['loss'], 0
            filename = f'head_epoch_{epoch:02d}.safetensors'
            save_file(trainable_state(model), str(OUT / filename))
            dump(OUT / 'best.json', dict(entry, checkpoint=filename))
        else:
            stale += 1
        dump(OUT / 'history.json', history)
        torch.save(dict(model=trainable_state(model), optimizer=optimizer.state_dict(),
                        scheduler=scheduler.state_dict(), epoch=epoch, best_loss=best_loss, stale=stale,
                        history=history, config=CONFIG, hashes=hashes, sampler_rng=rng.getstate(),
                        torch_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all(),
                        python_rng=random.getstate(), numpy_rng=np.random.get_state()), OUT / 'last.pt')
        print(json.dumps(entry), flush=True)
    del optimizer, scheduler
    torch.cuda.empty_cache()
    return history


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--output', default='laya_run_v2')
    parser.add_argument('--cache-from')
    args = parser.parse_args()
    OUT = HERE / args.output
    if OUT.resolve().parent != HERE.resolve():
        raise ValueError('Output must be a direct child of the experiment directory')
    if (OUT / 'config.json').exists() and not args.resume:
        raise RuntimeError('Run already exists; use --resume rather than overwrite it')
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError('CUDA BF16 required; CPU fallback disabled')
    torch.set_num_threads(4)
    random.seed(CONFIG['seed'])
    np.random.seed(CONFIG['seed'])
    torch.manual_seed(CONFIG['seed'])
    torch.cuda.manual_seed_all(CONFIG['seed'])
    started = time.perf_counter()
    data = HERE / 'data'
    eval_path = HERE.parent / 'cases.jsonl'
    rows = read_rows(data / 'finetuning_cases.jsonl')
    evaluation = read_rows(eval_path)
    validate(rows, evaluation)
    train_rows, val_rows = read_rows(data / 'train.jsonl'), read_rows(data / 'validation.jsonl')
    assert train_rows == [r for r in rows if r['split'] == 'train']
    assert val_rows == [r for r in rows if r['split'] == 'validation']
    manifest = json.loads((data / 'manifest.json').read_text(encoding='utf-8'))
    assert sha(eval_path) == manifest['evaluation_sha256_before']
    hashes = {name: sha(data / name) for name in ('train.jsonl', 'validation.jsonl', 'finetuning_cases.jsonl')}
    hashes.update(evaluation=sha(eval_path), contract=contract_sha256())
    spec = json.loads((ROOT / '.cache/decision_sources/artifacts.json').read_text())['laya']
    OUT.mkdir(exist_ok=True)
    dump(OUT / 'config.json', dict(**CONFIG, hashes=hashes, checkpoint=spec))
    adapter = LocalAdapter('laya', spec, device='cuda', dtype='bfloat16')
    model = adapter.engine.model
    configure_model(model)
    frozen_before = frozen_hash(model)
    original_head = trainable_state(model)
    if args.resume:
        original_head = load_file(str(OUT / 'original_head.safetensors'))
    else:
        save_file(original_head, str(OUT / 'original_head.safetensors'))
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
    print(json.dumps(dict(gpu=torch.cuda.get_device_name(), trainable_parameters=trainable,
                          frozen_parameters=frozen, frozen_backbone=True)), flush=True)
    cache_path = Path(args.cache_from) if args.cache_from else OUT / 'features.pt'
    if args.cache_from and not cache_path.exists():
        raise ValueError('Requested feature cache does not exist')
    if cache_path.exists():
        cached = torch.load(cache_path, map_location='cpu', weights_only=False)
        if cached['hashes'] != hashes or cached['frozen_hash'] != frozen_before:
            raise ValueError('Cached frozen features differ from inputs/model')
        train_items, val_items = cached['train'], cached['validation']
        model.encoder.cpu()
    else:
        train_items = cache_features(adapter.engine, train_rows, augment=True)
        val_items = cache_features(adapter.engine, val_rows)
        torch.save(dict(train=train_items, validation=val_items, hashes=hashes,
                        frozen_hash=frozen_before), cache_path)
    _, initial_validation = evaluate_features(model, val_items)
    torch.cuda.reset_peak_memory_stats()
    history = train(model, train_items, val_items, hashes, args.resume)
    training_peak_mb = max(round(torch.cuda.max_memory_allocated() / 1024**2, 1),
                           max(entry['peak_allocated_mb'] for entry in history))
    best = json.loads((OUT / 'best.json').read_text())
    selected_path = OUT / best.get('checkpoint', 'best_head.safetensors')
    apply_head(model, load_file(str(selected_path)))
    # Match the upstream single-request inference shape for calibration/parity.
    # BF16 padded batches can slightly change probabilities without changing routes.
    best_z, final_validation = evaluate_features(model, val_items, batch_size=1)
    target = torch.tensor([it['label'] for it in val_items])
    temperatures = torch.logspace(math.log10(0.25), math.log10(4), 81)
    temperature = float(min(temperatures, key=lambda t: float(F.cross_entropy(best_z / t, target))))
    dump(OUT / 'calibration.json', dict(temperature=temperature, threshold=0.5,
                                      fitted_on='40 validation cases only'))
    # The test set is evaluated only now, after checkpoint and temperature are fixed.
    apply_head(model, original_head)
    baseline = evaluate_full(adapter, evaluation, OUT / 'before.jsonl')
    apply_head(model, load_file(str(selected_path)))
    adapter.engine.temperature_by_options = dict(adapter.engine.temperature_by_options, **{'choice:2': temperature})
    trained = evaluate_full(adapter, evaluation, OUT / 'after.jsonl', selected_path)
    # Reloaded full inference must agree with the cached validation-head path.
    parity = []
    for row, cached_logits in zip(val_rows, best_z):
        probability = adapter.predict({'query': row['query'], 'history': row['history']})['probabilities']['search']
        expected = float(torch.softmax(cached_logits / temperature, -1)[0])
        parity.append(dict(id=row['id'], full=probability, cached=expected,
                           difference=abs(probability-expected),
                           same_route=(probability>=0.5)==(expected>=0.5)))
    dump(OUT / 'parity.json', parity)
    if any(r['difference'] > 0.005 or not r['same_route'] for r in parity):
        raise RuntimeError('Frozen-cache/full-inference parity failed; see parity.json')
    assert frozen_hash(model) == frozen_before, 'Frozen parameters changed'
    assert sha(eval_path) == hashes['evaluation'], 'Evaluation file changed'
    assert all(p.grad is None for p in model.encoder.parameters()), 'Backbone received gradients'
    summary = dict(model=spec, config=CONFIG, hashes=hashes, gpu=torch.cuda.get_device_name(),
                   torch_version=torch.__version__, cuda_version=torch.version.cuda,
                   trainable_parameters=trainable, frozen_parameters=frozen,
                   frozen_parameters_unchanged=True, backbone_gradients_absent=True,
                   input_truncations=0, initial_validation=initial_validation,
                   selected_checkpoint=json.loads((OUT / 'best.json').read_text()),
                   final_validation=final_validation, epochs_completed=len(history),
                   temperature=temperature, baseline=baseline, trained=trained,
                   training_peak_allocated_mb=training_peak_mb,
                   total_peak_allocated_mb=round(torch.cuda.max_memory_allocated() / 1024**2, 1),
                   peak_reserved_mb=round(torch.cuda.max_memory_reserved() / 1024**2, 1),
                   last_invocation_seconds=round(time.perf_counter() - started, 1),
                   feature_cache=str(cache_path.resolve().relative_to(ROOT)),
                   cache_feature_dtype=str(train_items[0]['features'].dtype),
                   evaluation_unchanged=True, cache_full_inference_parity=True,
                   limitations='Small constructed training pilot; existing evaluation repeatedly inspected; no fresh production test.')
    dump(OUT / 'summary.json', summary)
    lines = ['# Laya frozen-backbone training results', '',
             f"GPU: {summary['gpu']}. Train: 160; validation: 40; evaluation: 100.", '',
             f"Trained {trainable:,} parameters in the two decision layers and scorer; froze {frozen:,} parameters.",
             f"Selected epoch {summary['selected_checkpoint']['epoch']} by validation loss; threshold stayed 0.5.", '',
             '| Model | Overall | Single-turn | Multi-turn | Missed search / 50 | Extra search / 50 | Median ms |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for name, result in [('Laya before', baseline), ('Laya fine-tuned', trained)]:
        m = result['overall']
        lines.append(f"| {name} | {m['accuracy']:.0%} | {result['single']['accuracy']:.0%} | {result['multi']['accuracy']:.0%} | {m['missed_search']} | {m['extra_search']} | {m['median_ms']:.1f} |")
    lines += ['', f"Training peak allocated VRAM: {training_peak_mb:.1f} MiB. Last invocation: {summary['last_invocation_seconds']} seconds.", '',
              f"Validation accuracy: {final_validation['accuracy']:.1%}; selected by validation loss, not evaluation accuracy.", '',
              'The overall gain is driven by single-turn cases. Multi-turn accuracy regressed and extra searches increased; this checkpoint remains a pilot.', '',
              'Frozen weights were hash-checked unchanged; no backbone gradients; all histories fit; cached/full inference agreed.', '',
              f"This run does not change the production router or the original model snapshot. Restore the pinned original Laya model, then load {selected_path.name} and the validation temperature for this checkpoint.", '',
              summary['limitations'], '']
    (OUT / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
