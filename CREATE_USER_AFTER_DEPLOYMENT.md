# Create User After Deployment via SSH

## 🔐 Steps to Create Admin/User Account via SSH

### Step 1: Connect to Your Server via SSH

```bash
# Connect to your server
ssh admin@ip-172-26-10-8
# Or if using key file:
ssh -i /path/to/key.pem admin@ip-172-26-10-8
```

### Step 2: Navigate to Project Directory

```bash
# Find your project directory (common locations)
cd /home/admin/adams-django-main
# OR
cd /var/www/adams/adams-django-main
# OR wherever you deployed the project

# Verify you're in the right place
ls -la
# You should see: manage.py, requirements.txt, etc.
```

### Step 3: Activate Virtual Environment

```bash
# Activate the virtual environment
source venv/bin/activate

# Verify Python and Django
python --version
python manage.py --version
```

### Step 4: Create User - Choose One Method

---

## Method 1: Create Default Admin User (Recommended)

This creates the `techbless` admin user automatically:

```bash
python manage.py create_techbless_superuser
```

**Result:**
- Username: `techbless`
- Email: `techbless7@gmail.com`
- Password: `admin123`
- Role: Admin (full access)

---

## Method 2: Create Custom Superuser (Django Default)

Interactive command - prompts for username, email, password:

```bash
python manage.py createsuperuser
```

**Follow the prompts:**
```
Username: your_username
Email address: your_email@example.com
Password: ********
Password (again): ********
```

---

## Method 3: Create Custom User via Script

```bash
# Using the custom script
python create_superuser.py
```

**Or with custom credentials:**
```bash
python create_custom_superuser.py username email password
```

**Example:**
```bash
python create_custom_superuser.py myadmin admin@adams.org.in MySecurePass123!
```

---

## Method 4: Create User via Django Shell

```bash
# Open Django shell
python manage.py shell
```

Then run:
```python
from app.models import User
import random
import time

# Generate unique mobile numbers
timestamp = int(time.time())
whatsapp_num = f"9{timestamp % 1000000000:09d}"
mobile_num = f"8{(timestamp + 1) % 1000000000:09d}"

# Create user
user = User.objects.create_user(
    username='your_username',
    email='your_email@example.com',
    password='your_password',
    role='admin',  # Options: 'admin', 'student', 'intern', 'doctor'
    is_superuser=True,
    is_staff=True,
    is_active=True,
    # Required fields
    gender='Male',
    whatsapp_number=whatsapp_num,
    mobile_number=mobile_num,
    address_communication='Your Address',
    address_permanent='Your Address',
    district='Thiruvananthapuram',
    father_spouse_details='N/A',
    blood_group='O+',
    university_name='Your University',
    country_university='India',
    year_of_joining='2020',
    year_of_completion='2024',
    photo='',
    passport='',
    medical_qualification=''
)

print(f"User '{user.username}' created successfully!")
exit()
```

---

## Method 5: Create Regular User (Non-Admin)

```bash
python manage.py shell
```

```python
from app.models import User
import random
import time

timestamp = int(time.time())
whatsapp_num = f"9{timestamp % 1000000000:09d}"
mobile_num = f"8{(timestamp + 1) % 1000000000:09d}"

user = User.objects.create_user(
    username='student123',
    email='student@example.com',
    password='student_password',
    role='student',  # Regular user, not admin
    is_superuser=False,
    is_staff=False,
    is_active=True,
    gender='Male',
    whatsapp_number=whatsapp_num,
    mobile_number=mobile_num,
    address_communication='Address',
    address_permanent='Address',
    district='Thiruvananthapuram',
    father_spouse_details='N/A',
    blood_group='O+',
    university_name='University',
    country_university='India',
    year_of_joining='2020',
    year_of_completion='2024',
    photo='',
    passport='',
    medical_qualification=''
)

print(f"User '{user.username}' created successfully!")
exit()
```

---

## ✅ Verify User Creation

```bash
python manage.py shell
```

```python
from app.models import User

# List all users
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}, Role: {user.role}, Is Admin: {user.is_superuser}")

# Check specific user
user = User.objects.get(username='techbless')
print(f"\nUser Details:")
print(f"  Username: {user.username}")
print(f"  Email: {user.email}")
print(f"  Is Superuser: {user.is_superuser}")
print(f"  Is Staff: {user.is_staff}")
print(f"  Is Active: {user.is_active}")
print(f"  Role: {user.role}")

exit()
```

---

## 🔄 Update Existing User to Admin

```bash
python manage.py shell
```

```python
from app.models import User

# Get user
user = User.objects.get(username='existing_username')

# Make admin
user.is_superuser = True
user.is_staff = True
user.role = 'admin'
user.is_active = True
user.set_password('new_password')  # Optional: change password
user.save()

print(f"User '{user.username}' updated to admin!")
exit()
```

---

## 📋 Quick Reference Commands

### Most Common: Create Default Admin
```bash
cd /home/admin/adams-django-main  # Your path
source venv/bin/activate
python manage.py create_techbless_superuser
```

### Create Custom Admin
```bash
cd /home/admin/adams-django-main
source venv/bin/activate
python manage.py createsuperuser
```

### Create User via Script
```bash
cd /home/admin/adams-django-main
source venv/bin/activate
python create_custom_superuser.py username email password
```

---

## 🎯 Complete Example Workflow

```bash
# 1. SSH to server
ssh admin@ip-172-26-10-8

# 2. Navigate to project
cd /home/admin/adams-django-main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Create default admin user
python manage.py create_techbless_superuser

# 5. Verify
python manage.py shell
# Then in shell:
# from app.models import User
# print(User.objects.filter(username='techbless').exists())
# exit()

# 6. Test login at: https://adams.org.in/admin_panel
```

---

## 🔐 Default Admin Credentials (After Running create_techbless_superuser)

- **Username:** `techbless`
- **Email:** `techbless7@gmail.com`
- **Password:** `admin123`
- **⚠️ Change password after first login!**

---

## 🛡️ Security Tips

1. **Change default password immediately** after first login
2. **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
3. **Limit admin access** to trusted IPs via Nginx if possible
4. **Monitor user activity** through Django admin logs
5. **Regular password rotation** for admin accounts

---

## ❓ Troubleshooting

### Issue: "Command not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate
```

### Issue: "No module named 'django'"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database connection error"
```bash
# Check database is running
sudo systemctl status postgresql

# Check .env file has correct database credentials
cat .env | grep DB_
```

### Issue: "Permission denied"
```bash
# Check file permissions
ls -la manage.py

# Fix if needed
chmod +x manage.py
```

---

## 📝 Summary

**Easiest Method:**
```bash
ssh admin@ip-172-26-10-8
cd /home/admin/adams-django-main
source venv/bin/activate
python manage.py create_techbless_superuser
```

**Login with:**
- Username: `techbless`
- Password: `admin123`
- URL: `https://adams.org.in/admin_panel`
