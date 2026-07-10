"""
reader.py
Lee archivos PDF, DOCX y TXT y devuelve una lista de páginas/bloques de texto.
Cada elemento es un dict con: {texto, pagina, archivo}.
No interrumpe la ejecución si un archivo falla: registra el error y continúa.
"""

import os
from typing import List, Dict, Any

from utils.logger import obtener_logger

logger = obtener_logger()


def leer_archivo(ruta: str, encoding_fallback: str = "latin-1") -> List[Dict[str, Any]]:
    """
    Lee un archivo y devuelve lista de bloques: [{texto, pagina, archivo}].
    Soporta .pdf, .docx, .txt.
    """
    ext = os.path.splitext(ruta)[1].lower()
    nombre = os.path.basename(ruta)
    try:
        if ext == ".pdf":
            return _leer_pdf(ruta, nombre)
        elif ext == ".docx":
            return _leer_docx(ruta, nombre)
        elif ext == ".txt":
            return _leer_txt(ruta, nombre, encoding_fallback)
        else:
            logger.warning(f"Extensión no soportada ignorada: {ruta}")
            return []
    except Exception as e:
        logger.error(f"Error leyendo {ruta}: {e}")
        return []


def _leer_pdf(ruta: str, nombre: str) -> List[Dict[str, Any]]:
    """Lee un PDF con pdfplumber. Devuelve una entrada por página."""
    import pdfplumber

    bloques = []
    with pdfplumber.open(ruta) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""
            if texto.strip():
                bloques.append({"texto": texto, "pagina": i, "archivo": nombre})
            else:
                logger.warning(f"{nombre} – página {i} sin texto extraíble (puede ser imagen).")
    if not bloques:
        logger.warning(f"{nombre}: no se pudo extraer texto de ninguna página.")
    return bloques


def _leer_docx(ruta: str, nombre: str) -> List[Dict[str, Any]]:
    """
    Lee un DOCX con python-docx.
    Estrategia: cada párrafo no vacío es un bloque individual.
    Agrupa párrafos consecutivos cortos (< 120 chars) con el siguiente
    para evitar micro-bloques de encabezado sueltos.
    """
    from docx import Document

    doc = Document(ruta)
    bloques = []
    buffer_texto = []
    buffer_pagina = 1
    pagina_simulada = 1
    chars_acumulados = 0

    for parrafo in doc.paragraphs:
        texto = parrafo.text.strip()
        if not texto:
            # Salto de párrafo en blanco: vaciar buffer si tiene contenido sustancial
            if chars_acumulados >= 80:
                bloques.append({
                    "texto": " ".join(buffer_texto),
                    "pagina": buffer_pagina,
                    "archivo": nombre,
                })
                pagina_simulada += 1
                buffer_texto = []
                buffer_pagina = pagina_simulada
                chars_acumulados = 0
            continue

        buffer_texto.append(texto)
        chars_acumulados += len(texto)

        # Si el párrafo es largo o el buffer ya acumuló suficiente, emitir bloque
        if len(texto) >= 120 or chars_acumulados >= 300:
            bloques.append({
                "texto": " ".join(buffer_texto),
                "pagina": buffer_pagina,
                "archivo": nombre,
            })
            pagina_simulada += 1
            buffer_texto = []
            buffer_pagina = pagina_simulada
            chars_acumulados = 0

    # Vaciar lo que quede
    if buffer_texto and chars_acumulados >= 40:
        bloques.append({
            "texto": " ".join(buffer_texto),
            "pagina": buffer_pagina,
            "archivo": nombre,
        })

    if not bloques:
        logger.warning(f"{nombre}: no se extrajo ningún bloque del DOCX.")
    return bloques


def _leer_txt(ruta: str, nombre: str, encoding_fallback: str) -> List[Dict[str, Any]]:
    """Lee un TXT. Divide por saltos de línea dobles como bloques."""
    for enc in ["utf-8", encoding_fallback]:
        try:
            with open(ruta, "r", encoding=enc) as f:
                contenido = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        logger.error(f"No se pudo decodificar {nombre} con ningún encoding.")
        return []

    bloques_raw = [b.strip() for b in contenido.split("\n\n") if b.strip()]
    return [
        {"texto": bloque, "pagina": i + 1, "archivo": nombre}
        for i, bloque in enumerate(bloques_raw)
    ]


def leer_carpeta(
    carpeta: str,
    extensiones: List[str],
    encoding_fallback: str = "latin-1",
) -> List[Dict[str, Any]]:
    """
    Lee todos los archivos soportados en una carpeta.
    Devuelve lista plana de bloques de todos los documentos.
    """
    todos = []
    if not os.path.isdir(carpeta):
        logger.error(f"La carpeta no existe: {carpeta}")
        return todos

    archivos = [
        f for f in os.listdir(carpeta)
        if os.path.splitext(f)[1].lower() in extensiones
    ]
    if not archivos:
        logger.warning(f"No se encontraron archivos soportados en: {carpeta}")
        return todos

    for nombre_archivo in sorted(archivos):
        ruta_completa = os.path.join(carpeta, nombre_archivo)
        logger.info(f"Leyendo: {nombre_archivo}")
        bloques = leer_archivo(ruta_completa, encoding_fallback)
        todos.extend(bloques)

    return todos
