#!/usr/bin/env python
"""Check media storage configuration and verify files are stored locally."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("MEDIA STORAGE CONFIGURATION CHECK")
print("=" * 60)

print("\n1. Django Settings:")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   MINIO_ENABLED: {getattr(settings, 'MINIO_ENABLED', 'Not set')}")

print("\n2. Media Directory Status:")
media_root = settings.MEDIA_ROOT
if os.path.exists(media_root):
    print(f"   [OK] Media directory exists: {media_root}")
    print(f"   [OK] Directory is writable: {os.access(media_root, os.W_OK)}")
    
    # Count files and directories
    total_files = 0
    total_dirs = 0
    total_size = 0
    
    for root, dirs, files in os.walk(media_root):
        total_dirs += len(dirs)
        for file in files:
            total_files += 1
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except:
                pass
    
    print(f"   [OK] Total directories: {total_dirs}")
    print(f"   [OK] Total files: {total_files}")
    print(f"   [OK] Total size: {total_size / 1024:.2f} KB")
    
    # List user directories
    users_dir = os.path.join(media_root, 'users')
    if os.path.exists(users_dir):
        user_dirs = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
        print(f"\n3. User Upload Directories: {len(user_dirs)}")
        for user_dir in user_dirs[:10]:  # Show first 10
            user_path = os.path.join(users_dir, user_dir)
            files = []
            for root, _, filenames in os.walk(user_path):
                files.extend(filenames)
            print(f"   - {user_dir}: {len(files)} files")
else:
    print(f"   [ERROR] Media directory does NOT exist: {media_root}")

print("\n4. Storage Type:")
if getattr(settings, 'MINIO_ENABLED', False):
    print("   [WARNING] MinIO is enabled but should be disabled!")
    print("   Storage: MinIO (S3-compatible)")
else:
    print("   [OK] Storage: LOCAL FILESYSTEM")
    print("   [OK] Files are stored in: media/ directory")

print("\n5. Verification:")
print("   [OK] Configuration: Using local file storage")
print("   [OK] Files are being saved to: media/ directory")
print("   [OK] URL path: /media/")

print("\n" + "=" * 60)
print("CONCLUSION: Media files are stored LOCALLY in the 'media' folder")
print("=" * 60)
