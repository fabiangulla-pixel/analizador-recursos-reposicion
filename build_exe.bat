@echo off
REM ============================================================
REM build_exe.bat
REM Script para construir el ejecutable con PyInstaller
REM Ejecutar desde la carpeta raíz del proyecto:
REM   cd C:\ruta\al\proyecto
REM   build_exe.bat
REM ============================================================

echo.
echo ============================================================
echo  PASO 1: Verificando entorno Python
echo ============================================================
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado en el PATH.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  PASO 2: Instalando dependencias
echo ============================================================
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  PASO 3: Pre-descargando modelo de embeddings
echo  (Solo necesario la primera vez)
echo ============================================================
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print('Modelo listo.')"
if errorlevel 1 (
    echo ERROR: No se pudo descargar el modelo. Verifica la conexión a internet.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  PASO 4: Construyendo ejecutable (modo one-folder)
echo ============================================================
pyinstaller recursos_reposicion.spec --clean
if errorlevel 1 (
    echo ERROR: PyInstaller falló.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  LISTO
echo ============================================================
echo  Ejecutable generado en: dist\AnalizadorRecursos\
echo  Archivo principal:      dist\AnalizadorRecursos\AnalizadorRecursos.exe
echo.
echo  Para distribuir: comprime la carpeta dist\AnalizadorRecursos\
echo  y compártela. El usuario solo debe descomprimir y ejecutar.
echo ============================================================
pause
