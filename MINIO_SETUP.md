# MinIO Setup Guide for Production Deployment

## Overview

The application is now configured to work with MinIO for production deployment. The code includes:
- ✅ Proper MinIO connection handling
- ✅ Automatic bucket creation
- ✅ Secure connection support (HTTPS)
- ✅ Production-ready error handling
- ✅ Fallback to local storage only in DEBUG mode

## Configuration

### Environment Variables

Set these environment variables in your production environment:

```bash
MINIO_URL=localhost:9000          # MinIO server URL (or IP:port)
MINIO_ACCESS_KEY=your_access_key   # MinIO access key
MINIO_SECRET_KEY=your_secret_key   # MinIO secret key
MINIO_BUCKET_NAME=adams            # Bucket name for storing files
MINIO_SECURE=false                 # Set to "true" for HTTPS connections
```

### For Secure Connections (HTTPS)

If your MinIO server uses HTTPS:

```bash
MINIO_URL=https://your-minio-server.com:9000
# OR
MINIO_URL=your-minio-server.com:9000
MINIO_SECURE=true
```

## Testing MinIO Connection

Before deploying, test your MinIO connection:

```bash
python test_minio_connection.py
```

This script will:
1. Check MinIO configuration
2. Test connection to MinIO server
3. Verify bucket exists (creates if needed)
4. Test file upload and retrieval
5. Clean up test files

## Deployment Checklist

### 1. Install and Start MinIO Server

On your production server:

```bash
# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# Create data directory
sudo mkdir -p /opt/minio/data
sudo chown -R $USER:$USER /opt/minio

# Start MinIO (or use systemd service)
minio server /opt/minio/data --console-address ":9001"
```

### 2. Create Systemd Service (Recommended)

Create `/etc/systemd/system/minio.service`:

```ini
[Unit]
Description=MinIO Object Storage
After=network.target

[Service]
Type=simple
User=your_user
Group=your_group
ExecStart=/usr/local/bin/minio server /opt/minio/data --console-address ":9001"
Restart=always
Environment="MINIO_ROOT_USER=your_root_user"
Environment="MINIO_ROOT_PASSWORD=your_root_password"

[Install]
WantedBy=multi-user.target
```

Start MinIO:
```bash
sudo systemctl daemon-reload
sudo systemctl enable minio
sudo systemctl start minio
sudo systemctl status minio
```

### 3. Create Access Key and Secret Key

1. Access MinIO Console: `http://your-server:9001`
2. Login with root credentials
3. Go to Access Keys → Create Access Key
4. Save the Access Key and Secret Key
5. Set these in your environment variables

### 4. Create Bucket

The application will automatically create the bucket if it doesn't exist, but you can also create it manually:

1. In MinIO Console, go to Buckets
2. Create bucket named `adams` (or your configured bucket name)
3. Set appropriate access policies

### 5. Set Environment Variables

In your Django application's environment (`.env` file or systemd service):

```bash
MINIO_URL=localhost:9000
MINIO_ACCESS_KEY=your_access_key_from_console
MINIO_SECRET_KEY=your_secret_key_from_console
MINIO_BUCKET_NAME=adams
```

### 6. Verify Configuration

Run the test script:
```bash
python test_minio_connection.py
```

You should see:
```
[SUCCESS] MinIO is properly configured and working!
```

## Production Behavior

### When MinIO is Available:
- ✅ All file uploads go to MinIO
- ✅ Files are stored in the configured bucket
- ✅ Automatic bucket creation if missing
- ✅ Proper error handling and logging

### When MinIO is NOT Available:
- ❌ **Production (DEBUG=False)**: Registration/uploads will fail with clear error messages
- ⚠️ **Development (DEBUG=True)**: Falls back to local storage in `media/` folder

## Troubleshooting

### Connection Refused
```
Error: Failed to establish connection
```
**Solution:**
- Verify MinIO server is running: `systemctl status minio`
- Check MinIO URL is correct
- Verify firewall allows connection to MinIO port (9000)

### Authentication Failed
```
Error: Access Denied
```
**Solution:**
- Verify MINIO_ACCESS_KEY and MINIO_SECRET_KEY are correct
- Check access key has proper permissions in MinIO console
- Ensure bucket access policy allows your access key

### Bucket Not Found
```
Error: Bucket does not exist
```
**Solution:**
- Application will auto-create bucket, but verify MINIO_BUCKET_NAME is correct
- Check access key has permission to create buckets
- Manually create bucket in MinIO console if needed

### File Upload Fails
```
Error: Failed to upload file
```
**Solution:**
- Check MinIO server logs: `journalctl -u minio -f`
- Verify disk space on MinIO server
- Check file size limits
- Verify network connectivity

## Security Best Practices

1. **Use Strong Credentials**: Use strong root user password and access keys
2. **Limit Access**: Only grant necessary permissions to access keys
3. **Use HTTPS**: Enable secure connections in production
4. **Firewall Rules**: Restrict MinIO access to application server only
5. **Regular Backups**: Backup MinIO data directory regularly

## Monitoring

Monitor MinIO health:
```bash
# Check MinIO status
systemctl status minio

# View MinIO logs
journalctl -u minio -f

# Test connection
curl http://localhost:9000/minio/health/live
```

## Support

For issues:
1. Check MinIO server logs
2. Run `python test_minio_connection.py`
3. Verify all environment variables are set
4. Check network connectivity
5. Review application logs for detailed error messages
