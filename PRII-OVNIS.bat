@echo off
rem Double-click launcher (Windows). First run installs dependencies (needs
rem internet once); later runs start the app directly and work offline.
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel% neq 0 (
    echo Python 3 is required. Install it from https://www.python.org/downloads/
    pause
    exit /b 1
  )
  set "PYTHON=python"
)

%PYTHON% desktop\setup.py --ensure
if %errorlevel% neq 0 pause & exit /b 1
".venv\Scripts\python.exe" desktop\launch.py %*
if %errorlevel% neq 0 pause
