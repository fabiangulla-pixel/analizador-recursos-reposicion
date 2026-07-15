"""Tests de procesamiento/taxonomia.py — clasificación por categoría jurídica."""

import numpy as np

import procesamiento.vectorizador as vectorizador_mod
from procesamiento.taxonomia import CATEGORIAS, SIN_CLASIFICAR, clasificar_argumentos

N_CATEGORIAS = len(CATEGORIAS)


def _mock_vectorizar_categorias(base_ortogonal: np.ndarray):
    """Devuelve embeddings ortogonales, uno por categoría, en el orden real de CATEGORIAS."""

    def _fake(textos):
        assert len(textos) == N_CATEGORIAS
        return base_ortogonal

    return _fake


def test_lista_vacia_no_falla():
    assert clasificar_argumentos([], np.zeros((0, 3))) == []


def test_asigna_categoria_de_mayor_similitud(monkeypatch):
    # clasificar_argumentos importa vectorizar de forma diferida (dentro de la
    # función) para evitar un import circular con vectorizador.py; por eso se
    # parchea el módulo real, no un nombre importado en taxonomia.py.
    nombres = list(CATEGORIAS.keys())
    base = np.eye(N_CATEGORIAS)  # una categoría por eje, perfectamente ortogonales
    monkeypatch.setattr(vectorizador_mod, "vectorizar", _mock_vectorizar_categorias(base))

    argumentos = [{"id": 0, "texto": "cualquier cosa"}]
    embeddings = np.array([base[2]])  # idéntico a la 3ra categoría

    resultado = clasificar_argumentos(argumentos, embeddings, umbral_minimo=0.30)
    assert resultado[0]["categoria_juridica"] == nombres[2]
    assert resultado[0]["categoria_similitud"] == 1.0


def test_bajo_el_umbral_queda_sin_clasificar(monkeypatch):
    base = np.eye(N_CATEGORIAS)
    monkeypatch.setattr(vectorizador_mod, "vectorizar", _mock_vectorizar_categorias(base))

    argumentos = [{"id": 0, "texto": "algo ambiguo"}]
    # vector con baja similitud a todas las categorías (perpendicular-ish, escalado pequeño)
    embeddings = np.array([np.full(N_CATEGORIAS, 0.1)])

    resultado = clasificar_argumentos(argumentos, embeddings, umbral_minimo=0.9)
    assert resultado[0]["categoria_juridica"] == SIN_CLASIFICAR


def test_categorias_son_textos_curados_no_vacios():
    assert len(CATEGORIAS) >= 5
    for nombre, descripcion in CATEGORIAS.items():
        assert nombre.strip()
        assert len(descripcion) > 30  # descripciones sustanciales, no placeholders
