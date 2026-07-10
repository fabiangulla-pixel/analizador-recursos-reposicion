"""Tests de procesamiento/comparador.py — clasificación de argumentos vs. base."""

import numpy as np

import procesamiento.comparador as comparador
from procesamiento.comparador import (
    _clasificar_resolucion,
    comparar_con_base,
    comparar_grupos_con_base,
)

UMBRAL = 0.70


def test_clasifica_resuelto_desde_el_umbral():
    assert _clasificar_resolucion(0.70, UMBRAL) == ("SI", "alta", False)
    assert _clasificar_resolucion(0.95, UMBRAL) == ("SI", "alta", False)


def test_clasifica_probablemente_en_banda_intermedia():
    # Banda: [0.8 * umbral, umbral) = [0.56, 0.70)
    assert _clasificar_resolucion(0.60, UMBRAL) == ("PROBABLEMENTE", "media", True)
    assert _clasificar_resolucion(0.56, UMBRAL) == ("PROBABLEMENTE", "media", True)


def test_clasifica_no_resuelto_con_confianza_gradual():
    # 0.50: media (>= 0.35) y requiere revisión (>= 0.42)
    assert _clasificar_resolucion(0.50, UMBRAL) == ("NO", "media", True)
    # 0.20: por debajo de todo → NO con confianza alta y sin revisión
    assert _clasificar_resolucion(0.20, UMBRAL) == ("NO", "alta", False)


def test_comparar_sin_base_marca_todo_para_revision():
    argumentos = [{"id": 0, "texto": "algo"}]
    resultado = comparar_con_base(argumentos, np.zeros((1, 2)), [], UMBRAL)
    assert resultado[0]["ya_resuelto_en_decision_base"] == "NO"
    assert resultado[0]["requiere_revision_humana"] is True
    assert resultado[0]["confianza"] == "baja"


def test_comparar_con_base_encuentra_mejor_evidencia(monkeypatch):
    # La base tiene 2 bloques con embeddings ortogonales conocidos
    bloques_base = [
        {"texto": "bloque sobre notificación " * 20, "pagina": 1, "archivo": "base.pdf"},
        {"texto": "bloque sobre caducidad " * 20, "pagina": 2, "archivo": "base.pdf"},
    ]
    monkeypatch.setattr(comparador, "vectorizar", lambda textos: np.array([[1.0, 0.0], [0.0, 1.0]]))
    argumentos = [{"id": 0, "texto": "argumento"}]
    emb_args = np.array([[0.0, 1.0]])  # idéntico al bloque de caducidad

    resultado = comparar_con_base(argumentos, emb_args, bloques_base, UMBRAL)
    assert resultado[0]["ya_resuelto_en_decision_base"] == "SI"
    assert resultado[0]["similitud_base"] == 1.0
    assert resultado[0]["evidencia_resolucion_base"].startswith("bloque sobre caducidad")


def test_comparar_grupos_usa_centroide(monkeypatch):
    bloques_base = [{"texto": "texto base", "pagina": 1, "archivo": "base.pdf"}]
    monkeypatch.setattr(comparador, "vectorizar", lambda textos: np.array([[1.0, 0.0]]))
    grupos = [{"grupo_id": 0, "centroide": np.array([1.0, 0.0])}]

    resultado = comparar_grupos_con_base(grupos, bloques_base, UMBRAL)
    assert resultado[0]["ya_resuelto"] == "SI"
    assert resultado[0]["similitud_base"] == 1.0
