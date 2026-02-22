#!/usr/bin/env python
"""
Script to create a superuser for ADAMS Django application.
Run this script inside the Docker container.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from app.models import User

def create_superuser():
    # Get credentials from environment or use defaults
    username = os.getenv('SUPERUSER_USERNAME', 'admin')
    email = os.getenv('SUPERUSER_EMAIL', 'admin@adams.org.in')
    password = os.getenv('SUPERUSER_PASSWORD', 'admin123')
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists. Updating to superuser...")
        user = User.objects.get(username=username)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save()
        print(f"User '{username}' updated to superuser successfully!")
    else:
        # Create new superuser with required fields
        print(f"Creating superuser: {username}")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
            is_active=True,
            # Required fields for User model
            gender='Male',
            whatsapp_number='1234567890',
            mobile_number='1234567891',  # Different from whatsapp to avoid unique constraint
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
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("\nYou can now login with these credentials.")

if __name__ == '__main__':
    create_superuser()
