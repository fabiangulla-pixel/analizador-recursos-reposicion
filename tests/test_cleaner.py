"""Tests de ingesta/cleaner.py — limpieza de texto jurídico."""

from ingesta.cleaner import limpiar_bloques, limpiar_texto


def test_limpiar_texto_elimina_numeracion_de_pagina():
    assert "Página 3 de 10" not in limpiar_texto("Argumento central. Página 3 de 10")


def test_limpiar_texto_elimina_lineas_decorativas():
    texto = "Primera parte ______ segunda parte ------ fin"
    limpio = limpiar_texto(texto)
    assert "______" not in limpio
    assert "------" not in limpio
    assert "Primera parte" in limpio


def test_limpiar_texto_normaliza_espacios_y_saltos():
    limpio = limpiar_texto("hola    mundo\n\n\n\n\nchao")
    assert "  " not in limpio
    assert "\n\n\n" not in limpio


def test_limpiar_texto_elimina_form_feed():
    assert "\f" not in limpiar_texto("antes\fdespués")


def test_limpiar_bloques_filtra_cortos_y_preserva_metadatos():
    bloques = [
        {"texto": "x" * 100, "pagina": 1, "archivo": "a.pdf"},
        {"texto": "corto", "pagina": 2, "archivo": "a.pdf"},
    ]
    resultado = limpiar_bloques(bloques, min_longitud=80)
    assert len(resultado) == 1
    assert resultado[0]["pagina"] == 1
    assert resultado[0]["archivo"] == "a.pdf"


def test_limpiar_bloques_no_muta_los_originales():
    bloques = [{"texto": "y" * 100 + "   con espacios   ", "pagina": 1, "archivo": "b.pdf"}]
    limpiar_bloques(bloques, min_longitud=80)
    assert bloques[0]["texto"].endswith("   ")
