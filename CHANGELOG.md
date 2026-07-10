# Changelog

Todas las novedades relevantes del proyecto, de la más reciente a la más antigua.

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
