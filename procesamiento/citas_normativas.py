"""
citas_normativas.py
Extrae citas de normas y jurisprudencia colombianas de un texto (offline, regex).
Inspirado en el diseño de eyecite (Free Law Project) adaptado al derecho colombiano.

Cobertura v1: leyes (con artículo si es explícito), decretos, resoluciones,
sentencias de la Corte Constitucional (C-/T-/SU-), códigos por sigla y
Constitución Política. Los radicados del Consejo de Estado y de la CSJ quedan
para v2: su formato es demasiado variable para regex confiable.
"""

import re
from typing import Any

# "artículo 76 de la Ley 1437 de 2011" o "Ley 1437 de 2011".
# El lookbehind evita capturar el "Ley" interno de "Decreto Ley 019 de 2012".
_RE_LEY = re.compile(
    r"(?:[Aa]rt(?:ículo|\.)?\s*(\d+[A-Za-z]?)\s+de\s+la\s+)?"
    r"(?<!ecreto\s)[Ll]ey\s+(?:[Ee]statutaria\s+)?(\d{1,4})\s+de\s+(\d{4})"
)
# "artículo 5 del Decreto 1082 de 2015" o "Decreto Ley 019 de 2012"
_RE_DECRETO = re.compile(
    r"(?:[Aa]rt(?:ículo|\.)?\s*(\d+[A-Za-z]?)\s+del\s+)?"
    r"[Dd]ecreto(?:\s+[Ll]ey|\s+[Ll]egislativo|\s+[Rr]eglamentario)?\s+(\d{1,5})\s+de\s+(\d{4})"
)
_RE_RESOLUCION = re.compile(r"[Rr]esoluci[oó]n\s+(?:[Nn][o°.\s]{0,3})?(\d{1,6})\s+de\s+(\d{4})")
# "Sentencia C-123 de 2020", "T-025/04", "SU-1184 de 2001"
_RE_SENTENCIA = re.compile(r"\b(C|T|SU)\s*-\s*(\d{1,4})\s*(?:de\s+|/)(\d{2,4})\b")
_RE_CODIGO = re.compile(r"\b(CPACA|CGP|CPC|CST|CPP|CCA)\b")
_RE_CONSTITUCION = re.compile(
    r"(?:[Aa]rt(?:ículo|\.)?\s*(\d+[A-Za-z]?)\s+de\s+la\s+)?"
    r"[Cc]onstituci[oó]n\s+[Pp]ol[ií]tica"
)


def _anio4(anio: str) -> str:
    """Expande años de 2 dígitos: 04 → 2004, 98 → 1998 (corte en 30)."""
    if len(anio) == 4:
        return anio
    return ("20" + anio) if int(anio) <= 30 else ("19" + anio)


def extraer_citas(texto: str) -> list[str]:
    """
    Devuelve las citas normativas del texto, normalizadas, únicas y en orden
    de aparición. Ej.: ["Ley 1437 de 2011, art. 76", "Sentencia C-123 de 2020"].
    """
    encontradas: list[tuple[int, str]] = []

    for m in _RE_LEY.finditer(texto):
        cita = f"Ley {m[2]} de {m[3]}"
        if m[1]:
            cita += f", art. {m[1]}"
        encontradas.append((m.start(), cita))

    for m in _RE_DECRETO.finditer(texto):
        cita = f"Decreto {m[2]} de {m[3]}"
        if m[1]:
            cita += f", art. {m[1]}"
        encontradas.append((m.start(), cita))

    for m in _RE_RESOLUCION.finditer(texto):
        encontradas.append((m.start(), f"Resolución {m[1]} de {m[2]}"))

    for m in _RE_SENTENCIA.finditer(texto):
        encontradas.append((m.start(), f"Sentencia {m[1]}-{m[2]} de {_anio4(m[3])}"))

    for m in _RE_CODIGO.finditer(texto):
        encontradas.append((m.start(), m[1]))

    for m in _RE_CONSTITUCION.finditer(texto):
        cita = "Constitución Política"
        if m[1]:
            cita += f", art. {m[1]}"
        encontradas.append((m.start(), cita))

    encontradas.sort(key=lambda par: par[0])
    unicas: list[str] = []
    for _, cita in encontradas:
        if cita not in unicas:
            unicas.append(cita)
    return unicas


def anotar_citas(argumentos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Añade a cada argumento el campo 'citas_normativas' (lista de strings)."""
    for arg in argumentos:
        arg["citas_normativas"] = extraer_citas(arg.get("texto", ""))
    return argumentos
