@echo off
setlocal enabledelayedexpansion
title Wiki URL Analyzer - Iniciador
color 0B

echo ============================================
echo   Wiki URL Analyzer - Iniciador automatico
echo ============================================
echo.

REM --- 1. Comprobar que Python esta instalado ---
echo [1/4] Comprobando instalacion de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] No se encontro Python en el sistema.
    echo Por favor instala Python 3.13 o superior desde https://www.python.org/downloads/
    echo Asegurate de marcar la opcion "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
echo       Python %PY_VERSION% detectado correctamente.
echo.

REM --- 2. Crear entorno virtual si no existe ---
echo [2/4] Comprobando entorno virtual...
if not exist "venv\Scripts\activate.bat" (
    echo       No se encontro un entorno virtual. Creando uno nuevo...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo       Entorno virtual creado correctamente en .\venv
) else (
    echo       Entorno virtual encontrado.
)
echo.

REM --- 3. Activar entorno e instalar dependencias ---
echo [3/4] Instalando dependencias desde requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Ocurrio un problema instalando las dependencias.
    pause
    exit /b 1
)
echo       Dependencias instaladas correctamente.
echo.

REM --- 4. Iniciar la aplicacion ---
echo [4/4] Iniciando Wiki URL Analyzer...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion se cerro debido a un error. Revisa logs\app.log
    pause
    exit /b 1
)

endlocal
