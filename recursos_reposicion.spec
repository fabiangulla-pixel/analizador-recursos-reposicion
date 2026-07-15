# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller para AnalizadorRecursos
# Generado automáticamente — editar solo si cambian dependencias.

import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ── Ruta del modelo (actualizar si cambia la versión) ───────────────────────
MODEL_SNAPSHOT = r"C:\Users\Lenovo\.cache\huggingface\hub\models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2\snapshots\e8f8c211226b894fcb81acc59f3b34ba3efd5f42"

block_cipher = None

datas_st  = collect_data_files("sentence_transformers")
datas_tok = collect_data_files("tokenizers")
datas_cfg = [
    ("config.yaml", "."),
    ("icono.ico",   "."),
]

# Incluir el modelo completo dentro del ejecutable.
# IMPORTANTE: sentence_transformers.SentenceTransformer(nombre, cache_folder=X)
# exige la estructura real de caché de HuggingFace dentro de X:
#   models--<org>--<modelo>/snapshots/<hash>/*  (+ refs/main con el hash)
# Empaquetar el modelo en una carpeta plana (bug real detectado 14-jul-2026:
# el .exe cargaba "OK" en apariencia pero cache_folder nunca encontraba el
# modelo con esa forma, rompiendo la carga 100% offline) hace que la app
# no encuentre el modelo sin internet aunque los archivos estén ahí.
MODEL_HASH = os.path.basename(MODEL_SNAPSHOT)
MODEL_REPO_DIR = os.path.dirname(os.path.dirname(MODEL_SNAPSHOT))
_DEST_REPO = os.path.join("_modelos_cache",
                          "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2")

model_datas = []
if os.path.isdir(MODEL_SNAPSHOT):
    model_datas = [(MODEL_SNAPSHOT, os.path.join(_DEST_REPO, "snapshots", MODEL_HASH))]
    _refs_main = os.path.join(MODEL_REPO_DIR, "refs", "main")
    if os.path.isfile(_refs_main):
        model_datas.append((_refs_main, os.path.join(_DEST_REPO, "refs")))

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=datas_cfg + datas_st + datas_tok + model_datas,
    hiddenimports=[
        "sklearn.utils._cython_blas",
        "sklearn.neighbors.typedefs",
        "sklearn.neighbors._partition_nodes",
        "sklearn.tree._utils",
        "pdfplumber",
        "pdfminer",
        "pdfminer.high_level",
        "pdfminer.layout",
        "docx",
        "openpyxl",
        "sentence_transformers",
        "transformers",
        "torch",
        "huggingface_hub",
        "safetensors",
        "tokenizers",
        "fitz",
        "pymupdf",
        "pytesseract",
    ]
    + collect_submodules("sklearn")
    + collect_submodules("sentence_transformers"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "IPython", "jupyter", "notebook", "pytest",
              "PyQt5", "PyQt6", "PySide2", "PySide6"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── ONE-FOLDER (distribución principal) ─────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AnalizadorRecursos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="icono.ico",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AnalizadorRecursos",
)
