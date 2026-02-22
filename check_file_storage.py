"""
Check file storage locations for users
Shows whether files are stored in MinIO or locally
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from app.models import User
from django.conf import settings

def check_file_storage():
    """Check where user files are stored"""
    print("=" * 70)
    print("File Storage Location Check")
    print("=" * 70)
    
    users = User.objects.all().order_by('-date_joined')[:5]
    
    print(f"\nChecking {len(users)} most recent users:\n")
    
    for user in users:
        print(f"User: {user.username} (ID: {user.id})")
        print(f"  Status: {user.status}")
        
        # Check each file field
        file_fields = {
            'photo': user.photo,
            'state_nmc': user.state_nmc,
            'passport': user.passport,
            'medical_qualification': user.medical_qualification,
            'payment_transaction_proof': user.payment_transaction_proof,
        }
        
        for field_name, file_path in file_fields.items():
            if not file_path or file_path == "" or file_path == "None":
                print(f"    {field_name}: Not provided (optional field)")
            elif file_path.startswith("media/"):
                # Local file
                full_path = os.path.join(str(settings.BASE_DIR), file_path)
                exists = os.path.exists(full_path)
                status = "[OK] EXISTS" if exists else "[MISSING]"
                print(f"    {field_name}: LOCAL ({file_path}) {status}")
            else:
                # MinIO file
                print(f"    {field_name}: MINIO ({file_path})")
        
        print()
    
    print("=" * 70)
    print("\nStorage Summary:")
    print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"  MINIO_ENABLED: {settings.MINIO_ENABLED}")
    print(f"  MINIO_URL: {settings.MINIO_URL}")
    print(f"  MINIO_BUCKET_NAME: {settings.MINIO_BUCKET_NAME}")
    print("=" * 70)

if __name__ == '__main__':
    check_file_storage()
