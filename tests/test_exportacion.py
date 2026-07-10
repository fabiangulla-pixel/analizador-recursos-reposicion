"""Tests de exportacion/ — cada exportador produce su archivo, legible y con los datos."""

import json

import pandas as pd
from docx import Document

from exportacion.consolidado import (
    construir_consolidado,
    exportar_consolidado_json,
    exportar_consolidado_markdown,
)
from exportacion.indice import exportar_indice_decision
from exportacion.matriz import construir_dataframe, exportar_matriz
from exportacion.reporte import exportar_reporte_ejecutivo
from exportacion.trazabilidad import exportar_trazabilidad
from exportacion.word_export import exportar_informe_word


def test_matriz_dataframe_columnas_y_contenido(argumentos_procesados):
    df = construir_dataframe(argumentos_procesados)
    assert len(df) == 2
    assert df.loc[0, "grupo_argumental"] == "Grupo 1"
    assert df.loc[0, "ya_resuelto_en_decision_base"] == "SI"
    assert df.loc[1, "requiere_revision_humana"]


def test_exportar_matriz_genera_xlsx_y_csv(argumentos_procesados, tmp_path):
    exportar_matriz(argumentos_procesados, str(tmp_path), True, True)
    xlsx = tmp_path / "matriz_argumentos.xlsx"
    csv = tmp_path / "matriz_argumentos.csv"
    assert xlsx.exists() and csv.exists()
    assert len(pd.read_excel(xlsx)) == 2


def test_consolidado_serializable_sin_numpy(grupos_procesados):
    data = construir_consolidado(grupos_procesados)
    json.dumps(data)  # no debe lanzar TypeError por arrays numpy
    assert data[0]["ya_resuelto"] == "SI"
    assert len(data[0]["variantes"]) == 1


def test_exportar_consolidado_json_y_md(grupos_procesados, tmp_path):
    exportar_consolidado_json(grupos_procesados, str(tmp_path))
    exportar_consolidado_markdown(grupos_procesados, str(tmp_path))
    cargado = json.loads((tmp_path / "consolidado_grupos.json").read_text(encoding="utf-8"))
    assert len(cargado) == 2
    md = (tmp_path / "consolidado_grupos.md").read_text(encoding="utf-8")
    assert "Grupo 1" in md


def test_exportar_indice_clasifica_por_estado(grupos_procesados, tmp_path):
    exportar_indice_decision(grupos_procesados, str(tmp_path))
    md = (tmp_path / "propuesta_indice_decision.md").read_text(encoding="utf-8")
    assert "Argumentos nuevos" in md
    assert "Grupo 2" in md  # el grupo NO resuelto aparece como nuevo


def test_exportar_reporte_cuenta_metricas(argumentos_procesados, grupos_procesados, tmp_path):
    exportar_reporte_ejecutivo(argumentos_procesados, grupos_procesados, str(tmp_path))
    md = (tmp_path / "reporte_ejecutivo.md").read_text(encoding="utf-8")
    assert "| Documentos procesados | 2 |" in md
    assert "| Args. ya resueltos en base | 1 |" in md


def test_exportar_trazabilidad_auditable(argumentos_procesados, grupos_procesados, tmp_path):
    cfg = {"procesamiento": {"umbral_resuelto": 0.70}}
    exportar_trazabilidad(argumentos_procesados, grupos_procesados, str(tmp_path), cfg)
    data = json.loads((tmp_path / "trazabilidad.json").read_text(encoding="utf-8"))
    assert data["configuracion"] == cfg
    assert data["resumen"]["total_argumentos"] == 2
    assert data["grupos"][0]["miembros_ids"] == [0]
    assert "centroide" not in data["grupos"][0]


def test_exportar_informe_word_abre_y_tiene_contenido(
    argumentos_procesados, grupos_procesados, tmp_path
):
    exportar_informe_word(argumentos_procesados, grupos_procesados, str(tmp_path))
    ruta = tmp_path / "informe_analisis.docx"
    assert ruta.exists()
    doc = Document(str(ruta))  # el archivo abre sin reparación
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert "RECURSOS DE REPOSICIÓN" in texto
