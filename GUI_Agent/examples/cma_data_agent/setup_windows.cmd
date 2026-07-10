@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo [cma_data_agent] Setting up Python virtual environment...
echo.

set "PY_CMD="
where py >nul 2>nul
if %ERRORLEVEL%==0 set "PY_CMD=py -3"
if not defined PY_CMD (
    where python >nul 2>nul
    if %ERRORLEVEL%==0 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo [ERROR] Python was not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)

%PY_CMD% -m venv .venv
if not %ERRORLEVEL%==0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium

echo.
echo [cma_data_agent] Setup complete.
echo.
echo Next steps:
echo   1. call .venv\Scripts\activate.bat
echo   2. python login_save_session.py
echo   3. python explore_page.py
echo.
pause
