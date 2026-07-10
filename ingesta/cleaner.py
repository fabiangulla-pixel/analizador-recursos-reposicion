"""
cleaner.py
Limpia y normaliza texto extraído de documentos.
Elimina ruido sin destruir contenido jurídico relevante.
"""

import re
from typing import List, Dict, Any


# Patrones de ruido comunes en documentos jurídicos escaneados/exportados
_PATRONES_RUIDO = [
    r"Página\s+\d+\s+de\s+\d+",
    r"^\s*\d+\s*$",              # Líneas con solo número de página
    r"_{3,}",                    # Líneas de subrayado decorativo
    r"-{3,}",                    # Líneas de guiones decorativos
    r"\f",                       # Saltos de página (form feed)
]

_RE_RUIDO = re.compile("|".join(_PATRONES_RUIDO), re.IGNORECASE | re.MULTILINE)
_RE_ESPACIOS = re.compile(r" {2,}")
_RE_SALTOS = re.compile(r"\n{3,}")


def limpiar_texto(texto: str) -> str:
    """
    Aplica limpieza básica a un bloque de texto:
    - elimina patrones de ruido,
    - normaliza espacios y saltos de línea,
    - recorta espacios extremos.
    """
    texto = _RE_RUIDO.sub(" ", texto)
    texto = _RE_ESPACIOS.sub(" ", texto)
    texto = _RE_SALTOS.sub("\n\n", texto)
    return texto.strip()


def limpiar_bloques(bloques: List[Dict[str, Any]], min_longitud: int = 80) -> List[Dict[str, Any]]:
    """
    Aplica limpiar_texto() a cada bloque y descarta los que queden
    con menos de min_longitud caracteres (ruido puro).

    Args:
        bloques: Lista de dicts {texto, pagina, archivo}.
        min_longitud: Longitud mínima en caracteres para conservar un bloque.

    Returns:
        Lista filtrada y limpiada.
    """
    resultado = []
    for bloque in bloques:
        texto_limpio = limpiar_texto(bloque["texto"])
        if len(texto_limpio) >= min_longitud:
            resultado.append({**bloque, "texto": texto_limpio})
    return resultado
