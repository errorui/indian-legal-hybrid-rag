"""Create an isolated environment sharing read-only project dependencies on this host."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / '.cache/decision_env'
subprocess.run([sys.executable, '-m', 'venv', str(ENV)], check=True)
# A nested venv inherits the base interpreter, not its creator's packages.
# Expose the existing runtime without installing/upgrading anything in it.
sites = [p for p in sys.path if p.endswith('site-packages')]
target = ENV / ('Lib/site-packages' if sys.platform == 'win32' else
                f'lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages')
(target / 'project_runtime.pth').write_text('\n'.join(sites)+'\n', encoding='utf-8')
print(str(ENV / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')))
