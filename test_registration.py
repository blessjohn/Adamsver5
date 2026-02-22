"""
Test script for registration form submission
Run this script to test the registration form with sample data
"""
import os
import sys
import django
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_image(filename='test.jpg'):
    """Create a simple test image file"""
    # Create a simple 1x1 pixel image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(filename, img_io.read(), content_type='image/jpeg')

def test_registration_form():
    """Test the registration form submission"""
    client = Client()
    
    # First, get the registration page to get CSRF token
    print("Step 1: Getting registration page...")
    response = client.get('/register/')
    
    if response.status_code != 200:
        print(f"Error: Could not access registration page. Status: {response.status_code}")
        return
    
    print("[OK] Registration page loaded successfully")
    
    # Extract CSRF token from the response
    csrf_token = None
    if 'csrftoken' in response.cookies:
        csrf_token = response.cookies['csrftoken'].value
    else:
        # Try to extract from HTML
        import re
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.content.decode())
        if match:
            csrf_token = match.group(1)
    
    if not csrf_token:
        print("Warning: Could not extract CSRF token. Continuing anyway...")
    
    # Prepare test data
    print("\nStep 2: Preparing test data...")
    
    # Generate unique username and email to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_username = f"testuser_{timestamp}"
    test_email = f"test_{timestamp}@example.com"
    test_whatsapp = f"+9198765432{timestamp[-4:]}"
    test_mobile = f"+9198765433{timestamp[-4:]}"
    
    # Create test image files
    photo_file = create_test_image('photo.jpg')
    passport_file = create_test_image('passport.jpg')
    medical_qual_file = create_test_image('medical.jpg')
    payment_proof_file = create_test_image('payment.jpg')
    
    # Prepare form data
    form_data = {
        'username': test_username,
        'first_name': 'Test',
        'middle_name': 'Middle',
        'last_name': 'User',
        'gender': 'Male',
        'email': test_email,
        'whatsapp_number': test_whatsapp,
        'mobile_number': test_mobile,
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'district': 'Thiruvananthapuram',
        'address_communication': '123 Test Street, Test City, Test State - 123456',
        'address_permanent': '123 Test Street, Test City, Test State - 123456',
        'father_spouse_details': 'Father Name: Test Father, Occupation: Engineer',
        'blood_group': 'O+',
        'educational_status': 'Student (@Abroad University)',
        'category': 'Student',
        'university_name': 'Test Medical University',
        'country_university': 'India',
        'year_of_joining': '2020-01-15',
        'year_of_completion': '2025-06-30',
        'date_time_of_payment': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'willing_to_be_donor': 'false',
        'agreement': 'true',
        'mid': '',
        'application': 'true',
    }
    
    # Add CSRF token if available
    if csrf_token:
        form_data['csrfmiddlewaretoken'] = csrf_token
    
    # Prepare file data
    file_data = {
        'photo': photo_file,
        'passport': passport_file,
        'medical_qualification': medical_qual_file,
        'payment_transaction_proof': payment_proof_file,
        # 'state_nmc' is optional, so we'll skip it
    }
    
    print("[OK] Test data prepared")
    print(f"  Username: {test_username}")
    print(f"  Email: {test_email}")
    
    # Submit the form
    print("\nStep 3: Submitting registration form...")
    response = client.post('/register/', data=form_data, files=file_data, follow=True)
    
    # Check response
    print(f"\nResponse Status Code: {response.status_code}")
    
    if response.status_code == 200:
        # Check if registration was successful (should redirect to login)
        if response.redirect_chain:
            print(f"[OK] Redirect detected: {response.redirect_chain[-1][0]}")
            if 'login' in response.redirect_chain[-1][0]:
                print("[OK] Registration successful! Redirected to login page.")
            else:
                print("⚠ Unexpected redirect location")
        else:
            # Check for form errors
            if 'form' in response.context:
                form = response.context['form']
                if form.errors:
                    print("\n[ERROR] Registration failed with errors:")
                    for field, errors in form.errors.items():
                        print(f"  {field}: {', '.join(errors)}")
                else:
                    print("[OK] Form appears valid, but no redirect occurred")
            else:
                # Check for success messages
                messages = list(response.context.get('messages', []))
                if messages:
                    for message in messages:
                        print(f"Message: {message}")
                else:
                    print("⚠ No form context or messages found")
                    # Print response content for debugging
                    content = response.content.decode('utf-8')
                    if 'error' in content.lower() or 'invalid' in content.lower():
                        print("  Response contains error messages")
    else:
        print(f"[ERROR] Registration failed with status code: {response.status_code}")
        print("Response content (first 500 chars):")
        print(response.content.decode('utf-8')[:500])
    
    # Check if user was created
    print("\nStep 4: Verifying user creation...")
    from app.models import User
    try:
        user = User.objects.get(username=test_username)
        print(f"[OK] User created successfully!")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.first_name} {user.last_name}")
        
        # Clean up - delete test user
        print("\nStep 5: Cleaning up test user...")
        user.delete()
        print("[OK] Test user deleted")
        
    except User.DoesNotExist:
        print("[ERROR] User was not created in database")
    
    print("\n" + "="*50)
    print("Registration form test completed!")
    print("="*50)

if __name__ == '__main__':
    try:
        test_registration_form()
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
