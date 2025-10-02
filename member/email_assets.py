"""
Utility functions for handling email images and assets
"""
import base64
import os
from django.conf import settings


def get_logo_base64():
    """
    Get base64 encoded logo for email embedding
    """
    try:
        logo_path = os.path.join(settings.STATIC_ROOT or (settings.BASE_DIR / 'static'), 'images', 'logo-notext-white.png')
        
        # Try different possible paths
        possible_paths = [
            logo_path,
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo-notext-white.png'),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'logo-notext-white.png'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'rb') as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    return f"data:image/png;base64,{encoded}"
                    
        # If no logo found, return None - template will handle fallback
        return None
        
    except Exception as e:
        print(f"Error getting logo base64: {e}")
        return None


def get_logo_url(request=None):
    """
    Get logo URL for email templates
    """
    try:
        if request:
            # Use request to build absolute URL
            from django.urls import reverse
            try:
                from django.contrib.staticfiles import finders
                logo_path = finders.find('images/logo-notext-white.png')
                if logo_path:
                    return request.build_absolute_uri('/static/images/logo-notext-white.png')
            except:
                pass
            return request.build_absolute_uri('/static/images/logo-notext-white.png')
        else:
            # Fallback to configured domain or production URL
            from django.conf import settings
            
            # Try to get current site domain
            try:
                from django.contrib.sites.models import Site
                current_site = Site.objects.get_current()
                domain = current_site.domain
                protocol = 'https' if not settings.DEBUG else 'http'
                return f"{protocol}://{domain}/static/images/logo-notext-white.png"
            except:
                # Hard-coded fallback for production
                return "https://sea-map-staging.up.railway.app/static/images/logo-notext-white.png"
                
    except Exception as e:
        print(f"Error getting logo URL: {e}")
        return "https://sea-map-staging.up.railway.app/static/images/logo-notext-white.png"