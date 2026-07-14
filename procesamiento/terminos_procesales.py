"""
terminos_procesales.py
Calendario de días hábiles colombiano y verificación de oportunidad de un
recurso (CPACA art. 76: 10 días hábiles siguientes a la notificación).

Base legal del calendario: Ley 51 de 1983 (Ley Emiliani) — festivos fijos que
no se trasladan, festivos que se trasladan al lunes siguiente, y los tres
festivos móviles ligados a la Pascua (Ascensión, Corpus Christi, Sagrado
Corazón). Pascua se calcula con el algoritmo de Meeus/Jones/Butcher (estándar,
validado aquí contra 6 fechas oficiales de 2026 obtenidas por fuente primaria).

ADVERTENCIA IMPORTANTE: el Congreso puede crear festivos nuevos por ley en
cualquier momento (ej.: Ley 2578 de 2026 añadió el 13 de julio). Estos NO son
derivables del algoritmo y viven en _FESTIVOS_AD_HOC, con su fuente y fecha de
verificación. Esta tabla debe revisarse cada año — un festivo desactualizado
puede hacer que la herramienta declare "oportuno" un recurso que no lo es.
"""

from dataclasses import dataclass
from datetime import date, timedelta

# Festivos creados por ley específica, no derivables de Ley 51/1983.
# Cada entrada: fecha, nombre, fuente. Verificado por última vez: 2026-07-12.
_FESTIVOS_AD_HOC: dict[date, str] = {
    date(2026, 7, 13): "Virgen del Rosario de Chiquinquirá (Ley 2578 de 2026)",
}


def _pascua(anio: int) -> date:
    """Domingo de Pascua (algoritmo de Meeus/Jones/Butcher, calendario gregoriano)."""
    a = anio % 19
    b = anio // 100
    c = anio % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    mes = (h + ll - 7 * m + 114) // 31
    dia = ((h + ll - 7 * m + 114) % 31) + 1
    return date(anio, mes, dia)


def _proximo_lunes(fecha: date) -> date:
    """Si ya es lunes, la misma fecha; si no, el lunes siguiente."""
    dias_hasta_lunes = (7 - fecha.weekday()) % 7
    return fecha + timedelta(days=dias_hasta_lunes)


def _festivos_fijos(anio: int) -> dict[date, str]:
    """Festivos que NO se trasladan (Ley 51/1983, art. 1)."""
    pascua = _pascua(anio)
    return {
        date(anio, 1, 1): "Año Nuevo",
        pascua - timedelta(days=3): "Jueves Santo",
        pascua - timedelta(days=2): "Viernes Santo",
        date(anio, 5, 1): "Día del Trabajo",
        date(anio, 7, 20): "Independencia de Colombia",
        date(anio, 8, 7): "Batalla de Boyacá",
        date(anio, 12, 8): "Inmaculada Concepción",
        date(anio, 12, 25): "Navidad",
    }


def _festivos_emiliani(anio: int) -> dict[date, str]:
    """Festivos que se trasladan al lunes siguiente (Ley 51/1983, art. 1)."""
    pascua = _pascua(anio)
    candidatos = {
        date(anio, 1, 6): "Reyes Magos",
        date(anio, 3, 19): "San José",
        pascua + timedelta(days=39): "Ascensión del Señor",
        pascua + timedelta(days=60): "Corpus Christi",
        pascua + timedelta(days=68): "Sagrado Corazón de Jesús",
        date(anio, 6, 29): "San Pedro y San Pablo",
        date(anio, 8, 15): "Asunción de la Virgen",
        date(anio, 10, 12): "Día de la Raza y la Diversidad Étnica",
        date(anio, 11, 1): "Todos los Santos",
        date(anio, 11, 11): "Independencia de Cartagena",
    }
    return {_proximo_lunes(fecha): nombre for fecha, nombre in candidatos.items()}


def festivos_colombia(anio: int) -> dict[date, str]:
    """Todos los festivos colombianos del año, fecha → nombre."""
    festivos = {**_festivos_fijos(anio), **_festivos_emiliani(anio)}
    festivos.update({f: n for f, n in _FESTIVOS_AD_HOC.items() if f.year == anio})
    return festivos


def es_festivo(fecha: date) -> bool:
    return fecha in festivos_colombia(fecha.year)


def es_dia_habil(fecha: date) -> bool:
    """Lunes a viernes y no festivo. No considera vacancia judicial (variable cada año)."""
    return fecha.weekday() < 5 and not es_festivo(fecha)


def sumar_dias_habiles(fecha_inicio: date, n_dias: int) -> date:
    """Avanza n_dias hábiles desde fecha_inicio (sin contar fecha_inicio)."""
    fecha = fecha_inicio
    contados = 0
    while contados < n_dias:
        fecha += timedelta(days=1)
        if es_dia_habil(fecha):
            contados += 1
    return fecha


@dataclass
class Oportunidad:
    fecha_notificacion: date
    fecha_radicacion: date
    dias_habiles_aplicados: int
    dia_limite: date
    oportuno: bool


def evaluar_oportunidad(
    fecha_notificacion: date,
    fecha_radicacion: date,
    dias_habiles: int = 10,
) -> Oportunidad:
    """
    Evalúa si un recurso radicado en fecha_radicacion es oportuno frente a la
    notificación, contando dias_habiles días hábiles siguientes (CPACA art. 76:
    10 días para el recurso de reposición). El día límite es el último día
    hábil en que aún puede radicarse.
    """
    dia_limite = sumar_dias_habiles(fecha_notificacion, dias_habiles)
    return Oportunidad(
        fecha_notificacion=fecha_notificacion,
        fecha_radicacion=fecha_radicacion,
        dias_habiles_aplicados=dias_habiles,
        dia_limite=dia_limite,
        oportuno=fecha_radicacion <= dia_limite,
    )
