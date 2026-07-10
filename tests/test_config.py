"""Tests de app/config_loader.py — el config.yaml real carga y tiene las claves esperadas."""

from app.config_loader import cargar_config


def test_config_real_carga_con_claves_completas():
    cfg = cargar_config()
    assert cfg["procesamiento"]["umbral_resuelto"] == 0.70
    assert cfg["procesamiento"]["modelo_embeddings"]
    assert ".pdf" in cfg["ingesta"]["extensiones_soportadas"]
    assert isinstance(cfg["exportacion"]["generar_xlsx"], bool)
