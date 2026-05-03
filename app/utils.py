from io import BytesIO
import random
import string
import os

from django.conf import settings
from django.core.mail import EmailMessage

from loguru import logger

from minio import Minio
from minio.error import S3Error
import qrcode

from .models import OTP

# Initialize the MinIO client (lazy initialization to avoid connection errors at startup)
_minio_client = None
_minio_client_failed = False  # Track if client initialization failed
_bucket_name = None

def get_minio_client():
    """Get or create MinIO client instance (lazy initialization)"""
    global _minio_client, _minio_client_failed, _bucket_name
    
    # Reset failed flag to retry connection
    # This allows retrying if MinIO becomes available
    if _minio_client_failed:
        _minio_client = None
        _minio_client_failed = False
    
    if _minio_client is None:
        try:
            # Only create client if MinIO is enabled
            if not settings.MINIO_ENABLED:
                return None
            
            # Determine if connection should be secure (HTTPS)
            # Check if URL contains https:// or if MINIO_SECURE env var is set
            minio_url = settings.MINIO_URL
            secure = bool(getattr(settings, "MINIO_SECURE", False))
            if minio_url.startswith('https://'):
                secure = True
                minio_url = minio_url.replace('https://', '')
            elif minio_url.startswith('http://'):
                minio_url = minio_url.replace('http://', '')
            
            logger.info(f"Initializing MinIO client - URL: {minio_url}, Secure: {secure}")
            
            # Create MinIO client with timeout settings for faster failure detection
            from urllib3 import PoolManager
            from urllib3.util.retry import Retry
            
            # Configure retry strategy with shorter timeouts
            retry_strategy = Retry(
                total=2,  # Only 2 retries instead of default
                backoff_factor=0.5,  # Shorter backoff
                status_forcelist=[500, 502, 503, 504],
            )
            
            # Create HTTP client with timeout
            http_client = PoolManager(
                retries=retry_strategy,
                timeout=5.0,  # 5 second timeout instead of default 30+
                maxsize=10
            )
            
            _minio_client = Minio(
                minio_url,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=secure,
                http_client=http_client,
            )
            
            # Test connection and ensure bucket exists (with timeout)
            try:
                # Test connection by listing buckets (with timeout)
                _minio_client.list_buckets()
                logger.info("MinIO connection successful")
                
                # Ensure bucket exists
                _bucket_name = settings.MINIO_BUCKET_NAME
                if not _minio_client.bucket_exists(_bucket_name):
                    _minio_client.make_bucket(_bucket_name)
                    logger.info(f"Bucket '{_bucket_name}' created successfully.")
                else:
                    logger.info(f"Bucket '{_bucket_name}' already exists and is accessible.")
            except Exception as e:
                logger.error(f"MinIO connection or bucket verification failed: {e}")
                _minio_client = None  # Set to None so upload function knows MinIO is not available
                _minio_client_failed = True  # Mark as failed
                # Don't raise exception here - let upload function handle it
        except Exception as e:
            logger.error(f"Could not initialize MinIO client: {e}")
            _minio_client = None
            _minio_client_failed = True  # Mark as failed
            # Don't raise exception - let upload function handle it gracefully
    return _minio_client

def upload_file_to_minio(file_obj, object_name: str, content_type: str | None = None) -> bool:
    """
    Upload a file-like object (Django UploadedFile) to MinIO.
    Returns True on success, False on failure.
    """
    if not settings.MINIO_ENABLED:
        logger.error("MinIO upload attempted but MINIO_ENABLED is false")
        return False

    client = get_minio_client()
    if client is None:
        logger.error("MinIO client not available")
        return False

    bucket = settings.MINIO_BUCKET_NAME
    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        # Prefer known size if available (Django UploadedFile has `.size`)
        length = getattr(file_obj, "size", None)
        if length is None:
            # Fallback: read into memory
            data = file_obj.read()
            length = len(data)
            file_obj = BytesIO(data)
            file_obj.seek(0)

        client.put_object(
            bucket,
            object_name,
            file_obj,
            length=length,
            content_type=content_type or "application/octet-stream",
        )
        logger.info(f"Uploaded object to MinIO: bucket={bucket}, object={object_name}, bytes={length}")
        return True
    except Exception as e:
        logger.exception(f"MinIO upload failed for object={object_name}: {e}")
        return False


