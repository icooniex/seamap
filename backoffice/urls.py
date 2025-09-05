from django.urls import path
from . import views

urlpatterns = [
    # Back office authentication
    path('login/', views.BackOfficeLoginView.as_view(), name='backoffice_login'),
    path('logout/', views.backoffice_logout, name='backoffice_logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='backoffice_dashboard'),
    
    # User Management
    path('users/', views.user_management, name='backoffice_users'),
    path('users/<int:user_id>/', views.user_detail, name='backoffice_user_detail'),
    
    # Company Management
    path('companies/', views.company_management, name='backoffice_companies'),
    path('companies/<int:company_id>/', views.company_detail, name='backoffice_company_detail'),
    
    # Verification Management
    path('verification/', views.verification_dashboard, name='backoffice_verification'),
    path('verification/users/', views.user_verification, name='backoffice_user_verification'),
    path('verification/users/<int:user_id>/update/', views.update_user_verification, name='backoffice_update_user_verification'),
    path('verification/companies/', views.company_verification, name='backoffice_company_verification'),
    path('verification/companies/<int:company_id>/update/', views.update_company_verification, name='backoffice_update_company_verification'),
    
    # Document Management
    path('documents/', views.document_management, name='backoffice_documents'),
    path('documents/members/', views.member_documents, name='backoffice_member_documents'),
    path('documents/companies/', views.company_documents, name='backoffice_company_documents'),
    path('documents/member/<int:doc_id>/', views.member_document_detail, name='backoffice_member_document_detail'),
    path('documents/company/<int:doc_id>/', views.company_document_detail, name='backoffice_company_document_detail'),
    path('documents/member/<int:doc_id>/review/', views.review_member_document, name='backoffice_review_member_document'),
    path('documents/company/<int:doc_id>/review/', views.review_company_document, name='backoffice_review_company_document'),
]
