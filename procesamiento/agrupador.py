"""
agrupador.py
Agrupa argumentos similares usando clustering jerárquico aglomerativo.
Cada cluster representa un "grupo argumental" recurrente.
"""

import numpy as np
from typing import List, Dict, Any, Tuple

from utils.logger import obtener_logger

logger = obtener_logger()


def agrupar_argumentos(
    argumentos: List[Dict[str, Any]],
    embeddings: np.ndarray,
    umbral_distancia: float = 0.30,
    metodo: str = "agglomerative",
) -> List[Dict[str, Any]]:
    """
    Asigna un grupo a cada argumento.
    Añade los campos: grupo_id, recurrente.

    Args:
        argumentos: Lista de dicts de argumentos.
        embeddings: Array numpy (n_args, dim).
        umbral_distancia: Distancia máxima para agrupar (1 - similitud).
        metodo: "agglomerative" (recomendado) o "kmeans".

    Returns:
        Lista de argumentos con campo 'grupo_id' añadido.
    """
    if len(argumentos) == 0:
        return argumentos

    if len(argumentos) == 1:
        argumentos[0]["grupo_id"] = 0
        argumentos[0]["recurrente"] = False
        return argumentos

    etiquetas = _clustering(embeddings, umbral_distancia, metodo)

    # Contar tamaño de cada grupo para marcar recurrentes
    conteo: Dict[int, int] = {}
    for e in etiquetas:
        conteo[e] = conteo.get(e, 0) + 1

    for i, arg in enumerate(argumentos):
        gid = int(etiquetas[i])
        arg["grupo_id"] = gid
        arg["recurrente"] = conteo[gid] > 1

    n_grupos = len(set(etiquetas))
    logger.info(f"Agrupación: {len(argumentos)} argumentos → {n_grupos} grupos.")
    return argumentos


def _clustering(
    embeddings: np.ndarray,
    umbral_distancia: float,
    metodo: str,
) -> np.ndarray:
    """Ejecuta el algoritmo de clustering y devuelve array de etiquetas."""
    from sklearn.preprocessing import normalize
    from sklearn.cluster import AgglomerativeClustering

    # Distancia coseno = 1 - similitud coseno (embeddings ya normalizados)
    X = normalize(embeddings)

    if metodo == "kmeans":
        from sklearn.cluster import KMeans
        n = max(2, min(len(X) // 3, 30))
        modelo = KMeans(n_clusters=n, random_state=42, n_init="auto")
        return modelo.fit_predict(X)

    # Con menos de 2 muestras no tiene sentido agrupar
    if len(X) < 2:
        return np.zeros(len(X), dtype=int)

    # Agglomerative con distancia coseno
    try:
        modelo = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=umbral_distancia,
            metric="cosine",
            linkage="average",
        )
        return modelo.fit_predict(X)
    except Exception as e:
        # Fallback: un cluster por muestra si el clustering falla
        from utils.logger import obtener_logger
        obtener_logger().warning(f"Clustering falló ({e}), asignando grupos individuales.")
        return np.arange(len(X), dtype=int)


def construir_grupos(
    argumentos: List[Dict[str, Any]],
    embeddings: np.ndarray,
) -> List[Dict[str, Any]]:
    """
    Construye la lista de grupos argumentales con metadatos de cada grupo.
    Devuelve lista de dicts con info del grupo.
    """
    grupos_dict: Dict[int, List[int]] = {}
    for i, arg in enumerate(argumentos):
        gid = arg.get("grupo_id", 0)
        grupos_dict.setdefault(gid, []).append(i)

    grupos = []
    for gid, indices in sorted(grupos_dict.items()):
        miembros = [argumentos[i] for i in indices]
        archivos = list({m["archivo"] for m in miembros})
        # Centroide del grupo = media de embeddings de sus miembros
        emb_grupo = embeddings[indices]
        centroide = emb_grupo.mean(axis=0)

        # El "argumento representativo" es el más cercano al centroide
        sims = emb_grupo @ centroide
        rep_idx = int(np.argmax(sims))
        texto_representativo = miembros[rep_idx]["texto"]

        grupos.append({
            "grupo_id": gid,
            "nombre_tentativo": f"Grupo {gid + 1}",
            "n_argumentos": len(miembros),
            "archivos": archivos,
            "recurrente": len(archivos) > 1,
            "texto_representativo": texto_representativo,
            "miembros": miembros,
            "centroide": centroide,
        })

    return grupos
