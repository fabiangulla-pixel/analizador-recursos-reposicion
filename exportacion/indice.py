"""
indice.py
Genera una propuesta de índice para la decisión final en formato Markdown.
"""

import os
from typing import Any

from utils.logger import obtener_logger

logger = obtener_logger()


def exportar_indice_decision(grupos: list[dict[str, Any]], carpeta_salida: str) -> None:
    """
    Genera un índice sugerido para redactar la decisión final,
    organizando los grupos por estado de resolución.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta = os.path.join(carpeta_salida, "propuesta_indice_decision.md")

    resueltos = [g for g in grupos if g.get("ya_resuelto") == "SI"]
    probables = [g for g in grupos if g.get("ya_resuelto") == "PROBABLEMENTE"]
    nuevos = [g for g in grupos if g.get("ya_resuelto") == "NO"]

    lineas = [
        "# Propuesta de índice para la decisión final\n",
        "> Este índice fue generado automáticamente. Debe ser revisado y ajustado por el funcionario responsable.\n",
        "---\n",
        "## I. Consideraciones preliminares\n",
        "1. Competencia para resolver",
        "2. Oportunidad de los recursos",
        "3. Legitimación de los recurrentes\n",
        "---\n",
        "## II. Argumentos nuevos (requieren respuesta expresa)\n",
    ]

    if nuevos:
        for i, g in enumerate(nuevos, start=1):
            nombre = g.get("nombre_tentativo", f"Grupo {g['grupo_id'] + 1}")
            lineas.append(f"{i}. **{nombre}**")
            lineas.append(f"   - Documentos: {', '.join(g['archivos'])}")
            lineas.append(f"   - Argumentos: {g['n_argumentos']}")
            lineas.append(f"   - Representativo: _{g.get('texto_representativo', '')[:200]}_\n")
    else:
        lineas.append("_(No se identificaron argumentos nuevos)_\n")

    lineas += [
        "---\n",
        "## III. Argumentos posiblemente ya resueltos (verificar)\n",
    ]
    if probables:
        for i, g in enumerate(probables, start=1):
            nombre = g.get("nombre_tentativo", f"Grupo {g['grupo_id'] + 1}")
            lineas.append(
                f"{i}. **{nombre}** — similitud con base: {g.get('similitud_base', 0):.2%}"
            )
            lineas.append(f"   - Evidencia: _{g.get('evidencia_base', '')[:200]}_\n")
    else:
        lineas.append("_(Ninguno en esta categoría)_\n")

    lineas += [
        "---\n",
        "## IV. Argumentos ya resueltos en la decisión base (confirmar y ratificar)\n",
    ]
    if resueltos:
        for i, g in enumerate(resueltos, start=1):
            nombre = g.get("nombre_tentativo", f"Grupo {g['grupo_id'] + 1}")
            lineas.append(f"{i}. **{nombre}** — similitud: {g.get('similitud_base', 0):.2%}")
            lineas.append(f"   - Evidencia: _{g.get('evidencia_base', '')[:200]}_\n")
    else:
        lineas.append("_(Ninguno en esta categoría)_\n")

    lineas += [
        "---\n",
        "## V. Decisión\n",
        "1. Parte resolutiva",
        "2. Notificación\n",
    ]

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    logger.info(f"Propuesta de índice exportada: {ruta}")
