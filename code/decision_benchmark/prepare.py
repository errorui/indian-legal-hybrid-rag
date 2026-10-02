"""Download pinned artifacts into the project cache, without changing backend packages."""
import json
from pathlib import Path
from huggingface_hub import snapshot_download
import huggingface_hub.file_download

ROOT = Path(__file__).resolve().parents[2]

def main():
    # Windows may report symlink support for a parent directory but deny nested
    # snapshots. This downloader deliberately uses ordinary files.
    huggingface_hub.file_download.are_symlinks_supported = lambda cache_dir=None: False
    manifest = json.loads((ROOT / '.cache/decision_sources/sources.json').read_text())
    patterns = {
        'modernjev': ['config.json', 'model.safetensors', 'tokenizer*.json', 'predict.py'],
        'laya': ['encoder/config.json', 'model.safetensors', 'tokenizer/*', 'rl_agent_config.json', 'rl_agent_api.py', 'rl_common.py'],
        'qwen_jev': ['decision_config.json', 'head.safetensors', 'backbone/*', 'tokenizer/*'],
    }
    for name, spec in manifest.items():
        print('Downloading ' + name, flush=True)
        path = snapshot_download(spec['repo'], revision=spec['revision'], allow_patterns=patterns[name],
                                 cache_dir=str(ROOT / '.cache/decision_models'))
        spec['path'] = str(Path(path).resolve().relative_to(ROOT))
        if name == 'qwen_jev':
            spec['code_path'] = '.cache/decision_sources/qwen_code/src'
        target = ROOT / '.cache/decision_sources/artifacts.json'
        target.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print('Ready ' + name, flush=True)

if __name__ == '__main__':
    main()
