# Changelog

Todas las novedades relevantes del proyecto, de la más reciente a la más antigua.

## [1.2.0] — 2026-07-12 · Primer producto de la Suite Legal

Este proyecto pasa a ser "P1 — Analizador PRO" de una suite comercial más
amplia (ver `C:\Users\Lenovo\suite-legal\PLAN_SUITE_LEGAL.md`). Nuevas
funciones del roadmap de prioridad 1:

### Añadido
- **Extractor de citas normativas colombianas** (`procesamiento/citas_normativas.py`):
  leyes, decretos, resoluciones, sentencias C-/T-/SU-, códigos por sigla
  (CPACA, CGP...) y Constitución Política. Columna `citas_normativas` nueva
  en la matriz de argumentos. Inspirado en el diseño de eyecite (Free Law
  Project), adaptado al derecho colombiano. 11 tests.
- **Calendario de días hábiles colombiano y verificación de oportunidad**
  (`procesamiento/terminos_procesales.py`): festivos completos (Ley 51/1983 +
  tabla de festivos ad hoc creados por ley, verificados contra fuente oficial
  para 2026 — incluye el nuevo festivo del 13 de julio, Ley 2578 de 2026),
  `evaluar_oportunidad()` para el término de 10 días hábiles del CPACA art. 76.
  Módulo independiente, listo para invocarse desde la GUI con fechas
  confirmadas por el abogado (no se extraen automáticamente del texto — ver
  ROADMAP para el porqué). 10 tests. Núcleo directo del futuro producto P3
  (calculadora de términos procesales standalone).

## [1.1.0] — 2026-07-10 · Pase de calidad (Modo-Ingeniero)

Sin cambios de comportamiento en el pipeline validado, salvo una mejora de
robustez del .exe:

### Corregido
- **El .exe ya no requiere internet si el modelo está descargado**: al detectar
  el modelo en `_modelos_cache/` se fuerza `HF_HUB_OFFLINE=1` antes de importar
  sentence-transformers. Sin esto, HuggingFace hace una petición HEAD de
  verificación al hub y el análisis falla en equipos sin conexión aunque el
  modelo esté completo en disco (lección aprendida en otros .exe congelados).

### Infraestructura
- **Control de versiones**: repositorio git con `.gitignore` y `.gitattributes`;
  el commit inicial captura el código tal como funcionó en el caso real.
- **Lint + formato**: ruff configurado en `pyproject.toml` (154 hallazgos
  corregidos en automático + 5 manuales: variables muertas e índices sin usar).
  `B905` y `UP015` ignorados de forma documentada para no tocar semántica.
- **Tests**: suite nueva de 36 tests offline en `tests/` (limpieza, segmentación,
  clustering, comparación con base, todos los exportadores incluido el Word).
  Corre en ~4 s, sin modelo de embeddings ni red.
- **CI local**: `check.bat` y `Makefile` (lint + formato + tests) y hook de
  pre-commit (`scripts/install_hooks.py`) que aborta el commit si algo falla.
- **Higiene**: utilidades de desarrollo movidas a `scripts/` con README;
  el antiguo `test_pipeline.py` es ahora `scripts/e2e_pipeline.py` con rutas
  portables (antes tenía rutas absolutas de esta máquina).

## [1.0.0] — 2026-04-07 · Versión inicial

- Pipeline completo: ingesta (PDF/DOCX/TXT) → limpieza → segmentación de
  argumentos → embeddings locales (`paraphrase-multilingual-MiniLM-L12-v2`) →
  clustering aglomerativo → comparación contra la resolución base → exportación
  (XLSX, CSV, JSON, Markdown, informe Word, trazabilidad).
- GUI de escritorio (Tkinter) y ejecutable PyInstaller (`AnalizadorRecursos.exe`).
- Usada con éxito en un caso real (expediente 20016795, 2 recursos analizados).
