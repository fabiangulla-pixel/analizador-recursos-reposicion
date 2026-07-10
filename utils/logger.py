"""
logger.py
Configura el sistema de logging de la aplicación.
Los logs se escriben a consola y a archivo en la carpeta de salida.
"""

import logging
import os


def configurar_logger(nivel: str = "INFO", ruta_log: str | None = None) -> logging.Logger:
    """
    Configura y devuelve el logger principal de la aplicación.

    Args:
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR).
        ruta_log: Ruta completa del archivo de log. Si es None, solo loguea a consola.
    """
    logger = logging.getLogger("recursos_reposicion")
    logger.setLevel(getattr(logging, nivel.upper(), logging.INFO))

    if logger.handlers:
        logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler de consola
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Handler de archivo (si se indica ruta)
    if ruta_log:
        os.makedirs(os.path.dirname(ruta_log), exist_ok=True)
        fh = logging.FileHandler(ruta_log, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def obtener_logger() -> logging.Logger:
    """Devuelve el logger ya configurado (o uno básico si aún no se configuró)."""
    return logging.getLogger("recursos_reposicion")
