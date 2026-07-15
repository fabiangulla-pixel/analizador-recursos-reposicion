"""Tests de ingesta/reader.py — lectura de archivos (sin PDFs reales)."""

import pytest

import ingesta.reader as reader
from ingesta.ocr_respaldo import ocr_disponible
from ingesta.reader import leer_archivo, leer_carpeta


def test_txt_divide_por_doble_salto(tmp_path):
    f = tmp_path / "recurso.txt"
    f.write_text("bloque uno\n\nbloque dos", encoding="utf-8")
    bloques = leer_archivo(str(f))
    assert [b["texto"] for b in bloques] == ["bloque uno", "bloque dos"]
    assert bloques[0]["pagina"] == 1
    assert bloques[1]["pagina"] == 2
    assert bloques[0]["archivo"] == "recurso.txt"


def test_txt_fallback_latin1(tmp_path):
    f = tmp_path / "latin.txt"
    f.write_bytes("sanción y niñez".encode("latin-1"))
    bloques = leer_archivo(str(f), encoding_fallback="latin-1")
    assert bloques[0]["texto"] == "sanción y niñez"


def test_extension_no_soportada_devuelve_vacio(tmp_path):
    f = tmp_path / "imagen.jpg"
    f.write_bytes(b"\xff\xd8")
    assert leer_archivo(str(f)) == []


def test_leer_carpeta_inexistente_devuelve_vacio(tmp_path):
    assert leer_carpeta(str(tmp_path / "no_existe"), [".txt"]) == []


def test_leer_carpeta_filtra_extensiones_y_ordena(tmp_path):
    (tmp_path / "b.txt").write_text("contenido de be", encoding="utf-8")
    (tmp_path / "a.txt").write_text("contenido de a", encoding="utf-8")
    (tmp_path / "ignorar.jpg").write_bytes(b"x")
    bloques = leer_carpeta(str(tmp_path), [".txt"])
    assert [b["archivo"] for b in bloques] == ["a.txt", "b.txt"]


def _pdf_con_texto_nativo(ruta: str, texto: str) -> None:
    import fitz

    doc = fitz.open()
    pagina = doc.new_page()
    pagina.insert_text((72, 72), texto, fontsize=14)
    doc.save(ruta)
    doc.close()


def _pdf_escaneado_sin_texto(ruta: str, texto: str) -> None:
    """Genera un PDF cuya única página es una imagen (sin capa de texto)."""
    import fitz
    from PIL import Image, ImageDraw

    imagen = Image.new("RGB", (800, 200), "white")
    ImageDraw.Draw(imagen).text((20, 80), texto, fill="black")
    ruta_png = ruta.replace(".pdf", ".png")
    imagen.save(ruta_png)

    doc = fitz.open()
    pagina = doc.new_page(width=800, height=200)
    pagina.insert_image(pagina.rect, filename=ruta_png)
    doc.save(ruta)
    doc.close()


def test_pdf_con_texto_nativo_se_marca_como_nativo(tmp_path):
    ruta = str(tmp_path / "recurso.pdf")
    _pdf_con_texto_nativo(ruta, "Texto real y seleccionable del recurso.")
    bloques = leer_archivo(ruta)
    assert len(bloques) == 1
    assert bloques[0]["fuente"] == "nativo"
    assert "Texto real" in bloques[0]["texto"]


def test_pdf_escaneado_sin_ocr_disponible_se_omite(tmp_path, monkeypatch):
    ruta = str(tmp_path / "escaneado.pdf")
    _pdf_escaneado_sin_texto(ruta, "contenido escaneado")
    monkeypatch.setattr(reader, "ocr_disponible", lambda: False)
    assert leer_archivo(ruta) == []


def test_pdf_escaneado_con_ocr_mockeado_se_marca_como_ocr(tmp_path, monkeypatch):
    ruta = str(tmp_path / "escaneado.pdf")
    _pdf_escaneado_sin_texto(ruta, "contenido escaneado")
    monkeypatch.setattr(reader, "ocr_disponible", lambda: True)
    monkeypatch.setattr(reader, "ocr_pagina_pdf", lambda ruta_pdf, num, lang="spa": "texto via ocr")

    bloques = leer_archivo(ruta)
    assert len(bloques) == 1
    assert bloques[0]["fuente"] == "ocr"
    assert bloques[0]["texto"] == "texto via ocr"


@pytest.mark.skipif(not ocr_disponible(), reason="Tesseract no instalado en esta máquina")
def test_pdf_escaneado_ocr_real_recupera_texto_reconocible(tmp_path):
    ruta = str(tmp_path / "escaneado_real.pdf")
    _pdf_escaneado_sin_texto(ruta, "RECURSO DE REPOSICION")
    bloques = leer_archivo(ruta)
    assert len(bloques) == 1
    assert bloques[0]["fuente"] == "ocr"
    # OCR real sobre texto sintético: no exigimos exactitud perfecta ni que
    # respete la tilde, solo la raíz de la palabra clave más distintiva
    # ('ó'.upper() sigue siendo 'Ó', no 'O').
    assert "REPOSICI" in bloques[0]["texto"].upper()
