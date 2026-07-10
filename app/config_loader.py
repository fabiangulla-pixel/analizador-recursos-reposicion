"""
config_loader.py
Carga config.yaml de forma segura tanto en modo desarrollo como empaquetado con PyInstaller.
"""

import os
import sys

import yaml


def get_base_path() -> str:
    """
    Devuelve la ruta base del proyecto.
    En modo PyInstaller (onefile/onefolder) usa sys._MEIPASS.
    En modo desarrollo usa la carpeta del proyecto.
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cargar_config() -> dict:
    """Carga y devuelve el diccionario de configuración desde config.yaml."""
    ruta = os.path.join(get_base_path(), "config.yaml")
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró config.yaml en: {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