def fetch_file_from_minio(object_name: str) -> bytes | None:
    """Fetch an object from MinIO and return its bytes, or None on failure."""
    if not settings.MINIO_ENABLED:
        return None

    client = get_minio_client()
    if client is None:
        return None

    bucket = settings.MINIO_BUCKET_NAME
    response = None
    try:
        response = client.get_object(bucket, object_name)
        return response.read()
    except Exception as e:
        logger.exception(f"MinIO fetch failed for object={object_name}: {e}")
        return None
    finally:
        try:
            if response is not None:
                response.close()
                response.release_conn()
        except Exception:
            pass


def delete_file_from_minio(object_name: str) -> bool:
    """Delete an object from MinIO. Returns True on success, False on failure."""
    if not settings.MINIO_ENABLED:
        logger.error("MinIO delete attempted but MINIO_ENABLED is false")
        return False

    client = get_minio_client()
    if client is None:
        logger.error("MinIO client not available")
        return False

    bucket = settings.MINIO_BUCKET_NAME
    try:
        client.remove_object(bucket, object_name)
        logger.info(f"Deleted object from MinIO: bucket={bucket}, object={object_name}")
        return True
    except Exception as e:
        logger.exception(f"MinIO delete failed for object={object_name}: {e}")
        return False


def get_gallery_images():
    """
    Fetch gallery images from database with descriptions.

    Returns:
        list: A list of dictionaries containing image data including name and description.
              Returns empty list if there is an error.

    Example:
        >>> get_gallery_images()
        [{'name': 'image1.jpg', 'title': 'Event 2024', 'description': 'Annual meet'}, ...]
    """
    try:
        from .models import GalleryImage
        
        logger.info(f"Fetching gallery images from database")
        gallery_images = GalleryImage.objects.all()
        
        images = []
        for img in gallery_images:
            images.append({
                "name": img.image_name,
                "title": img.title or "",
                "description": img.description or "",
                "id": img.id
            })
        
        logger.info(f"Successfully fetched {len(images)} gallery images")
        return images
    except Exception as e:
        logger.error(f"Error fetching gallery images: {e}")
        return []


def upload_image_to_minio(file, file_name):
    """Backward-compatible wrapper used by older scripts."""
    return upload_file_to_minio(file, file_name, getattr(file, "content_type", None))


def delete_image_from_minio(file_name):
    """
    Delete an image from MinIO storage.

    Args:
        file_name (str): Name of the file to delete from MinIO

    Returns:
        bool: True if deletion was successful, False otherwise

    Example:
        >>> success = delete_image_from_minio('images/image.jpg')
    """
    return delete_file_from_minio(file_name)


def generate_qr_code_live(user):
    """
    Generate a QR code image containing the user's username.

    Args:
        user: User object containing username attribute

    Returns:
        BytesIO: Buffer containing the generated QR code image in PNG format

    Example:
        >>> user = User.objects.get(username='john')
        >>> qr_buffer = generate_qr_code_live(user)
    """
    # Use only the username for the QR code
    username = user.username
    logger.info(f"Generating QR code for user: {username}")

    # Create the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(username)  # Add only the username
    qr.make(fit=True)
    logger.debug("QR code data added and generated")

    # Create the image
    img = qr.make_image(fill_color="black", back_color="white")
    logger.debug("QR code image created")

    # Save the image to a buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    logger.info("QR code image saved to buffer successfully")
    return buffer


def generate_random_password(length=8):
    """
    Generate a simple random password containing letters and digits.

    Args:
        length (int): Length of the password to generate. Defaults to 8.

    Returns:
        str: Random password string of specified length.

    Example:
        >>> password = generate_random_password(10)
        >>> print(password)  # Prints something like 'x2Mk9p4Lq'
    """
    logger.info(f"Generating simple random password of length {length}")
    characters = string.ascii_letters + string.digits  # Simple characters set
    password = "".join(random.choice(characters) for _ in range(length))
    logger.debug(f"Generated password of length {len(password)}")
    return password



