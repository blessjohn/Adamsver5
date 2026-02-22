# PowerShell script to start MinIO using Docker
# Make sure Docker is installed and running

Write-Host "Starting MinIO server..." -ForegroundColor Green

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if MinIO container already exists
$containerExists = docker ps -a --filter "name=minio" --format "{{.Names}}"
if ($containerExists -eq "minio") {
    Write-Host "MinIO container exists. Starting it..." -ForegroundColor Yellow
    docker start minio
} else {
    Write-Host "Creating new MinIO container..." -ForegroundColor Yellow
    docker run -d `
        -p 9000:9000 `
        -p 9001:9001 `
        --name minio `
        -e "MINIO_ROOT_USER=fire_user" `
        -e "MINIO_ROOT_PASSWORD=fire_pasword" `
        minio/minio server /data --console-address ":9001"
}

Start-Sleep -Seconds 3

# Check if MinIO is running
$running = docker ps --filter "name=minio" --format "{{.Names}}"
if ($running -eq "minio") {
    Write-Host "[SUCCESS] MinIO is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "MinIO Server: http://localhost:9000" -ForegroundColor Cyan
    Write-Host "MinIO Console: http://localhost:9001" -ForegroundColor Cyan
    Write-Host "Login: fire_user / fire_pasword" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Open MinIO Console: http://localhost:9001"
    Write-Host "2. Login with fire_user / fire_pasword"
    Write-Host "3. Go to Access Keys and create a new access key"
    Write-Host "4. Update .env file with the access key and secret key"
    Write-Host "5. Test connection: python test_minio_connection.py"
} else {
    Write-Host "[ERROR] Failed to start MinIO. Check Docker logs: docker logs minio" -ForegroundColor Red
}
