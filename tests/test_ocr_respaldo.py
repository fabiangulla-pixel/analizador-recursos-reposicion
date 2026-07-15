"""Tests de ingesta/ocr_respaldo.py — localización de Tesseract y OCR de páginas."""

import ingesta.ocr_respaldo as ocr_respaldo
from ingesta.ocr_respaldo import localizar_tesseract, ocr_disponible, ocr_pagina_pdf


def test_localizar_usa_path_del_sistema_primero(monkeypatch):
    monkeypatch.setattr(ocr_respaldo.shutil, "which", lambda _: "/usr/bin/tesseract")
    assert localizar_tesseract() == "/usr/bin/tesseract"


def test_localizar_usa_cache_si_no_hay_en_path(tmp_path, monkeypatch):
    exe = tmp_path / "tesseract.exe"
    exe.write_text("stub")
    cache = tmp_path / "tesseract_path.txt"
    cache.write_text(str(exe), encoding="utf-8")

    monkeypatch.setattr(ocr_respaldo.shutil, "which", lambda _: None)
    monkeypatch.setattr(ocr_respaldo, "_CACHE_RUTA", cache)
    assert localizar_tesseract() == str(exe)


def test_localizar_prueba_candidatos_y_escribe_cache(tmp_path, monkeypatch):
    exe = tmp_path / "Tesseract-OCR" / "tesseract.exe"
    exe.parent.mkdir()
    exe.write_text("stub")
    cache = tmp_path / "tesseract_path.txt"

    monkeypatch.setattr(ocr_respaldo.shutil, "which", lambda _: None)
    monkeypatch.setattr(ocr_respaldo, "_CACHE_RUTA", cache)
    monkeypatch.setattr(ocr_respaldo, "_CANDIDATOS", [exe])

    assert localizar_tesseract() == str(exe)
    assert cache.read_text(encoding="utf-8").strip() == str(exe)


def test_localizar_devuelve_none_si_no_encuentra_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(ocr_respaldo.shutil, "which", lambda _: None)
    monkeypatch.setattr(ocr_respaldo, "_CACHE_RUTA", tmp_path / "no_existe.txt")
    monkeypatch.setattr(ocr_respaldo, "_CANDIDATOS", [tmp_path / "tampoco_existe.exe"])
    assert localizar_tesseract() is None


def test_ocr_disponible_refleja_localizar(monkeypatch):
    monkeypatch.setattr(ocr_respaldo, "localizar_tesseract", lambda: None)
    assert ocr_disponible() is False
    monkeypatch.setattr(ocr_respaldo, "localizar_tesseract", lambda: "/bin/tesseract")
    assert ocr_disponible() is True


def test_ocr_pagina_pdf_sin_tesseract_devuelve_vacio(monkeypatch):
    monkeypatch.setattr(ocr_respaldo, "localizar_tesseract", lambda: None)
    assert ocr_pagina_pdf("cualquier_ruta.pdf", 1) == ""


def test_configurar_tessdata_prefix_usa_primera_carpeta_con_spa(tmp_path, monkeypatch):
    sin_spa = tmp_path / "sin_spa"
    sin_spa.mkdir()
    con_spa = tmp_path / "con_spa"
    con_spa.mkdir()
    (con_spa / "spa.traineddata").write_text("stub")

    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)
    monkeypatch.setattr(ocr_respaldo, "_CANDIDATOS_TESSDATA", [sin_spa, con_spa])

    # monkeypatch.delenv sobre una variable AUSENTE no registra nada que
    # restaurar (ver _pytest/monkeypatch.py: delitem no apila undo si
    # `name not in dic`). Como _configurar_tessdata_prefix() escribe
    # os.environ directamente (no vía monkeypatch), esa escritura queda sin
    # rastrear y contamina la sesión completa de pytest para tests
    # posteriores. Limpiar explícitamente en el propio test.
    try:
        ocr_respaldo._configurar_tessdata_prefix()
        assert ocr_respaldo.os.environ["TESSDATA_PREFIX"] == str(con_spa)
    finally:
        ocr_respaldo.os.environ.pop("TESSDATA_PREFIX", None)


def test_configurar_tessdata_prefix_no_pisa_variable_existente(monkeypatch):
    monkeypatch.setenv("TESSDATA_PREFIX", "/ya/configurado")
    monkeypatch.setattr(ocr_respaldo, "_CANDIDATOS_TESSDATA", [])
    ocr_respaldo._configurar_tessdata_prefix()
    assert ocr_respaldo.os.environ["TESSDATA_PREFIX"] == "/ya/configurado"
