# scripts/

Utilidades de desarrollo. No forman parte del producto.

| Script | Qué hace |
|---|---|
| `crear_docs_prueba.py` | Genera los documentos sintéticos de `prueba/` (resolución base + 4 recursos DOCX) para probar el pipeline sin datos reales. |
| `crear_icono.py` | Genera `icono.ico` de la aplicación. |
| `e2e_pipeline.py` | Prueba de humo manual: corre el pipeline completo (con modelo de embeddings real) sobre `prueba/`. No es parte de la suite de pytest. |
| `install_hooks.py` | Instala el hook de pre-commit que corre `check.bat` antes de cada commit. |
