"""Tests de ingesta/reader.py — lectura de archivos (sin PDFs reales)."""

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
