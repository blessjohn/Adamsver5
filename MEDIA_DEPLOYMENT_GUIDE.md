# Media Folder Deployment Guide

## ✅ Yes, the media folder will work in deployment!

The local `media/` folder setup will work perfectly in production. Here's what you need to know:

## 📁 Current Configuration

- **MEDIA_ROOT**: `media/` (project root)
- **MEDIA_URL**: `/media/`
- **Storage**: Local filesystem (no MinIO required)

## 🚀 Deployment Steps

### 1. Ensure Media Folder Exists on Server

```bash
# On your production server
cd /var/www/adams/adams-django-main  # or your deployment path
mkdir -p media
chmod 755 media
```

### 2. Set Proper Permissions

```bash
# Make sure Django/Gunicorn user can write to media folder
sudo chown -R www-data:www-data media/  # For Ubuntu/Debian
# OR
sudo chown -R nginx:nginx media/  # If using nginx user
```

### 3. Update Nginx Configuration

Your `nginx.conf` already has media configuration, but update the path:

```nginx
# Media files (user uploads)
location /media/ {
    alias /var/www/adams/adams-django-main/media/;  # Update this path!
    expires 7d;
    add_header Cache-Control "public";
    
    # Security: prevent directory listing
    autoindex off;
    
    # Allow large file uploads
    client_max_body_size 100M;
}
```

**Important**: Update `/var/www/adams/adams-django-main/media/` to match your actual deployment path!

### 4. Verify Django Settings

In `adams/settings.py`, ensure:
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

### 5. Test Media Serving

After deployment:
```bash
# Test if media files are accessible
curl http://your-domain.com/media/users/test/photo/image.jpg
```

## ⚠️ Important Considerations

### 1. **Disk Space**
- Monitor disk usage regularly
- Media files grow over time
- Consider cleanup policies for old files

### 2. **Backups**
```bash
# Backup media folder regularly
tar -czf media-backup-$(date +%Y%m%d).tar.gz media/
```

### 3. **Permissions**
- Django/Gunicorn process must have write access
- Nginx must have read access
- Typical: `chmod 755 media/` and `chmod 644 media/**/*`

### 4. **File Size Limits**
- Nginx: `client_max_body_size 100M;` (already configured)
- Django: No default limit (good for large files)

### 5. **Security**
- Nginx serves files directly (faster than Django)
- Files are publicly accessible via `/media/` URL
- Consider adding authentication for sensitive files if needed

## 📋 Deployment Checklist

- [ ] Media folder created on server
- [ ] Proper permissions set (755 for directories, 644 for files)
- [ ] Nginx configuration updated with correct path
- [ ] Nginx configuration tested and reloaded
- [ ] Django MEDIA_ROOT points to correct path
- [ ] Test file upload works
- [ ] Test file access via URL works
- [ ] Backup strategy in place

## 🔄 Migration from MinIO (if needed)

If you have existing files in MinIO:
1. Download all files from MinIO
2. Upload to `media/` folder maintaining directory structure
3. Update database paths from MinIO paths to `media/` paths

## 💾 Backup Commands

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/media"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/media-$DATE.tar.gz /var/www/adams/adams-django-main/media/
# Keep only last 30 days
find $BACKUP_DIR -name "media-*.tar.gz" -mtime +30 -delete
```

## 🎯 Advantages of Local Media Storage

✅ **Simple**: No external service needed
✅ **Fast**: Direct file system access
✅ **Cost-effective**: No storage service fees
✅ **Easy backups**: Standard file system backups
✅ **Full control**: Complete ownership of files

## ⚠️ Limitations

⚠️ **Scalability**: Limited by server disk space
⚠️ **Redundancy**: Single point of failure (use backups!)
⚠️ **Performance**: May be slower than CDN for high traffic

## 🚨 For High-Traffic Sites

If you expect high traffic or need redundancy:
- Consider using cloud storage (AWS S3, Google Cloud Storage)
- Or use a CDN for media files
- Or set up multiple servers with shared storage (NFS)

## 📝 Quick Deployment Commands

```bash
# 1. Create media directory
mkdir -p /var/www/adams/adams-django-main/media
chmod 755 /var/www/adams/adams-django-main/media

# 2. Set ownership (adjust user/group as needed)
sudo chown -R www-data:www-data /var/www/adams/adams-django-main/media

# 3. Update nginx config
sudo nano /etc/nginx/sites-available/adams
# Update media path in nginx.conf

# 4. Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx

# 5. Verify Django can write
sudo -u www-data touch /var/www/adams/adams-django-main/media/test.txt
sudo -u www-data rm /var/www/adams/adams-django-main/media/test.txt
```

## ✅ Conclusion

**Yes, the media folder will work perfectly in deployment!** Just ensure:
1. Folder exists with proper permissions
2. Nginx is configured to serve `/media/`
3. Django has write access
4. Regular backups are set up

Your current setup is production-ready! 🎉
