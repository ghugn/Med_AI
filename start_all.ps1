# ═══════════════════════════════════════════════════════════════
#   MedAI — Khởi chạy medpilot-core + Frontend MOCK
# ═══════════════════════════════════════════════════════════════
#   medpilot-core:  http://localhost:8000 (Scribe, Reminder, Chat)
#   Frontend:       http://localhost:3000 (Giao diện Web)
# ═══════════════════════════════════════════════════════════════

Write-Host ""
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   MedAI — Starting All Services                  ║" -ForegroundColor Cyan
Write-Host "║   1. medpilot-core (Port 8000 - Backend)        ║" -ForegroundColor Cyan
Write-Host "║   2. medpilot-frontend (Port 3000 - Production) ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ─── 1. Start medpilot-core (port 8000) ─────────────────────
Write-Host "[1/2] Starting medpilot-core on port 8000..." -ForegroundColor Yellow

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

# ─── 2. Start Frontend (port 3000) ────────────────────────
Write-Host "[2/2] Building and Starting Frontend on port 3000 (Production Mode)..." -ForegroundColor Yellow

$frontendDir = Join-Path $BaseDir "medpilot-frontend"
$frontendCmd = "cd '$frontendDir'; npm run build; npm run start"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

# Chờ Frontend khởi động
Start-Sleep -Seconds 5

# ─── 4. Info & Browser ──────────────────────────────────────
Write-Host ""
Write-Host "✅ Tất cả services đã khởi chạy!" -ForegroundColor Green
Write-Host ""
Write-Host "   medpilot-core:          http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend (Web UI):      http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Đang mở trình duyệt..." -ForegroundColor Gray

Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Nhấn Enter để đóng cửa sổ này (các server vẫn chạy)..." -ForegroundColor DarkGray
Read-Host