def generate_otp():
    """
    Generate a random 6-digit OTP (One Time Password).

    Returns:
        str: A random 6-digit number as string between 100000 and 999999

    Example:
        >>> otp = generate_otp()
        >>> print(otp)  # Prints something like '483591'
    """
    logger.info("Generating new OTP")
    otp = str(random.randint(100000, 999999))
    logger.debug(f"Generated OTP: {otp}")
    return otp


def send_otp_via_email(user):
    """
    Generate and send a one-time password (OTP) to a user via email.

    Args:
        user: User object containing email attribute

    Returns:
        bool: True if OTP was sent successfully, False otherwise

    Example:
        >>> user = User.objects.get(username='john')
        >>> success = send_otp_via_email(user)
    """
    try:
        logger.info(f"Sending OTP to user: {user}")
        otp = generate_otp()
        logger.debug(f"Generated OTP for user {user}")

        OTP.objects.update_or_create(user=user, defaults={"otp_code": otp})
        logger.debug(f"Saved OTP to database for user {user}")

        html_content = f"""
                    <html>
                        <body style="font-family: 'Arial', sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                            <table width="100%" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                <tr>
                                    <td style="padding: 20px; text-align: center; background-color: #2c3e50; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                        <h1 style="color: #ffffff; margin: 0;">Association of Doctors and Medical Students (ADAMS)</h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 20px;">
                                        <h2 style="color: #2c3e50;">🔑 Your Secure Login OTP</h2>
                                        <p style="color: #333333;">
                                            Dear {user.first_name},  
                                            Here is your One-Time Password (OTP) for secure login to ADAMS:
                                        </p>
                                        <div style="background-color: #f1f8e9; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                                            <span style="font-size: 32px; font-weight: bold; color: #28a745;">{otp}</span>
                                        </div>
                                        <p style="color: #555555;">
                                            This OTP is valid for the next <strong>5 minutes</strong>. Please enter it promptly to complete your login.
                                        </p>
                                        <p style="color: #e74c3c;">
                                            ⚠️ If you did not request this OTP, please ignore this message or contact our support team immediately.
                                        </p>
                                        <p style="color: #7f8c8d;">Warm regards, <br>The ADAMS Team</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 14px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                        <p style="margin: 0;">Need help? <a href="https://adams.org.in/contact" style="color: #3498db;">Contact Us</a></p>
                                    </td>
                                </tr>
                            </table>
                        </body>
                    </html>
                    """

        # send_mail(
        #     subject="Your Login OTP",
        #     message=message,
        #     from_email="your-email@gmail.com",
        #     recipient_list=[user.email],
        # )

        subject="Your Secure Login OTP"
        recipient_list=[user.email]  # Must be a list
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )

        # Set HTML content type
        email.content_subtype = "html"

        # Send email
        email.send(fail_silently=False)
        logger.info(f"Successfully sent OTP email to {user.email}")
        return True
    except Exception as e:
        logger.exception(f"Error sending OTP to {user}: {e}")
        return False


