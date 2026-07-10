"""
vectorizador.py
Genera embeddings semánticos de textos usando sentence-transformers.
El modelo se carga una sola vez y se reutiliza.
Compatible con empaquetado PyInstaller: el modelo se descarga/cachea en
una carpeta local del usuario o se puede empaquetar manualmente.
"""

import os
import sys

import numpy as np

from utils.logger import obtener_logger

logger = obtener_logger()

# Singleton del modelo para no recargarlo en cada llamada
_modelo = None
_nombre_modelo_cargado: str | None = None


def _get_cache_dir() -> str:
    """
    Devuelve la carpeta de caché del modelo.
    En modo PyInstaller frozen usa una carpeta junto al ejecutable.
    En modo desarrollo usa la carpeta estándar de HuggingFace.
    """
    if getattr(sys, "frozen", False):
        # Junto al ejecutable, dentro de una carpeta oculta de datos
        base = os.path.dirname(sys.executable)
        return os.path.join(base, "_modelos_cache")
    return None  # None = HuggingFace usa su cache por defecto (~/.cache/huggingface)


def cargar_modelo(nombre_modelo: str) -> None:
    """Carga el modelo de embeddings en memoria (solo la primera vez)."""
    global _modelo, _nombre_modelo_cargado

    if _modelo is not None and _nombre_modelo_cargado == nombre_modelo:
        return  # Ya cargado

    import io
    import sys

    from sentence_transformers import SentenceTransformer

    cache_dir = _get_cache_dir()
    logger.info(f"Cargando modelo de embeddings: {nombre_modelo}")

    _old_stdout = sys.stdout
    _old_stderr = sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        if cache_dir:
            _modelo = SentenceTransformer(nombre_modelo, cache_folder=cache_dir)
        else:
            _modelo = SentenceTransformer(nombre_modelo)
        _nombre_modelo_cargado = nombre_modelo
    except Exception as e:
        logger.error(f"Error cargando modelo {nombre_modelo}: {e}")
        raise
    finally:
        sys.stdout = _old_stdout
        sys.stderr = _old_stderr

    logger.info("Modelo cargado correctamente.")


def vectorizar(textos: list[str], batch_size: int = 32) -> np.ndarray:
    """
    Genera embeddings para una lista de textos.
    Devuelve array numpy de shape (n_textos, dim_embedding).
    """
    if _modelo is None:
        raise RuntimeError("El modelo no está cargado. Llama a cargar_modelo() primero.")

    logger.info(f"Vectorizando {len(textos)} textos...")

    # Silenciar tqdm/progress bars para evitar el error 'NoneType has no attribute isatty'
    # que ocurre cuando se corre desde GUI sin consola adjunta.
    import io
    import sys

    _old_stdout = sys.stdout
    _old_stderr = sys.stderr
    try:
        # Redirigir stdout/stderr a un buffer silencioso durante encode
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        embeddings = _modelo.encode(
            textos,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
    finally:
        sys.stdout = _old_stdout
        sys.stderr = _old_stderr

    logger.info("Vectorización completada.")
    return embeddings


def similitud_coseno(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Calcula similitud coseno entre dos vectores normalizados.
    Como usamos normalize_embeddings=True, equivale al producto punto.
    """
    return float(np.dot(vec_a, vec_b))


def matriz_similitud(embeddings: np.ndarray) -> np.ndarray:
    """
    Calcula la matriz de similitud coseno entre todos los embeddings.
    Devuelve array de shape (n, n).
    """
    return np.dot(embeddings, embeddings.T)
