from django.urls import path
from . import views
from .views import OnboardingRoleSelectionView

urlpatterns = [
    # Onboarding flow
    path('onboarding/', OnboardingRoleSelectionView.as_view(), name='onboarding_role_selection'),
    path('onboarding/startup/', views.onboarding_startup_new, name='onboarding_startup_new'),
    path('onboarding/investor/', views.onboarding_investor, name='onboarding_investor'),
    path('onboarding/corporate/', views.onboarding_corporate, name='onboarding_corporate'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
]
