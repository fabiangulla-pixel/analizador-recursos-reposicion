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
    En modo PyInstaller frozen usa sys._MEIPASS: en builds one-folder (PyInstaller
    6.x) es la carpeta persistente _internal/, donde realmente aterrizan los
    datos empaquetados (datas del .spec) — no junto al .exe, que es un
    directorio distinto y vacío. Mismo criterio que app/config_loader.py.
    En modo desarrollo usa la carpeta estándar de HuggingFace.
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
        return os.path.join(base, "_modelos_cache")
    return None  # None = HuggingFace usa su cache por defecto (~/.cache/huggingface)


def _modelo_en_cache(cache_dir: str | None, nombre_modelo: str) -> bool:
    """True si el modelo ya está descargado en la carpeta de caché local."""
    if not cache_dir or not os.path.isdir(cache_dir):
        return False
    slug = nombre_modelo.replace("/", "--")
    plano = nombre_modelo.replace("/", "_")
    return any(slug in entrada or plano in entrada for entrada in os.listdir(cache_dir))


def _activar_modo_offline_si_cacheado(cache_dir: str | None, nombre_modelo: str) -> bool:
    """
    Si el modelo ya está en caché, fuerza el modo offline de HuggingFace.
    Sin esto, el .exe hace una petición HEAD de verificación al hub y falla
    en equipos sin internet aunque el modelo esté completo en disco.
    """
    if _modelo_en_cache(cache_dir, nombre_modelo):
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        return True
    return False


def cargar_modelo(nombre_modelo: str) -> None:
    """Carga el modelo de embeddings en memoria (solo la primera vez)."""
    global _modelo, _nombre_modelo_cargado

    if _modelo is not None and _nombre_modelo_cargado == nombre_modelo:
        return  # Ya cargado

    import io
    import sys

    # Antes de importar sentence_transformers: HuggingFace lee las variables
    # de entorno offline en el momento del import.
    cache_dir = _get_cache_dir()
    if _activar_modo_offline_si_cacheado(cache_dir, nombre_modelo):
        logger.info("Modelo ya en caché local: modo offline activado (HF_HUB_OFFLINE=1).")

    from sentence_transformers import SentenceTransformer

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
