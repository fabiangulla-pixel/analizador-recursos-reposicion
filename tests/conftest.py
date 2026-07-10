"""Configuración compartida de la suite: raíz del proyecto en sys.path y fixtures."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest


@pytest.fixture
def argumentos_procesados():
    """Dos argumentos ya pasados por todo el pipeline (sin embeddings)."""
    return [
        {
            "id": 0,
            "texto": "El recurrente alega que la sanción vulnera el debido proceso "
            "porque no fue notificado en debida forma de la apertura de la investigación.",
            "pagina": 1,
            "archivo": "recurso_a.docx",
            "es_argumentativo": True,
            "grupo_id": 0,
            "recurrente": True,
            "similitud_base": 0.91,
            "ya_resuelto_en_decision_base": "SI",
            "evidencia_resolucion_base": "Sobre la notificación, la resolución señaló...",
            "confianza": "alta",
            "requiere_revision_humana": False,
        },
        {
            "id": 1,
            "texto": "Solicita la nulidad de la resolución por caducidad de la facultad "
            "sancionatoria, pues transcurrieron más de tres años desde los hechos.",
            "pagina": 3,
            "archivo": "recurso_b.docx",
            "es_argumentativo": True,
            "grupo_id": 1,
            "recurrente": False,
            "similitud_base": 0.40,
            "ya_resuelto_en_decision_base": "NO",
            "evidencia_resolucion_base": "",
            "confianza": "media",
            "requiere_revision_humana": True,
        },
    ]


@pytest.fixture
def grupos_procesados(argumentos_procesados):
    """Dos grupos argumentales completos, como los produce construir_grupos + comparador."""
    return [
        {
            "grupo_id": 0,
            "nombre_tentativo": "Grupo 1",
            "n_argumentos": 1,
            "archivos": ["recurso_a.docx"],
            "recurrente": False,
            "texto_representativo": argumentos_procesados[0]["texto"],
            "miembros": [argumentos_procesados[0]],
            "centroide": np.array([1.0, 0.0]),
            "ya_resuelto": "SI",
            "similitud_base": 0.91,
            "evidencia_base": "Sobre la notificación, la resolución señaló...",
        },
        {
            "grupo_id": 1,
            "nombre_tentativo": "Grupo 2",
            "n_argumentos": 1,
            "archivos": ["recurso_b.docx"],
            "recurrente": False,
            "texto_representativo": argumentos_procesados[1]["texto"],
            "miembros": [argumentos_procesados[1]],
            "centroide": np.array([0.0, 1.0]),
            "ya_resuelto": "NO",
            "similitud_base": 0.40,
            "evidencia_base": "",
        },
    ]
