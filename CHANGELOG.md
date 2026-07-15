# Changelog

Todas las novedades relevantes del proyecto, de la más reciente a la más antigua.

## [1.3.1] — 2026-07-15 · Dos bugs críticos de empaquetado corregidos

El .exe recompilado con todo lo de 1.2.0/1.3.0 **no cargaba el modelo 100%
offline** — dos bugs independientes en `recursos_reposicion.spec` y
`procesamiento/vectorizador.py`, encontrados al hacer el smoke-test real del
build (no solo verificar que compilara):

### Corregido
- **Estructura de caché del modelo incorrecta**: `SentenceTransformer(...,
  cache_folder=X)` exige la estructura real de HuggingFace dentro de X
  (`models--<org>--<modelo>/snapshots/<hash>/*` + `refs/main`), pero el
  `.spec` empaquetaba el modelo en una carpeta plana
  (`_modelos_cache/paraphrase-multilingual-MiniLM-L12-v2/`). Corregido para
  replicar la estructura anidada real, verificada cargando el modelo en una
  caché vacía para confirmar el formato exacto antes de aplicar el fix.
- **Ruta de caché apuntando al lugar equivocado**: PyInstaller 6.x (builds
  one-folder) coloca todos los `datas` del `.spec` dentro de `_internal/`,
  no junto al `.exe`. `_get_cache_dir()` en `vectorizador.py` buscaba con
  `os.path.dirname(sys.executable)` (nivel del `.exe`, vacío), en vez de
  `sys._MEIPASS` (que en builds one-folder es la carpeta `_internal/`
  persistente donde realmente aterrizan los datos) — mismo patrón que ya
  usaba correctamente `app/config_loader.py`. Ambos bugs se compensaban en
  apariencia (el modelo "existía" en el build, solo que en el lugar
  equivocado) y solo se detectan cargando el modelo de verdad, no
  inspeccionando archivos.
- **Verificación real, no solo build exitoso**: simulado el entorno frozen
  exacto (`sys.frozen`, `sys._MEIPASS` apuntando al `_internal/` real del
  build) con `HF_HUB_OFFLINE=1`, sin `HF_HOME` ni caché real del usuario
  accesible (USERPROFILE/HOME apuntando a una carpeta inexistente) — el
  modelo cargó y vectorizó correctamente sin ninguna red ni caché de
  respaldo, confirmando que el .exe funciona 100% offline de verdad.

Nota de diseño: se revisó también `utils/expedientes_db.py` (escrito hoy con
el mismo patrón `os.path.dirname(sys.executable)`) — en ese caso SÍ es
correcto, porque la base de datos se crea en tiempo de ejecución (no es un
recurso pre-empaquetado que PyInstaller reubique), y tenerla junto al .exe
es además más visible/conveniente para el usuario que dentro de `_internal/`.

Redesplegado en `Desktop\Mis Apps\AnalizadorRecursos\` (ubicación real
actual — el Escritorio se reorganizó desde el último despliegue conocido).

## [1.3.0] — 2026-07-12 · Prioridad 2 del roadmap

### Añadido
- **Borrador real de decisión en Word** (`exportacion/borrador_decision.py`):
  `borrador_decision.docx` con la estructura real del acto administrativo
  (CONSIDERANDO numerado por grupo con evidencia citada textualmente,
  RESUELVE con artículos), no solo un índice de referencia. Grupos nuevos
  primero. Todo dato que solo el funcionario conoce queda `[PENDIENTE: ...]`
  explícito. 8 tests, verificado imprimiendo el documento completo.
- **Taxonomía de argumentos por categoría jurídica** (`procesamiento/taxonomia.py`):
  7 categorías curadas, similitud de embeddings sin modelo nuevo. Calibrado
  con el modelo real: 7/7 correctas en ejemplos jurídicos, umbral 0.30 con
  margen amplio frente a ruido. Columna `categoria_juridica` en la matriz.
- **HDBSCAN como método de clustering alternativo**
  (`procesamiento/agrupador.py`): `metodo_clustering: "hdbscan"` en
  `config.yaml`, sin dependencia nueva (ya en scikit-learn). Reasigna el
  ruido (-1) a grupos individuales. Hallazgo de calibración documentado en
  el ROADMAP: menos estable que agglomerative en muestras pequeñas con
  `min_cluster_size=2` (7/10 semillas limpias en pruebas sintéticas) — sigue
  siendo opcional, no el método por defecto.

- **Registro de expedientes** (`utils/expedientes_db.py`): cada análisis
  exitoso queda registrado en `expedientes.db` (SQLite local junto al
  ejecutable) con fecha, nombre, rutas y totales. Conexión abierta y
  cerrada por uso, nunca cacheada entre hilos. Un fallo al registrar nunca
  revienta un análisis ya exitoso. Solo capa de datos: la vista en la GUI
  (listar/reabrir/comparar expedientes) queda pendiente. 9 tests, incluida
  una prueba de registros concurrentes desde 10 hilos.

Con esto se completan los 4 ítems de prioridad 2 del roadmap en su capa de
datos/lógica (queda pendiente conectar 2 de ellos a la GUI: el calendario de
oportunidad y la vista de expedientes).

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
- **OCR de respaldo para PDFs escaneados** (`ingesta/ocr_respaldo.py`):
  cuando una página no tiene texto embebido, se renderiza con PyMuPDF y se
  reconoce con Tesseract (mismo patrón de localización de binario y de
  `TESSDATA_PREFIX` que Bashkar Station). Cada bloque queda marcado
  `fuente: "nativo"` u `"ocr"`, propagado hasta la columna `fuente_texto` de
  la matriz — transparencia sobre qué texto puede tener errores de OCR.
  15 tests (6 unitarios con mocks + 1 con Tesseract real de punta a punta).
- **PDF anotado por argumento** (`exportacion/pdf_anotado.py`): genera
  `recursos_anotados/anotado_<archivo>.pdf` por cada recurso PDF, con cada
  argumento resaltado (verde/naranja/rojo según su resolución) y un
  comentario con su grupo y similitud — mismo mecanismo que la skill
  /verificar-creditos. Solo aplica a argumentos con texto nativo (no a los
  recuperados por OCR, que no tienen capa de texto en el PDF original).
  Nuevo paso del pipeline al 99%. 9 tests, verificado además renderizando
  visualmente un caso realista (no solo contando anotaciones por script).

Con esto se completan los 4 ítems de prioridad 1 del roadmap de P1.

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
