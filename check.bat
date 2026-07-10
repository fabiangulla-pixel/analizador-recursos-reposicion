@echo off
REM check.bat - CI local: lint + formato + tests. Corre todo de un golpe.
setlocal
set PY=%~dp0venv_build\Scripts\python.exe
if not exist "%PY%" set PY=python

echo === 1/3 Lint (ruff check) ===
"%PY%" -m ruff check .
if errorlevel 1 goto :fallo

echo === 2/3 Formato (ruff format --check) ===
"%PY%" -m ruff format --check .
if errorlevel 1 goto :fallo

echo === 3/3 Tests (pytest) ===
"%PY%" -m pytest -q
if errorlevel 1 goto :fallo

echo.
echo [OK] Todo en verde.
exit /b 0

:fallo
echo.
echo [FALLO] Revisa los errores de arriba.
exit /b 1
