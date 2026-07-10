"""Tests de procesamiento/segmentador.py — detección de bloques argumentativos."""

from procesamiento.segmentador import _dividir_parrafos, segmentar_bloques

TEXTO_ARGUMENTATIVO = (
    "El recurrente alega que la resolución vulnera el debido proceso, pues la entidad "
    "omitió valorar las pruebas aportadas oportunamente durante la investigación."
)
TEXTO_DESCRIPTIVO = (
    "Bogotá D.C., quince (15) de marzo. Radicado 20016795. Expediente sancionatorio "
    "remitido por la Dirección de Vigilancia con sus anexos correspondientes."
)


def _bloque(texto, pagina=1, archivo="doc.pdf"):
    return {"texto": texto, "pagina": pagina, "archivo": archivo}


def test_marca_argumentativo_por_palabras_clave():
    args = segmentar_bloques([_bloque(TEXTO_ARGUMENTATIVO)], min_longitud=80)
    assert len(args) == 1
    assert args[0]["es_argumentativo"] is True


def test_marca_descriptivo_sin_indicadores():
    args = segmentar_bloques([_bloque(TEXTO_DESCRIPTIVO)], min_longitud=80)
    assert len(args) == 1
    assert args[0]["es_argumentativo"] is False


def test_filtra_parrafos_cortos():
    args = segmentar_bloques([_bloque("Muy corto.")], min_longitud=80)
    assert args == []


def test_divide_por_doble_salto_y_asigna_ids_consecutivos():
    texto = TEXTO_ARGUMENTATIVO + "\n\n" + TEXTO_DESCRIPTIVO
    args = segmentar_bloques([_bloque(texto)], min_longitud=80)
    assert [a["id"] for a in args] == [0, 1]


def test_conserva_pagina_y_archivo():
    args = segmentar_bloques([_bloque(TEXTO_ARGUMENTATIVO, pagina=7, archivo="r.docx")], 80)
    assert args[0]["pagina"] == 7
    assert args[0]["archivo"] == "r.docx"


def test_dividir_parrafos_colapsa_saltos_simples():
    partes = _dividir_parrafos("línea uno\nlínea dos\n\nsegundo párrafo")
    assert partes == ["línea uno línea dos", "segundo párrafo"]
