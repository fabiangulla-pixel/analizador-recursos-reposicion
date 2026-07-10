"""
trazabilidad.py
Genera el archivo de trazabilidad completo en JSON para auditoría técnica.
"""

import json
import os
from datetime import datetime
from typing import Any

from utils.logger import obtener_logger

logger = obtener_logger()


def exportar_trazabilidad(
    argumentos: list[dict[str, Any]],
    grupos: list[dict[str, Any]],
    carpeta_salida: str,
    config_usada: dict[str, Any],
) -> None:
    """
    Exporta un JSON completo con todos los argumentos, grupos y la configuración
    usada para el análisis. Permite reproducir o auditar la decisión algorítmica.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    ruta = os.path.join(carpeta_salida, "trazabilidad.json")

    # Serializar argumentos (sin embeddings numpy)
    args_serializables = []
    for a in argumentos:
        args_serializables.append(
            {
                k: v
                for k, v in a.items()
                if k != "embedding"  # excluir arrays numpy no serializables
            }
        )

    # Serializar grupos (sin centroides numpy)
    grupos_serializables = []
    for g in grupos:
        g_serial = {k: v for k, v in g.items() if k not in ("centroide", "miembros")}
        g_serial["miembros_ids"] = [m.get("id") for m in g.get("miembros", [])]
        grupos_serializables.append(g_serial)

    payload = {
        "fecha_analisis": datetime.now().isoformat(),
        "version": "1.0.0",
        "configuracion": config_usada,
        "resumen": {
            "total_argumentos": len(argumentos),
            "total_grupos": len(grupos),
        },
        "argumentos": args_serializables,
        "grupos": grupos_serializables,
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Trazabilidad exportada: {ruta}")
