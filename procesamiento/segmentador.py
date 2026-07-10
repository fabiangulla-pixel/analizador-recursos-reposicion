"""
segmentador.py
Detecta y extrae bloques argumentativos de texto jurídico.
Estrategia: divide por párrafos y aplica heurísticas para identificar
bloques con contenido argumentativo (vs encabezados, datos, etc.).
"""

import re
from typing import List, Dict, Any

from utils.logger import obtener_logger

logger = obtener_logger()

# Palabras clave que sugieren contenido argumentativo
_INDICADORES_ARGUMENTO = re.compile(
    r"\b(consider[ao]|alega|manifiesta|sostiene|arguye|señala|indica|afirma|"
    r"solicita|pide|pretende|aduce|expone|reclama|impugna|controvierte|"
    r"vulnera|viola|infringe|desconoce|incumple|omite|lesiona|"
    r"derecho|garantía|principio|debido proceso|nulidad|prescripción|"
    r"caducidad|inconstitucional|ilegal|arbitrario|"
    r"por tanto|en consecuencia|por lo anterior|en conclusión)\b",
    re.IGNORECASE,
)


def segmentar_bloques(
    bloques: List[Dict[str, Any]], min_longitud: int = 80
) -> List[Dict[str, Any]]:
    """
    Toma bloques crudos (un bloque = texto de una página o sección)
    y los divide en argumentos individuales por párrafo.
    Filtra párrafos sin contenido argumentativo aparente.

    Devuelve lista de argumentos con: {id, texto, pagina, archivo, es_argumentativo}.
    """
    argumentos = []
    id_arg = 0

    for bloque in bloques:
        parrafos = _dividir_parrafos(bloque["texto"])
        for parrafo in parrafos:
            if len(parrafo) < min_longitud:
                continue
            es_arg = bool(_INDICADORES_ARGUMENTO.search(parrafo))
            argumentos.append({
                "id": id_arg,
                "texto": parrafo,
                "pagina": bloque["pagina"],
                "archivo": bloque["archivo"],
                "es_argumentativo": es_arg,
            })
            id_arg += 1

    total = len(argumentos)
    arg_count = sum(1 for a in argumentos if a["es_argumentativo"])
    logger.info(f"Segmentación: {total} bloques, {arg_count} marcados como argumentativos.")
    return argumentos


def _dividir_parrafos(texto: str) -> List[str]:
    """
    Divide un texto en párrafos por doble salto de línea o punto seguido de mayúscula
    al inicio de línea. Limpia cada párrafo.
    """
    # Primero dividir por doble salto
    partes = re.split(r"\n{2,}", texto)
    resultado = []
    for parte in partes:
        parte = parte.replace("\n", " ").strip()
        if parte:
            resultado.append(parte)
    return resultado
