@echo off
setlocal
echo ==========================================
echo  State-Based Intent Drift Detector Launcher
echo ==========================================

REM Check for Python
where python >nul 2>nul
if %errorlevel%==0 (
    set PY_CMD=python
    goto :check_pip
)

where py >nul 2>nul
if %errorlevel%==0 (
    set PY_CMD=py
    goto :check_pip
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    set PY_CMD=python3
    goto :check_pip
)

echo [ERROR] Python not found via 'python', 'py', or 'python3'.
echo Please install Python from https://python.org and add it to PATH.
pause
exit /b 1

:check_pip
echo [INFO] Using Python command: %PY_CMD%

REM Install requirements
echo [INFO] Installing dependencies from requirements.txt...
%PY_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Run Streamlit
echo [INFO] Starting Streamlit Application...
%PY_CMD% -m streamlit run main.py

pause
