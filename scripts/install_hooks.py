"""Instala el hook de pre-commit que corre check.bat (lint + formato + tests)
antes de cada commit. Si algo falla, el commit se aborta.

Uso:  venv_build\\Scripts\\python.exe scripts\\install_hooks.py
"""

import os
import stat

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(RAIZ, ".git", "hooks", "pre-commit")

CONTENIDO = """#!/bin/sh
# Hook generado por scripts/install_hooks.py - CI local antes de cada commit.
# Invoca python del venv directamente: pasar por cmd.exe es fragil en Git Bash
# (MSYS convierte /c en C:\\ y cmd no hereda bien el directorio de trabajo).
cd "$(git rev-parse --show-toplevel)" || exit 1
PY=./venv_build/Scripts/python.exe
[ -x "$PY" ] || PY=python

echo "=== 1/3 Lint (ruff check) ==="
"$PY" -m ruff check . || exit 1
echo "=== 2/3 Formato (ruff format --check) ==="
"$PY" -m ruff format --check . || exit 1
echo "=== 3/3 Tests (pytest) ==="
"$PY" -m pytest -q || exit 1
echo "[OK] Todo en verde."
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
