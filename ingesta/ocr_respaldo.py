"""
ocr_respaldo.py
OCR de respaldo para páginas de PDF sin texto embebido (documentos escaneados).
Se activa solo cuando pdfplumber no logra extraer texto de una página — el
recurso no queda fuera del análisis solo por ser una imagen.

Sigue el mismo patrón de localización de Tesseract usado en Bashkar Station:
shutil.which() -> archivo de caché tesseract_path.txt -> rutas candidatas de
Program Files -> None (OCR no disponible, se degrada sin romper el pipeline).
"""

import os
import shutil
from pathlib import Path

from utils.logger import obtener_logger

logger = obtener_logger()

_RAIZ_PROYECTO = Path(__file__).parent.parent
_CACHE_RUTA = _RAIZ_PROYECTO / "tesseract_path.txt"
_CANDIDATOS = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
]
# El instalador de Tesseract para Windows no siempre trae spa.traineddata;
# mismo patrón que Bashkar Station: buscar el paquete de idioma en la carpeta
# de usuario antes que en la carpeta de instalación.
_CANDIDATOS_TESSDATA = [
    Path.home() / "tessdata",
    Path(r"C:\Users\Lenovo\tessdata"),
    Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tessdata"),
]

_DPI_RENDER = 200  # suficiente para OCR de texto de tamaño carta/oficio


def _configurar_tessdata_prefix() -> None:
    """Fuerza TESSDATA_PREFIX a la primera carpeta candidata que tenga spa.traineddata."""
    if "TESSDATA_PREFIX" in os.environ:
        return
    for carpeta in _CANDIDATOS_TESSDATA:
        if (carpeta / "spa.traineddata").exists():
            os.environ["TESSDATA_PREFIX"] = str(carpeta)
            return


def localizar_tesseract() -> str | None:
    """Devuelve la ruta al ejecutable de Tesseract, o None si no está instalado."""
    en_path = shutil.which("tesseract")
    if en_path:
        return en_path

    if _CACHE_RUTA.exists():
        cacheada = _CACHE_RUTA.read_text(encoding="utf-8").strip()
        if Path(cacheada).exists():
            return cacheada

    for candidato in _CANDIDATOS:
        if candidato.exists():
            _CACHE_RUTA.write_text(str(candidato), encoding="utf-8")
            return str(candidato)

    return None


def ocr_disponible() -> bool:
    return localizar_tesseract() is not None


def ocr_pagina_pdf(ruta_pdf: str, numero_pagina: int, lang: str = "spa") -> str:
    """
    Renderiza una página de un PDF (1-indexada) como imagen y le aplica OCR.
    Devuelve el texto reconocido, o cadena vacía si OCR no está disponible o falla.
    """
    tesseract_cmd = localizar_tesseract()
    if not tesseract_cmd:
        return ""

    try:
        import fitz  # pymupdf
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        _configurar_tessdata_prefix()

        doc = fitz.open(ruta_pdf)
        try:
            pagina = doc[numero_pagina - 1]
            pixmap = pagina.get_pixmap(dpi=_DPI_RENDER)
            imagen_bytes = pixmap.tobytes("png")
        finally:
            doc.close()

        from io import BytesIO

        from PIL import Image

        imagen = Image.open(BytesIO(imagen_bytes)).convert("L")
        texto = pytesseract.image_to_string(imagen, config=f"--oem 3 --psm 3 -l {lang}")
        return texto
    except Exception as e:
        logger.warning(f"OCR de respaldo falló en página {numero_pagina} de {ruta_pdf}: {e}")
        return ""
