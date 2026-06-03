@echo off
echo ===========================================
echo   AI Assistant - Starting Services...
echo ===========================================

:: Start Backend in a new window
echo Starting FastAPI Backend...
if exist ".venv\Scripts\python.exe" (
    start "FastAPI Backend" cmd /c ".venv\Scripts\python.exe simple_backend.py"
) else (
    start "FastAPI Backend" cmd /c "python simple_backend.py"
)

:: Wait a bit for backend to initialize
timeout /t 3 > nul

:: Start Frontend in a new window
echo Starting React Frontend...
cd frontend
start "React Frontend" cmd /c "npm run dev"
cd ..

echo.
echo ===========================================
echo   Services are running in separate windows.
echo   - Backend: http://127.0.0.1:8000
echo   - Frontend: http://localhost:5173
echo ===========================================
echo You can close this window.
pause
