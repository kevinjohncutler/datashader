import os
import subprocess
import sys
from pathlib import Path


def _run(script: Path, cwd: Path) -> str:
    env = os.environ.copy()
    env['NUMBA_DEBUG_CACHE'] = '1'
    return subprocess.check_output([sys.executable, str(script)], cwd=cwd, env=env, text=True)


def test_numba_caching(tmp_path: Path) -> None:
    module = tmp_path / 'mod.py'
    module.write_text(
        'from datashader.utils import ngjit\n'
        '@ngjit\n'
        'def func(n):\n'
        '    total = 0\n'
        '    for i in range(n):\n'
        '        total += i\n'
        '    return total\n'
    )

    script = tmp_path / 'run.py'
    script.write_text(
        'import time\n'
        'from mod import func\n'
        'start = time.time()\n'
        'func(1)\n'
        'print("done", time.time() - start)\n'
    )

    first = _run(script, tmp_path)
    assert 'data loaded' not in first

    second = _run(script, tmp_path)
    assert 'data loaded' in second
