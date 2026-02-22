# How to Start MinIO for File Storage

## Quick Start

MinIO is required for file storage. Files will NOT be saved if MinIO is not running.

### Option 1: Using Docker (Recommended for Development)

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=fire_user" \
  -e "MINIO_ROOT_PASSWORD=fire_pasword" \
  minio/minio server /data --console-address ":9001"
```

Access MinIO Console: http://localhost:9001
- Username: `fire_user`
- Password: `fire_pasword`

### Option 2: Download and Run MinIO Binary

1. Download MinIO:
   - Windows: https://dl.min.io/server/minio/release/windows-amd64/minio.exe
   - Linux: https://dl.min.io/server/minio/release/linux-amd64/minio

2. Run MinIO:
```bash
# Windows
minio.exe server C:\minio-data --console-address ":9001"

# Linux
chmod +x minio
./minio server /opt/minio/data --console-address ":9001"
```

Set environment variables:
```bash
set MINIO_ROOT_USER=fire_user
set MINIO_ROOT_PASSWORD=fire_pasword
```

### Option 3: Using MinIO on Remote Server

If MinIO is running on a remote server, update `.env`:
```bash
MINIO_URL=your-server-ip:9000
# or
MINIO_URL=minio.yourdomain.com:9000
```

## Create Access Key

1. Access MinIO Console: http://localhost:9001 (or your server:9001)
2. Login with root credentials (fire_user / fire_pasword)
3. Go to **Access Keys** → **Create Access Key**
4. Save the Access Key and Secret Key
5. Update `.env` file:
```bash
MINIO_ACCESS_KEY=your_access_key_from_console
MINIO_SECRET_KEY=your_secret_key_from_console
```

## Verify MinIO is Running

```bash
# Test connection
python test_minio_connection.py

# Or check manually
curl http://localhost:9000/minio/health/live
```

## Current Configuration

Your `.env` file should have:
```bash
MINIO_URL=localhost:9000          # Use 'localhost' for local, 'minio' for Docker network, or server IP for remote
MINIO_ACCESS_KEY=fire_user
MINIO_SECRET_KEY=fire_pasword
MINIO_BUCKET_NAME=adams
```

## Important Notes

- **Files will NOT be saved if MinIO is not running**
- The application will show an error if MinIO is unavailable
- Make sure MinIO is running before registering users
- For production, MinIO must be running as a service
