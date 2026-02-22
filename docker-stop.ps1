# PowerShell script to stop Docker services
# Usage: .\docker-stop.ps1

Write-Host "Stopping Docker services..." -ForegroundColor Cyan
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Services stopped" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to stop services" -ForegroundColor Red
}
