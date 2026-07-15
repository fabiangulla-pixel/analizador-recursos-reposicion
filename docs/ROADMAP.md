# Roadmap — Analizador de Recursos de Reposición

Ideas priorizadas para facilitarle más la vida a los abogados que resuelven
recursos, informadas por una revisión de proyectos similares en GitHub
(2026-07-10). Principio rector del proyecto: **100% local, sin APIs de pago,
el abogado decide — la herramienta organiza y evidencia.**

## Qué existe afuera (referencias)

| Proyecto | Qué hace | Qué nos enseña |
|---|---|---|
| [eyecite](https://github.com/freelawproject/eyecite) (Free Law Project) | Extrae citas legales de cualquier texto (55M+ citas, EE. UU.) | El patrón "extraer y resolver citas normativas" es la función más valiosa de las herramientas jurídicas maduras. No sirve directo para Colombia, pero el diseño sí. |
| [OpenContracts](https://github.com/Open-Source-Legal/OpenContracts) | Plataforma de inteligencia documental jurídica con parsers/embedders intercambiables | Arquitectura por componentes intercambiables — ya la tenemos (ingesta/procesamiento/exportación). Validación del enfoque. |
| [Legal-Text-Analytics](https://github.com/Liquid-Legal-Institute/Legal-Text-Analytics) y [awesome-legal-nlp](https://github.com/maastrichtlawtech/awesome-legal-nlp) | Listas curadas de métodos y recursos de NLP jurídico | Catálogo para robar ideas con criterio. |
| [Key Point Analysis de sentencias](https://arxiv.org/pdf/2212.12238) (paper) | Encode con Legal-BERT → clustering aglomerativo/HDBSCAN → punto clave por grupo | Exactamente nuestro pipeline. Mejora sugerida: probar HDBSCAN (no exige umbral fijo de distancia). |
| [lm-legal-es / RoBERTalex](https://github.com/PlanTL-GOB-ES/lm-legal-es) y [legal-longformer-base-8192-spanish](https://huggingface.co/mrm8488/legal-longformer-base-8192-spanish) | Modelos de lenguaje jurídico en español (Plan-TL, BSC) | Candidatos para subir la calidad de los embeddings en texto jurídico español. Más pesados que MiniLM: evaluar costo/beneficio en .exe. |
| [OpenLex](https://github.com/PyAr/OpenLex) | Gestión de estudios jurídicos (Python, Argentina) | El nicho hispano está poco cubierto — esta herramienta tiene espacio real. |

## Prioridad 1 — Alto valor, bajo riesgo, offline

1. ✅ **Extractor de citas normativas colombianas** — HECHO (12-jul-2026,
   `procesamiento/citas_normativas.py`, commit `f3aaa35`). Leyes, decretos,
   resoluciones, sentencias C-/T-/SU-, códigos por sigla, Constitución.
   Integrado a la matriz (columna `citas_normativas`).
2. ✅ **Calendario de días hábiles y verificación de oportunidad** — HECHO
   (12-jul-2026, `procesamiento/terminos_procesales.py`). Festivos colombianos
   completos (Ley 51/1983 + festivos ad hoc por ley, verificados contra fuente
   oficial 2026), `evaluar_oportunidad()` para CPACA art. 76 (10 días hábiles).
   **Decisión de diseño**: NO se integró extracción automática de fechas desde
   el texto del expediente — identificar cuál fecha es "notificación" y cuál es
   "radicación" en un PDF libre es poco confiable y una fecha mal identificada
   podría hacer que la herramienta declare "oportuno" un recurso que no lo es
   (playbook: nunca fabricar un dato incierto en una pieza que el abogado usará
   para decidir). v1 queda como función lista para invocar manualmente desde la
   GUI (el abogado confirma las dos fechas) — ver ítem 2bis. También es el
   núcleo directo de **P3** como calculadora standalone.
   - [ ] 2bis: wire a la GUI — dos campos de fecha + botón "verificar oportunidad".
   - [ ] Revisar `_FESTIVOS_AD_HOC` cada enero (el Congreso puede añadir festivos).
3. ✅ **OCR de respaldo para PDFs escaneados** — HECHO (12-jul-2026,
   `ingesta/ocr_respaldo.py`). Cuando una página de PDF no tiene texto
   embebido, se renderiza con PyMuPDF y se le aplica Tesseract (mismo patrón
   de localización que Bashkar Station: PATH → caché → Program Files, más
   `TESSDATA_PREFIX` apuntando a `C:\Users\Lenovo\tessdata` porque el
   instalador de Windows no trae `spa.traineddata`). Cada bloque queda
   marcado `fuente: "nativo"` u `"ocr"` (columna `fuente_texto` en la matriz)
   para que el abogado sepa qué texto puede tener errores de reconocimiento.
   Se degrada sin romper el pipeline si Tesseract no está instalado.
4. ✅ **PDF anotado por argumento** — HECHO (12-jul-2026,
   `exportacion/pdf_anotado.py`). Genera `recursos_anotados/anotado_<archivo>.pdf`
   por cada recurso en PDF: resalta el inicio de cada argumento (color verde/
   naranja/rojo según si ya fue resuelto en la base, mismo esquema que el
   informe Word) con comentario de grupo y similitud — mismo mecanismo
   Highlight+comentario que la skill /verificar-creditos. Verificado
   renderizando el PDF de salida (no solo contando anotaciones por script).
   **Limitación honesta y documentada**: solo funciona sobre argumentos
   `fuente: "nativo"` — las páginas que vinieron de OCR de respaldo no tienen
   capa de texto seleccionable en el PDF original, así que no hay nada que
   resaltar ahí (se cuentan aparte como `omitidos_por_ocr`, no se ocultan).
   Documentos .docx/.txt no se anotan (mecanismo distinto, fuera de alcance).

   **Prioridad 1 del roadmap original: COMPLETA** (los 4 ítems).

## Prioridad 2 — Valor alto, esfuerzo medio

5. ✅ **Borrador de proyecto de decisión en Word** — HECHO (12-jul-2026,
   `exportacion/borrador_decision.py`, commit `5613eb4`). Genera
   `borrador_decision.docx`: esqueleto real del acto administrativo
   (encabezado, CONSIDERANDO numerado por grupo con evidencia citada
   textualmente, RESUELVE con artículos), no solo un índice. Grupos nuevos
   primero (mayor prioridad de redacción). Todo dato que solo el funcionario
   conoce queda como `[PENDIENTE: ...]` explícito — sin IA generativa, puro
   ensamblaje de lo ya extraído.
6. ✅ **Clasificación del tipo de argumento por taxonomía jurídica** — HECHO
   (12-jul-2026, `procesamiento/taxonomia.py`, commit `e150064`). 7
   categorías curadas (debido proceso, caducidad/prescripción, falta de
   competencia, proporcionalidad de la sanción, valoración probatoria,
   nulidad por vicios de forma, falsa motivación), similitud de embeddings
   contra descripciones curadas — sin modelo nuevo, sin entrenamiento.
   Calibrado con el modelo real: 7/7 categorías correctas sobre ejemplos
   jurídicos reales (similitud 0.58–0.78), umbral 0.30 con margen amplio
   frente a texto irrelevante (similitud -0.09).
7. ✅ **HDBSCAN como método de clustering alternativo** — HECHO (12-jul-2026,
   `procesamiento/agrupador.py::_clustering_hdbscan`). Disponible como
   `metodo_clustering: "hdbscan"` en `config.yaml`; ya no requiere paquete
   externo (`sklearn.cluster.HDBSCAN` desde scikit-learn 1.3, ya cubierto por
   `requirements.txt`). Reasigna el ruido (-1) a grupos individuales en vez
   de fusionarlo bajo una etiqueta común.
   **Hallazgo honesto de calibración**: con `min_cluster_size=2` (necesario
   para no perder grupos recurrentes de solo 2 documentos, que es el valor
   central de esta herramienta), HDBSCAN es notablemente menos estable que
   agglomerative en las muestras pequeñas típicas de este dominio (decenas
   de bloques argumentativos): en pruebas con nubes sintéticas bien
   separadas, solo 7/10 semillas produjeron la agrupación limpia esperada
   (las otras fragmentaron una nube densa en sub-grupos espurios). Por eso
   sigue siendo una alternativa opcional, no el método por defecto — falta
   comparar directamente con el caso real 20016795 antes de recomendarlo.
8. **Gestión de expedientes**: hoy cada análisis es una carpeta suelta; una vista
   "expediente" (base + recursos + resultados + fecha) permitiría reabrir y
   comparar análisis. SQLite local, como en otros proyectos de la casa.

## Prioridad 3 — Explorar con calma

9. **Embeddings jurídicos en español** (RoBERTalex / legal-longformer): medir en
   el caso real si mejoran la agrupación frente a MiniLM multilingüe. Ojo: motor
   más pesado en el .exe y primera descarga mayor.
10. **Resumen extractivo por grupo**: además del argumento representativo
    (centroide), las 2-3 frases más centrales del grupo (TextRank local).

## Deuda técnica consciente

- [ ] GUI (`app/gui.py`) sin tests (Tkinter; requiere display — se prueba a mano).
- [ ] `build_exe.bat` no se valida en CI (compilación manual con `--clean`).
- [ ] Redistribuir el .exe cuando se acumulen mejoras funcionales (el desplegado
      en el Escritorio es anterior al fix de HF_HUB_OFFLINE) — dueño: Claude,
      cuando Fabian lo pida.
