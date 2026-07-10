"""
e2e_pipeline.py — Corre el pipeline COMPLETO sin GUI para detectar bugs rápidamente.

Es una prueba de humo manual: carga el modelo de embeddings real y procesa los
documentos sintéticos de prueba/. No forma parte de la suite de pytest (tarda
minutos la primera vez por la descarga del modelo).

Uso:  venv_build\\Scripts\\python.exe scripts\\e2e_pipeline.py
"""

import os
import sys

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAIZ)

from app.pipeline import ejecutar_analisis

BASE = os.path.join(_RAIZ, "prueba", "resolucion_base.docx")
RECURS = os.path.join(_RAIZ, "prueba", "recursos")
SALIDA = os.path.join(_RAIZ, "prueba", "resultados")


def cb(msg, pct):
    print(f"[{pct:3d}%] {msg}")


if __name__ == "__main__":
    resultado = ejecutar_analisis(BASE, RECURS, SALIDA, callback_progreso=cb)
    print("\n=== RESULTADO ===")
    print(resultado)
