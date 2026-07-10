"""
comparador.py
Compara cada argumento/grupo contra la resolución sancionatoria base
para determinar si ya fue resuelto, probablemente resuelto, o es nuevo.
"""

from typing import Any

import numpy as np

from procesamiento.vectorizador import vectorizar
from utils.logger import obtener_logger

logger = obtener_logger()


def _clasificar_resolucion(similitud: float, umbral: float) -> tuple[str, str, bool]:
    """
    Clasifica el estado de resolución de un argumento.

    Returns:
        (ya_resuelto_str, confianza, requiere_revision_humana)
    """
    if similitud >= umbral:
        return "SI", "alta", False
    elif similitud >= umbral * 0.80:
        return "PROBABLEMENTE", "media", True
    else:
        return "NO", "alta" if similitud < umbral * 0.50 else "media", similitud >= umbral * 0.60


def comparar_con_base(
    argumentos: list[dict[str, Any]],
    embeddings_args: np.ndarray,
    bloques_base: list[dict[str, Any]],
    umbral_resuelto: float = 0.70,
) -> list[dict[str, Any]]:
    """
    Para cada argumento, busca el fragmento más similar en la resolución base
    y determina si ya fue resuelto.

    Añade a cada argumento:
        - similitud_base
        - ya_resuelto_en_decision_base
        - evidencia_resolucion_base
        - confianza
        - requiere_revision_humana
    """
    if not bloques_base:
        logger.warning("No hay bloques de la resolución base. No se puede comparar.")
        for arg in argumentos:
            arg.update(
                {
                    "similitud_base": 0.0,
                    "ya_resuelto_en_decision_base": "NO",
                    "evidencia_resolucion_base": "",
                    "confianza": "baja",
                    "requiere_revision_humana": True,
                }
            )
        return argumentos

    textos_base = [b["texto"] for b in bloques_base]
    logger.info(f"Vectorizando {len(textos_base)} bloques de la resolución base...")
    emb_base = vectorizar(textos_base)
    # Garantizar shape 2D (n_bloques, dim)
    if emb_base.ndim == 1:
        emb_base = emb_base.reshape(1, -1)

    logger.info(f"Comparando {len(argumentos)} argumentos contra la base...")
    for i, arg in enumerate(argumentos):
        emb_arg = embeddings_args[i]
        # Similitud contra todos los bloques de la base
        sims = emb_base @ emb_arg
        sims = np.atleast_1d(sims)
        idx_max = int(np.argmax(sims))
        sim_max = float(sims[idx_max])

        ya_resuelto, confianza, rev_humana = _clasificar_resolucion(sim_max, umbral_resuelto)

        arg["similitud_base"] = round(sim_max, 4)
        arg["ya_resuelto_en_decision_base"] = ya_resuelto
        arg["evidencia_resolucion_base"] = bloques_base[idx_max]["texto"][:400]
        arg["confianza"] = confianza
        arg["requiere_revision_humana"] = rev_humana

    resueltos = sum(1 for a in argumentos if a["ya_resuelto_en_decision_base"] == "SI")
    probables = sum(1 for a in argumentos if a["ya_resuelto_en_decision_base"] == "PROBABLEMENTE")
    nuevos = sum(1 for a in argumentos if a["ya_resuelto_en_decision_base"] == "NO")
    logger.info(
        f"Comparación: {resueltos} resueltos, {probables} probablemente resueltos, {nuevos} nuevos."
    )
    return argumentos


def comparar_grupos_con_base(
    grupos: list[dict[str, Any]],
    bloques_base: list[dict[str, Any]],
    umbral_resuelto: float = 0.70,
) -> list[dict[str, Any]]:
    """
    Compara cada grupo argumental (usando su centroide) contra la base.
    Añade estado de resolución al grupo.
    """
    if not bloques_base:
        for g in grupos:
            g["ya_resuelto"] = "NO"
            g["evidencia_base"] = ""
            g["similitud_base"] = 0.0
        return grupos

    textos_base = [b["texto"] for b in bloques_base]
    emb_base = vectorizar(textos_base)
    if emb_base.ndim == 1:
        emb_base = emb_base.reshape(1, -1)

    for grupo in grupos:
        centroide = grupo["centroide"]
        sims = np.atleast_1d(emb_base @ centroide)
        idx_max = int(np.argmax(sims))
        sim_max = float(sims[idx_max])
        ya_resuelto, _, _ = _clasificar_resolucion(sim_max, umbral_resuelto)

        grupo["ya_resuelto"] = ya_resuelto
        grupo["similitud_base"] = round(sim_max, 4)
        grupo["evidencia_base"] = bloques_base[idx_max]["texto"][:400]

    return grupos
