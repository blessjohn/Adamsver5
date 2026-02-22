#!/usr/bin/env python
"""
Script to check whether the application is using MinIO or local storage.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from django.conf import settings
from app.models import User
from app.utils import get_minio_client

def check_storage():
    print("=" * 60)
    print("Storage Configuration Check")
    print("=" * 60)
    
    # Check environment variables
    print("\n[1] Environment Configuration:")
    print(f"  MINIO_URL: {os.getenv('MINIO_URL', 'Not set')}")
    print(f"  MINIO_ACCESS_KEY: {'Set' if os.getenv('MINIO_ACCESS_KEY') else 'Not set'}")
    print(f"  MINIO_SECRET_KEY: {'Set' if os.getenv('MINIO_SECRET_KEY') else 'Not set'}")
    print(f"  MINIO_BUCKET_NAME: {os.getenv('MINIO_BUCKET_NAME', 'Not set')}")
    
    # Check Django settings
    print("\n[2] Django Settings:")
    print(f"  MINIO_ENABLED: {settings.MINIO_ENABLED}")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Check MinIO connection
    print("\n[3] MinIO Connection Test:")
    try:
        client = get_minio_client()
        if client:
            print("  ✓ MinIO client created successfully")
            try:
                buckets = client.list_buckets()
                print(f"  ✓ Connected to MinIO server")
                print(f"  ✓ Available buckets: {[b.name for b in buckets]}")
                
                bucket_name = settings.MINIO_BUCKET_NAME
                if client.bucket_exists(bucket_name):
                    print(f"  ✓ Bucket '{bucket_name}' exists")
                    
                    # List some objects in the bucket
                    objects = list(client.list_objects(bucket_name, recursive=False))
                    print(f"  ✓ Objects in bucket: {len(objects)} files")
                    if objects:
                        print(f"    Sample files: {[obj.object_name for obj in objects[:3]]}")
                else:
                    print(f"  ✗ Bucket '{bucket_name}' does not exist")
            except Exception as e:
                print(f"  ✗ MinIO connection failed: {e}")
                client = None
        else:
            print("  ✗ MinIO client is None (not connected)")
    except Exception as e:
        print(f"  ✗ Error getting MinIO client: {e}")
        client = None
    
    # Check user files
    print("\n[4] User File Storage Analysis:")
    users_with_files = User.objects.exclude(photo='').exclude(photo__isnull=True)[:10]
    minio_files = 0
    local_files = 0
    
    for user in users_with_files:
        if user.photo:
            if user.photo.startswith('media/'):
                local_files += 1
            else:
                minio_files += 1
    
    print(f"  Total users with files checked: {len(users_with_files)}")
    print(f"  Files in MinIO: {minio_files}")
    print(f"  Files in local storage: {local_files}")
    
    if users_with_files:
        print("\n  Sample file paths:")
        for user in users_with_files[:3]:
            print(f"    {user.username}: {user.photo[:60] if user.photo else 'None'}")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("Storage Status:")
    print("=" * 60)
    
    if settings.MINIO_ENABLED and client:
        print("  ✓ USING MINIO for file storage")
        print("  ✓ MinIO is configured and connected")
        if minio_files > 0 or local_files == 0:
            print("  ✓ Files are being stored in MinIO")
        else:
            print("  ⚠ Some files may still be in local storage")
    elif settings.MINIO_ENABLED and not client:
        print("  ⚠ MINIO ENABLED but NOT CONNECTED")
        print("  ⚠ Files may fail to upload")
    else:
        print("  ✗ USING LOCAL STORAGE (MinIO not enabled)")
        print("  ⚠ This is not recommended for production")
    
    print("=" * 60)

if __name__ == '__main__':
    check_storage()
