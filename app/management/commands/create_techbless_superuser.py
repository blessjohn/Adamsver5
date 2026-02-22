"""
Django management command to create techbless superuser.
This ensures the superuser exists after deployment.
"""
from django.core.management.base import BaseCommand
from app.models import User
import random
import time


class Command(BaseCommand):
    help = 'Creates or updates the techbless superuser account'

    def handle(self, *args, **options):
        username = 'techbless'
        email = 'techbless7@gmail.com'
        password = 'admin123'  # Change this in production via environment variable
        
        # Check if user already exists by email
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            self.stdout.write(f"User with email '{email}' already exists. Updating to superuser...")
            user.username = username
            user.role = 'admin'
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{username}' updated to superuser successfully!"))
            return
        
        # Check if user already exists by username
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(f"User '{username}' already exists. Updating to superuser...")
            user.email = email
            user.role = 'admin'
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{username}' updated to superuser successfully!"))
            return
        
        # Generate unique mobile numbers
        max_attempts = 100
        whatsapp_num = None
        mobile_num = None
        
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
            timestamp = int(time.time())
            whatsapp_num = f"9{timestamp % 1000000000:09d}"
            mobile_num = f"8{(timestamp + 1) % 1000000000:09d}"
        
        # Create new superuser
        self.stdout.write(f"Creating superuser: {username}")
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin',
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
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully!"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating user: {e}"))
            raise
