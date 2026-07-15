"""Tests de procesamiento/agrupador.py — clustering y construcción de grupos."""

import numpy as np

from procesamiento.agrupador import _clustering_hdbscan, agrupar_argumentos, construir_grupos


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


def test_hdbscan_agrupa_dos_clusters_densos_reales():
    # 6 puntos en dos nubes densas bien separadas + normalización previa.
    # Semilla fija verificada manualmente (ver nota de estabilidad más abajo):
    # con min_cluster_size=2, HDBSCAN es sensible a fluctuaciones de densidad
    # locales en muestras muy pequeñas y puede fragmentar una nube densa en
    # sub-grupos con otras semillas — no es un fallo de esta función, es una
    # característica documentada del algoritmo a este ajuste. Este test
    # verifica el comportamiento correcto en un caso reproducible, no que
    # HDBSCAN sea perfectamente estable para cualquier entrada (no lo es).
    rng = np.random.default_rng(2)
    nube_a = rng.normal(loc=[1.0, 0.0, 0.0], scale=0.02, size=(6, 3))
    nube_b = rng.normal(loc=[0.0, 1.0, 0.0], scale=0.02, size=(6, 3))
    from sklearn.preprocessing import normalize

    X = normalize(np.vstack([nube_a, nube_b]))

    etiquetas = _clustering_hdbscan(X)
    assert len(set(etiquetas[:6])) == 1  # toda la nube A en un solo grupo
    assert len(set(etiquetas[6:])) == 1  # toda la nube B en un solo grupo
    assert etiquetas[0] != etiquetas[6]  # y son grupos distintos entre sí


def test_hdbscan_nunca_deja_expuesta_la_etiqueta_de_ruido():
    # Con puntos deliberadamente dispersos (sin estructura de cluster clara),
    # HDBSCAN marcaría casi todo como ruido (-1). Lo que SÍ es 100% garantizado
    # por esta función (lógica propia, no de HDBSCAN) es que -1 nunca queda
    # expuesto en el resultado final: cada punto de ruido se reasigna a un
    # grupo individual único.
    rng = np.random.default_rng(3)
    X_disperso = rng.uniform(-1, 1, size=(10, 3))
    from sklearn.preprocessing import normalize

    X = normalize(X_disperso)

    etiquetas = _clustering_hdbscan(X)
    assert -1 not in etiquetas
    assert len(etiquetas) == 10


def test_hdbscan_reasigna_ruido_a_grupos_individuales_no_fusionados(monkeypatch):
    # Qué puntos concretos HDBSCAN marca como ruido depende de la geometría
    # exacta de los datos (no es algo que deba fijar un test unitario). Lo
    # que SÍ es responsabilidad de esta función, y por tanto lo que se
    # prueba aquí de forma determinista, es la lógica de reasignación:
    # mockeamos la salida de HDBSCAN con dos etiquetas de ruido (-1) y
    # verificamos que cada una recibe su propio grupo nuevo, sin fusionarse
    # entre sí ni con los clusters reales 0 y 1.
    class _HDBSCANFalso:
        def __init__(self, **kwargs):
            pass

        def fit_predict(self, X):
            return np.array([0, 0, 0, 1, 1, 1, -1, -1])

    # _clustering_hdbscan importa HDBSCAN de forma diferida (dentro de la
    # función); se parchea el módulo real, recogido en el import diferido.
    import sklearn.cluster as sklearn_cluster_mod

    monkeypatch.setattr(sklearn_cluster_mod, "HDBSCAN", _HDBSCANFalso)

    etiquetas = _clustering_hdbscan(np.zeros((8, 3)))
    assert -1 not in etiquetas
    assert list(etiquetas[:6]) == [0, 0, 0, 1, 1, 1]  # clusters reales intactos
    assert etiquetas[6] == 2  # primer punto de ruido -> nuevo grupo
    assert etiquetas[7] == 3  # segundo punto de ruido -> otro grupo distinto
    assert etiquetas[6] != etiquetas[7]


def test_agrupar_argumentos_acepta_metodo_hdbscan():
    rng = np.random.default_rng(2)
    nube_a = rng.normal(loc=[1.0, 0.0], scale=0.02, size=(4, 2))
    nube_b = rng.normal(loc=[0.0, 1.0], scale=0.02, size=(4, 2))
    embeddings = np.vstack([nube_a, nube_b])

    argumentos = agrupar_argumentos(_args(8), embeddings, metodo="hdbscan")
    ids = [a["grupo_id"] for a in argumentos]
    assert len(set(ids[:4])) == 1
    assert len(set(ids[4:])) == 1
    assert ids[0] != ids[4]
