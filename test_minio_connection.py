"""
Test MinIO connection and configuration
Run this script to verify MinIO is properly configured and accessible
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from django.conf import settings
from app.utils import get_minio_client, upload_image_to_minio
from io import BytesIO

def test_minio_connection():
    """Test MinIO connection and configuration"""
    print("=" * 60)
    print("MinIO Connection Test")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Checking MinIO Configuration:")
    print(f"   MINIO_URL: {settings.MINIO_URL}")
    print(f"   MINIO_BUCKET_NAME: {settings.MINIO_BUCKET_NAME}")
    print(f"   MINIO_ACCESS_KEY: {'*' * len(settings.MINIO_ACCESS_KEY) if settings.MINIO_ACCESS_KEY else 'NOT SET'}")
    print(f"   MINIO_SECRET_KEY: {'*' * len(settings.MINIO_SECRET_KEY) if settings.MINIO_SECRET_KEY else 'NOT SET'}")
    print(f"   MINIO_ENABLED: {settings.MINIO_ENABLED}")
    print(f"   DEBUG: {settings.DEBUG}")
    
    if not settings.MINIO_ENABLED:
        print("\n[ERROR] MinIO is not fully configured!")
        print("Please set the following environment variables:")
        print("  - MINIO_URL")
        print("  - MINIO_ACCESS_KEY")
        print("  - MINIO_SECRET_KEY")
        print("  - MINIO_BUCKET_NAME")
        return False
    
    # Test connection
    print("\n2. Testing MinIO Connection:")
    try:
        client = get_minio_client()
        if client is None:
            print("   [ERROR] Could not create MinIO client")
            return False
        
        # List buckets to test connection
        buckets = client.list_buckets()
        print(f"   [OK] Connection successful!")
        print(f"   Found {len(buckets)} bucket(s)")
        
        # Check if our bucket exists
        bucket_exists = client.bucket_exists(settings.MINIO_BUCKET_NAME)
        if bucket_exists:
            print(f"   [OK] Bucket '{settings.MINIO_BUCKET_NAME}' exists")
        else:
            print(f"   [WARNING] Bucket '{settings.MINIO_BUCKET_NAME}' does not exist")
            print(f"   Attempting to create bucket...")
            try:
                client.make_bucket(settings.MINIO_BUCKET_NAME)
                print(f"   [OK] Bucket '{settings.MINIO_BUCKET_NAME}' created successfully")
            except Exception as e:
                print(f"   [ERROR] Could not create bucket: {e}")
                return False
        
        # Test file upload
        print("\n3. Testing File Upload:")
        test_content = b"This is a test file for MinIO connection"
        test_file = BytesIO(test_content)
        test_file.name = "test_connection.txt"
        test_file.size = len(test_content)
        test_file.content_type = "text/plain"
        
        test_path = "test/test_connection.txt"
        success = upload_image_to_minio(test_file, test_path)
        
        if success:
            print(f"   [OK] Test file uploaded successfully to '{test_path}'")
            
            # Try to retrieve it
            try:
                response = client.get_object(settings.MINIO_BUCKET_NAME, test_path)
                data = response.read()
                if data == test_content:
                    print(f"   [OK] Test file retrieved and verified")
                else:
                    print(f"   [WARNING] Test file retrieved but content mismatch")
                
                # Clean up test file
                client.remove_object(settings.MINIO_BUCKET_NAME, test_path)
                print(f"   [OK] Test file cleaned up")
            except Exception as e:
                print(f"   [WARNING] Could not retrieve test file: {e}")
        else:
            print(f"   [ERROR] Test file upload failed")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] MinIO is properly configured and working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] MinIO connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify MinIO server is running: systemctl status minio")
        print("2. Check MinIO URL is correct")
        print("3. Verify access key and secret key are correct")
        print("4. Check network connectivity to MinIO server")
        return False

if __name__ == '__main__':
    try:
        success = test_minio_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
