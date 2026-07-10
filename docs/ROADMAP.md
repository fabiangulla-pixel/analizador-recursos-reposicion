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

1. **Extractor de citas normativas colombianas** (inspirado en eyecite, regex local):
   detectar `Ley 1437 de 2011, art. 76`, `Decreto`, `Resolución`, `Sentencia C-123/2020`,
   `T-`, `SU-`, CPACA, y añadir columnas `normas_citadas` / `jurisprudencia_citada`
   a la matriz. El abogado vería de un vistazo el fundamento de cada argumento y
   podría agrupar por fundamento jurídico, no solo por similitud semántica.
2. **Verificación de oportunidad del recurso**: extraer fechas (notificación de la
   resolución vs. radicación del recurso), calcular días hábiles (festivos de
   Colombia) y alertar si el recurso parece extemporáneo (CPACA art. 76: 10 días).
   Es lo primero que revisa un abogado y es puro cálculo local.
3. **OCR de respaldo para PDFs escaneados**: hoy `reader.py` solo advierte
   "página sin texto extraíble". Integrar Tesseract (ya dominado en Bashkar
   Station) para que los recursos escaneados no queden por fuera del análisis.
4. **PDF anotado por argumento**: generar copia del recurso con cada argumento
   resaltado y numerado con su grupo (estándar ya usado en /verificar-creditos).
   El abogado navega el expediente original con el mapa de argumentos encima.

## Prioridad 2 — Valor alto, esfuerzo medio

5. **Borrador de proyecto de decisión en Word**: hoy se exporta una propuesta de
   índice; el salto es generar el esqueleto completo del acto administrativo con
   una sección por grupo argumental, la evidencia de la resolución base citada
   textualmente y espacios `[PENDIENTE: respuesta del funcionario]`. Sin IA
   generativa: puro ensamblaje de lo ya extraído.
6. **Clasificación del tipo de argumento por taxonomía jurídica** (debido proceso,
   caducidad/prescripción, falta de competencia, proporcionalidad de la sanción,
   valoración probatoria…): similitud de embeddings contra descripciones curadas
   de cada categoría — sin modelo nuevo, sin entrenamiento.
7. **HDBSCAN como método de clustering alternativo** (paper de Key Point Analysis):
   no exige fijar `umbral_distancia` y maneja mejor grupos de densidad distinta.
   Añadir como opción en `config.yaml`, comparar con el caso real 20016795.
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
