"""
pdf_anotado.py
Genera una copia de cada recurso PDF original con los argumentos resaltados
y comentados: dónde está cada argumento, a qué grupo pertenece y si ya fue
resuelto en la resolución base. Mismo patrón de anotación (Highlight +
comentario vía fitz) usado en la skill /verificar-creditos.

Limitación honesta: solo se pueden resaltar argumentos con fuente "nativo"
(el PDF original tiene capa de texto real). Los argumentos que vinieron de
OCR de respaldo (ver ingesta/ocr_respaldo.py) no tienen texto seleccionable
en el PDF de origen — no hay nada que buscar/resaltar ahí — y quedan
señalados aparte, no se omiten en silencio.
"""

import os
from typing import Any

from utils.logger import obtener_logger

logger = obtener_logger()

_LARGO_BUSQUEDA = 80  # snippet corto y robusto para search_for en PDFs reales

# Mismo esquema de color que exportacion/word_export.py: consistencia visual
# entre el informe Word y el PDF anotado.
_VERDE = (0.11, 0.42, 0.23)
_NARANJA = (0.90, 0.49, 0.0)
_ROJO = (0.75, 0.22, 0.17)


def _color_por_estado(estado: str) -> tuple[float, float, float]:
    e = (estado or "").upper()
    if e == "SI":
        return _VERDE
    if e == "PROBABLEMENTE":
        return _NARANJA
    return _ROJO


def _snippet_busqueda(texto: str, largo: int = _LARGO_BUSQUEDA) -> str:
    """Fragmento corto y limpio para buscar con fitz.search_for (más robusto
    que buscar párrafos largos, que pueden partirse distinto en la capa de
    texto del PDF)."""
    normalizado = " ".join(texto.split())
    if len(normalizado) <= largo:
        return normalizado
    fragmento = normalizado[:largo]
    return fragmento.rsplit(" ", 1)[0] if " " in fragmento else fragmento


def _comentario_argumento(arg: dict[str, Any]) -> str:
    grupo = arg.get("grupo_id", 0) + 1
    estado = arg.get("ya_resuelto_en_decision_base", "N/D")
    similitud = arg.get("similitud_base", 0.0)
    recurrente = " · recurrente en varios documentos" if arg.get("recurrente") else ""
    return (
        f"Grupo {grupo}{recurrente}\n"
        f"¿Ya resuelto en la resolución base? {estado} (similitud {similitud:.0%})"
    )


def _anotar_un_pdf(ruta_pdf: str, argumentos_doc: list[dict[str, Any]], ruta_salida: str) -> dict:
    import fitz

    doc = fitz.open(ruta_pdf)
    resaltados, no_encontrados, omitidos_ocr = 0, [], 0

    for arg in argumentos_doc:
        if arg.get("fuente") != "nativo":
            omitidos_ocr += 1
            continue

        pagina_num = arg.get("pagina", 1)
        if pagina_num < 1 or pagina_num > doc.page_count:
            no_encontrados.append(arg.get("id"))
            continue

        pagina = doc.load_page(pagina_num - 1)
        snippet = _snippet_busqueda(arg.get("texto", ""))
        rects = pagina.search_for(snippet) if snippet else []
        if not rects:
            no_encontrados.append(arg.get("id"))
            continue

        annot = pagina.add_highlight_annot(rects[0])
        annot.set_colors(stroke=_color_por_estado(arg.get("ya_resuelto_en_decision_base")))
        annot.set_info(title="Analizador de Recursos", content=_comentario_argumento(arg))
        annot.update()
        resaltados += 1

    doc.save(ruta_salida, garbage=3, deflate=True)
    doc.close()
    return {
        "resaltados": resaltados,
        "no_encontrados": len(no_encontrados),
        "omitidos_por_ocr": omitidos_ocr,
    }


def generar_pdfs_anotados(
    argumentos: list[dict[str, Any]],
    carpeta_recursos: str,
    carpeta_salida: str,
) -> dict[str, dict]:
    """
    Genera un PDF anotado por cada documento fuente en formato .pdf que tenga
    argumentos. Devuelve {nombre_archivo: estadísticas} para el reporte.
    Los documentos .docx/.txt no se anotan (no aplica el mismo mecanismo).
    """
    por_documento: dict[str, list[dict[str, Any]]] = {}
    for arg in argumentos:
        nombre = arg.get("archivo", "")
        if nombre.lower().endswith(".pdf"):
            por_documento.setdefault(nombre, []).append(arg)

    if not por_documento:
        return {}

    carpeta_anotados = os.path.join(carpeta_salida, "recursos_anotados")
    os.makedirs(carpeta_anotados, exist_ok=True)

    resultado = {}
    for nombre, argumentos_doc in por_documento.items():
        ruta_original = os.path.join(carpeta_recursos, nombre)
        if not os.path.exists(ruta_original):
            logger.warning(f"No se pudo anotar {nombre}: no existe en {carpeta_recursos}.")
            continue

        ruta_salida = os.path.join(carpeta_anotados, f"anotado_{nombre}")
        try:
            stats = _anotar_un_pdf(ruta_original, argumentos_doc, ruta_salida)
            resultado[nombre] = stats
            logger.info(
                f"PDF anotado: {nombre} — {stats['resaltados']} resaltados, "
                f"{stats['no_encontrados']} no encontrados, "
                f"{stats['omitidos_por_ocr']} omitidos (fuente OCR)."
            )
        except Exception as e:
            logger.warning(f"Error anotando {nombre}: {e}")

    return resultado
