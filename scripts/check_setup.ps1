# Verify Python and key dependencies are available
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}

if (-not $python) {
    Write-Host "ERROR: Python 3.11+ not found. Install from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "       Enable 'Add Python to PATH' during installation." -ForegroundColor Red
    exit 1
}

Write-Host "Python: $python" -ForegroundColor Green
& $python --version

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $python -m venv .venv
}

$pip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"
& $pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env not found. Copy .env.example to .env and add your API keys." -ForegroundColor Yellow
} else {
    Write-Host ".env found." -ForegroundColor Green
}

Write-Host "`nSetup check complete. Run: .\scripts\start_all.ps1" -ForegroundColor Cyan
