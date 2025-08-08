"""
Custom upload functions for different file types
"""
import os
from django.conf import settings


def profile_picture_upload_to(instance, filename):
    """
    Custom upload path for profile pictures
    Organizes files by user ID for better structure
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename: profile_pictures/user_id/profile.ext
    return f'profile_pictures/user_{instance.user.id}/profile.{ext}'


def company_logo_upload_to(instance, filename):
    """
    Custom upload path for company logos
    Organizes files by company ID for better structure
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename: company_logos/company_id/logo.ext
    return f'company_logos/company_{instance.id}/logo.{ext}'


def document_upload_to(instance, filename):
    """
    Custom upload path for documents (for future use)
    Private storage for sensitive documents
    """
    # Get file extension
    ext = filename.split('.')[-1]
    # Keep original filename but organize by user/company
    if hasattr(instance, 'company'):
        return f'documents/company_{instance.company.id}/{filename}'
    elif hasattr(instance, 'user'):
        return f'documents/user_{instance.user.id}/{filename}'
    else:
        return f'documents/misc/{filename}'