def send_new_account_credentials_email(
    *,
    username,
    email,
    password_plain,
    login_url="",
    profile_url="",
    upload_url="",
):
    """
    Email a newly created user their username, email, and plaintext password (registration or bulk).
    Includes reminders to change password regularly and to upload missing profile documents.
    """
    from django.utils.html import escape

    u = escape(username or "")
    em = escape(email or "")
    pw = escape(password_plain or "")
    login_href = escape(login_url or "")
    profile_href = escape(profile_url or "")
    upload_href = escape(upload_url or "")

    login_block = (
        f'<p style="margin:12px 0;"><a href="{login_href}" style="color:#0d6efd;">Open login page</a></p>'
        if login_href
        else "<p style=\"margin:12px 0;\">Log in through your ADAMS portal.</p>"
    )
    profile_block = (
        f'<p style="margin:8px 0;"><a href="{profile_href}" style="color:#0d6efd;">Your profile</a></p>'
        if profile_href
        else ""
    )
    if upload_href:
        upload_sentence = (
            f'If anything is still missing, use '
            f'<a href="{upload_href}" style="color:#0d6efd;">Upload missing files</a> from your profile.'
        )
    else:
        upload_sentence = (
            'If anything is still missing, open your profile and use "Upload missing files".'
        )

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;background:#f4f6f9;margin:0;padding:24px;">
      <table width="100%" style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;
        box-shadow:0 2px 8px rgba(0,0,0,.08);">
        <tr>
          <td style="padding:20px;background:#243c71;color:#fff;text-align:center;">
            <h1 style="margin:0;font-size:1.25rem;">ADAMS — Account created</h1>
          </td>
        </tr>
        <tr>
          <td style="padding:24px;color:#333;line-height:1.55;">
            <p>Your ADAMS member account is ready. Use the credentials below to sign in.</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:0.95rem;">
              <tr><td style="padding:8px 0;font-weight:600;width:140px;">Username</td>
                  <td style="padding:8px 0;font-family:ui-monospace,monospace;">{u}</td></tr>
              <tr><td style="padding:8px 0;font-weight:600;">Email</td>
                  <td style="padding:8px 0;">{em}</td></tr>
              <tr><td style="padding:8px 0;font-weight:600;">Password</td>
                  <td style="padding:8px 0;font-family:ui-monospace,monospace;">{pw}</td></tr>
            </table>
            <p style="margin:16px 0 8px;"><strong>Security:</strong> Please change your password regularly
              and do not share it with anyone.</p>
            <p style="margin:8px 0 16px;"><strong>Documents:</strong> {upload_sentence}
              <em>You may ignore this notice if you have already uploaded everything in the portal.</em></p>
            {login_block}
            {profile_block}
            <p style="margin-top:20px;color:#6c757d;font-size:0.9rem;">— ADAMS</p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    try:
        msg = EmailMessage(
            subject="ADAMS — Your account has been created",
            body=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        logger.info("Sent new-account credentials email to %s (username=%s)", email, username)
        return True
    except Exception as e:
        logger.exception("Failed to send new-account email to %s: %s", email, e)
        return False


def send_email_with_attachments(
    subject,
    recipient_list,
    template_type="welcome",
    custom_message=None,
    attachments=None,
):
    """
    Send emails with optional attachments and templated content.

    Args:
        subject (str): Email subject line
        recipient_list (list): List of recipient email addresses
        template_type (str): Type of email template to use ('welcome', 'notification', 'custom')
        custom_message (str): Custom message for template_type='custom'
        attachments (list): List of file objects to attach

    Returns:
        bool: True if email sent successfully, False otherwise

    Example:
        >>> attachments = [('report.pdf', pdf_data, 'application/pdf')]
        >>> success = send_email_with_attachments(
        ...     subject='Welcome!',
        ...     recipient_list=['user@example.com'],
        ...     template_type='welcome',
        ...     attachments=attachments
        ... )
    """
    try:
        logger.info(f"Sending {template_type} email to {recipient_list}")

        # Email templates
        templates = {
            "welcome": f"""
                <html>
                <body style="font-family: 'Arial', sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                <table width="100%" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <tr>
                    <td style="padding: 20px; text-align: center; background-color: #2c3e50;">
                        <h1 style="color: #ffffff; margin: 0;">Association of Doctors and Medical Students (ADAMS)</h1>
                    </td>
                    </tr>
                    <tr>
                    <td style="padding: 20px;">
                        <h2 style="color: #2c3e50;">🎉 Welcome to ADAMS!</h2>
                        <p style="color: #333333;">
                        Hello, and thank you for joining us! We’re excited to have you as part of our vibrant community of doctors and medical students.
                        </p>
                        <p style="color: #555555;">
                        Here are some helpful links to get you started:
                        </p>
                        <ul style="color: #333333; padding-left: 20px;">
                        <li><a href="https://adams.org.in/" style="color: #3498db; text-decoration: none;">Visit Our Website</a></li>
                        <li><a href="https://adams.org.in/about" style="color: #3498db; text-decoration: none;">Learn About Us</a></li>
                        <li><a href="https://adams.org.in/contact" style="color: #3498db; text-decoration: none;">Contact Support</a></li>
                        </ul>
                        <p style="color: #555555;">
                        We look forward to seeing you thrive and contribute to our mission.
                        </p>
                        <p style="color: #7f8c8d;">Warm regards, <br>The ADAMS Team</p>
                    </td>
                    </tr>
                    <tr>
                    <td style="background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 14px;">
                        <p style="margin: 0;">Need help? <a href="https://adams.org.in/contact" style="color: #3498db;">Contact Us</a></p>
                    </td>
                    </tr>
                </table>
                </body>
            </html>


            """,
            "notification": f"""
                <html>
                    <body style="font-family: 'Arial', sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                    <table width="100%" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <tr>
                        <td style="padding: 20px; background-color: #007bff; color: #ffffff; text-align: center;">
                            <h1 style="margin: 0;">Association of Doctors and Medical Students (ADAMS)</h1>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #2c3e50;">🔔 New Notification</h3>
                            <p style="color: #333333;">Dear Member,</p>
                            <p style="color: #555555;">You have a new update from ADAMS:</p>
                            <p style="color: #333333; background-color: #f0f8ff; padding: 10px; border-left: 4px solid #007bff;">
                            {custom_message}.
                            </p>
                            <p style="color: #7f8c8d;">Stay connected for more updates from ADAMS.</p>
                        </td>
                        </tr>
                        <tr>
                        <td style="background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 14px;">
                            <p style="margin: 0;">Visit <a href="https://adams.org.in/" style="color: #3498db;">Our Website</a> for more details.</p>
                        </td>
                        </tr>
                    </table>
                    </body>
                </html>


            """,
            "custom": f"""
                <html>
                    <body style="font-family: 'Arial', sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                    <table width="100%" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <tr>
                        <td style="padding: 20px; text-align: center; background-color: #28a745; color: #ffffff;">
                            <h1 style="margin: 0;">Association of Doctors and Medical Students (ADAMS)</h1>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding: 20px;">
                            <h3 style="color: #2c3e50;">📧 Message</h3>
                            <div style="border: 1px solid #eeeeee; padding: 15px; background-color: #fafafa;">
                            {custom_message}
                            </div>
                        </td>
                        </tr>
                        <tr>
                        <td style="background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 14px;">
                            <p style="margin: 0;">For inquiries, <a href="https://adams.org.in/contact" style="color: #3498db;">Contact Us</a></p>
                        </td>
                        </tr>
                    </table>
                    </body>
                </html>

            """,
        }

        # Get email content based on template type
        html_content = templates.get(template_type, templates["custom"])

        # Create email message
        from django.core.mail import EmailMessage

        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )

        # Set HTML content type
        email.content_subtype = "html"

        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                name, content, mime_type = attachment
                email.attach(name, content, mime_type)
                logger.debug(f"Added attachment: {name}")

        # Send email
        email.send(fail_silently=False)
        logger.info(f"Successfully sent {template_type} email to {recipient_list}")
        return True

    except Exception as e:
        logger.exception(f"Error sending email to {recipient_list}: {e}")
        return False


# Paths used when bulk-import did not supply real files (see bulk_user_import.DOC_PLACEHOLDER).
MEMBER_PROFILE_FILE_FIELDS = (
    "photo",
    "passport",
    "medical_qualification",
    "payment_transaction_proof",
    "state_nmc",
)


def stored_file_is_missing(value):
    """
    True when no real member file is stored (empty/whitespace, or bulk placeholder path).
    """
    if value is None:
        return True
    s = str(value).strip()
    if not s:
        return True
    normalized = s.replace("\\", "/").lower()
    if "bulk-import/pending" in normalized:
        return True
    return False


def member_profile_file_gaps(user):
    """Map each profile file field to whether the member still needs to upload it."""
    return {
        field: stored_file_is_missing(getattr(user, field, None))
        for field in MEMBER_PROFILE_FILE_FIELDS
    }
