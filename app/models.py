import pytz
from django.db import models
from django.core.validators import RegexValidator
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=gender_choices)
    whatsapp_number = models.CharField(max_length=15, unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    address_communication = models.TextField()
    address_permanent = models.TextField()
    district_choices = [
        ('Thiruvananthapuram', 'Thiruvananthapuram'), 
        ('Kollam', 'Kollam'),
        ('Pathanamthitta', 'Pathanamthitta'),
        ('Alappuzha', 'Alappuzha'),
        ('Kottayam', 'Kottayam'),
        ('Idukki', 'Idukki'),
        ('Ernakulam', 'Ernakulam'),
        ('Thrissur', 'Thrissur'),
        ('Palakkad', 'Palakkad'),
        ('Malappuram', 'Malappuram'),
        ('Kozhikode', 'Kozhikode'),
        ('Wayanad', 'Wayanad'),
        ('Kannur', 'Kannur'),
        ('Kasaragod', 'Kasaragod'),
        ('Others', 'Others')
    ]
    # district = models.CharField(max_length=50, choices=district_choices)
    district = models.CharField(max_length=50)

    father_spouse_details = models.TextField()
    blood_group_choices = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Bombay Group', 'Bombay Group')
    ]
    blood_group = models.CharField(max_length=15, choices=blood_group_choices)
    role = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('intern', 'Intern'),
        ('doctor', 'Doctor'),
    
    )
    role = models.CharField(max_length=10, choices=role, default='student')
    educational_status = (
        ('Student (@Abroad University)', 'Student (@Abroad University)'),
        ('Graduated / FMGE Aspirant', 'Graduated / FMGE Aspirant'),
        ('FMGE Passed Candidate', 'FMGE Passed Candidate'),
        ('Internship', 'Internship'),
        ('Working Doctor', 'Working Doctor'),
        ('Post Graduation ongoing', 'Post Graduation ongoing'),
        ('Post Graduation Completed, Working', 'Post Graduation Completed, Working')
    )
    educational_status = models.CharField(max_length=50, choices=educational_status, default='Student (@Abroad University)')
    # Category You Belong To For Membership
    category = (
        ('Student', 'Student'),
        ('Graduate/Trying FMGE', 'Graduate/Trying FMGE'),
        ('FMGE passed', 'FMGE passed'),
        ('Working Doctor', 'Working Doctor (With SMC/NMC Registration)'),
        ('PG Doctor', 'Working PG Doctor (With SMC/NMC Registration)')
    )
    category = models.CharField(max_length=50, choices=category, default='Student')
    # University Name Short forms not accepted
    university_name = models.CharField(max_length=100)
    # Country University is situated
    country_university = models.CharField(max_length=100)
    # Year of Joining Medical Education  *
    year_of_joining = models.CharField(max_length=100)
    # Year of Completion/Expected Completion of course  *
    year_of_completion = models.CharField(max_length=100)
    # Upload recent passport size photo  * Upload front facing photograph .it will be used for Association ID card
    photo = models.CharField(max_length=500)
    # State/NMC registeration certificate For registered doctors.
    state_nmc = models.CharField(max_length=500, blank=True, null=True, default='')
    # Passport (Front and Back) *
    passport = models.CharField(max_length=500)
    # Upload Medical qualification. (Provisional/Permanent)Degree/ Diploma Certificate/ Student ID Card 
    medical_qualification = models.CharField(max_length=500)

    """
    Payment Section

    Step 1 -Reffer website to select membership.

    Step 2 -Make payment using QR code given in website and download/save or screenshot the payment transaction number/ID.

    Step 3 -Upload the screenshot/slip containing transaction number of payment in this section.
    """

    # Date and time of Payment (Transaction) *
    date_time_of_payment = models.CharField(max_length=100)
    # Upload Payment Transaction Proof/screenshot  *
    payment_transaction_proof = models.CharField(max_length=500)

    """
    Registration completion page

    After submitting the form, while the form is processed, you will be contacted back by our officially notified team or member. 
    Upon successful verification of the application (following rules and regulations of the ADAMS) by the committee, your membership will be granted.
    """

    # Willing to be a blood donor?
    willing_to_be_donor = models.BooleanField(default=False, null=True, blank=True)
    # Agreement for Joining Association of Doctors And Medical Students (ADAMS) *
    agreement = models.BooleanField(default=False)

    # Are you in any district group of AKFMA.If yes mention your MID. MID can be collected by contacting assigned district admins informed in the AKFMA District Groups.
    mid = models.CharField(max_length=100, blank=True, null=True)

    # I agree to the terms and conditions of the association and I hereby submit my application for membership in ADAMS
    application = models.BooleanField(default=False)   

    status = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=status, default='pending')
    admin_remarks = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
    )


class Complaints(models.Model):
    cid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint = models.TextField()
    status = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=status, default='pending')

    class Meta:
        ordering = ['-cid']

class Announcement(models.Model):
    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.TextField()
    date = models.DateField(auto_now_add=True)
    date_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    hyper_link = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-date_time']

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Skip the expiration check and just validate if the OTP code matches
        return True  # OTP will always be valid when the code matches

class CategoryChangeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_category = models.CharField(max_length=50)
    requested_category = models.CharField(max_length=50)
    request_status_choices = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    request_status = models.CharField(max_length=10, choices=request_status_choices, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    admin_decision_date = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-request_date']
        
    def __str__(self):
        return f"{self.user.username} - {self.current_category} to {self.requested_category}"
