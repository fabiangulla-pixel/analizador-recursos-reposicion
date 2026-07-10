"""
consolidado.py
Genera el consolidado por grupos argumentales en JSON y Markdown.
"""

import json
import os
from typing import Any

from utils.logger import obtener_logger

logger = obtener_logger()


def construir_consolidado(grupos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Construye la estructura de consolidado serializable (sin numpy arrays)."""
    resultado = []
    for g in grupos:
        miembros_serializables = [
            {
                "id": m.get("id"),
                "texto": m.get("texto", "")[:600],
                "archivo": m.get("archivo"),
                "pagina": m.get("pagina"),
                "similitud_base": m.get("similitud_base"),
            }
            for m in g.get("miembros", [])
        ]
        resultado.append(
            {
                "grupo_id": g["grupo_id"],
                "nombre": g.get("nombre_tentativo", f"Grupo {g['grupo_id'] + 1}"),
                "n_argumentos": g["n_argumentos"],
                "recurrente": g["recurrente"],
                "archivos": g["archivos"],
                "texto_representativo": g.get("texto_representativo", ""),
                "ya_resuelto": g.get("ya_resuelto", ""),
                "similitud_base": g.get("similitud_base", 0.0),
                "evidencia_base": g.get("evidencia_base", ""),
                "variantes": miembros_serializables,
            }
        )
    return resultado


def exportar_consolidado_json(grupos: list[dict[str, Any]], carpeta_salida: str) -> None:
    data = construir_consolidado(grupos)
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta = os.path.join(carpeta_salida, "consolidado_grupos.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Consolidado JSON exportado: {ruta}")


def exportar_consolidado_markdown(grupos: list[dict[str, Any]], carpeta_salida: str) -> None:
    data = construir_consolidado(grupos)
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta = os.path.join(carpeta_salida, "consolidado_grupos.md")

    lineas = ["# Consolidado de grupos argumentales\n"]
    for g in data:
        estado = g["ya_resuelto"] or "SIN DATOS"
        recurrente = "Sí" if g["recurrente"] else "No"
        lineas.append(f"## {g['nombre']} (ID {g['grupo_id']})")
        lineas.append(f"- **Argumentos en el grupo:** {g['n_argumentos']}")
        lineas.append(f"- **Recurrente (varios documentos):** {recurrente}")
        lineas.append(f"- **Documentos:** {', '.join(g['archivos'])}")
        lineas.append(f"- **¿Ya resuelto en decisión base?** {estado}")
        lineas.append(f"- **Similitud con base:** {g['similitud_base']:.2%}")
        lineas.append(f"\n### Argumento representativo\n> {g['texto_representativo'][:500]}")
        if g["evidencia_base"]:
            lineas.append(f"\n### Evidencia en la resolución base\n> {g['evidencia_base'][:400]}")
        lineas.append("\n---\n")

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    logger.info(f"Consolidado Markdown exportado: {ruta}")
