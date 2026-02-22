#!/usr/bin/env python
"""
Script to create a superuser with custom credentials.
Usage: python create_custom_superuser.py <username> <email> <password>
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from app.models import User

def create_custom_superuser(username, email, password):
    """Create a superuser with custom credentials."""
    import random
    
    # Check if user already exists by email
    if User.objects.filter(email=email).exists():
        print(f"Email '{email}' already exists. Updating user to superuser...")
        user = User.objects.get(email=email)
        user.username = username
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save()
        print(f"User updated to superuser successfully!")
        return user
    # Check if user already exists by username
    elif User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists. Updating to superuser...")
        user = User.objects.get(username=username)
        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save()
        print(f"User '{username}' updated to superuser successfully!")
        return user
    else:
        # Generate unique mobile numbers
        max_attempts = 100
        for attempt in range(max_attempts):
            # Generate random unique numbers
            whatsapp_num = f"9{random.randint(100000000, 999999999)}"
            mobile_num = f"8{random.randint(100000000, 999999999)}"
            
            # Check if numbers are already in use
            if not User.objects.filter(whatsapp_number=whatsapp_num).exists() and \
               not User.objects.filter(mobile_number=mobile_num).exists():
                break
        else:
            # Fallback: use timestamp-based numbers
            import time
            timestamp = int(time.time())
            whatsapp_num = f"9{timestamp % 1000000000:09d}"
            mobile_num = f"8{(timestamp + 1) % 1000000000:09d}"
        
        # Create new superuser with required fields
        print(f"Creating superuser: {username}")
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_superuser=True,
                is_staff=True,
                is_active=True,
                # Required fields for User model
                gender='Male',
                whatsapp_number=whatsapp_num,
                mobile_number=mobile_num,
                address_communication='Admin Address',
                address_permanent='Admin Address',
                district='Thiruvananthapuram',
                father_spouse_details='Admin',
                blood_group='O+',
                university_name='Admin University',
                country_university='India',
                year_of_joining='2020',
                year_of_completion='2024',
                photo='',
                passport='',
                medical_qualification=''
            )
            print(f"Superuser '{username}' created successfully!")
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            # Try to get or create with different approach
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                    'gender': 'Male',
                    'whatsapp_number': whatsapp_num,
                    'mobile_number': mobile_num,
                    'address_communication': 'Admin Address',
                    'address_permanent': 'Admin Address',
                    'district': 'Thiruvananthapuram',
                    'father_spouse_details': 'Admin',
                    'blood_group': 'O+',
                    'university_name': 'Admin University',
                    'country_university': 'India',
                    'year_of_joining': '2020',
                    'year_of_completion': '2024',
                    'photo': '',
                    'passport': '',
                    'medical_qualification': ''
                }
            )
            if not created:
                user.username = username
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.set_password(password)
                user.save()
            else:
                user.set_password(password)
                user.save()
            print(f"Superuser '{username}' created/updated successfully!")
            return user

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python create_custom_superuser.py <username> <email> <password>")
        print("\nExample:")
        print("  python create_custom_superuser.py myadmin admin@example.com mypassword123")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_custom_superuser(username, email, password)
    print(f"\nYou can now login with:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
