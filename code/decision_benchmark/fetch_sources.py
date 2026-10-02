"""Fetch small upstream inference sources for inspection, never execute them."""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.cache' / 'decision_sources'

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    pinned = json.loads((Path(__file__).parent / 'model_sources.json').read_text())
    specs = {
        'modernjev': ('MaziyarPanahi/ModernJEV-Decide-Preview', ['predict.py', 'config.json']),
        'laya': ('convaiinnovations/laya', ['rl_agent_api.py', 'rl_common.py', 'rl_agent_config.json']),
        'qwen_jev': ('joyfox/Qwen3.5-0.8B-JEV', ['decision_config.json', 'backbone/config.json']),
    }
    manifest = {}
    for name, (repo, files) in specs.items():
        revision = pinned[name]['revision']
        folder = CACHE / name
        folder.mkdir(exist_ok=True)
        for file in files:
            data = urllib.request.urlopen(f'https://huggingface.co/{repo}/resolve/{revision}/{file}', timeout=30).read()
            (folder / file.replace('/', '_')).write_bytes(data)
        manifest[name] = {'repo': repo, 'revision': revision}
    code_revision = pinned['qwen_jev']['code_revision']
    manifest['qwen_jev']['code_revision'] = code_revision
    tree = json.load(urllib.request.urlopen(f"https://api.github.com/repos/joyfoxai/jev-inference/git/trees/{code_revision}?recursive=1", timeout=30))
    for item in tree['tree']:
        path = item['path']
        if item['type'] == 'blob' and (path.endswith('.py') or path.endswith('pyproject.toml')):
            target = CACHE / 'qwen_code' / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(urllib.request.urlopen(f"https://raw.githubusercontent.com/joyfoxai/jev-inference/{code_revision}/{path}", timeout=30).read())
    (CACHE / 'sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
