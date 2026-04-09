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
    
    # Two-Factor Authentication
    path('verify-2fa-login/', views.verify_2fa_login, name='verify_2fa_login'),
    path('resend-2fa-otp/', views.resend_2fa_otp, name='resend_2fa_otp'),
    
    # Onboarding flow
    path('onboarding/', OnboardingRoleSelectionView.as_view(), name='onboarding_role_selection'),
    path('onboarding/profile/', views.onboarding_user_profile, name='onboarding_user_profile'),
    path('onboarding/startup/', views.onboarding_startup_new, name='onboarding_startup_new'),
    path('onboarding/investor/', views.onboarding_investor, name='onboarding_investor'),
    path('onboarding/corporate/', views.onboarding_corporate, name='onboarding_corporate'),
    
    # Dashboard
    path('dashboard/startups/', views.startup_matchmaking, name='dashboard'),
    
    # Profile Pages
    path('startup/<int:startup_id>/', views.startup_profile, name='startup_profile'),
    path('investor/<int:investor_id>/', views.investor_profile, name='investor_profile'),
    path('corporate/<int:corporate_id>/', views.corporate_profile, name='corporate_profile'),
    
    # Account Settings
    path('account-settings/', views.account_settings, name='account_settings'),
    path('account-settings/personal/', views.personal_profile_edit, name='personal_profile_edit'),
    path('account-settings/company/', views.company_profile_edit, name='company_profile_edit'),
    path('account-settings/startup/', views.startup_company_profile_edit, name='startup_company_profile_edit'),
    path('account-settings/documents/', views.document_management, name='document_management'),
    path('account-settings/verification/', views.verification_center, name='verification_center'),
    
    # Security
    path('toggle-2fa/', views.toggle_two_factor_auth, name='toggle_2fa'),
    path('send-2fa-verification/', views.send_2fa_verification, name='send_2fa_verification'),
    path('verify-and-toggle-2fa/', views.verify_and_toggle_2fa, name='verify_and_toggle_2fa'),
    path('test-2fa-email/', views.test_2fa_email, name='test_2fa_email'),
    
    # Document Management APIs
    path('api/documents/upload/', views.upload_document, name='upload_document'),
    path('api/documents/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('api/documents/<int:doc_id>/view/', views.view_document, name='view_document'),
    path('api/documents/<int:doc_id>/toggle-publish/', views.toggle_document_publish, name='toggle_document_publish'),
    
    # Legal Pages
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('environment-agreement/', views.environment_agreement, name='environment_agreement'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('match-score/', views.match_score_explanation, name='match_score_explanation'),
]
