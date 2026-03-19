@echo off
REM ═══════════════════════════════════════════════════════════════
REM   MedAI — Khởi chạy cả medpilot-core + medpilot-triage
REM ═══════════════════════════════════════════════════════════════
REM   medpilot-core:  http://localhost:8000 (RAG + LLM chính)
REM   medpilot-triage:     http://localhost:8080 (Triage/Workflow PoC API)
REM   Frontend:       http://localhost:3000 (Giao diện Web)
REM   Docs:           http://localhost:8080/api/docs
REM ═══════════════════════════════════════════════════════════════

echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║   MedAI — Starting All Services                  ║
echo ╚═══════════════════════════════════════════════════╝
echo.

SET BASE_DIR=%~dp0

REM ─── 1. Start medpilot-core (port 8000) ─────────────────────
echo [1/3] Starting medpilot-core on port 8000...
cd /d "%BASE_DIR%medpilot-core"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

start "medpilot-core [Port 8000]" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Chờ medpilot-core khởi động
timeout /t 3 /nobreak > nul

REM ─── 2. Start medpilot-triage (port 8080) ──────────────────
echo [2/3] Starting medpilot-triage on port 8080...
cd /d "%BASE_DIR%medpilot-triage"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

start "medpilot-triage [Port 8080]" cmd /k "python main.py"

REM Chờ medpilot-triage khởi động
timeout /t 3 /nobreak > nul

REM ─── 3. Start Frontend (port 3000) ────────────────────────
echo [3/3] Starting Frontend on port 3000...
cd /d "%BASE_DIR%medpilot-frontend"
start "Frontend [Port 3000]" cmd /k "python -m http.server 3000"

REM Chờ Frontend khởi động
timeout /t 2 /nobreak > nul

REM ─── 4. Mở browser ──────────────────────────────────────────
echo.
echo ✅ Tất cả services đã khởi chạy!
echo.
echo    medpilot-core (RAG):    http://localhost:8000/docs
echo    medpilot-triage API Docs:    http://localhost:8080/api/docs
echo    Frontend (Web UI):      http://localhost:3000
echo.
echo Đang mở trình duyệt...
start http://localhost:3000

echo.
echo Nhấn phím bất kỳ để đóng cửa sổ này (các server vẫn chạy)...
pause > nul
