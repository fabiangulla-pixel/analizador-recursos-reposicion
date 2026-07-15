"""
expedientes_db.py
Registro local (SQLite) de los análisis ejecutados: permite ver qué
expedientes se han procesado, cuándo y con qué resultado, sin depender de
recordar carpetas sueltas.

Es solo la capa de datos — todavía no tiene vista en la GUI (ver
docs/ROADMAP.md, ítem 8). El pipeline la usa para registrar cada análisis
exitoso; el resto de la app puede consultarla cuando se construya la vista.

Importante: nunca se cachea una conexión sqlite3 compartida (lección de
otros proyectos de la casa — sqlite3 no admite compartir una conexión entre
hilos). ejecutar_analisis() corre en un hilo separado de la GUI, así que
cada función aquí abre y cierra su propia conexión por uso.
"""

import os
import sqlite3
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS expedientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_analisis TEXT NOT NULL,
    nombre_expediente TEXT,
    ruta_base TEXT NOT NULL,
    carpeta_recursos TEXT NOT NULL,
    carpeta_salida TEXT NOT NULL,
    total_documentos INTEGER,
    total_argumentos INTEGER,
    total_grupos INTEGER
)
"""


def _ruta_db() -> str:
    """
    Ubicación de la base de datos. Mismo criterio que _modelos_cache en
    vectorizador.py: junto al ejecutable cuando está empaquetado, en la
    raíz del proyecto en modo desarrollo.
    """
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "expedientes.db")


@contextmanager
def _conexion() -> Iterator[sqlite3.Connection]:
    con = sqlite3.connect(_ruta_db())
    try:
        con.execute(_ESQUEMA)
        con.commit()
        con.row_factory = sqlite3.Row
        yield con
    finally:
        con.close()


def registrar_expediente(
    ruta_base: str,
    carpeta_recursos: str,
    carpeta_salida: str,
    total_documentos: int,
    total_argumentos: int,
    total_grupos: int,
    nombre_expediente: str | None = None,
) -> int:
    """Guarda un registro del análisis recién ejecutado. Devuelve el id asignado."""
    if not nombre_expediente:
        nombre_expediente = os.path.basename(os.path.normpath(carpeta_recursos))
    with _conexion() as con:
        cur = con.execute(
            """INSERT INTO expedientes
               (fecha_analisis, nombre_expediente, ruta_base, carpeta_recursos,
                carpeta_salida, total_documentos, total_argumentos, total_grupos)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().isoformat(timespec="seconds"),
                nombre_expediente,
                ruta_base,
                carpeta_recursos,
                carpeta_salida,
                total_documentos,
                total_argumentos,
                total_grupos,
            ),
        )
        con.commit()
        return int(cur.lastrowid)


def listar_expedientes(limite: int = 100) -> list[dict[str, Any]]:
    """Expedientes registrados, más reciente primero."""
    with _conexion() as con:
        # id como desempate: fecha_analisis tiene resolución de 1 segundo y
        # dos registros rápidos consecutivos pueden empatar; el id
        # autoincremental sí refleja siempre el orden real de inserción.
        filas = con.execute(
            "SELECT * FROM expedientes ORDER BY fecha_analisis DESC, id DESC LIMIT ?",
            (limite,),
        ).fetchall()
        return [dict(f) for f in filas]


def obtener_expediente(id_expediente: int) -> dict[str, Any] | None:
    with _conexion() as con:
        fila = con.execute("SELECT * FROM expedientes WHERE id = ?", (id_expediente,)).fetchone()
        return dict(fila) if fila else None


def eliminar_expediente(id_expediente: int) -> bool:
    """Borra el REGISTRO del expediente. No toca los archivos en disco."""
    with _conexion() as con:
        cur = con.execute("DELETE FROM expedientes WHERE id = ?", (id_expediente,))
        con.commit()
        return cur.rowcount > 0
