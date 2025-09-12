from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from . import views

app_name = 'backoffice'

def is_admin_user(user):
    """Check if user is staff or superuser"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def backoffice_root(request):
    """Redirect root backoffice URL to appropriate page"""
    if is_admin_user(request.user):
        return redirect('backoffice:dashboard')
    else:
        return redirect('backoffice:login')

urlpatterns = [
    # Root redirect
    path('', backoffice_root, name='root'),
    
    # Back office authentication
    path('login/', views.BackOfficeLoginView.as_view(), name='login'),
    path('logout/', views.backoffice_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Company Management
    path('companies/', views.company_management, name='company_management'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    
    # Verification Management
    path('verification/', views.verification_dashboard, name='verification_dashboard'),
    path('verification/users/', views.user_verification, name='user_verification'),
    path('verification/users/<int:user_id>/update/', views.update_user_verification, name='update_user_verification'),
    path('verification/companies/', views.company_verification, name='company_verification'),
    path('verification/companies/<int:company_id>/update/', views.update_company_verification, name='update_company_verification'),
    
    # Document Management
    path('documents/', views.document_management, name='document_dashboard'),
    path('documents/members/', views.member_documents, name='member_documents'),
    path('documents/companies/', views.company_documents, name='company_documents'),
    path('documents/member/<int:doc_id>/', views.member_document_detail, name='member_document_detail'),
    path('documents/company/<int:doc_id>/', views.company_document_detail, name='company_document_detail'),
    path('documents/member/<int:doc_id>/review/', views.review_member_document, name='review_member_document'),
    path('documents/company/<int:doc_id>/review/', views.review_company_document, name='review_company_document'),
    
    # Challenge Management
    path('challenges/', views.challenge_management, name='challenge_management'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/review/', views.review_challenge, name='review_challenge'),
    path('challenges/<int:challenge_id>/publish/', views.publish_challenge, name='publish_challenge'),
    
    # Problem Statement Management
    path('problems/', views.problem_management, name='problem_management'),
    path('problems/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problems/<int:problem_id>/review/', views.review_problem, name='review_problem'),
    path('problems/<int:problem_id>/publish/', views.publish_problem, name='publish_problem'),
]
