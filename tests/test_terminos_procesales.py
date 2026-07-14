"""
Tests de procesamiento/terminos_procesales.py — calendario de festivos y
oportunidad de recursos.

Los festivos de 2026 usados como ancla fueron verificados contra fuentes
oficiales (búsqueda web, 2026-07-12), no recordados de memoria: Reyes,
San José, Ascensión, Corpus Christi, Sagrado Corazón, San Pedro y San Pablo,
Asunción, Día de la Raza y Todos los Santos.
"""

from datetime import date

from procesamiento.terminos_procesales import (
    es_dia_habil,
    es_festivo,
    evaluar_oportunidad,
    festivos_colombia,
    sumar_dias_habiles,
)


def test_pascua_2026_coincide_con_fuente_oficial():
    # Domingo de Pascua 2026 = 5 de abril, derivado de 3 festivos oficiales
    # independientes (Ascensión, Corpus Christi, Sagrado Corazón).
    festivos = festivos_colombia(2026)
    assert date(2026, 4, 2) in festivos  # Jueves Santo = Pascua - 3
    assert date(2026, 4, 3) in festivos  # Viernes Santo = Pascua - 2


def test_festivos_fijos_no_se_trasladan():
    festivos = festivos_colombia(2026)
    assert festivos[date(2026, 1, 1)] == "Año Nuevo"
    assert festivos[date(2026, 5, 1)] == "Día del Trabajo"
    assert festivos[date(2026, 7, 20)] == "Independencia de Colombia"
    assert festivos[date(2026, 8, 7)] == "Batalla de Boyacá"
    assert festivos[date(2026, 12, 8)] == "Inmaculada Concepción"
    assert festivos[date(2026, 12, 25)] == "Navidad"


def test_festivos_emiliani_2026_contra_fuente_oficial():
    festivos = festivos_colombia(2026)
    esperados = {
        date(2026, 1, 12): "Reyes Magos",
        date(2026, 3, 23): "San José",
        date(2026, 5, 18): "Ascensión del Señor",
        date(2026, 6, 8): "Corpus Christi",
        date(2026, 6, 15): "Sagrado Corazón de Jesús",
        date(2026, 6, 29): "San Pedro y San Pablo",
        date(2026, 8, 17): "Asunción de la Virgen",
        date(2026, 10, 12): "Día de la Raza y la Diversidad Étnica",
        date(2026, 11, 2): "Todos los Santos",
    }
    for fecha, nombre in esperados.items():
        assert festivos[fecha] == nombre, f"{fecha} esperado {nombre}, fue {festivos.get(fecha)}"


def test_festivo_ad_hoc_2026_chiquinquira():
    # Ley 2578 de 2026, no derivable del algoritmo — verificado por fuente
    # primaria, no por el cálculo de Ley 51/1983.
    assert es_festivo(date(2026, 7, 13))
    assert festivos_colombia(2026)[date(2026, 7, 13)].startswith("Virgen del Rosario")


def test_festivo_ad_hoc_no_contamina_otros_anios():
    assert date(2026, 7, 13) not in festivos_colombia(2025)
    assert date(2026, 7, 13) not in festivos_colombia(2027)


def test_proximo_lunes_ya_es_lunes_no_se_mueve():
    # San Pedro y San Pablo 2026 (29 jun) cae en lunes: no se traslada.
    festivos = festivos_colombia(2026)
    assert festivos[date(2026, 6, 29)] == "San Pedro y San Pablo"


def test_es_dia_habil_excluye_fin_de_semana_y_festivos():
    assert es_dia_habil(date(2026, 7, 6)) is True  # lunes ordinario
    assert es_dia_habil(date(2026, 7, 4)) is False  # sábado
    assert es_dia_habil(date(2026, 7, 5)) is False  # domingo
    assert es_dia_habil(date(2026, 1, 1)) is False  # festivo fijo


def test_sumar_dias_habiles_salta_fin_de_semana_y_festivo():
    # Jueves 2026-07-09 + 3 días hábiles: vie10(1º), salta sáb11/dom12,
    # lun13 es festivo ad hoc -> salta, mar14(2º), mie15(3º).
    resultado = sumar_dias_habiles(date(2026, 7, 9), 3)
    assert resultado == date(2026, 7, 15)
    assert es_dia_habil(resultado)


def test_evaluar_oportunidad_recurso_dentro_del_plazo():
    notificacion = date(2026, 6, 1)  # lunes
    limite = sumar_dias_habiles(notificacion, 10)
    resultado = evaluar_oportunidad(notificacion, limite, dias_habiles=10)
    assert resultado.oportuno is True
    assert resultado.dia_limite == limite


def test_evaluar_oportunidad_recurso_extemporaneo():
    notificacion = date(2026, 6, 1)
    limite = sumar_dias_habiles(notificacion, 10)
    un_dia_habil_tarde = sumar_dias_habiles(limite, 1)
    resultado = evaluar_oportunidad(notificacion, un_dia_habil_tarde, dias_habiles=10)
    assert resultado.oportuno is False
