@echo off
REM ===============================================================
REM   MedAI - Khởi chạy medpilot-core + Frontend MOCK
REM ===============================================================
REM   medpilot-core:  http://localhost:8000 (Scribe, Reminder, Chat)
REM   Frontend:       http://localhost:3000 (Giao diện Web)
REM ===============================================================

echo.
echo ===================================================
echo    MedAI - Starting All Services
echo    1. medpilot-core (Port 8000 - Backend)
echo    2. medpilot-frontend (Port 3000 - Production)
echo ===================================================
echo.

SET BASE_DIR=%~dp0

REM --- 1. Start medpilot-core (port 8000) ---
echo [1/2] Starting medpilot-core on port 8000...
cd /d "%BASE_DIR%medpilot-core"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

start "medpilot-core [Port 8000]" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Cho medpilot-core khoi dong
timeout /t 3 /nobreak > nul

REM --- 2. Start Frontend (port 3000) in Production Mode ---
echo [2/2] Building and Starting Frontend on port 3000 (Production Mode)...
cd /d "%BASE_DIR%medpilot-frontend"
start "Frontend (Production) [Port 3000]" cmd /k "npm run build && npm run start"

REM Cho Frontend khoi dong
timeout /t 5 /nobreak > nul

REM --- 4. Mo browser ---
echo.
echo [OK] Tat ca services da khoi chay!
echo.
echo    medpilot-core:    http://localhost:8000/docs
echo    Frontend Web UI:  http://localhost:3000
echo.
echo Dang mo trinh duyet...
start http://localhost:3000

echo.
echo Nhan phim bat ky de dong cua so nay (cac server van chay)...
pause > nul
