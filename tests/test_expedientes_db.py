"""Tests de utils/expedientes_db.py — registro local de expedientes."""

import threading

import utils.expedientes_db as expedientes_db
from utils.expedientes_db import (
    eliminar_expediente,
    listar_expedientes,
    obtener_expediente,
    registrar_expediente,
)


def _db_aislada(tmp_path, monkeypatch, nombre="test.db"):
    monkeypatch.setattr(expedientes_db, "_ruta_db", lambda: str(tmp_path / nombre))


def test_registrar_y_listar(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    id1 = registrar_expediente("base.docx", "recursos/", "salida1/", 2, 5, 3)
    id2 = registrar_expediente("base.docx", "recursos/", "salida2/", 3, 8, 4)

    expedientes = listar_expedientes()
    assert len(expedientes) == 2
    assert {e["id"] for e in expedientes} == {id1, id2}


def test_lista_mas_reciente_primero(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    id1 = registrar_expediente("b.docx", "r/", "s1/", 1, 1, 1)
    id2 = registrar_expediente("b.docx", "r/", "s2/", 1, 1, 1)
    expedientes = listar_expedientes()
    assert expedientes[0]["id"] == id2
    assert expedientes[1]["id"] == id1


def test_nombre_expediente_por_defecto_usa_carpeta_recursos(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    registrar_expediente("b.docx", "/ruta/algo/Recursos_20016795", "s/", 1, 1, 1)
    exp = listar_expedientes()[0]
    assert exp["nombre_expediente"] == "Recursos_20016795"


def test_nombre_expediente_explicito_se_respeta(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    registrar_expediente("b.docx", "r/", "s/", 1, 1, 1, nombre_expediente="Caso Diego Fernández")
    exp = listar_expedientes()[0]
    assert exp["nombre_expediente"] == "Caso Diego Fernández"


def test_obtener_expediente_por_id(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    id1 = registrar_expediente("b.docx", "r/", "s/", 4, 10, 6)
    exp = obtener_expediente(id1)
    assert exp["total_argumentos"] == 10
    assert exp["total_grupos"] == 6
    assert exp["total_documentos"] == 4


def test_obtener_expediente_inexistente_devuelve_none(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    assert obtener_expediente(9999) is None


def test_eliminar_expediente(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    id1 = registrar_expediente("b.docx", "r/", "s/", 1, 1, 1)
    assert eliminar_expediente(id1) is True
    assert obtener_expediente(id1) is None
    assert eliminar_expediente(id1) is False  # ya no existe, segunda vez


def test_base_de_datos_vacia_no_falla(tmp_path, monkeypatch):
    _db_aislada(tmp_path, monkeypatch)
    assert listar_expedientes() == []


def test_registros_concurrentes_desde_varios_hilos_no_corrompen_datos(tmp_path, monkeypatch):
    # Cada función abre y cierra su propia conexión (nunca comparte una
    # conexión sqlite3 entre hilos) — se verifica lanzando el registro desde
    # varios hilos a la vez, como ocurriría si el pipeline corriera dos
    # análisis en paralelo.
    _db_aislada(tmp_path, monkeypatch)

    def _registrar(i):
        registrar_expediente("b.docx", "r/", f"salida_{i}/", 1, i, i)

    hilos = [threading.Thread(target=_registrar, args=(i,)) for i in range(10)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert len(listar_expedientes(limite=100)) == 10
