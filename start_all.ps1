# ═══════════════════════════════════════════════════════════════
#   MedAI — Khởi chạy cả medpilot-core + medpilot-triage
# ═══════════════════════════════════════════════════════════════
#   medpilot-core:  http://localhost:8000 (RAG + LLM chính)
#   medpilot-triage:     http://localhost:8080 (Triage/Workflow PoC API)
#   Frontend:       http://localhost:3000 (Giao diện Web)
#   Docs:           http://localhost:8080/api/docs
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   MedAI — Starting All Services                  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ─── 1. Start medpilot-core (port 8000) ─────────────────────
Write-Host "[1/3] Starting medpilot-core on port 8000..." -ForegroundColor Yellow

$medpilotDir = Join-Path $BaseDir "medpilot-core"
$medpilotVenv = Join-Path $medpilotDir ".venv\Scripts\Activate.ps1"

$medpilotCmd = ""
if (Test-Path $medpilotVenv) {
    $medpilotCmd = "cd '$medpilotDir'; & '$medpilotVenv'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
} else {
    $medpilotCmd = "cd '$medpilotDir'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", $medpilotCmd -WindowStyle Normal

# Chờ medpilot-core khởi động
Start-Sleep -Seconds 3

# ─── 2. Start medpilot-triage (port 8080) ──────────────────
Write-Host "[2/3] Starting medpilot-triage on port 8080..." -ForegroundColor Yellow

$backendDir = Join-Path $BaseDir "medpilot-triage"
$backendVenv = Join-Path $backendDir ".venv\Scripts\Activate.ps1"

$backendCmd = ""
if (Test-Path $backendVenv) {
    $backendCmd = "cd '$backendDir'; & '$backendVenv'; python main.py"
} else {
    $backendCmd = "cd '$backendDir'; python main.py"
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Chờ medpilot-triage khởi động
Start-Sleep -Seconds 3

# ─── 3. Start Frontend (port 3000) ────────────────────────
Write-Host "[3/3] Starting Frontend on port 3000..." -ForegroundColor Yellow

$frontendDir = Join-Path $BaseDir "medpilot-frontend"
$frontendCmd = "cd '$frontendDir'; python -m http.server 3000"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

# Chờ Frontend khởi động
Start-Sleep -Seconds 2

# ─── 4. Info & Browser ──────────────────────────────────────
Write-Host ""
Write-Host "✅ Tất cả services đã khởi chạy!" -ForegroundColor Green
Write-Host ""
Write-Host "   medpilot-core (RAG):    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   medpilot-triage API Docs:    http://localhost:8080/api/docs" -ForegroundColor White
Write-Host "   Frontend (Web UI):      http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Đang mở trình duyệt..." -ForegroundColor Gray

Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Nhấn Enter để đóng cửa sổ này (các server vẫn chạy)..." -ForegroundColor DarkGray
Read-Host
