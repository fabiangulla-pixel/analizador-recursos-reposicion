# Analizador de Recursos de Reposición

Aplicación de escritorio para Windows que analiza una resolución sancionatoria base
y múltiples recursos de reposición, agrupa los argumentos, detecta los ya resueltos
y exporta matrices e informes para redactar la decisión final.

---

## Requisitos del equipo de desarrollo

- Windows 10/11
- Python 3.10 o superior
- Conexión a internet (solo para descargar el modelo de embeddings la primera vez)

## Instalación para desarrollo

```bash
cd recursos_reposicion
pip install -r requirements.txt
python main.py
```

---

## Cómo construir el ejecutable distribuible

```bat
build_exe.bat
```

El ejecutable quedará en `dist\AnalizadorRecursos\`.
Para distribuir, comprime esa carpeta y compártela.
Los usuarios finales solo deben descomprimir y hacer doble clic en `AnalizadorRecursos.exe`.

---

## Archivos generados tras el análisis

| Archivo | Descripción |
|---|---|
| `matriz_argumentos.xlsx` | Tabla completa de argumentos con metadatos |
| `matriz_argumentos.csv` | Misma tabla en formato CSV |
| `consolidado_grupos.json` | Grupos argumentales con trazabilidad |
| `consolidado_grupos.md` | Consolidado en formato legible |
| `propuesta_indice_decision.md` | Índice sugerido para la decisión final |
| `reporte_ejecutivo.md` | Resumen del análisis |
| `trazabilidad.json` | JSON completo para auditoría |
| `analisis.log` | Log técnico del proceso |

---

## Ajuste de umbrales (config.yaml)

| Parámetro | Descripción | Default |
|---|---|---|
| `umbral_similitud` | Similitud mínima para considerar argumentos iguales | 0.75 |
| `umbral_resuelto` | Similitud mínima para marcar argumento como resuelto | 0.70 |
| `umbral_distancia` | Distancia máxima para agrupar (clustering) | 0.30 |
| `min_longitud_bloque` | Mínimo de caracteres por bloque | 80 |

---

## Estructura del proyecto

```
recursos_reposicion/
├── main.py
├── config.yaml
├── requirements.txt
├── build_exe.bat
├── recursos_reposicion.spec
├── app/          (GUI y pipeline)
├── ingesta/      (lectura y limpieza de documentos)
├── procesamiento/ (segmentación, vectorización, agrupación, comparación)
├── exportacion/  (generación de archivos de salida)
└── utils/        (logger)
```
