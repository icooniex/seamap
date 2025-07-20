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
from django.urls import path, include
from member.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include member app URLs
    path('', include('member.urls')),
    
    # Legacy URLs (keeping for compatibility)
    path('signup/', signup, name='signup'),
    path('dash/', dashboard2, name='dash'),
    path('matchmaking/investors/', investor_matchmaking, name='investor_matchmaking'),
    path('dashboard/startup', dashboard, name='dashboard_startup'),
    path('dashboard/problem-statement', problem, name='problem'),
    path('dashboard/challenge', challenge, name='challenge'),
    path('dashboard/accelerator-landing', accelerator_landing, name='accelerator_landing'),
    path('dashboard/startup-detail', startup_detail, name='startup_detail'),
    path('dashboard/investor-detail', investor_detail, name='investor_detail'),
    path('startup/profile/<int:startup_id>/', startup_profile, name='startup_profile'),
    path('investor/profile/<int:investor_id>/', investor_profile, name='investor_profile'),
    path('corporate/profile/<int:corporate_id>/', corporate_profile, name='corporate_profile'),

    # path('onboarding/startup/1', onboarding_startup_step1, name='onboarding_startup_step1'),
    # path('onboarding/startup/2', onboarding_startup_step2, name='onboarding_startup_step2'),
    # path('onboarding/startup/3', onboarding_startup_step3, name='onboarding_startup_step3'),
    # path('onboarding/startup/4', onboarding_startup_step4, name='onboarding_startup_step4'),
    # path('onboarding/startup/5', onboarding_startup_step5, name='onboarding_startup_step5'),
    # path('onboarding/startup/6', onboarding_startup_step6, name='onboarding_startup_step6'),
    # path('onboarding/startup/single', onboarding_startup_single_page, name='onboarding_startup_single_page'),
]
