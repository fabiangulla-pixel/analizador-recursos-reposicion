"""Tests de procesamiento/citas_normativas.py — extractor de citas colombianas."""

from procesamiento.citas_normativas import anotar_citas, extraer_citas


def test_ley_simple():
    assert extraer_citas("conforme a la Ley 1437 de 2011") == ["Ley 1437 de 2011"]


def test_ley_con_articulo():
    citas = extraer_citas("según el artículo 76 de la Ley 1437 de 2011, el recurso...")
    assert citas == ["Ley 1437 de 2011, art. 76"]


def test_decreto_con_variantes():
    texto = "el Decreto Ley 019 de 2012 y el artículo 5 del Decreto 1082 de 2015"
    assert extraer_citas(texto) == ["Decreto 019 de 2012", "Decreto 1082 de 2015, art. 5"]


def test_resolucion():
    assert extraer_citas("mediante Resolución No. 4521 de 2024 se impuso") == [
        "Resolución 4521 de 2024"
    ]


def test_sentencias_ambos_formatos():
    texto = "como sostuvo la Corte en la Sentencia C-123 de 2020 y en la T-025/04"
    assert extraer_citas(texto) == ["Sentencia C-123 de 2020", "Sentencia T-025 de 2004"]


def test_anio_dos_digitos_siglo_pasado():
    assert extraer_citas("la SU-1184/98") == ["Sentencia SU-1184 de 1998"]


def test_codigos_por_sigla_y_constitucion():
    texto = "vulnera el CPACA y el artículo 29 de la Constitución Política"
    assert extraer_citas(texto) == ["CPACA", "Constitución Política, art. 29"]


def test_dedup_conservando_orden():
    texto = "la Ley 80 de 1993... insiste en la Ley 80 de 1993 y luego la Ley 1150 de 2007"
    assert extraer_citas(texto) == ["Ley 80 de 1993", "Ley 1150 de 2007"]


def test_texto_sin_citas():
    assert extraer_citas("El recurrente manifiesta su inconformidad general.") == []


def test_anotar_citas_agrega_campo_a_argumentos():
    argumentos = [
        {"id": 0, "texto": "viola la Ley 1437 de 2011"},
        {"id": 1, "texto": "sin citas aquí"},
    ]
    resultado = anotar_citas(argumentos)
    assert resultado[0]["citas_normativas"] == ["Ley 1437 de 2011"]
    assert resultado[1]["citas_normativas"] == []
