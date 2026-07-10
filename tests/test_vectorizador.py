"""Tests de procesamiento/vectorizador.py — detección de caché y modo offline.

No cargan el modelo real: solo la lógica que decide activar HF_HUB_OFFLINE,
que evita que el .exe falle sin internet con el modelo ya descargado.
"""

import numpy as np

from procesamiento.vectorizador import (
    _activar_modo_offline_si_cacheado,
    _modelo_en_cache,
    similitud_coseno,
)

MODELO = "paraphrase-multilingual-MiniLM-L12-v2"


def test_cache_inexistente_no_activa_offline(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    assert _modelo_en_cache(str(tmp_path / "no_existe"), MODELO) is False
    assert _activar_modo_offline_si_cacheado(None, MODELO) is False


def test_cache_vacio_no_activa_offline(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    assert _activar_modo_offline_si_cacheado(str(tmp_path), MODELO) is False
    import os

    assert "HF_HUB_OFFLINE" not in os.environ


def test_modelo_cacheado_activa_offline(tmp_path, monkeypatch):
    # Layout real del hub de HuggingFace, verificado en el .exe desplegado
    (tmp_path / f"models--sentence-transformers--{MODELO}").mkdir()
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    monkeypatch.delenv("TRANSFORMERS_OFFLINE", raising=False)

    assert _activar_modo_offline_si_cacheado(str(tmp_path), MODELO) is True
    import os

    assert os.environ["HF_HUB_OFFLINE"] == "1"
    assert os.environ["TRANSFORMERS_OFFLINE"] == "1"
    # monkeypatch.delenv restaura el entorno al salir del test


def test_no_pisa_configuracion_previa_del_usuario(tmp_path, monkeypatch):
    (tmp_path / f"models--sentence-transformers--{MODELO}").mkdir()
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")

    _activar_modo_offline_si_cacheado(str(tmp_path), MODELO)
    import os

    assert os.environ["HF_HUB_OFFLINE"] == "0"  # setdefault no sobreescribe


def test_similitud_coseno_de_vectores_normalizados():
    assert similitud_coseno(np.array([1.0, 0.0]), np.array([1.0, 0.0])) == 1.0
    assert similitud_coseno(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == 0.0
