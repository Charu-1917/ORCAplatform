@echo off
REM Starts ORCA (backend + frontend) on port 8000 for this PC, other PCs and phones.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
set PYTHONDONTWRITEBYTECODE=1
".venv\Scripts\python.exe" run.py
pause
