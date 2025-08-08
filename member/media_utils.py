from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.conf import settings
import os

def serve_media_with_fallback(request, path):
    """
    Serve media files with fallback to default images
    """
    # Full path to the requested file
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Check if file exists
    if os.path.exists(full_path):
        # Serve the file normally
        from django.views.static import serve
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    
    # File doesn't exist, determine appropriate fallback
    if 'profile_pictures/' in path:
        return redirect('/static/images/default-profile.png')
    elif 'company_logos/' in path:
        return redirect('/static/images/default-company-logo.png')
    elif 'challenges/' in path:
        return redirect('/static/images/default-company-logo.png')
    elif 'problems/' in path:
        return redirect('/static/images/default-company-logo.png')
    else:
        # For other media files, return 404
        raise Http404("Media file not found")
