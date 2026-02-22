# PowerShell script to start Docker services
# Usage: .\docker-start.ps1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ADAMS Docker Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Creating .env from docker-compose.env.example..." -ForegroundColor Yellow
    Copy-Item docker-compose.env.example .env
    Write-Host "Please edit .env file and set your configuration values!" -ForegroundColor Red
    Write-Host "Press any key to continue after editing .env..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Cyan
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build and start services
Write-Host ""
Write-Host "Building and starting Docker services..." -ForegroundColor Cyan
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Services started successfully!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "MinIO Console: http://localhost:9001" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "View logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "Stop services: docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[ERROR] Failed to start services. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}
