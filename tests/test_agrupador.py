"""Tests de procesamiento/agrupador.py — clustering y construcción de grupos."""

import numpy as np

from procesamiento.agrupador import agrupar_argumentos, construir_grupos


def _args(n, archivo="doc.pdf"):
    return [{"id": i, "texto": f"argumento {i}", "pagina": 1, "archivo": archivo} for i in range(n)]


def test_argumento_unico_forma_su_propio_grupo():
    argumentos = agrupar_argumentos(_args(1), np.array([[1.0, 0.0]]))
    assert argumentos[0]["grupo_id"] == 0
    assert argumentos[0]["recurrente"] is False


def test_agrupa_similares_y_separa_distintos():
    # Dos vectores idénticos + uno ortogonal → 2 grupos
    embeddings = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    argumentos = agrupar_argumentos(_args(3), embeddings, umbral_distancia=0.30)

    grupos_ids = [a["grupo_id"] for a in argumentos]
    assert grupos_ids[0] == grupos_ids[1]
    assert grupos_ids[2] != grupos_ids[0]
    assert argumentos[0]["recurrente"] is True
    assert argumentos[2]["recurrente"] is False


def test_lista_vacia_no_falla():
    assert agrupar_argumentos([], np.zeros((0, 2))) == []


def test_construir_grupos_calcula_metadatos():
    embeddings = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    argumentos = _args(3)
    argumentos[0]["archivo"] = "a.pdf"
    argumentos[1]["archivo"] = "b.pdf"
    argumentos = agrupar_argumentos(argumentos, embeddings, umbral_distancia=0.30)

    grupos = construir_grupos(argumentos, embeddings)
    assert len(grupos) == 2

    grande = max(grupos, key=lambda g: g["n_argumentos"])
    assert grande["n_argumentos"] == 2
    assert sorted(grande["archivos"]) == ["a.pdf", "b.pdf"]
    assert grande["recurrente"] is True  # presente en varios documentos
    assert grande["texto_representativo"] in ("argumento 0", "argumento 1")
    assert grande["centroide"].shape == (2,)
