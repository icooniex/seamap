"""
Email utilities for sending OTP and other notifications
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


def send_otp_email(user, otp_code, context=None):
    """
    Send OTP verification email to user
    
    Args:
        user: Django User instance
        otp_code: 6-digit OTP code string
        context: Optional context message about what the OTP is for
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Your Verification Code - SEA-MaP Regional Platform for Innovation and Investments'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        # Get logo URL for email
        from .email_assets import get_logo_url, get_logo_base64
        logo_url = get_logo_url()
        logo_base64 = get_logo_base64()
        
        # Context for email templates
        email_context = {
            'user': user,
            'otp_code': otp_code,
            'logo_url': logo_url,
            'logo_base64': logo_base64,
            'context_message': context or "for account verification",
        }
        
        # Render HTML and text versions
        html_body = render_to_string('emails/otp_verification.html', email_context)
        text_body = render_to_string('emails/otp_verification.txt', email_context)
        
        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=to_email
        )
        
        # Attach HTML version
        msg.attach_alternative(html_body, "text/html")
        
        # Send email
        msg.send()
        
        logger.info(f"OTP email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
        return False


def send_2fa_enabled_notification(user):
    """
    Send notification when 2FA is enabled
    
    Args:
        user: Django User instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Two-Factor Authentication Enabled - SEA-MaP Regional Platform for Innovation and Investments'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        message = f"""
Hello {user.first_name or user.username},

Two-factor authentication has been successfully enabled for your SEA-MaP Regional Platform for Innovation and Investments account.

From now on, you'll receive a verification code via email each time you sign in to your account. This adds an extra layer of security to protect your account.

If you didn't enable this feature, please contact our support team immediately.

Best regards,
SEA-MaP Regional Platform for Innovation and Investments Team
        """.strip()
        
        from django.core.mail import send_mail
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=to_email,
            fail_silently=False
        )
        
        logger.info(f"2FA enabled notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send 2FA enabled notification to {user.email}: {str(e)}")
        return False


def send_2fa_disabled_notification(user):
    """
    Send notification when 2FA is disabled
    
    Args:
        user: Django User instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Two-Factor Authentication Disabled - SEA-MaP Regional Platform for Innovation and Investments' 
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        message = f"""
Hello {user.first_name or user.username},

Two-factor authentication has been disabled for your SEA-MaP Regional Platform for Innovation and Investments account.

Your account security level has been reduced. We recommend keeping 2FA enabled for better account protection.

If you didn't disable this feature, please contact our support team immediately and consider enabling 2FA again.

Best regards,
SEA-MaP Regional Platform for Innovation and Investments Team
        """.strip()
        
        from django.core.mail import send_mail
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=to_email,
            fail_silently=False
        )
        
        logger.info(f"2FA disabled notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send 2FA disabled notification to {user.email}: {str(e)}")
        return False


def send_company_onboarding_notification(user, company):
    """
    Send company profile submission confirmation email when a user completes company onboarding.
    Informs the user that their company profile has been received and is pending review.

    Args:
        user: Django User instance
        company: Company model instance (just created/updated during onboarding)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Company Profile Received — Pending Review - SEA-MaP Regional Platform for Innovation and Investments'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        # Get logo for email
        from .email_assets import get_logo_url, get_logo_base64
        logo_url = get_logo_url()
        logo_base64 = get_logo_base64()

        # Build human-readable company type
        company_type_map = {
            'startup': 'Startup / SME',
            'investor': 'Investor / Fund',
            'corporate': 'Corporate / Organization',
        }
        company_type_display = company_type_map.get(company.company_type, company.company_type.capitalize())

        # Context for email templates
        email_context = {
            'user': user,
            'company': company,
            'company_type_display': company_type_display,
            'submitted_at': now().strftime('%B %d, %Y at %H:%M UTC'),
            'logo_url': logo_url,
            'logo_base64': logo_base64,
        }

        # Render HTML and text versions
        html_body = render_to_string('emails/signup_confirmation.html', email_context)
        text_body = render_to_string('emails/signup_confirmation.txt', email_context)

        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=to_email
        )

        # Attach HTML version
        msg.attach_alternative(html_body, "text/html")

        # Send email
        msg.send()

        logger.info(f"Company onboarding notification sent to {user.email} for company '{company.company_name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to send company onboarding notification to {user.email}: {str(e)}")
        return False


def send_document_upload_notification(user, document_name, document_type_display, document_category, company_name=None):
    """
    Send document upload confirmation email to the user.

    Args:
        user: Django User instance
        document_name: Name/title of the uploaded document
        document_type_display: Human-readable document type label
        document_category: 'member' or 'company'
        company_name: Company name if the document is a company document, else None

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Document Received — Pending Review - SEA-MaP Regional Platform for Innovation and Investments'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        # Get logo for email
        from .email_assets import get_logo_url, get_logo_base64
        logo_url = get_logo_url()
        logo_base64 = get_logo_base64()

        # Context for email templates
        email_context = {
            'user': user,
            'document_name': document_name,
            'document_type_display': document_type_display,
            'document_category': document_category,
            'company_name': company_name,
            'uploaded_at': now().strftime('%B %d, %Y at %H:%M UTC'),
            'logo_url': logo_url,
            'logo_base64': logo_base64,
        }

        # Render HTML and text versions
        html_body = render_to_string('emails/document_upload_notification.html', email_context)
        text_body = render_to_string('emails/document_upload_notification.txt', email_context)

        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=to_email
        )

        # Attach HTML version
        msg.attach_alternative(html_body, "text/html")

        # Send email
        msg.send()

        logger.info(f"Document upload notification sent to {user.email} for document '{document_name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to send document upload notification to {user.email}: {str(e)}")
        return False


def send_challenge_submission_notification(user, challenge_title, company_name, submitted_at):
    """
    Send Innovation Challenge submission confirmation email to the submitting user.

    Args:
        user: Django User instance
        challenge_title: Title of the submitted challenge
        company_name: Name of the organising company
        submitted_at: datetime when the challenge was submitted

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Innovation Challenge Submission Received - SEA-MaP Regional Platform for Innovation and Investments'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        # Get logo for email
        from .email_assets import get_logo_url, get_logo_base64
        logo_url = get_logo_url()
        logo_base64 = get_logo_base64()

        # Context for email templates
        email_context = {
            'user': user,
            'challenge_title': challenge_title,
            'company_name': company_name,
            'submitted_at': submitted_at.strftime('%B %d, %Y at %H:%M UTC') if submitted_at else now().strftime('%B %d, %Y at %H:%M UTC'),
            'logo_url': logo_url,
            'logo_base64': logo_base64,
        }

        # Render HTML and text versions
        html_body = render_to_string('emails/challenge_submission_notification.html', email_context)
        text_body = render_to_string('emails/challenge_submission_notification.txt', email_context)

        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=to_email
        )

        # Attach HTML version
        msg.attach_alternative(html_body, "text/html")

        # Send email
        msg.send()

        logger.info(f"Challenge submission notification sent to {user.email} for challenge '{challenge_title}'")
        return True

    except Exception as e:
        logger.error(f"Failed to send challenge submission notification to {user.email}: {str(e)}")
        return False