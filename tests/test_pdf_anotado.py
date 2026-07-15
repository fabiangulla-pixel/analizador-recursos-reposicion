"""Tests de exportacion/pdf_anotado.py — resaltado de argumentos en el PDF original."""

from exportacion.pdf_anotado import (
    _color_por_estado,
    _comentario_argumento,
    _snippet_busqueda,
    generar_pdfs_anotados,
)


def _pdf_con_texto(ruta: str, lineas: list[str]) -> None:
    import fitz

    doc = fitz.open()
    pagina = doc.new_page()
    y = 72
    for linea in lineas:
        pagina.insert_text((72, y), linea, fontsize=12)
        y += 20
    doc.save(ruta)
    doc.close()


def test_snippet_busqueda_recorta_a_limite_de_palabra():
    texto = "El recurrente alega que la resolución vulnera el debido proceso de forma evidente"
    snippet = _snippet_busqueda(texto, largo=30)
    assert len(snippet) <= 30
    assert snippet == "El recurrente alega que la"  # no corta "resolución" a mitad de palabra


def test_snippet_busqueda_normaliza_espacios():
    assert _snippet_busqueda("hola   \n  mundo", largo=50) == "hola mundo"


def test_color_por_estado():
    assert _color_por_estado("SI") != _color_por_estado("NO")
    assert _color_por_estado("PROBABLEMENTE") != _color_por_estado("SI")
    assert _color_por_estado("") == _color_por_estado("NO")  # default = rojo


def test_comentario_incluye_grupo_y_estado():
    arg = {
        "grupo_id": 2,
        "ya_resuelto_en_decision_base": "SI",
        "similitud_base": 0.83,
        "recurrente": True,
    }
    comentario = _comentario_argumento(arg)
    assert "Grupo 3" in comentario
    assert "recurrente" in comentario
    assert "SI" in comentario
    assert "83%" in comentario


def test_generar_pdfs_anotados_resalta_argumento_nativo(tmp_path):
    carpeta_recursos = tmp_path / "recursos"
    carpeta_recursos.mkdir()
    carpeta_salida = tmp_path / "salida"

    ruta_pdf = str(carpeta_recursos / "recurso_a.pdf")
    _pdf_con_texto(ruta_pdf, ["El recurrente alega vulneracion del debido proceso."])

    argumentos = [
        {
            "id": 0,
            "texto": "El recurrente alega vulneracion del debido proceso.",
            "pagina": 1,
            "archivo": "recurso_a.pdf",
            "fuente": "nativo",
            "grupo_id": 0,
            "ya_resuelto_en_decision_base": "SI",
            "similitud_base": 0.9,
            "recurrente": False,
        }
    ]

    resultado = generar_pdfs_anotados(argumentos, str(carpeta_recursos), str(carpeta_salida))

    assert resultado["recurso_a.pdf"]["resaltados"] == 1
    assert resultado["recurso_a.pdf"]["no_encontrados"] == 0

    ruta_anotado = carpeta_salida / "recursos_anotados" / "anotado_recurso_a.pdf"
    assert ruta_anotado.exists()

    import fitz

    doc = fitz.open(str(ruta_anotado))
    anotaciones = list(doc[0].annots())
    assert len(anotaciones) == 1
    assert anotaciones[0].info["content"].startswith("Grupo 1")
    doc.close()


def test_generar_pdfs_anotados_omite_argumentos_de_ocr_sin_fallar(tmp_path):
    carpeta_recursos = tmp_path / "recursos"
    carpeta_recursos.mkdir()
    carpeta_salida = tmp_path / "salida"

    ruta_pdf = str(carpeta_recursos / "escaneado.pdf")
    _pdf_con_texto(ruta_pdf, ["texto irrelevante"])  # el PDF real no importa aquí

    argumentos = [
        {
            "id": 0,
            "texto": "argumento reconocido por ocr",
            "pagina": 1,
            "archivo": "escaneado.pdf",
            "fuente": "ocr",
            "grupo_id": 0,
            "ya_resuelto_en_decision_base": "NO",
            "similitud_base": 0.1,
        }
    ]

    resultado = generar_pdfs_anotados(argumentos, str(carpeta_recursos), str(carpeta_salida))
    assert resultado["escaneado.pdf"]["omitidos_por_ocr"] == 1
    assert resultado["escaneado.pdf"]["resaltados"] == 0


def test_generar_pdfs_anotados_ignora_documentos_no_pdf(tmp_path):
    argumentos = [
        {"id": 0, "texto": "algo", "pagina": 1, "archivo": "recurso.docx", "fuente": "nativo"}
    ]
    resultado = generar_pdfs_anotados(argumentos, str(tmp_path), str(tmp_path / "salida"))
    assert resultado == {}
    assert not (tmp_path / "salida").exists()  # no crea nada si no hay PDFs que anotar


def test_generar_pdfs_anotados_archivo_original_faltante_no_falla(tmp_path):
    argumentos = [
        {
            "id": 0,
            "texto": "algo",
            "pagina": 1,
            "archivo": "no_existe.pdf",
            "fuente": "nativo",
            "grupo_id": 0,
        }
    ]
    resultado = generar_pdfs_anotados(argumentos, str(tmp_path), str(tmp_path / "salida"))
    assert resultado == {}  # se registró el aviso, no crasheó


def test_generar_pdfs_anotados_texto_no_encontrado_se_reporta(tmp_path):
    carpeta_recursos = tmp_path / "recursos"
    carpeta_recursos.mkdir()
    carpeta_salida = tmp_path / "salida"

    ruta_pdf = str(carpeta_recursos / "recurso_b.pdf")
    _pdf_con_texto(ruta_pdf, ["Contenido totalmente distinto al argumento buscado."])

    argumentos = [
        {
            "id": 0,
            "texto": "Este texto no aparece en el PDF para nada.",
            "pagina": 1,
            "archivo": "recurso_b.pdf",
            "fuente": "nativo",
            "grupo_id": 0,
        }
    ]
    resultado = generar_pdfs_anotados(argumentos, str(carpeta_recursos), str(carpeta_salida))
    assert resultado["recurso_b.pdf"]["resaltados"] == 0
    assert resultado["recurso_b.pdf"]["no_encontrados"] == 1
