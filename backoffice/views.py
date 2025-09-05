from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json

from .forms import BackOfficeLoginForm
from member.models import Member, Company, MemberDocument, CompanyDocument, Challenge, ProblemStatement


def is_admin_user(user):
    """Check if user is staff or superuser"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


class BackOfficeLoginView(LoginView):
    """
    Back office login view - only for admin users
    """
    template_name = 'backoffice/login.html'
    form_class = BackOfficeLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to back office dashboard after successful login"""
        return '/backoffice/dashboard/'
    
    def form_valid(self, form):
        """Handle successful form submission"""
        user = form.get_user()
        
        # Double-check user permissions
        if not (user.is_staff or user.is_superuser):
            messages.error(self.request, 'Access denied. Admin privileges required.')
            return self.form_invalid(form)
        
        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def dashboard(request):
    """
    Back office dashboard with overview statistics
    """
    # Get overview statistics
    stats = {
        'total_members': Member.objects.count(),
        'total_companies': Company.objects.count(),
        'pending_verifications': Member.objects.filter(
            documents__status='pending'
        ).distinct().count(),
        'recent_signups': Member.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    # Get recent activities
    recent_members = Member.objects.select_related('user').order_by('-created_at')[:5]
    recent_companies = Company.objects.select_related('member__user').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_members': recent_members,
        'recent_companies': recent_companies,
    }
    
    return render(request, 'backoffice/dashboard.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def user_management(request):
    """
    User profile management page
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    members = Member.objects.select_related('user').prefetch_related('documents')
    
    # Apply search filter
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(job_position__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter == 'verified':
        members = members.filter(documents__status='approved').distinct()
    elif status_filter == 'pending':
        members = members.filter(documents__status='pending').distinct()
    elif status_filter == 'incomplete':
        members = members.filter(
            Q(user__first_name='') | Q(user__last_name='') | 
            Q(phone_number='') | Q(job_position='')
        )
    
    # Add document counts to each member
    members_with_counts = []
    for member in members:
        member.doc_count = member.documents.count()
        member.approved_docs = member.documents.filter(status='approved').count()
        member.pending_docs = member.documents.filter(status='pending').count()
        member.rejected_docs = member.documents.filter(status='rejected').count()
        members_with_counts.append(member)
    
    # Pagination
    paginator = Paginator(members_with_counts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_count': len(members_with_counts),
    }
    
    return render(request, 'backoffice/user_management.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def company_management(request):
    """
    Company profile management page
    """
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    companies = Company.objects.select_related('member__user').prefetch_related('documents')
    
    # Apply search filter
    if search_query:
        companies = companies.filter(
            Q(company_name__icontains=search_query) |
            Q(member__user__first_name__icontains=search_query) |
            Q(member__user__last_name__icontains=search_query) |
            Q(member__user__email__icontains=search_query) |
            Q(primary_location__icontains=search_query)
        )
    
    # Apply type filter
    if type_filter:
        companies = companies.filter(company_type=type_filter)
    
    # Apply status filter
    if status_filter == 'incomplete':
        companies = companies.filter(company_name='')
    
    # Add document counts to each company
    companies_with_counts = []
    for company in companies:
        company.doc_count = company.documents.count()
        # CompanyDocument doesn't have status field, so set these to 0
        company.approved_docs = 0
        company.pending_docs = 0
        companies_with_counts.append(company)
    
    # Pagination
    paginator = Paginator(companies_with_counts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get company type choices for filter dropdown
    company_types = Company.objects.values_list('company_type', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'company_types': company_types,
        'total_count': len(companies_with_counts),
    }
    
    return render(request, 'backoffice/company_management.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def user_detail(request, user_id):
    """
    User detail view for editing and verification
    """
    member = get_object_or_404(Member, id=user_id)
    companies = Company.objects.filter(member=member)
    documents = member.documents.all().order_by('-uploaded_at')
    
    # Calculate profile completeness
    total_fields = 6
    completed_fields = 0
    if member.user.first_name:
        completed_fields += 1
    if member.user.last_name:
        completed_fields += 1
    if member.user.email:
        completed_fields += 1
    if member.phone_number:
        completed_fields += 1
    if member.job_position:
        completed_fields += 1
    if member.short_bio:
        completed_fields += 1
    
    completion_percentage = (completed_fields * 100) // total_fields if total_fields > 0 else 0
    
    context = {
        'member': member,
        'companies': companies,
        'documents': documents,
        'total_fields': total_fields,
        'completed_fields': completed_fields,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'backoffice/user_detail.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def company_detail(request, company_id):
    """
    Company detail view for editing and verification
    """
    company = get_object_or_404(Company, id=company_id)
    documents = company.documents.all().order_by('-uploaded_at')
    
    # Calculate profile completeness based on company type
    total_fields = 0
    completed_fields = 0
    
    if company.company_type == 'startup':
        total_fields = 8
        if company.company_name:
            completed_fields += 1
        if company.company_description:
            completed_fields += 1
        if company.solution_description:
            completed_fields += 1
        if company.current_stage:
            completed_fields += 1
        if company.team_size:
            completed_fields += 1
        if company.primary_location:
            completed_fields += 1
        if company.funding_needed:
            completed_fields += 1
        if company.company_logo:
            completed_fields += 1
    elif company.company_type == 'investor':
        total_fields = 6
        if company.company_name:
            completed_fields += 1
        if company.company_description:
            completed_fields += 1
        if company.investment_philosophy:
            completed_fields += 1
        if company.investor_type:
            completed_fields += 1
        if company.primary_location:
            completed_fields += 1
        if company.average_deal_size:
            completed_fields += 1
    elif company.company_type == 'corporate':
        total_fields = 6
        if company.company_name:
            completed_fields += 1
        if company.company_description:
            completed_fields += 1
        if company.organization_type:
            completed_fields += 1
        if company.primary_location:
            completed_fields += 1
        if company.team_size:
            completed_fields += 1
        if company.industry_expertise:
            completed_fields += 1
    
    completion_percentage = (completed_fields * 100) // total_fields if total_fields > 0 else 0
    
    context = {
        'company': company,
        'documents': documents,
        'total_fields': total_fields,
        'completed_fields': completed_fields,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'backoffice/company_detail.html', context)


def backoffice_logout(request):
    """
    Back office logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('backoffice_login')
