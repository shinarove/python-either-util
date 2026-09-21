@echo off

cd /d "%~dp0\..\.."

set VENV_DIR=.venv

if not exist "%VENV_DIR%" (
    echo Virtual environment missing. Running setup...
    call scripts\windows\setup_venv.bat
)

call "%VENV_DIR%\Scripts\activate.bat"

:run_test
:: Clear the screen
cls
pytest

if %ERRORLEVEL% neq 0 (
    choice /C yn /M "Would you like to run the test again?"
    if errorlevel 1 goto :run_test
)