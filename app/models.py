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
    VISIBILITY_CHOICES = [
        ('public', 'Public (Everyone)'),
        ('members', 'Members Only'),
    ]
    
    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.TextField()
    date = models.DateField(auto_now_add=True)
    date_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    hyper_link = models.CharField(max_length=100, blank=True, null=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')

    class Meta:
        ordering = ['-date_time']


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_replies')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Rulebook(models.Model):
    title = models.CharField(max_length=200, default='ADAMS Rulebook')
    description = models.TextField(blank=True, null=True)
    pdf_file = models.CharField(max_length=500)  # MinIO path
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    image_name = models.CharField(max_length=500, unique=True)  # MinIO object name
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title or self.image_name


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


class RegistrationQuestion(models.Model):
    QUESTION_TYPES = [
        ('text', 'Short Answer (Text)'),
        ('textarea', 'Long Answer (Textarea)'),
        ('date', 'Date'),
        ('dropdown', 'Dropdown'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkbox'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('tel', 'Phone Number'),
        ('file', 'File Upload (PDF/JPG)'),
    ]
    
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='text')
    is_required = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Order in which question appears (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Only active questions appear in registration form")
    
    # For dropdown, radio, checkbox - store options as comma-separated values
    options = models.TextField(blank=True, null=True, help_text="For dropdown/radio/checkbox: comma-separated options (e.g., 'Option1,Option2,Option3')")
    
    # Placeholder or help text
    help_text = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_questions')
    
    class Meta:
        ordering = ['order', 'created_at']
        
    def __str__(self):
        return f"{self.question_text} ({self.get_question_type_display()})"
    
    def get_options_list(self):
        """Return options as a list"""
        if self.options:
            return [opt.strip() for opt in self.options.split(',') if opt.strip()]
        return []


class RegistrationAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registration_answers')
    question = models.ForeignKey(RegistrationQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    answer_date = models.DateField(blank=True, null=True)
    answer_number = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    answer_boolean = models.BooleanField(blank=True, null=True)
    answer_file = models.CharField(max_length=500, blank=True, null=True, help_text="MinIO file path for file uploads")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'question']
        ordering = ['question__order', 'created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question_text}: {self.get_answer_display()}"
    
    def get_answer_display(self):
        """Return the appropriate answer value based on question type"""
        if self.question.question_type == 'date':
            return str(self.answer_date) if self.answer_date else ''
        elif self.question.question_type == 'number':
            return str(self.answer_number) if self.answer_number else ''
        elif self.question.question_type in ['checkbox', 'radio']:
            return str(self.answer_boolean) if self.answer_boolean is not None else ''
        elif self.question.question_type == 'file':
            return self.answer_file or ''
        else:
            return self.answer_text or ''


class SystemSettings(models.Model):
    """System-wide settings that can be managed by admins"""
    key = models.CharField(max_length=100, unique=True, help_text="Setting key identifier")
    value = models.TextField(help_text="Setting value (can be JSON, boolean, text, etc.)")
    description = models.CharField(max_length=255, blank=True, null=True, help_text="Human-readable description")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_settings')
    
    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        try:
            setting = cls.objects.get(key=key)
            # Try to parse as boolean
            if setting.value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif setting.value.lower() in ['false', '0', 'no', 'off']:
                return False
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=None, user=None):
        """Set a setting value by key"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': str(value), 'description': description, 'updated_by': user}
        )
        if not created:
            setting.value = str(value)
            if description:
                setting.description = description
            if user:
                setting.updated_by = user
            setting.save()
        return setting