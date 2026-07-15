"""
pipeline.py
Orquestador principal del análisis.
Llama a cada módulo en orden y devuelve progreso mediante callback.
Diseñado para ejecutarse en un hilo separado para no bloquear la GUI.
"""

import os
from collections.abc import Callable
from typing import Any

from app.config_loader import cargar_config
from exportacion.consolidado import exportar_consolidado_json, exportar_consolidado_markdown
from exportacion.indice import exportar_indice_decision
from exportacion.matriz import exportar_matriz
from exportacion.pdf_anotado import generar_pdfs_anotados
from exportacion.reporte import exportar_reporte_ejecutivo
from exportacion.trazabilidad import exportar_trazabilidad
from exportacion.word_export import exportar_informe_word
from ingesta.cleaner import limpiar_bloques
from ingesta.reader import leer_archivo, leer_carpeta
from procesamiento.agrupador import agrupar_argumentos, construir_grupos
from procesamiento.citas_normativas import anotar_citas
from procesamiento.comparador import comparar_con_base, comparar_grupos_con_base
from procesamiento.segmentador import segmentar_bloques
from procesamiento.vectorizador import cargar_modelo, vectorizar
from utils.logger import configurar_logger, obtener_logger


def ejecutar_analisis(
    ruta_base: str,
    carpeta_recursos: str,
    carpeta_salida: str,
    callback_progreso: Callable[[str, int], None] | None = None,
) -> dict[str, Any]:
    """
    Ejecuta el pipeline completo de análisis.

    Args:
        ruta_base: Ruta al archivo de la resolución sancionatoria base.
        carpeta_recursos: Carpeta con los recursos de reposición.
        carpeta_salida: Carpeta donde se guardarán los resultados.
        callback_progreso: función(mensaje: str, porcentaje: int) para actualizar la GUI.

    Returns:
        Dict con resumen del análisis o clave 'error' si falló.
    """

    def progreso(msg: str, pct: int) -> None:
        if callback_progreso:
            callback_progreso(msg, pct)

    try:
        # ── 0. Configuración y logging ──────────────────────────────────────
        cfg = cargar_config()
        ruta_log = os.path.join(carpeta_salida, cfg["logging"]["archivo_log"])
        configurar_logger(cfg["logging"]["nivel"], ruta_log)
        log = obtener_logger()

        log.info("=== Inicio del análisis ===")
        progreso("Cargando configuración...", 5)

        ext = cfg["ingesta"]["extensiones_soportadas"]
        enc = cfg["ingesta"]["encoding_fallback"]
        min_lon = cfg["procesamiento"]["min_longitud_bloque"]
        modelo_nombre = cfg["procesamiento"]["modelo_embeddings"]
        umbral_res = cfg["procesamiento"]["umbral_resuelto"]
        umbral_dist = cfg["procesamiento"]["umbral_distancia"]
        metodo_cl = cfg["procesamiento"]["metodo_clustering"]

        # ── 1. Leer resolución base ─────────────────────────────────────────
        progreso("Leyendo resolución sancionatoria base...", 10)
        bloques_base_raw = leer_archivo(ruta_base, enc)
        if not bloques_base_raw:
            return {"error": f"No se pudo extraer texto de la resolución base: {ruta_base}"}
        bloques_base = limpiar_bloques(bloques_base_raw, min_lon)
        log.info(f"Resolución base: {len(bloques_base)} bloques limpios.")

        # ── 2. Leer recursos de reposición ──────────────────────────────────
        progreso("Leyendo recursos de reposición...", 20)
        bloques_recursos_raw = leer_carpeta(carpeta_recursos, ext, enc)
        if not bloques_recursos_raw:
            return {"error": f"No se encontraron documentos en: {carpeta_recursos}"}
        bloques_recursos = limpiar_bloques(bloques_recursos_raw, min_lon)
        log.info(f"Recursos: {len(bloques_recursos)} bloques limpios.")

        # ── 3. Segmentar argumentos ─────────────────────────────────────────
        progreso("Segmentando bloques argumentativos...", 30)
        argumentos = segmentar_bloques(bloques_recursos, min_lon)
        if not argumentos:
            return {"error": "No se encontraron argumentos en los recursos. Revisa los archivos."}

        progreso("Extrayendo citas normativas...", 35)
        argumentos = anotar_citas(argumentos)

        # ── 4. Cargar modelo y vectorizar ───────────────────────────────────
        progreso("Cargando modelo de lenguaje (primera vez puede tardar)...", 40)
        cargar_modelo(modelo_nombre)

        progreso("Vectorizando argumentos...", 50)
        textos = [a["texto"] for a in argumentos]
        embeddings = vectorizar(textos)

        # ── 5. Agrupar argumentos ───────────────────────────────────────────
        progreso("Agrupando argumentos similares...", 60)
        argumentos = agrupar_argumentos(argumentos, embeddings, umbral_dist, metodo_cl)
        grupos = construir_grupos(argumentos, embeddings)

        # ── 6. Comparar con resolución base ─────────────────────────────────
        progreso("Comparando argumentos con la resolución base...", 70)
        argumentos = comparar_con_base(argumentos, embeddings, bloques_base, umbral_res)
        grupos = comparar_grupos_con_base(grupos, bloques_base, umbral_res)

        # ── 7. Exportar resultados ──────────────────────────────────────────
        progreso("Exportando matriz de argumentos...", 80)
        exportar_matriz(
            argumentos,
            carpeta_salida,
            cfg["exportacion"]["generar_xlsx"],
            cfg["exportacion"]["generar_csv"],
        )

        progreso("Exportando consolidado de grupos...", 85)
        if cfg["exportacion"]["generar_json"]:
            exportar_consolidado_json(grupos, carpeta_salida)
        if cfg["exportacion"]["generar_markdown"]:
            exportar_consolidado_markdown(grupos, carpeta_salida)

        progreso("Generando propuesta de índice...", 88)
        exportar_indice_decision(grupos, carpeta_salida)

        progreso("Generando reporte ejecutivo...", 92)
        exportar_reporte_ejecutivo(argumentos, grupos, carpeta_salida)

        progreso("Exportando trazabilidad...", 93)
        exportar_trazabilidad(argumentos, grupos, carpeta_salida, cfg)

        progreso("Generando informe Word...", 97)
        exportar_informe_word(argumentos, grupos, carpeta_salida)

        progreso("Generando PDFs anotados...", 99)
        pdfs_anotados = generar_pdfs_anotados(argumentos, carpeta_recursos, carpeta_salida)

        progreso("¡Análisis completado!", 100)
        log.info("=== Análisis completado exitosamente ===")

        return {
            "ok": True,
            "total_argumentos": len(argumentos),
            "total_grupos": len(grupos),
            "carpeta_salida": carpeta_salida,
            "pdfs_anotados": pdfs_anotados,
        }

    except Exception as e:
        import traceback

        msg = f"Error en el análisis: {e}\n{traceback.format_exc()}"
        obtener_logger().error(msg)
        return {"error": str(e)}
