@echo off

cd /d "%~dp0\..\.."

set VENV_DIR=.venv
set REQ_FILE=requirements.txt

:: Check if venv exists; if not, create it
if not exist "%VENV_DIR%" (
    echo Virtual environment not found. Creating...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b %ERRORLEVEL%
    )
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip

:: Install packages from requirements.txt if the file exists
if exist "%REQ_FILE%" (
    echo Installing/Verifying dependencies from %REQ_FILE%...
    python -m pip install -r "%REQ_FILE%"
) else (
    echo Warning: %REQ_FILE% not found. Skipping dependency installation.
)

echo.
echo Setup complete! Check above for any errors.