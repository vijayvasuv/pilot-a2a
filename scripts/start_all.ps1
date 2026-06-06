# Start all A2A pilot services (run from project root)
# Usage: .\scripts\start_all.ps1

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Virtual env not found. Run: .\scripts\check_setup.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "A2A Support Pilot — starting services..." -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"

# Index KB if not already done
Write-Host "`n[1/5] Indexing knowledge base..." -ForegroundColor Yellow
& $python scripts/ingest_kb.py

# Start specialist agents (A2A servers)
Write-Host "`n[2/5] Starting login specialist (port 8001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; .\.venv\Scripts\uvicorn agents.login_specialist.agent:a2a_app --host 127.0.0.1 --port 8001"

Start-Sleep -Seconds 2

Write-Host "[3/5] Starting billing specialist (port 8002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; .\.venv\Scripts\uvicorn agents.billing_specialist.agent:a2a_app --host 127.0.0.1 --port 8002"

Start-Sleep -Seconds 2

Write-Host "[4/5] Starting ticket specialist (port 8003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; .\.venv\Scripts\uvicorn agents.ticket_specialist.agent:a2a_app --host 127.0.0.1 --port 8003"

Start-Sleep -Seconds 3

Write-Host "[5/5] Starting chat API (port 8080)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; .\.venv\Scripts\uvicorn chat_api.main:app --host 127.0.0.1 --port 8080"

Write-Host "`nAll services launched in separate windows." -ForegroundColor Green
Write-Host "Open chat UI: http://127.0.0.1:8080" -ForegroundColor Green
Write-Host "Agent cards:" -ForegroundColor Green
Write-Host "  Login:   http://127.0.0.1:8001/.well-known/agent-card.json"
Write-Host "  Billing: http://127.0.0.1:8002/.well-known/agent-card.json"
Write-Host "  Ticket:  http://127.0.0.1:8003/.well-known/agent-card.json"
