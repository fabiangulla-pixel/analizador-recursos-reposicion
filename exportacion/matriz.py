"""
matriz.py
Genera la matriz principal de argumentos en formato XLSX y/o CSV.
"""

import os
from typing import Any

import pandas as pd

from utils.logger import obtener_logger

logger = obtener_logger()

COLUMNAS = [
    "id_argumento",
    "grupo_argumental",
    "tipo_argumento",
    "texto_resumido_argumento",
    "texto_literal_clave",
    "documento_origen",
    "recurrente",
    "pagina_inicial",
    "ya_resuelto_en_decision_base",
    "evidencia_resolucion_base",
    "similitud",
    "confianza",
    "requiere_revision_humana",
    "observaciones",
]


def _resumir_texto(texto: str, max_chars: int = 200) -> str:
    if len(texto) <= max_chars:
        return texto
    return texto[:max_chars].rsplit(" ", 1)[0] + "…"


def construir_dataframe(argumentos: list[dict[str, Any]]) -> pd.DataFrame:
    """Convierte la lista de argumentos procesados en un DataFrame."""
    filas = []
    for arg in argumentos:
        filas.append(
            {
                "id_argumento": arg.get("id", ""),
                "grupo_argumental": f"Grupo {arg.get('grupo_id', '') + 1}",
                "tipo_argumento": "argumentativo" if arg.get("es_argumentativo") else "descriptivo",
                "texto_resumido_argumento": _resumir_texto(arg.get("texto", "")),
                "texto_literal_clave": arg.get("texto", "")[:500],
                "documento_origen": arg.get("archivo", ""),
                "recurrente": arg.get("recurrente", False),
                "pagina_inicial": arg.get("pagina", ""),
                "ya_resuelto_en_decision_base": arg.get("ya_resuelto_en_decision_base", ""),
                "evidencia_resolucion_base": arg.get("evidencia_resolucion_base", "")[:300],
                "similitud": arg.get("similitud_base", ""),
                "confianza": arg.get("confianza", ""),
                "requiere_revision_humana": arg.get("requiere_revision_humana", ""),
                "observaciones": "",
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS)


def exportar_matriz(
    argumentos: list[dict[str, Any]],
    carpeta_salida: str,
    generar_xlsx: bool = True,
    generar_csv: bool = True,
) -> None:
    """Exporta la matriz de argumentos a XLSX y/o CSV."""
    df = construir_dataframe(argumentos)
    os.makedirs(carpeta_salida, exist_ok=True)

    if generar_xlsx:
        ruta = os.path.join(carpeta_salida, "matriz_argumentos.xlsx")
        df.to_excel(ruta, index=False)
        logger.info(f"Matriz XLSX exportada: {ruta}")

    if generar_csv:
        ruta = os.path.join(carpeta_salida, "matriz_argumentos.csv")
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
        logger.info(f"Matriz CSV exportada: {ruta}")
