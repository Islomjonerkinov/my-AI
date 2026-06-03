@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe simple_backend.py
) else (
    python simple_backend.py
)
pause
