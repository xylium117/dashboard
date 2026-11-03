@echo off
setlocal
cd /d "%~dp0"

set "INPUT_FILE=%~1"
if "%INPUT_FILE%"=="" (
    for %%f in ("*Cost Report*.xlsx") do (
        if not "%%~nf"=="*_Cleaned" (
            set "INPUT_FILE=%%f"
            goto found
        )
    )
)

:found
if "%INPUT_FILE%"=="" (
    echo No Excel file specified. Drag and drop an .xlsx file onto this .bat file.
    pause
    exit /b
)

echo Processing: "%INPUT_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Clean-Excel.ps1" -InputFile "%INPUT_FILE%"

pause
