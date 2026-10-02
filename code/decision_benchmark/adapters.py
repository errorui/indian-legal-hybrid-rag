"""Adapters for reviewed, pinned upstream inference helpers."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from .contracts import (CHOICES, POLICY, QUESTION, THRESHOLD, fit_history,
                        make_state, record, serialize_conversation_state)

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocalAdapter:
    def __init__(self, name, spec, device='cuda', dtype='bfloat16'):
        import torch
        torch.set_num_threads(4)
        if device == 'cuda' and not torch.cuda.is_available():
            raise RuntimeError('CUDA GPU is required; CPU fallback is disabled')
        if device == 'cuda' and dtype == 'bfloat16' and not torch.cuda.is_bf16_supported():
            raise RuntimeError('This GPU does not support BF16; choose float32 explicitly')
        if device == 'cpu' and dtype != 'float32':
            raise ValueError('CPU comparison requires float32')
        self.device, self.dtype = device, dtype
        torch_dtype = getattr(torch,dtype)
        self.name, self.spec = name, spec
        path = Path(spec['path'])
        if not path.is_absolute():
            path = ROOT / path
        if name == 'modernjev':
            self.helper = load_module('modernjev_predict', path / 'predict.py')
            # Override only the helper's state rendering. Its default inserts
            # available_tools: [] even when our state intentionally omits tools.
            # Use this same renderer for budget checks and real inference.
            self.helper.serialize_state = serialize_conversation_state
            self.engine = self.helper.DecisionModel(str(path), device=device)
            self.engine.model.to(dtype=torch_dtype)
            self.engine.model.config.reference_compile = False
            self.tokenizer = self.engine.tokenizer
        elif name == 'laya':
            # Local helper imports rl_common by name; isolate it in this process.
            sys.path.insert(0, str(path))
            self.helper = load_module('laya_api', path / 'rl_agent_api.py')
            self.engine = self.helper.RLAgent(str(path), device=device)
            self.engine.model.to(dtype=torch_dtype)
            self.engine.dtype = torch_dtype
            self.tokenizer = self.engine.tok
        elif name == 'qwen_jev':
            code_path = Path(spec['code_path'])
            sys.path.insert(0, str(code_path if code_path.is_absolute() else ROOT / code_path))
            from jev_inference import DecisionEngine
            self.engine = DecisionEngine.load(str(path), device=device, dtype=dtype)
            self.tokenizer = self.engine.tokenizer
        else:
            raise ValueError('Unknown adapter ' + name)

    def synchronize(self):
        if self.device == 'cuda':
            import torch
            torch.cuda.synchronize()

    def fits(self, state):
        tok = self.tokenizer
        if self.name == 'modernjev':
            first = QUESTION + '\n\nSTATE:\n' + self.helper.serialize_state(state)
            return all(len(tok(first, f'{key}: {desc}', add_special_tokens=True)['input_ids']) <= 4096
                       for key, desc in CHOICES.items())
        if self.name == 'qwen_jev':
            from jev_inference.model import encode
            try:
                encode(tok, record(state), 1024)
                return True
            except ValueError:
                return False
        from rl_common import build_sequence, serialize_state
        internal = self.engine._to_internal(record(state)['questions']['route'])
        head_ids, _ = build_sequence(tok, '', internal, 512, self.engine.cfg['head_max_len'])
        length = len(tok(serialize_state(state), add_special_tokens=False)['input_ids'])
        return len(head_ids) + length <= 512

    def predict(self, payload):
        state, removed = fit_history(payload, self.fits)
        if self.name == 'modernjev':
            raw = self.engine.decide(state=state, question=QUESTION, criteria=CHOICES)
            route = raw['predicted_label']
            probs = {row['label']: row['score'] for row in raw['candidates']}
        else:
            request = record(state)
            if self.name == 'laya':
                raw = self.engine.system_one(state, request['questions'])['answers']['route']
            else:
                raw = self.engine.predict(request)['route']
            route, probs = raw['choice'], raw['probabilities']
        route = 'search' if probs['search'] >= THRESHOLD else 'no_search'
        return {'route': route, 'probabilities': probs, 'threshold': THRESHOLD, 'model': self.spec['repo'],
                'revision': self.spec['revision'], 'truncated': removed > 0,
                'removed_history_messages': removed, 'device': self.device, 'dtype': self.dtype}


class BaselineAdapter:
    """Exactly the current initial provider action, with no retrieval or final answer."""
    def __init__(self):
        from backend.core.config import settings
        from backend.services.provider_factory import create_chat_provider
        self.settings = settings
        self.provider = create_chat_provider(settings)
        if not self.provider.available:
            raise RuntimeError('Existing generation provider is unavailable')
        from ollama import Client
        self.provider._client = Client(host=settings.ollama_host,
                                       headers={'Authorization': f'Bearer {settings.ollama_api_key}'}, timeout=40)

    def predict(self, payload):
        from backend.services.langgraph_workflow import (LangGraphWorkflow, SearchCorpusInput,
            SearchCorpusTool, _ai_message)
        query = ' '.join(payload['query'].split())
        messages = [{'role': 'system', 'content': POLICY}]
        for m in payload.get('history', []):
            content = m['content']
            messages.append({'role': m['role'], 'content': content})
        messages.append({'role': 'user', 'content': query})
        args = {'model': self.settings.generation_model, 'messages': messages,
                'think': False,
                'tools': [{'type': 'function', 'function': {'name': SearchCorpusTool.name,
                           'description': CHOICES['search'],
                           'parameters': SearchCorpusInput.model_json_schema()}}]}
        response = _ai_message(self.provider.chat(**args))
        from langgraph.prebuilt import tools_condition
        destination = tools_condition({'messages': [response]})
        return {'route': 'search' if destination == 'tools' else 'no_search',
                'graph_destination': destination, 'tool_calls': response.tool_calls,
                'actual_tool_call': bool(response.tool_calls),
                'model': self.settings.generation_model, 'response_content': str(response.content)}
