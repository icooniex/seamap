"""
URL configuration for seamap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from member.views import *
from member.media_utils import serve_media_with_fallback

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include member app URLs
    path('', include('member.urls')),

    # Match making dashboard
    path('dashboard/startups/', startup_matchmaking, name='startup_matchmaking'),
    path('dashboard/investors/', investor_matchmaking, name='investor_matchmaking'),
    path('dashboard/corporates/', corporate_matchmaking, name='corporate_matchmaking'),

    path('dashboard/problem-statement/', problem, name='problem'),
    path('dashboard/problem-statement/<int:problem_id>/', problem_detail, name='problem_detail'),
    path('dashboard/problem-statement/create/', create_problem_statement, name='create_problem_statement'),
    path('dashboard/challenge/', challenge, name='challenge'),
    path('dashboard/challenge/<int:challenge_id>/', challenge_detail, name='challenge_detail'),
    path('dashboard/challenge/create/', create_challenge, name='create_challenge'),
    path('dashboard/accelerator-landing/', accelerator_landing, name='accelerator_landing'),
    
    path('startup/profile/<int:startup_id>/', startup_profile, name='startup_profile'),
    path('investor/profile/<int:investor_id>/', investor_profile, name='investor_profile'),
    path('corporate/profile/<int:corporate_id>/', corporate_profile, name='corporate_profile'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production (Railway) with fallback handling
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media_with_fallback, name='media'),
    ]
