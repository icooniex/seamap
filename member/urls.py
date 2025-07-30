from django.urls import path
from . import views
from .views import OnboardingRoleSelectionView

urlpatterns = [
    # Homepage
    path('', views.homepage, name='homepage'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Onboarding flow
    path('onboarding/', OnboardingRoleSelectionView.as_view(), name='onboarding_role_selection'),
    path('onboarding/profile/', views.onboarding_user_profile, name='onboarding_user_profile'),
    path('onboarding/startup/', views.onboarding_startup_new, name='onboarding_startup_new'),
    path('onboarding/investor/', views.onboarding_investor, name='onboarding_investor'),
    path('onboarding/corporate/', views.onboarding_corporate, name='onboarding_corporate'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Account Settings
    path('account-settings/', views.account_settings, name='account_settings'),
    path('account-settings/personal/', views.personal_profile_edit, name='personal_profile_edit'),
    path('account-settings/company/', views.company_profile_edit, name='company_profile_edit'),
    path('account-settings/documents/', views.document_management, name='document_management'),
    path('account-settings/verification/', views.verification_center, name='verification_center'),
]
