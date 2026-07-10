"""Instala el hook de pre-commit que corre check.bat (lint + formato + tests)
antes de cada commit. Si algo falla, el commit se aborta.

Uso:  venv_build\\Scripts\\python.exe scripts\\install_hooks.py
"""

import os
import stat

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(RAIZ, ".git", "hooks", "pre-commit")

CONTENIDO = """#!/bin/sh
# Hook generado por scripts/install_hooks.py - CI local antes de cada commit
cd "$(git rev-parse --show-toplevel)" || exit 1
cmd.exe /c check.bat
"""


def main() -> int:
    if not os.path.isdir(os.path.dirname(HOOK)):
        print("[FALLO] No existe .git/hooks — corre 'git init' primero.")
        return 1
    with open(HOOK, "w", encoding="utf-8", newline="\n") as f:
        f.write(CONTENIDO)
    os.chmod(HOOK, os.stat(HOOK).st_mode | stat.S_IEXEC)
    print(f"[OK] Hook instalado: {HOOK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
