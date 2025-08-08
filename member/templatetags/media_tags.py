from django import template
from django.conf import settings
import os

register = template.Library()

@register.simple_tag
def profile_picture_url(member):
    """Get profile picture URL with fallback"""
    if hasattr(member, 'get_profile_picture_url'):
        return member.get_profile_picture_url()
    
    if member.profile_picture and hasattr(member.profile_picture, 'url'):
        try:
            # For R2 storage, always return the URL (cloud storage handles existence)
            if getattr(settings, 'USE_CLOUDFLARE_R2', False):
                return member.profile_picture.url
            elif settings.DEBUG:
                # Local development - check file existence
                file_path = os.path.join(settings.MEDIA_ROOT, str(member.profile_picture))
                if os.path.exists(file_path):
                    return member.profile_picture.url
            else:
                # Production with local storage
                return member.profile_picture.url
        except:
            pass
    
    return '/static/images/default-profile.png'

@register.simple_tag
def company_logo_url(company):
    """Get company logo URL with fallback"""
    if hasattr(company, 'get_company_logo_url'):
        return company.get_company_logo_url()
    
    if company.company_logo and hasattr(company.company_logo, 'url'):
        try:
            # For R2 storage, always return the URL (cloud storage handles existence)
            if getattr(settings, 'USE_CLOUDFLARE_R2', False):
                return company.company_logo.url
            elif settings.DEBUG:
                # Local development - check file existence
                file_path = os.path.join(settings.MEDIA_ROOT, str(company.company_logo))
                if os.path.exists(file_path):
                    return company.company_logo.url
            else:
                # Production with local storage
                return company.company_logo.url
        except:
            pass
    
    # Return default logo based on company type
    default_logos = {
        'startup': '/static/images/default-startup-logo.png',
        'investor': '/static/images/default-investor-logo.png', 
        'corporate': '/static/images/default-corporate-logo.png',
    }
    return default_logos.get(company.company_type, '/static/images/default-company-logo.png')

@register.simple_tag
def safe_image_url(image_field, default_url='/static/images/default-profile.png'):
    """Generic image URL with fallback"""
    if image_field and hasattr(image_field, 'url'):
        try:
            if settings.DEBUG:
                file_path = os.path.join(settings.MEDIA_ROOT, str(image_field))
                if os.path.exists(file_path):
                    return image_field.url
            else:
                return image_field.url
        except:
            pass
    
    return default_url
