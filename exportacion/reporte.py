"""
reporte.py
Genera el reporte ejecutivo del análisis en formato Markdown.
"""

import os
from datetime import datetime
from typing import Any

from utils.logger import obtener_logger

logger = obtener_logger()


def exportar_reporte_ejecutivo(
    argumentos: list[dict[str, Any]],
    grupos: list[dict[str, Any]],
    carpeta_salida: str,
) -> None:
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta = os.path.join(carpeta_salida, "reporte_ejecutivo.md")

    total_args = len(argumentos)
    args_argumentativos = sum(1 for a in argumentos if a.get("es_argumentativo"))
    total_grupos = len(grupos)
    grupos_recurrentes = sum(1 for g in grupos if g.get("recurrente"))
    resueltos = sum(1 for a in argumentos if a.get("ya_resuelto_en_decision_base") == "SI")
    probables = sum(
        1 for a in argumentos if a.get("ya_resuelto_en_decision_base") == "PROBABLEMENTE"
    )
    nuevos = sum(1 for a in argumentos if a.get("ya_resuelto_en_decision_base") == "NO")
    rev_humana = sum(1 for a in argumentos if a.get("requiere_revision_humana"))

    # Top 5 grupos más grandes
    top_grupos = sorted(grupos, key=lambda g: g["n_argumentos"], reverse=True)[:5]

    # Documentos únicos
    docs = sorted({a["archivo"] for a in argumentos})

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    lineas = [
        "# Reporte ejecutivo del análisis",
        f"_Generado el {fecha}_\n",
        "---\n",
        "## Resumen general\n",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Documentos procesados | {len(docs)} |",
        f"| Total de bloques extraídos | {total_args} |",
        f"| Bloques argumentativos | {args_argumentativos} |",
        f"| Grupos argumentales identificados | {total_grupos} |",
        f"| Grupos recurrentes (varios docs) | {grupos_recurrentes} |",
        f"| Args. ya resueltos en base | {resueltos} |",
        f"| Args. probablemente resueltos | {probables} |",
        f"| Args. nuevos | {nuevos} |",
        f"| Requieren revisión humana | {rev_humana} |\n",
        "---\n",
        "## Documentos analizados\n",
    ]
    for doc in docs:
        lineas.append(f"- {doc}")

    lineas += [
        "\n---\n",
        "## Top 5 grupos argumentales más frecuentes\n",
    ]
    for g in top_grupos:
        lineas.append(
            f"- **{g.get('nombre_tentativo', 'Grupo')}**: "
            f"{g['n_argumentos']} argumentos | "
            f"Docs: {', '.join(g['archivos'])} | "
            f"¿Resuelto?: {g.get('ya_resuelto', 'N/D')}"
        )

    lineas += [
        "\n---\n",
        "## Alertas\n",
    ]
    if rev_humana > 0:
        lineas.append(
            f"- **{rev_humana} argumentos** requieren revisión humana (confianza media o baja)."
        )
    if nuevos > 0:
        lineas.append(f"- **{nuevos} argumentos nuevos** no encontrados en la resolución base.")
    if probables > 0:
        lineas.append(
            f"- **{probables} argumentos** probablemente ya resueltos — confirmar antes de omitir respuesta."
        )

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    logger.info(f"Reporte ejecutivo exportado: {ruta}")
