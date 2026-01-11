from io import BytesIO
import random
import string

from django.conf import settings
from django.core.mail import EmailMessage

from loguru import logger

from minio import Minio
from minio.error import S3Error
import qrcode

from .models import OTP

# Initialize the Minio client (lazy initialization to avoid connection errors at startup)
_minio_client = None
_bucket_name = settings.MINIO_BUCKET_NAME

def get_minio_client():
    """Get or create MinIO client instance (lazy initialization)"""
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
        # Try to ensure bucket exists (non-blocking, won't fail if MinIO is down)
        try:
            if not _minio_client.bucket_exists(_bucket_name):
                _minio_client.make_bucket(_bucket_name)
                logger.info(f"Bucket '{_bucket_name}' created successfully.")
            else:
                logger.info(f"Bucket '{_bucket_name}' already exists.")
        except Exception as e:
            logger.warning(f"Could not verify MinIO bucket (MinIO may not be running): {e}")
    return _minio_client

# Lazy MinIO client class for backward compatibility
class LazyMinioClient:
    """Lazy wrapper for MinIO client that initializes on first access"""
    def __getattr__(self, name):
        return getattr(get_minio_client(), name)

# Module-level variables for backward compatibility
minio_client = LazyMinioClient()
bucket_name = _bucket_name


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
    """
    Upload an image to MinIO storage.

    Args:
        file: File object containing the image data
        file_name (str): Name to use when storing the file

    Returns:
        bool: True if upload was successful, False otherwise

    Example:
        >>> with open('image.jpg', 'rb') as f:
        ...     success = upload_image_to_minio(f, 'images/image.jpg')
    """
    try:
        # Upload file to MinIO
        logger.info(f"Uploading image {file_name} to MinIO")
        client = get_minio_client()
        client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_name,
            data=file,
            length=file.size,
            content_type=file.content_type,
        )

        logger.info(f"Image {file_name} uploaded successfully")
        return True
    except Exception as e:
        logger.exception(f"Error uploading image {file_name}: {e}")
        return False


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
    try:
        # Delete file from MinIO
        logger.info(f"Deleting image {file_name} from MinIO")
        client = get_minio_client()
        client.remove_object(
            bucket_name=settings.MINIO_BUCKET_NAME, object_name=file_name
        )

        logger.info(f"Image {file_name} deleted successfully")
        return True
    except Exception as e:
        logger.exception(f"Error deleting image {file_name}: {e}")
        return False


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
