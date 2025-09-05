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
]
