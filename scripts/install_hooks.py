"""Generate a commit-msg git hook that prepends the pixi env's bin to PATH.

Run via: pixi run bootstrap
"""

import stat
import sys
from pathlib import Path

pixi_bin = Path(sys.executable).parent
hook = Path(".git/hooks/commit-msg")

hook.write_text(
    "#!/usr/bin/env bash\n"
    f'export PATH="{pixi_bin}:$PATH"\n'
    "exec pre-commit hook-impl"
    " --config=.pre-commit-config.yaml"
    " --hook-type=commit-msg"
    ' --hook-dir "$(cd "$(dirname "$0")" && pwd)"'
    ' -- "$@"\n'
)
hook.chmod(hook.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
print(f"Installed commit-msg hook (pixi env: {pixi_bin})")
