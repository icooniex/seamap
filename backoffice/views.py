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
    redirect_authenticated_user = False  # Changed to False to prevent redirect loop
    
    def dispatch(self, request, *args, **kwargs):
        """Handle request before processing"""
        # If user is already authenticated and is admin, redirect to dashboard
        if request.user.is_authenticated and is_admin_user(request.user):
            return redirect('backoffice:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
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
    
    # Apply status filter - use verification_status instead of documents__status
    if status_filter == 'verified':
        members = members.filter(verification_status='approved')
    elif status_filter == 'pending':
        members = members.filter(verification_status='pending')
    elif status_filter == 'incomplete':
        members = members.filter(
            Q(user__first_name='') | Q(user__last_name='') | 
            Q(phone_number='') | Q(job_position='')
        )
    
    # Add document counts to each member
    members_with_counts = []
    for member in members:
        member.doc_count = member.documents.count()
        # Since documents don't have status, we'll just show document counts
        member.total_docs = member.documents.count()
        member.has_docs = member.documents.count() > 0
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
    return redirect('backoffice:login')


# Verification Management Views

@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def verification_dashboard(request):
    """
    Verification dashboard showing overview of pending verifications
    """
    # Get verification statistics
    pending_users = Member.objects.filter(verification_status='pending').count()
    pending_companies = Company.objects.filter(verification_status='pending').count()
    under_review_users = Member.objects.filter(verification_status='under_review').count()
    under_review_companies = Company.objects.filter(verification_status='under_review').count()
    approved_users = Member.objects.filter(verification_status='approved').count()
    approved_companies = Company.objects.filter(verification_status='approved').count()
    
    # Get recent verification activity
    recent_user_verifications = Member.objects.filter(
        verification_status__in=['approved', 'rejected']
    ).select_related('verified_by', 'user').order_by('-verified_at')[:10]
    
    recent_company_verifications = Company.objects.filter(
        verification_status__in=['approved', 'rejected']
    ).select_related('verified_by', 'member__user').order_by('-verified_at')[:10]
    
    context = {
        'pending_users': pending_users,
        'pending_companies': pending_companies,
        'under_review_users': under_review_users,
        'under_review_companies': under_review_companies,
        'approved_users': approved_users,
        'approved_companies': approved_companies,
        'recent_user_verifications': recent_user_verifications,
        'recent_company_verifications': recent_company_verifications,
        'total_pending': pending_users + pending_companies,
    }
    
    return render(request, 'backoffice/verification_dashboard.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def user_verification(request):
    """
    User verification management
    """
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Build queryset
    users = Member.objects.select_related('user', 'verified_by').all()
    
    # Apply search
    if search_query:
        users = users.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(job_position__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        users = users.filter(verification_status=status_filter)
    
    # Order by verification priority (pending first, then by creation date)
    users = users.order_by('verification_status', '-created_at')
    
    # Paginate results
    paginator = Paginator(users, 25)  # Show 25 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status counts
    status_counts = {
        'all': Member.objects.count(),
        'pending': Member.objects.filter(verification_status='pending').count(),
        'under_review': Member.objects.filter(verification_status='under_review').count(),
        'approved': Member.objects.filter(verification_status='approved').count(),
        'rejected': Member.objects.filter(verification_status='rejected').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'total_users': users.count(),
    }
    
    return render(request, 'backoffice/user_verification.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
@require_http_methods(["POST"])
def update_user_verification(request, user_id):
    """
    Update user verification status
    """
    member = get_object_or_404(Member, id=user_id)
    
    action = request.POST.get('action')
    notes = request.POST.get('notes', '')
    
    if action in ['approve', 'reject', 'under_review']:
        if action == 'approve':
            member.verification_status = 'approved'
            message = f'User {member.user.get_full_name()} has been approved.'
        elif action == 'reject':
            member.verification_status = 'rejected'
            message = f'User {member.user.get_full_name()} has been rejected.'
        elif action == 'under_review':
            member.verification_status = 'under_review'
            message = f'User {member.user.get_full_name()} is now under review.'
        
        # Update verification fields
        member.verified_at = timezone.now()
        member.verified_by = request.user
        member.verification_notes = notes
        member.save()
        
        messages.success(request, message)
    else:
        messages.error(request, 'Invalid action.')
    
    return redirect('backoffice:user_verification')


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def company_verification(request):
    """
    Company verification management
    """
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    # Build queryset
    companies = Company.objects.select_related('member__user', 'verified_by').all()
    
    # Apply search
    if search_query:
        companies = companies.filter(
            Q(company_name__icontains=search_query) |
            Q(member__user__first_name__icontains=search_query) |
            Q(member__user__last_name__icontains=search_query) |
            Q(member__user__email__icontains=search_query) |
            Q(company_description__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        companies = companies.filter(verification_status=status_filter)
    
    # Apply type filter
    if type_filter:
        companies = companies.filter(company_type=type_filter)
    
    # Order by verification priority (pending first, then by creation date)
    companies = companies.order_by('verification_status', '-created_at')
    
    # Paginate results
    paginator = Paginator(companies, 25)  # Show 25 companies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status counts
    status_counts = {
        'all': Company.objects.count(),
        'pending': Company.objects.filter(verification_status='pending').count(),
        'under_review': Company.objects.filter(verification_status='under_review').count(),
        'approved': Company.objects.filter(verification_status='approved').count(),
        'rejected': Company.objects.filter(verification_status='rejected').count(),
    }
    
    # Get type counts
    type_counts = {
        'startup': Company.objects.filter(company_type='startup').count(),
        'investor': Company.objects.filter(company_type='investor').count(),
        'corporate': Company.objects.filter(company_type='corporate').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'status_counts': status_counts,
        'type_counts': type_counts,
        'total_companies': companies.count(),
    }
    
    return render(request, 'backoffice/company_verification.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
@require_http_methods(["POST"])
def update_company_verification(request, company_id):
    """
    Update company verification status
    """
    company = get_object_or_404(Company, id=company_id)
    
    action = request.POST.get('action')
    notes = request.POST.get('notes', '')
    
    if action in ['approve', 'reject', 'under_review']:
        if action == 'approve':
            company.verification_status = 'approved'
            message = f'Company {company.company_name} has been approved.'
        elif action == 'reject':
            company.verification_status = 'rejected'
            message = f'Company {company.company_name} has been rejected.'
        elif action == 'under_review':
            company.verification_status = 'under_review'
            message = f'Company {company.company_name} is now under review.'
        
        # Update verification fields
        company.verified_at = timezone.now()
        company.verified_by = request.user
        company.verification_notes = notes
        company.save()
        
        messages.success(request, message)
    else:
        messages.error(request, 'Invalid action.')
    
    return redirect('backoffice:company_verification')


# Document Management Views
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def document_management(request):
    """
    Document management dashboard
    """
    # Get document statistics
    member_docs = MemberDocument.objects.all()
    company_docs = CompanyDocument.objects.all()
    
    member_doc_stats = {
        'total': member_docs.count(),
        'pending': member_docs.filter(status='pending').count(),
        'approved': member_docs.filter(status='approved').count(),
        'rejected': member_docs.filter(status='rejected').count(),
        'under_review': member_docs.filter(status='under_review').count(),
    }
    
    company_doc_stats = {
        'total': company_docs.count(),
        'pending': company_docs.filter(status='pending').count(),
        'approved': company_docs.filter(status='approved').count(),
        'rejected': company_docs.filter(status='rejected').count(),
        'under_review': company_docs.filter(status='under_review').count(),
    }
    
    # Recent documents (last 10)
    recent_member_docs = member_docs.select_related('member__user').order_by('-uploaded_at')[:10]
    recent_company_docs = company_docs.select_related('company').order_by('-uploaded_at')[:10]
    
    context = {
        'member_doc_stats': member_doc_stats,
        'company_doc_stats': company_doc_stats,
        'recent_member_docs': recent_member_docs,
        'recent_company_docs': recent_company_docs,
    }
    
    return render(request, 'backoffice/document_management.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def member_documents(request):
    """
    Member documents management
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    # Base queryset
    documents = MemberDocument.objects.select_related('member__user', 'reviewed_by')
    
    # Apply filters
    if search_query:
        documents = documents.filter(
            Q(name__icontains=search_query) |
            Q(member__user__first_name__icontains=search_query) |
            Q(member__user__last_name__icontains=search_query) |
            Q(member__user__email__icontains=search_query) |
            Q(document_type__icontains=search_query)
        )
    
    if status_filter:
        documents = documents.filter(status=status_filter)
        
    if type_filter:
        documents = documents.filter(document_type=type_filter)
    
    # Get document types for filter dropdown
    document_types = MemberDocument.objects.exclude(
        document_type=''
    ).values_list('document_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'document_types': document_types,
        'status_choices': MemberDocument._meta.get_field('status').choices,
    }
    
    return render(request, 'backoffice/member_documents.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def company_documents(request):
    """
    Company documents management
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    # Base queryset
    documents = CompanyDocument.objects.select_related('company', 'reviewed_by')
    
    # Apply filters
    if search_query:
        documents = documents.filter(
            Q(name__icontains=search_query) |
            Q(company__company_name__icontains=search_query) |
            Q(company__member__user__email__icontains=search_query) |
            Q(document_type__icontains=search_query)
        )
    
    if status_filter:
        documents = documents.filter(status=status_filter)
        
    if type_filter:
        documents = documents.filter(document_type=type_filter)
    
    # Get document types for filter dropdown
    document_types = CompanyDocument.objects.exclude(
        document_type=''
    ).values_list('document_type', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'document_types': document_types,
        'status_choices': CompanyDocument._meta.get_field('status').choices,
    }
    
    return render(request, 'backoffice/company_documents.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def member_document_detail(request, doc_id):
    """
    Member document detail view
    """
    document = get_object_or_404(MemberDocument, id=doc_id)
    
    context = {
        'document': document,
    }
    
    return render(request, 'backoffice/member_document_detail.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def company_document_detail(request, doc_id):
    """
    Company document detail view
    """
    document = get_object_or_404(CompanyDocument, id=doc_id)
    
    context = {
        'document': document,
    }
    
    return render(request, 'backoffice/company_document_detail.html', context)


@require_http_methods(["POST"])
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def review_member_document(request, doc_id):
    """
    Review member document (AJAX)
    """
    try:
        data = json.loads(request.body)
        status = data.get('status')
        notes = data.get('notes', '')
        
        if status not in ['pending', 'approved', 'rejected', 'under_review']:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        document = get_object_or_404(MemberDocument, id=doc_id)
        document.status = status
        document.reviewed_at = timezone.now()
        document.reviewed_by = request.user
        document.review_notes = notes
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Document {status} successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["POST"])
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def review_company_document(request, doc_id):
    """
    Review company document (AJAX)
    """
    try:
        data = json.loads(request.body)
        status = data.get('status')
        notes = data.get('notes', '')
        
        if status not in ['pending', 'approved', 'rejected', 'under_review']:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        document = get_object_or_404(CompanyDocument, id=doc_id)
        document.status = status
        document.reviewed_at = timezone.now()
        document.reviewed_by = request.user
        document.review_notes = notes
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Document {status} successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})



# Challenge Management Views
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def challenge_management(request):
    """
    Challenge management page
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Base queryset
    challenges = Challenge.objects.select_related('organizer', 'created_by__user')
    
    # Apply filters
    if search_query:
        challenges = challenges.filter(
            Q(title__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(organizer__company_name__icontains=search_query) |
            Q(created_by__user__email__icontains=search_query)
        )
    
    if status_filter:
        challenges = challenges.filter(status=status_filter)
        
    if category_filter:
        challenges = challenges.filter(innovation_category=category_filter)
    
    # Get categories for filter dropdown
    categories = Challenge.objects.exclude(
        innovation_category=''
    ).values_list('innovation_category', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(challenges, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': categories,
        'status_choices': Challenge._meta.get_field('status').choices,
    }
    
    return render(request, 'backoffice/challenge_management.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def challenge_detail(request, challenge_id):
    """
    Challenge detail view
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    context = {
        'challenge': challenge,
    }
    
    return render(request, 'backoffice/challenge_detail.html', context)

# Challenge Management Views
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def challenge_management(request):
    """
    Challenge management page
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Base queryset
    challenges = Challenge.objects.select_related('organizer', 'created_by__user')
    
    # Apply filters
    if search_query:
        challenges = challenges.filter(
            Q(title__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(organizer__company_name__icontains=search_query) |
            Q(created_by__user__email__icontains=search_query)
        )
    
    if status_filter:
        challenges = challenges.filter(status=status_filter)
        
    if category_filter:
        challenges = challenges.filter(innovation_category=category_filter)
    
    # Get categories for filter dropdown
    categories = Challenge.objects.exclude(
        innovation_category=''
    ).values_list('innovation_category', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(challenges, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': categories,
        'status_choices': Challenge._meta.get_field('status').choices,
    }
    
    return render(request, 'backoffice/challenge_management.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def challenge_detail(request, challenge_id):
    """
    Challenge detail view
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    context = {
        'challenge': challenge,
    }
    
    return render(request, 'backoffice/challenge_detail.html', context)


@require_http_methods(["POST"])
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def review_challenge(request, challenge_id):
    """
    Review challenge (AJAX)
    """
    try:
        data = json.loads(request.body)
        status = data.get('status')
        notes = data.get('notes', '')
        
        if status not in ['draft', 'pending', 'approved', 'rejected', 'published']:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        challenge = get_object_or_404(Challenge, id=challenge_id)
        challenge.status = status
        challenge.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Challenge {status} successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["POST"])
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def publish_challenge(request, challenge_id):
    """
    Publish approved challenge
    """
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id)
        
        if challenge.status != 'approved':
            return JsonResponse({
                'success': False, 
                'message': 'Challenge must be approved before publishing'
            })
        
        challenge.status = 'published'
        challenge.published_at = timezone.now()
        challenge.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Challenge published successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# Problem Statement Management Views
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def problem_management(request):
    """
    Problem statement management page
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    problems = ProblemStatement.objects.select_related('company', 'created_by__user')
    
    # Apply filters
    if search_query:
        problems = problems.filter(
            Q(title__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(company__company_name__icontains=search_query) |
            Q(created_by__user__email__icontains=search_query)
        )
    
    if status_filter:
        problems = problems.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': ProblemStatement._meta.get_field('status').choices,
    }
    
    return render(request, 'backoffice/problem_management.html', context)


@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def problem_detail(request, problem_id):
    """
    Problem statement detail view
    """
    problem = get_object_or_404(ProblemStatement, id=problem_id)
    
    context = {
        'problem': problem,
    }
    
    return render(request, 'backoffice/problem_detail.html', context)


@require_http_methods(["POST"])
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def review_problem(request, problem_id):
    """
    Review problem statement (AJAX)
    """
    try:
        data = json.loads(request.body)
        status = data.get('status')
        notes = data.get('notes', '')
        
        if status not in ['draft', 'pending', 'approved', 'rejected', 'published']:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        problem = get_object_or_404(ProblemStatement, id=problem_id)
        problem.status = status
        problem.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Problem statement {status} successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["POST"])
@user_passes_test(is_admin_user, login_url='/backoffice/login/')
def publish_problem(request, problem_id):
    """
    Publish approved problem statement
    """
    try:
        problem = get_object_or_404(ProblemStatement, id=problem_id)
        
        if problem.status != 'approved':
            return JsonResponse({
                'success': False, 
                'message': 'Problem statement must be approved before publishing'
            })
        
        problem.status = 'published'
        problem.published_at = timezone.now()
        problem.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Problem statement published successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
