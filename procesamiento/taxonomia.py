"""
taxonomia.py
Clasifica cada argumento en una categoría jurídica reconocible (debido
proceso, caducidad, falta de competencia, etc.) por similitud semántica
contra descripciones curadas de cada categoría. No entrena ni carga un
modelo nuevo: reutiliza el mismo motor de embeddings ya cargado para
segmentar/agrupar los argumentos.

Es una heurística de apoyo, no una calificación jurídica vinculante: el
abogado decide. Por eso se conserva la similitud junto a la categoría
asignada, para que quede claro cuándo la clasificación es dudosa.
"""

from typing import Any

import numpy as np

from utils.logger import obtener_logger

logger = obtener_logger()

SIN_CLASIFICAR = "Sin clasificar"

CATEGORIAS: dict[str, str] = {
    "Debido proceso": (
        "El acto administrativo vulnera el debido proceso porque no se notificó "
        "correctamente, no se permitió ejercer el derecho de defensa o "
        "contradicción, o se omitieron etapas procesales obligatorias."
    ),
    "Caducidad o prescripción": (
        "La facultad sancionatoria de la entidad ha caducado o prescrito porque "
        "transcurrió el término legal para investigar o sancionar los hechos."
    ),
    "Falta de competencia": (
        "La autoridad que expidió el acto carecía de competencia legal, funcional "
        "o territorial para hacerlo."
    ),
    "Proporcionalidad de la sanción": (
        "La sanción impuesta es desproporcionada, excesiva o no se ajusta a la "
        "gravedad de la falta ni a los criterios legales de graduación de la pena."
    ),
    "Valoración probatoria": (
        "Las pruebas del expediente no fueron valoradas correctamente, se "
        "desconocieron pruebas aportadas por el investigado, o no existe prueba "
        "suficiente que soporte la sanción impuesta."
    ),
    "Nulidad por vicios de forma": (
        "El acto administrativo tiene vicios de forma: falta de motivación, "
        "ausencia de requisitos formales, o defectos en el procedimiento de "
        "su expedición."
    ),
    "Falsa motivación": (
        "El acto se basa en una falsa motivación porque los hechos o el derecho "
        "invocados no corresponden a la realidad o fueron tergiversados."
    ),
}


def clasificar_argumentos(
    argumentos: list[dict[str, Any]],
    embeddings: np.ndarray,
    umbral_minimo: float = 0.30,
) -> list[dict[str, Any]]:
    """
    Añade a cada argumento 'categoria_juridica' y 'categoria_similitud'.
    Si la mejor similitud no alcanza umbral_minimo, la categoría queda como
    SIN_CLASIFICAR (más honesto que forzar una categoría poco pertinente).
    """
    if len(argumentos) == 0:
        return argumentos

    from procesamiento.vectorizador import vectorizar

    nombres = list(CATEGORIAS.keys())
    emb_categorias = vectorizar(list(CATEGORIAS.values()))

    for i, arg in enumerate(argumentos):
        sims = np.atleast_1d(emb_categorias @ embeddings[i])
        idx_max = int(np.argmax(sims))
        sim_max = float(sims[idx_max])

        arg["categoria_similitud"] = round(sim_max, 4)
        arg["categoria_juridica"] = nombres[idx_max] if sim_max >= umbral_minimo else SIN_CLASIFICAR

    conteo: dict[str, int] = {}
    for arg in argumentos:
        cat = arg["categoria_juridica"]
        conteo[cat] = conteo.get(cat, 0) + 1
    logger.info(f"Clasificación por categoría jurídica: {conteo}")
    return argumentos
