@echo off
chcp 65001 > nul
title Actualizar bases en la web

echo.
echo ========================================
echo   ACTUALIZANDO BASES EN LA WEB
echo ========================================
echo.

cd /d "%~dp0"

echo Archivos actuales en la carpeta bases/:
echo.
dir /b "bases\*.xlsx" "bases\*.xls" 2>nul
echo.

git add bases/
git add .gitignore

git diff --cached --name-only | findstr "bases" > nul
if errorlevel 1 (
    echo No hay cambios en la carpeta bases/.
    echo Fijate que el Excel este guardado dentro de:
    echo.
    echo   %~dp0bases\
    echo.
    pause
    exit /b
)

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set dt=%%a
set FECHA=%dt:~6,2%/%dt:~4,2%/%dt:~0,4% %dt:~8,2%:%dt:~10,2%

git commit -m "Actualiza bases/ - %FECHA%"

echo.
echo Subiendo a la web...
git push origin main

if errorlevel 1 (
    echo.
    echo ERROR al subir. Verificá tu conexion a internet.
    pause
    exit /b
)

echo.
echo ========================================
echo   LISTO! La web se actualiza en ~2 min
echo ========================================
echo.
pause
