from multiprocessing import context
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django import forms
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import models
from .models import Member, Company, INVESTOR_TYPE_CHOICES, FUNDING_SIZE_CHOICES, DEAL_SIZE_CHOICES
from .forms import EmailLoginForm, SignUpForm, CompanyForm, StartupForm, InvestorForm, CorporateForm
import json
import random
from django.views import View

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views import View


def homepage(request):
    """Homepage view with platform overview"""
    return render(request, 'homepage.html')


class CustomLoginView(LoginView):
    """
    Custom login view with email authentication and remember me functionality
    """
    template_name = 'member/login.html'
    form_class = EmailLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to startup matchmaking dashboard after successful login"""
        return '/dashboard/startups/'
    
    def form_valid(self, form):
        """Handle successful form submission"""
        remember_me = form.cleaned_data.get('remember_me', False)
        
        # Set session expiry based on remember me checkbox
        if remember_me:
            # Remember for 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        else:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        
        # Don't show welcome message - let the dashboard handle login success
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        # Add form errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add extra context to template"""
        context = super().get_context_data(**kwargs)
        # Preserve email value if login failed
        if self.request.method == 'POST':
            context['email'] = self.request.POST.get('username', '')
        return context


def custom_logout(request):
    """
    Custom logout view with redirect and success message
    """
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username or 'User'
        auth_logout(request)
        messages.success(request, f'You have been logged out successfully. See you again!')
    else:
        messages.info(request, 'You are already logged out.')
    
    # Redirect to login page after logout
    return redirect('login')


class OnboardingRoleSelectionView(View):
    """First step: Role selection page using Django class-based view"""
    def get(self, request):
        return render(request, 'onboarding/index.html')

    def post(self, request):
        user_role = request.POST.get('user_role')
        if not user_role:
            messages.error(request, 'Please select a role.')
            return render(request, 'onboarding/index.html')
        if user_role not in ['startup', 'investor', 'corporate']:
            messages.error(request, 'Please select a valid role.')
            return render(request, 'onboarding/index.html')
        request.session['selected_role'] = user_role
        # Redirect to user profile step first
        return redirect('onboarding_user_profile')

@login_required
def dashboard(request):
    """Dashboard after successful onboarding"""
    try:
        member = Member.objects.get(user=request.user)
        # Get user's companies
        companies = Company.objects.filter(member=member)
        primary_company = companies.filter(is_primary=True).first()
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found. Please complete onboarding.')
        return redirect('onboarding_role_selection')
    
    context = {
        'member': member,
        'companies': companies,
        'primary_company': primary_company,
    }
    return render(request, 'dashboard.html', context)

def calculate_match_score(startup):
    """
    Calculate a mock match score for a startup based on various factors.
    In a real implementation, this would use ML algorithms and user preferences.
    """
    score = 50  # Base score
    
    # Add points based on various factors
    if startup.current_stage:
        stage_scores = {
            'idea': 60,
            'prototype': 70,
            'validation': 75,
            'early': 80,
            'scaling': 85,
            'profitable': 90
        }
        score += stage_scores.get(startup.current_stage, 0) - 50
    
    # Add points for having a website
    if startup.website:
        score += 10
    
    # Add points for team size (sweet spot for early stage)
    if startup.team_size:
        team_scores = {
            '1': 65,
            '2-5': 85,
            '6-10': 90,
            '11-25': 85,
            '26-50': 80,
            '51-100': 75,
            '100+': 70
        }
        team_score = team_scores.get(startup.team_size, 70)
        score = (score + team_score) // 2
    
    # Add points for innovation types (diversified approach)
    if startup.innovation_types and len(startup.innovation_types) > 0:
        score += min(len(startup.innovation_types) * 5, 20)
    
    # Add points for having support areas defined
    if startup.support_areas and len(startup.support_areas) > 0:
        score += 5
    
    # Add some randomness to make it more realistic
    score += random.randint(-10, 15)
    
    # Ensure score is within bounds
    return max(0, min(100, score))

@login_required
def startup_matchmaking(request):
    """Startup matchmaking view with search and filter functionality"""
    
    # Get search query
    search_query = request.GET.get('q', '').strip()
    
    # Get filter parameters
    filter_stage = request.GET.get('stage', '')
    filter_location = request.GET.getlist('location')
    filter_funding_min = request.GET.get('funding_min', '')
    filter_funding_max = request.GET.get('funding_max', '')
    filter_team_size = request.GET.getlist('team_size')
    filter_technologies = request.GET.getlist('technologies')
    filter_match_score = request.GET.get('match_score', '0')
    
    # Base queryset - get all startup companies
    startups = Company.objects.filter(
        company_type='startup',
        is_active=True
    ).select_related('member__user').order_by('-created_at')
    
    # Apply search filter
    if search_query:
        startups = startups.filter(
            models.Q(company_name__icontains=search_query) |
            models.Q(company_description__icontains=search_query) |
            models.Q(solution_description__icontains=search_query) |
            models.Q(member__user__first_name__icontains=search_query) |
            models.Q(member__user__last_name__icontains=search_query)
        )
    
    # Apply stage filter
    if filter_stage:
        startups = startups.filter(current_stage=filter_stage)
    
    # Apply location filter
    if filter_location:
        startups = startups.filter(primary_location__in=filter_location)
    
    # Apply team size filter
    if filter_team_size:
        startups = startups.filter(team_size__in=filter_team_size)
    
    # Apply funding range filter
    if filter_funding_min or filter_funding_max:
        funding_filters = models.Q()
        if filter_funding_min:
            # Map funding ranges to minimum values for comparison
            funding_range_map = {
                'under_10k': 0,
                '10k_50k': 10000,
                '50k_100k': 50000,
                '100k_500k': 100000,
                '500k_1m': 500000,
                '1m_5m': 1000000,
                '5m_10m': 5000000,
                'over_10m': 10000000,
            }
            min_amount = int(filter_funding_min)
            # Filter startups seeking funding above minimum
            for key, value in funding_range_map.items():
                if value >= min_amount:
                    funding_filters |= models.Q(funding_needed=key)
        startups = startups.filter(funding_filters)
    
    # Apply technology filter (search in innovation_types)
    if filter_technologies:
        tech_filters = models.Q()
        for tech in filter_technologies:
            tech_filters |= models.Q(innovation_types__icontains=tech)
        startups = startups.filter(tech_filters)
    
    # Add mock match scores for demonstration
    startups_with_scores = []
    for startup in startups:
        # Calculate a mock match score based on various factors
        match_score = calculate_match_score(startup)
        
        # Only include if meets minimum match score
        if int(filter_match_score) == 0 or match_score >= int(filter_match_score):
            startup.match_score = match_score
            startups_with_scores.append(startup)
    
    # Sort by match score if filtering by score
    if int(filter_match_score) > 0:
        startups_with_scores.sort(key=lambda x: x.match_score, reverse=True)
    
    # Get filter options for the form
    locations = Company.objects.filter(
        company_type='startup',
        is_active=True,
        primary_location__isnull=False
    ).values_list('primary_location', flat=True).distinct()
    
    stages = Company.objects.filter(
        company_type='startup',
        is_active=True,
        current_stage__isnull=False
    ).values_list('current_stage', flat=True).distinct()
    
    team_sizes = Company.objects.filter(
        company_type='startup',
        is_active=True,
        team_size__isnull=False
    ).values_list('team_size', flat=True).distinct()
    
    context = {
        'startups': startups_with_scores,
        'search_query': search_query,
        'filter_stage': filter_stage,
        'filter_location': filter_location,
        'filter_team_size': filter_team_size,
        'filter_technologies': filter_technologies,
        'filter_match_score': int(filter_match_score),
        'available_locations': sorted(set(locations)),
        'available_stages': sorted(set(stages)),
        'available_team_sizes': sorted(set(team_sizes)),
        'total_startups': len(startups_with_scores),
    }
    return render(request, 'matchmaking/startup_matchmaking.html', context)

def onboarding_investor(request):
    """Investor onboarding page - Organization profile setup"""
    # Check if user has completed profile setup
    try:
        member = Member.objects.get(user=request.user)
        if not member.profile_completed:
            messages.warning(request, 'Please complete your profile first.')
            return redirect('onboarding_user_profile')
    except Member.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('onboarding_role_selection')
    
    # No longer check member user_type since companies can have different types
    # This view creates investor-type companies
    
    if request.method == 'POST':
        try:
            # Handle multiple selections for funding_stage, investment_categories, and market_country_interests
            funding_stages = request.POST.getlist('funding_stage')
            investment_categories = request.POST.getlist('investment_categories')
            market_country_interests = request.POST.getlist('market_country_interests')
            
            # Create new company profile (investor organization)
            company = Company.objects.create(
                member=member,
                company_type='investor',  # Set company type as investor
                company_name=request.POST.get('company_name', ''),
                investor_type=request.POST.get('investor_type', ''),
                website=request.POST.get('website', '') or None,
                founded_year=int(request.POST.get('founded_year')) if request.POST.get('founded_year') else None,
                team_size=request.POST.get('team_size', ''),
                primary_location=request.POST.get('primary_location', ''),
                company_description=request.POST.get('company_description', ''),
                # Investment information
                funding_size=request.POST.get('funding_size', ''),
                average_deal_size=request.POST.get('average_deal_size', ''),
                funding_stages=funding_stages,
                investment_categories=investment_categories,
                market_country_interests=market_country_interests,
                investment_philosophy=request.POST.get('investment_philosophy', ''),
                # Additional information
                additional_info=request.POST.get('additional_info', ''),
                # Set as primary company
                is_primary=True
            )
            
            # Handle company logo upload
            if 'company_logo' in request.FILES:
                company.company_logo = request.FILES['company_logo']
                company.save()
            
            # Update member consent and onboarding status
            member.consent_info = request.POST.get('consent_info') == 'on'
            member.consent_marketplace = request.POST.get('consent_marketplace') == 'on'
            member.onboarding_completed = True
            member.save()
            
            # Clear session
            if 'selected_role' in request.session:
                del request.session['selected_role']
            
            messages.success(request, f'Welcome to SEA-MAP, {company.company_name}! Your investor registration is complete.')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'onboarding/investor_onboarding_complete.html', {'member': member})
    
    context = {
        'member': member,
    }
    return render(request, 'onboarding/investor_onboarding_complete.html', context)

def onboarding_corporate(request):
    """Handle corporate onboarding process"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to complete your onboarding.')
        return redirect('login')
    
    try:
        member = Member.objects.get(user=request.user)
        
        # No longer check member user_type since companies can have different types
        # This view creates corporate-type companies
        
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found. Please contact support.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Extract form data
            company_name = request.POST.get('company_name', '').strip()
            organization_type = request.POST.get('organization_type', '').strip()
            website = request.POST.get('website', '').strip()
            founded_year = request.POST.get('founded_year', '')
            team_size = request.POST.get('team_size', '').strip()
            primary_location = request.POST.get('primary_location', '').strip()
            company_description = request.POST.get('company_description', '').strip()
            
            # Multi-select fields (checkbox arrays)
            industry_expertise = request.POST.getlist('industry_expertise')
            technological_areas = request.POST.getlist('technological_areas') 
            market_country_interests = request.POST.getlist('market_country_interests')
            collaboration_methods = request.POST.getlist('collaboration_methods')
            
            # Step 3 fields
            specific_goals = request.POST.get('specific_goals', '').strip()
            collaborate_startups = request.POST.get('collaborate_startups', '').strip()
            additional_info = request.POST.get('additional_info', '').strip()
            
            # Consent fields
            consent_info = request.POST.get('consent_info') == 'on'
            consent_marketplace = request.POST.get('consent_marketplace') == 'on'
            
            # Basic validation
            if not all([company_name, organization_type, team_size, primary_location]):
                messages.error(request, 'Please fill in all required fields.')
                context = {'member': member}
                return render(request, 'onboarding/corporate_onboarding.html', context)
            
            if not consent_info or not consent_marketplace:
                messages.error(request, 'Please accept both consent agreements.')
                context = {'member': member}
                return render(request, 'onboarding/corporate_onboarding.html', context)
            
            # Convert founded year to integer if provided
            founded_year_int = None
            if founded_year.strip():
                try:
                    founded_year_int = int(founded_year)
                except ValueError:
                    messages.error(request, 'Please enter a valid founded year.')
                    context = {'member': member}
                    return render(request, 'onboarding/corporate_onboarding.html', context)
            
            # Check if company already exists for this member
            company, created = Company.objects.get_or_create(
                member=member,
                company_name=company_name,
                defaults={
                    'company_type': 'corporate',  # Set company type as corporate
                    'website': website,
                    'founded_year': founded_year_int,
                    'team_size': team_size,
                    'primary_location': primary_location,
                    'company_description': company_description,
                    'organization_type': organization_type,
                    'funding_stages': [],  # Corporate doesn't have funding stages like investors
                    'investment_categories': technological_areas,  # Use technological areas as categories
                    'market_country_interests': market_country_interests,
                    'investment_philosophy': specific_goals,  # Use specific goals as philosophy
                    'support_areas': collaboration_methods,  # Use collaboration methods as support areas
                    'additional_info': additional_info,
                    'is_primary': True,
                    'is_active': True
                }
            )
            
            # If company already exists, update it
            if not created:
                company.company_type = 'corporate'  # Ensure company type is set
                company.website = website
                company.founded_year = founded_year_int
                company.team_size = team_size
                company.primary_location = primary_location
                company.company_description = company_description
                company.organization_type = organization_type
                company.investment_categories = technological_areas
                company.market_country_interests = market_country_interests
                company.investment_philosophy = specific_goals
                company.support_areas = collaboration_methods
                company.additional_info = additional_info
            
            # Handle file upload
            if 'company_logo' in request.FILES and request.FILES['company_logo']:
                company.company_logo = request.FILES['company_logo']
            
            company.save()
            
            # Update member consent and onboarding status
            member.consent_info = consent_info
            member.consent_marketplace = consent_marketplace
            member.onboarding_completed = True
            member.save()
            
            messages.success(request, 'Corporate onboarding completed successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred while saving your information: {str(e)}')
            context = {'member': member}
            return render(request, 'onboarding/corporate_onboarding.html', context)
    
    # GET request - show form
    context = {
        'member': member,
    }
    return render(request, 'onboarding/corporate_onboarding.html', context)

def signup(request):
    if request.method == 'POST':
        print(f"POST data received: {request.POST}")  # Debug print
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Specify the backend when logging in after signup
                login(request, user, backend='member.backends.EmailBackend')
                messages.success(request, f'Account created successfully for {user.get_full_name()}!')
                # Redirect to role selection instead of dashboard
                return redirect('onboarding_role_selection')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Add form errors to messages for debugging
            print(f"Form errors: {form.errors}")  # Debug print
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    return render(request, 'member/signup.html', {'form': form})



def calculate_investor_match_score(investor):
    """
    Calculate a mock match score for an investor based on various factors.
    In a real implementation, this would use ML algorithms and user preferences.
    """
    score = 60  # Base score
    
    # Add points based on investor type
    if investor.investor_type:
        type_scores = {
            'angel': 75,
            'vc': 85,
            'pe': 80,
            'corporate': 70,
            'grant': 90,
            'accelerator': 85
        }
        score += type_scores.get(investor.investor_type, 0) - 60
    
    # Add points for having clear funding stages
    if investor.funding_stages and len(investor.funding_stages) > 0:
        score += min(len(investor.funding_stages) * 8, 25)
    
    # Add points for having investment categories
    if investor.investment_categories and len(investor.investment_categories) > 0:
        score += min(len(investor.investment_categories) * 5, 20)
    
    # Add points for having clear funding size
    if investor.funding_size:
        score += 15
    
    # Add points for having website and description
    if investor.website:
        score += 8
    if investor.company_description:
        score += 7
    
    # Add some randomness to make it more realistic
    import random
    score += random.randint(-8, 12)
    
    # Ensure score is within bounds
    return max(0, min(100, score))

@login_required
def investor_matchmaking(request):
    """Investor matchmaking view with search and filter functionality"""
    
    # Get search query
    search_query = request.GET.get('q', '').strip()
    
    # Get filter parameters
    filter_investor_type = request.GET.getlist('investor_type')
    filter_location = request.GET.getlist('primary_location')
    filter_funding_size = request.GET.getlist('funding_size')
    filter_preferred_stages = request.GET.getlist('preferred_stages')
    filter_investment_categories = request.GET.getlist('investment_categories')
    filter_match_score = request.GET.get('match_score', '0')
    
    # Base queryset - get all investor companies
    investors = Company.objects.filter(
        company_type='investor',
        is_active=True
    ).select_related('member__user').order_by('-created_at')
    
    # Apply search filter
    if search_query:
        investors = investors.filter(
            models.Q(company_name__icontains=search_query) |
            models.Q(company_description__icontains=search_query) |
            models.Q(investment_philosophy__icontains=search_query) |
            models.Q(member__user__first_name__icontains=search_query) |
            models.Q(member__user__last_name__icontains=search_query)
        )
    
    # Apply investor type filter
    if filter_investor_type:
        investors = investors.filter(investor_type__in=filter_investor_type)
    
    # Apply location filter
    if filter_location:
        investors = investors.filter(primary_location__in=filter_location)
    
    # Apply funding size filter
    if filter_funding_size:
        investors = investors.filter(funding_size__in=filter_funding_size)
    
    # Apply preferred stages filter
    if filter_preferred_stages:
        stage_filters = models.Q()
        for stage in filter_preferred_stages:
            stage_filters |= models.Q(funding_stages__icontains=stage)
        investors = investors.filter(stage_filters)
    
    # Apply investment categories filter
    if filter_investment_categories:
        category_filters = models.Q()
        for category in filter_investment_categories:
            category_filters |= models.Q(investment_categories__icontains=category)
        investors = investors.filter(category_filters)
    
    # Add mock match scores and filter by minimum match score
    investors_with_scores = []
    for investor in investors:
        # Calculate a mock match score based on various factors
        match_score = calculate_investor_match_score(investor)
        
        # Only include if meets minimum match score
        if int(filter_match_score) == 0 or match_score >= int(filter_match_score):
            investor.match_score = match_score
            # Add preferred_stages and investment_categories as lists for template compatibility
            if investor.funding_stages:
                investor.preferred_stages = investor.funding_stages
            else:
                investor.preferred_stages = []
                
            investors_with_scores.append(investor)
    
    # Sort by match score if filtering by score
    if int(filter_match_score) > 0:
        investors_with_scores.sort(key=lambda x: x.match_score, reverse=True)
    
    # Get filter options for the form
    available_investor_types = Company.objects.filter(
        company_type='investor',
        is_active=True,
        investor_type__isnull=False
    ).values_list('investor_type', flat=True).distinct()
    
    available_locations = Company.objects.filter(
        company_type='investor',
        is_active=True,
        primary_location__isnull=False
    ).values_list('primary_location', flat=True).distinct()
    
    available_funding_sizes = Company.objects.filter(
        company_type='investor',
        is_active=True,
        funding_size__isnull=False
    ).values_list('funding_size', flat=True).distinct()
    
    context = {
        'investors': investors_with_scores,
        'search_query': search_query,
        'filter_investor_type': filter_investor_type,
        'filter_location': filter_location,
        'filter_funding_size': filter_funding_size,
        'filter_preferred_stages': filter_preferred_stages,
        'filter_investment_categories': filter_investment_categories,
        'filter_match_score': int(filter_match_score),
        'available_investor_types': sorted(set(available_investor_types)),
        'available_locations': sorted(set(available_locations)),
        'available_funding_sizes': sorted(set(available_funding_sizes)),
        'total_investors': len(investors_with_scores),
    }
    
    return render(request, 'matchmaking/investor_matchmaking.html', context)

def calculate_corporate_match_score(corporate):
    """
    Calculate a mock match score for a corporate based on various factors.
    In a real implementation, this would use ML algorithms and user preferences.
    """
    score = 65  # Base score
    
    # Add points based on organization type
    if corporate.organization_type:
        type_scores = {
            'enterprise': 80,
            'startup': 85,
            'government': 75,
            'ngo': 70,
            'educational': 90
        }
        score += type_scores.get(corporate.organization_type, 0) - 65
    
    # Add points for having clear funding/deal size
    if corporate.average_deal_size:
        score += 15
    
    # Add points for having innovation types
    if corporate.innovation_types and len(corporate.innovation_types) > 0:
        score += min(len(corporate.innovation_types) * 6, 25)
    
    # Add points for having support areas defined
    if corporate.support_areas and len(corporate.support_areas) > 0:
        score += min(len(corporate.support_areas) * 4, 20)
    
    # Add points for company size (larger companies often have more resources)
    if corporate.team_size:
        team_scores = {
            '1': 50,
            '2-5': 60,
            '6-10': 70,
            '11-25': 75,
            '26-50': 80,
            '51-100': 85,
            '100+': 90
        }
        team_score = team_scores.get(corporate.team_size, 70)
        score = (score + team_score) // 2
    
    # Add points for having website and description
    if corporate.website:
        score += 8
    if corporate.company_description:
        score += 7
    
    # Add some randomness to make it more realistic
    import random
    score += random.randint(-8, 12)
    
    # Ensure score is within bounds
    return max(0, min(100, score))

@login_required
def corporate_matchmaking(request):
    """Corporate matchmaking view with search and filter functionality"""
    
    # Get search query
    search_query = request.GET.get('q', '').strip()
    
    # Get filter parameters
    filter_organization_type = request.GET.getlist('organization_type')
    filter_location = request.GET.getlist('location')
    filter_average_deal_size = request.GET.getlist('average_deal_size')
    filter_team_size = request.GET.getlist('team_size')
    filter_innovation_types = request.GET.getlist('innovation_types')
    filter_match_score = request.GET.get('match_score', '0')
    
    # Base queryset - get all corporate companies
    corporates = Company.objects.filter(
        company_type='corporate',
        is_active=True
    ).select_related('member__user').order_by('-created_at')
    
    # Apply search filter
    if search_query:
        corporates = corporates.filter(
            models.Q(company_name__icontains=search_query) |
            models.Q(company_description__icontains=search_query) |
            models.Q(innovation_types__icontains=search_query) |
            models.Q(member__user__first_name__icontains=search_query) |
            models.Q(member__user__last_name__icontains=search_query)
        )
    
    # Apply organization type filter
    if filter_organization_type:
        corporates = corporates.filter(organization_type__in=filter_organization_type)
    
    # Apply location filter
    if filter_location:
        corporates = corporates.filter(primary_location__in=filter_location)
    
    # Apply team size filter
    if filter_team_size:
        corporates = corporates.filter(team_size__in=filter_team_size)
    
    # Apply average deal size filter
    if filter_average_deal_size:
        corporates = corporates.filter(average_deal_size__in=filter_average_deal_size)
    
    # Apply innovation types filter
    if filter_innovation_types:
        tech_filters = models.Q()
        for tech in filter_innovation_types:
            tech_filters |= models.Q(innovation_types__icontains=tech)
        corporates = corporates.filter(tech_filters)
    
    # Add mock match scores and filter by minimum match score
    corporates_with_scores = []
    for corporate in corporates:
        # Calculate a mock match score based on various factors
        match_score = calculate_corporate_match_score(corporate)
        
        # Only include if meets minimum match score
        if int(filter_match_score) == 0 or match_score >= int(filter_match_score):
            corporate.match_score = match_score
            corporates_with_scores.append(corporate)
    
    # Sort by match score if filtering by score
    if int(filter_match_score) > 0:
        corporates_with_scores.sort(key=lambda x: x.match_score, reverse=True)
    
    # Get filter options for the form
    available_organization_types = Company.objects.filter(
        company_type='corporate',
        is_active=True,
        organization_type__isnull=False
    ).values_list('organization_type', flat=True).distinct()
    
    available_locations = Company.objects.filter(
        company_type='corporate',
        is_active=True,
        primary_location__isnull=False
    ).values_list('primary_location', flat=True).distinct()
    
    available_team_sizes = Company.objects.filter(
        company_type='corporate',
        is_active=True,
        team_size__isnull=False
    ).values_list('team_size', flat=True).distinct()
    
    available_deal_sizes = Company.objects.filter(
        company_type='corporate',
        is_active=True,
        average_deal_size__isnull=False
    ).values_list('average_deal_size', flat=True).distinct()
    
    context = {
        'corporates': corporates_with_scores,
        'search_query': search_query,
        'filter_organization_type': filter_organization_type,
        'filter_location': filter_location,
        'filter_average_deal_size': filter_average_deal_size,
        'filter_team_size': filter_team_size,
        'filter_innovation_types': filter_innovation_types,
        'filter_match_score': int(filter_match_score),
        'available_organization_types': sorted(set(available_organization_types)),
        'available_locations': sorted(set(available_locations)),
        'available_team_sizes': sorted(set(available_team_sizes)),
        'available_deal_sizes': sorted(set(available_deal_sizes)),
        'total_corporates': len(corporates_with_scores),
    }
    
    return render(request, 'matchmaking/corporate_matchmaking.html', context)





def problem(request):
    return render(request, 'resources/problem.html')

def challenge(request):
    return render(request, 'resources/challenge.html')

def challenge_detail(request, challenge_id):
    """Display detailed challenge page"""
    # For now, return the template with static data
    # In the future, you can fetch actual challenge data from database
    context = {
        'challenge_id': challenge_id,
    }
    return render(request, 'resources/challenge_detail.html', context)

def problem_detail(request, problem_id):
    """Display detailed problem statement page"""
    # For now, return the template with static data
    # In the future, you can fetch actual problem data from database
    context = {
        'problem_id': problem_id,
    }
    return render(request, 'resources/problem_detail.html', context)

def accelerator_landing(request):
    return render(request, 'accelerator_landing.html')


def startup_profile(request, startup_id):
    """Display detailed startup profile page"""
    # Fetch the actual startup from the database
    startup = get_object_or_404(Company, pk=startup_id, company_type='startup', is_active=True)
    
    # Calculate match score based on actual data
    match_score = calculate_match_score(startup)
    
    # Helper function to get human-readable display values
    def get_display_value(field_value, choices_dict=None):
        if choices_dict and field_value:
            return choices_dict.get(field_value, field_value)
        return field_value or ''
    
    # Innovation types display mapping
    innovation_types_display = []
    if startup.innovation_types:
        innovation_mapping = {
            'eliminate_redesign': 'Eliminate & Redesign Packaging',
            'refill_reuse': 'Refill & Reuse Solutions',
            'collection_sorting': 'Collection & Sorting Technologies',
            'advanced_recycling': 'Advanced Recycling & Upcycling',
            'bioplastics': 'Bioplastics & Compostable Materials',
            'waste_management': 'Waste Management Infrastructure',
            'data_monitoring': 'Data, Monitoring & Traceability',
            'other': 'Other Innovation',
        }
        innovation_types_display = [innovation_mapping.get(cat, cat) for cat in startup.innovation_types]
    
    # Support areas display mapping
    support_areas_display = []
    if startup.support_areas:
        support_mapping = {
            'funding': 'Funding & Investment',
            'mentorship': 'Mentorship & Advisory',
            'technical': 'Technical Support',
            'market_access': 'Market Access',
            'partnership': 'Strategic Partnerships',
            'research': 'Research & Development',
            'pilot_programs': 'Pilot Programs',
            'other': 'Other Support',
        }
        support_areas_display = [support_mapping.get(area, area) for area in startup.support_areas]

    # Map database fields to template variables
    startup_data = {
        # Basic Company Information
        'id': startup.id,
        'company_name': startup.company_name,
        'description': startup.company_description or '',
        'short_description': startup.solution_description or startup.company_description[:120] + '...' if startup.company_description and len(startup.company_description) > 120 else startup.company_description or '',
        'detailed_description': startup.company_description or '',
        'website': startup.website or '',
        'linkedin_url': getattr(startup.member.user, 'linkedin_url', ''),
        'logo': startup.company_logo if startup.company_logo else None,
        
        # Header Information
        'match_percentage': match_score,
        'headquarters_location': startup.primary_location or '',
        'founding_year': startup.founded_year or '',
        'team_size': startup.team_size or '',
        'development_stage': startup.current_stage or '',
        'current_stage': startup.current_stage or '',
        
        # Industry & Solution Categories  
        'primary_sectors': innovation_types_display or ['Technology'],
        'solution_categories': innovation_types_display or ['Innovation Solutions'],
        'innovation_types': innovation_types_display or [],
        
        # Funding Information
        'funding_goal': startup.funding_needed or '',
        'funding_needed': startup.funding_needed or '',
        'funding_raised': '',  # Could be added as model field
        'funding_progress': 0,  # Could be calculated based on funding data
        'development_progress': 75 if startup.current_stage else 50,  # Default based on stage
        
        # Problem & Solution
        'problem_statement': startup.solution_description or startup.company_description or '',
        'innovation_description': startup.solution_description or '',
        'solution_description': startup.solution_description or '',
        'innovation_stage_description': f"Currently in {startup.current_stage} stage" if startup.current_stage else '',
        
        # Technology & Innovation
        'technology_stack': innovation_types_display or ['Technology Solutions'],
        'core_technologies': innovation_types_display or [],
        'intellectual_property': [],  # Could be added as model field
        
        # Market & Traction
        'target_markets': startup.market_country_interests or [],
        'market_country_interests': startup.market_country_interests or [],
        'customer_segments': support_areas_display or [],
        'customers_count': '',  # Could be added as model field
        'revenue_growth': '',  # Could be added as model field
        'annual_revenue': '',  # Could be added as model field
        'market_opportunity_description': startup.investment_philosophy or '',
        
        # Financing Details
        'use_of_funds': startup.additional_info or 'Funding will be used for product development and market expansion.',
        'financial_projections': '',  # Could be added as model field
        'funding_history': [],  # Could be added as model field or separate model
        'funding_round': startup.current_stage or '',
        
        # Team Information
        'founders': [
            {
                'name': startup.member.user.get_full_name() or startup.member.user.username,
                'position': 'Founder',
                'bio': f"Founder of {startup.company_name}",
                'photo': startup.member.profile_picture if hasattr(startup.member, 'profile_picture') else None
            }
        ] if startup.member else [],
        'engineering_team_size': str(max(1, int(startup.team_size or '1') // 3)) if startup.team_size and startup.team_size.isdigit() else '',
        'team_description': f"Our team at {startup.company_name} is dedicated to {', '.join(innovation_types_display[:2])}." if innovation_types_display else f"Dedicated team at {startup.company_name}.",
        'core_expertise': innovation_types_display or ['Technology Innovation'],
        'team_breakdown': {
            'total': int(startup.team_size or '1') if startup.team_size and startup.team_size.isdigit() else 1,
            'engineers': max(1, int(startup.team_size or '1') // 3) if startup.team_size and startup.team_size.isdigit() else 1,
            'business': max(1, int(startup.team_size or '1') // 4) if startup.team_size and startup.team_size.isdigit() else 1,
        },
        'team_experience': f"Combined experience in {', '.join(innovation_types_display[:2])}" if innovation_types_display else 'Experienced team',
        
        # News & Updates - Mock data based on company info
        'recent_news': [
            {
                'title': f'{startup.company_name} Advances in {innovation_types_display[0] if innovation_types_display else "Innovation"}',
                'summary': f'Company makes progress in {innovation_types_display[0].lower() if innovation_types_display else "technology development"}.',
                'date': '2024-12-01',
                'category': 'Development',
                'link': '#',
                'image': None
            },
            {
                'title': f'New Milestones at {startup.company_name}',
                'summary': f'Team expansion and progress in {startup.current_stage} stage.' if startup.current_stage else 'Continued growth and development.',
                'date': '2024-11-15',
                'category': 'Company',
                'link': '#',
                'image': None
            }
        ] if startup.company_name else [],
        
        # Contact & Partnership
        'contact_email': startup.member.user.email if startup.member else '',
        'partnership_message': startup.additional_info or f'We are seeking partnerships and investment opportunities. Contact us to learn more about {startup.company_name}.',
        'partnership_opportunities': support_areas_display or [
            'Strategic Partnerships',
            'Investment Opportunities',
            'Technology Collaboration',
            'Market Development'
        ],
        
        # Additional template fields for compatibility
        'short_summary': startup.solution_description or startup.company_description or '',
        'type_tags': innovation_types_display[:3] if innovation_types_display else ['Startup'],
        'primary_location': startup.primary_location or '',
        'business_model': startup.organization_type or 'B2B',
        'headquarters': startup.primary_location or '',
        'deployment_sites': f"{len(startup.market_country_interests)} countries" if startup.market_country_interests else '',
        'coverage_area': ', '.join(startup.market_country_interests[:3]) if startup.market_country_interests else '',
        'founded_display': str(startup.founded_year) if startup.founded_year else '',
        'team_size_display': f"{startup.team_size} members" if startup.team_size else '',
        'industry': ', '.join(innovation_types_display[:2]) if innovation_types_display else 'Technology',
        'stage': startup.current_stage or 'Development',
        'revenue': '',  # Could be added as model field
        'match_score': match_score,
        'innovation_progress': 75 if startup.current_stage else 50,
        'patents_pending': 0,  # Could be added as model field
        'ip_description': '',  # Could be added as model field
        'revenue_type': 'Revenue',  # Could be added as model field
        'customer_count': '',  # Could be added as model field
        'growth_rate': '',  # Could be added as model field
        'growth_period': 'Annual',  # Could be added as model field
        'investment_highlights': [
            {
                'title': 'Innovation Focus',
                'description': f'Specialized in {", ".join(innovation_types_display[:2])}' if innovation_types_display else 'Technology innovation'
            },
            {
                'title': 'Market Opportunity',
                'description': f'Operating in {len(startup.market_country_interests)} markets' if startup.market_country_interests else 'Strong market potential'
            },
            {
                'title': 'Team Strength',
                'description': f'{startup.team_size} team members' if startup.team_size else 'Dedicated team'
            },
            {
                'title': 'Development Stage',
                'description': f'Currently in {startup.current_stage} stage' if startup.current_stage else 'Active development'
            }
        ],
        'awards': [],  # Could be added as model field
        'certifications': [],  # Could be added as model field
    }
    
    return render(request, 'member/startup_profile.html', {'startup': startup_data})

def investor_profile(request, investor_id):
    """Display detailed investor profile page"""
    # Fetch the actual investor from the database
    investor = get_object_or_404(Company, pk=investor_id, company_type='investor', is_active=True)
    
    # Calculate match score based on actual data
    match_score = calculate_investor_match_score(investor)
    
    # Helper function to get human-readable display values
    def get_display_value(field_value, choices_dict=None):
        if choices_dict and field_value:
            return choices_dict.get(field_value, field_value)
        return field_value or ''
    
    # Investment categories display mapping
    investment_categories_display = []
    if investor.investment_categories:
        category_mapping = {
            'eliminate_redesign': 'Eliminate & Redesign Packaging',
            'refill_reuse': 'Refill & Reuse Solutions',
            'collection_sorting': 'Collection & Sorting Technologies',
            'advanced_recycling': 'Advanced Recycling & Upcycling',
            'bioplastics': 'Bioplastics & Compostable Materials',
            'waste_management': 'Waste Management Infrastructure',
            'data_monitoring': 'Data, Monitoring & Traceability',
            'other': 'Other',
        }
        investment_categories_display = [category_mapping.get(cat, cat) for cat in investor.investment_categories]
    
    # Funding stages display mapping
    funding_stages_display = []
    if investor.funding_stages:
        stages_mapping = {
            'pre_seed': 'Pre-Seed',
            'seed': 'Seed',
            'series_a': 'Series A',
            'series_b': 'Series B',
            'series_c': 'Series C',
            'series_d_plus': 'Series D+',
            'growth': 'Growth',
        }
        funding_stages_display = [stages_mapping.get(stage, stage) for stage in investor.funding_stages]
    
    # Map database fields to template variables
    investor_data = {
        # Basic Company Information
        'id': investor.id,
        'company_name': investor.company_name,
        'investor_type': get_display_value(investor.investor_type, dict(INVESTOR_TYPE_CHOICES)),
        'description': investor.company_description or '',
        'short_description': investor.company_description[:120] + '...' if investor.company_description and len(investor.company_description) > 120 else investor.company_description or '',
        'detailed_description': investor.company_description or '',
        'website': investor.website or '',
        'linkedin_url': getattr(investor.member.user, 'linkedin_url', ''),
        'logo': investor.company_logo if investor.company_logo else None,
        
        # Header Information
        'match_percentage': match_score,
        'headquarters_location': investor.primary_location or '',
        'founded_year': investor.founded_year or '',
        'team_size': investor.team_size or '',
        'aum': get_display_value(investor.funding_size, dict(FUNDING_SIZE_CHOICES)) if investor.funding_size else '',
        
        # Investment Categories
        'investment_sectors': investment_categories_display,
        'investment_categories': investment_categories_display,
        'investment_types': funding_stages_display,
        'geographic_focus': investor.market_country_interests or [],
        
        # Investment Information
        'total_fund_size': get_display_value(investor.funding_size, dict(FUNDING_SIZE_CHOICES)) if investor.funding_size else '',
        'funding_size': get_display_value(investor.funding_size, dict(FUNDING_SIZE_CHOICES)) if investor.funding_size else '',
        'average_deal_size': get_display_value(investor.average_deal_size, dict(DEAL_SIZE_CHOICES)) if investor.average_deal_size else '',
        'min_investment': '',  # Not in model - could be calculated or added as field
        'max_investment': '',  # Not in model - could be calculated or added as field
        'preferred_stages': funding_stages_display,
        'investment_timeline': '3-6 months',  # Default - could be added as model field
        'board_participation': 'Active',  # Default - could be added as model field
        'follow_on_strategy': 'Yes',  # Default - could be added as model field
        
        # About Company
        'investment_philosophy': investor.investment_philosophy or '',
        'value_proposition': investor.investment_philosophy or '',  # Using same field for now
        
        # Market Interest
        'sector_focus': [
            {
                'name': cat,
                'percentage': 100 // len(investment_categories_display) if investment_categories_display else 0,
                'description': cat
            } for cat in investment_categories_display[:5]  # Limit to 5 for display
        ],
        'target_markets': investor.market_country_interests or [],
        'market_opportunity_focus': investor.investment_philosophy or '',
        
        # Portfolio Information - Mock data for now (could be implemented with a Portfolio model)
        'portfolio_companies': [
            {
                'name': f"Portfolio Company {i+1}",
                'sector': cat if i < len(investment_categories_display) else 'Technology',
                'stage': funding_stages_display[i % len(funding_stages_display)] if funding_stages_display else 'Series A',
                'description': f"Description for portfolio company {i+1}",
                'logo': None,
                'status': 'Active' if i % 3 != 0 else 'Exited',
                'investment_year': str(2020 + i)
            } for i, cat in enumerate(investment_categories_display[:6])  # Show up to 6 companies
        ] if investment_categories_display else [],
        'total_investments': len(investment_categories_display) * 5 if investment_categories_display else 0,
        'active_portfolio': len(investment_categories_display) * 3 if investment_categories_display else 0,
        'successful_exits': len(investment_categories_display) if investment_categories_display else 0,
        'portfolio_valuation': get_display_value(investor.funding_size, dict(FUNDING_SIZE_CHOICES)) if investor.funding_size else '',
        
        # Team Information - Mock data based on available data
        'partners': [
            {
                'name': investor.member.user.get_full_name() or investor.member.user.username,
                'position': 'Partner',
                'bio': f"Partner at {investor.company_name}",
                'photo': investor.member.profile_picture if hasattr(investor.member, 'profile_picture') else None,
                'linkedin': '#'
            }
        ] if investor.member else [],
        'investment_team_size': str(max(1, int(investor.team_size or '1') // 2)) if investor.team_size and investor.team_size.isdigit() else '1',
        'total_team_size': investor.team_size or '',
        'team_description': f"Our team at {investor.company_name} combines industry expertise with investment experience.",
        'advisory_board': [],
        
        # Investment Criteria - Based on investment philosophy
        'investment_criteria': [
            line.strip() for line in (investor.investment_philosophy or '').split('.') 
            if line.strip() and len(line.strip()) > 10
        ][:5] if investor.investment_philosophy else [
            'Strong founding team with relevant experience',
            'Large addressable market opportunity',
            'Scalable business model',
            'Clear path to profitability'
        ],
        'due_diligence_process': 'Our investment process typically involves initial screening, due diligence, and investment committee review.',
        
        # News & Updates - Mock data based on company info
        'recent_news': [
            {
                'title': f'{investor.company_name} Expands Investment Focus',
                'summary': f'Investment firm expands focus to include {", ".join(investment_categories_display[:3])}.',
                'date': '2024-12-01',
                'category': 'Investment',
                'link': '#',
                'image': None
            },
            {
                'title': f'New Partnership Opportunities at {investor.company_name}',
                'summary': f'Seeking partnerships in {", ".join(investor.market_country_interests[:3]) if investor.market_country_interests else "Southeast Asia"}.',
                'date': '2024-11-15',
                'category': 'Partnership',
                'link': '#',
                'image': None
            }
        ] if investor.company_name else [],
        
        # Contact & Partnership
        'contact_email': investor.member.user.email if investor.member else '',
        'partnership_message': investor.additional_info or f'We are actively seeking investment opportunities. Contact us to learn more about partnership with {investor.company_name}.',
        'pitch_requirements': [
            'Executive Summary',
            'Business Plan or Pitch Deck',
            'Financial Projections',
            'Team Background',
            'Product Information'
        ],
        
        # Additional fields for template compatibility
        'company_type': get_display_value(investor.investor_type, dict(INVESTOR_TYPE_CHOICES)),
        'stage': 'Established',
        'industry': 'Investment Management',
        'match_score': match_score,
        'fund_stage': '',
        'investment_focus': ', '.join(funding_stages_display) if funding_stages_display else '',
        'ticket_size': get_display_value(investor.average_deal_size, dict(DEAL_SIZE_CHOICES)) if investor.average_deal_size else '',
        'portfolio_size': '',
        'geographic_reach': f"{len(investor.market_country_interests)} countries" if investor.market_country_interests else ''
    }
    
    return render(request, 'member/investor_profile.html', {'investor': investor_data})

def corporate_profile(request, corporate_id):
    """Display detailed corporate profile page"""
    # Fetch the actual corporate from the database
    corporate = get_object_or_404(Company, pk=corporate_id, company_type='corporate', is_active=True)
    
    # Calculate match score based on actual data
    match_score = calculate_corporate_match_score(corporate)
    
    # Helper function to get human-readable display values
    def get_display_value(field_value, choices_dict=None):
        if choices_dict and field_value:
            return choices_dict.get(field_value, field_value)
        return field_value or ''
    
    # Investment categories display mapping (using same categories as investor for consistency)
    investment_categories_display = []
    if corporate.investment_categories:
        category_mapping = {
            'eliminate_redesign': 'Eliminate & Redesign Packaging',
            'refill_reuse': 'Refill & Reuse Solutions',
            'collection_sorting': 'Collection & Sorting Technologies',
            'advanced_recycling': 'Advanced Recycling & Upcycling',
            'bioplastics': 'Bioplastics & Compostable Materials',
            'waste_management': 'Waste Management Infrastructure',
            'data_monitoring': 'Data, Monitoring & Traceability',
            'other': 'Other',
        }
        investment_categories_display = [category_mapping.get(cat, cat) for cat in corporate.investment_categories]
    
    # Support areas display mapping
    support_areas_display = []
    if corporate.support_areas:
        support_mapping = {
            'funding': 'Funding & Investment',
            'mentorship': 'Mentorship & Advisory',
            'technical': 'Technical Support',
            'market_access': 'Market Access',
            'partnership': 'Strategic Partnerships',
            'research': 'Research & Development',
            'pilot_programs': 'Pilot Programs',
            'other': 'Other Support',
        }
        support_areas_display = [support_mapping.get(area, area) for area in corporate.support_areas]

    # Map database fields to template variables
    corporate_data = {
        # Basic Company Information
        'id': corporate.id,
        'company_name': corporate.company_name,
        'description': corporate.company_description or '',
        'detailed_description': corporate.company_description or '',
        'website': corporate.website or '',
        'linkedin_url': getattr(corporate.member.user, 'linkedin_url', ''),
        'logo': corporate.company_logo if corporate.company_logo else None,
        
        # Header Information
        'match_percentage': match_score,
        'headquarters_location': corporate.primary_location or '',
        'founded_year': str(corporate.founded_year) if corporate.founded_year else '',
        'company_size': f"{corporate.team_size} employees" if corporate.team_size else '',
        'team_size': corporate.team_size or '',
        'organization_type': corporate.organization_type or '',
        'contact_email': corporate.member.user.email if corporate.member else '',
        
        # Financial & Scale Metrics - Enhanced with defaults based on team size
        'annual_revenue': '',  # Could be added as model field later
        'market_cap': '',  # Not in model - could be added as field
        'employee_count': corporate.team_size or '',
        'global_presence': f"{len(corporate.market_country_interests)} countries" if corporate.market_country_interests else '',
        'rd_team_size': str(max(1, int(corporate.team_size or '1') // 10)) + '+' if corporate.team_size and corporate.team_size.isdigit() else '',
        
        # Business Information
        'mission_vision': corporate.investment_philosophy or corporate.company_description or '',
        'business_model': f"{corporate.organization_type} with focus on {', '.join(investment_categories_display[:3])}" if investment_categories_display else corporate.organization_type or '',
        'growth_strategy': corporate.investment_philosophy[:100] + '...' if corporate.investment_philosophy and len(corporate.investment_philosophy) > 100 else corporate.investment_philosophy or '',
        'innovation_focus': ', '.join(investment_categories_display[:3]) if investment_categories_display else '',
        'esg_rating': 'B+',  # Default - could be added as model field
        
        # Organization & Industry
        'business_focus_areas': investment_categories_display or ['Technology Solutions'],
        'industry_expertise': investment_categories_display or ['Technology'],
        
        # Market Interest & Innovation
        'innovation_interest_description': corporate.investment_philosophy or corporate.company_description or 'We actively seek partnerships with innovative companies that align with our strategic focus areas.',
        'innovation_interest_categories': investment_categories_display or ['Technology Solutions'],
        'technology_scouting_areas': support_areas_display or ['Strategic Partnerships'],
        'target_markets': corporate.market_country_interests or [],
        'innovation_timeline': [
            'Q1 2025: Partnership Program Launch',
            'Q2 2025: Technology Integration',
            'Q3 2025: Market Expansion',
            'Q4 2025: Innovation Hub Development'
        ],
        'strategic_market_focus': f"Our strategic focus is on {', '.join(corporate.market_country_interests[:3])} markets" if corporate.market_country_interests else 'Regional market expansion',
        
        # Collaboration & Support
        'collaboration_overview': corporate.investment_philosophy or f'{corporate.company_name} believes in strategic partnerships to drive innovation and create meaningful impact.',
        'active_partnerships': str(len(investment_categories_display) * 5) + '+' if investment_categories_display else '10+',
        'innovation_budget': get_display_value(corporate.average_deal_size, dict(DEAL_SIZE_CHOICES)) if corporate.average_deal_size else '$1M+',
        'collaboration_types': [
            {
                'type': area,
                'description': f'{area} programs and initiatives.'
            } for area in support_areas_display[:4]
        ] if support_areas_display else [
            {
                'type': 'Strategic Partnerships',
                'description': 'Long-term collaboration initiatives.'
            }
        ],
        'collaboration_goals': [
            goal.strip() for goal in (corporate.investment_philosophy or '').split('.') 
            if goal.strip() and len(goal.strip()) > 10
        ][:6] if corporate.investment_philosophy else [
            'Strategic technology partnerships',
            'Innovation ecosystem development',
            'Market expansion support',
            'Technology advancement initiatives'
        ],
        'partnership_success_rate': '90%',  # Default - could be added as model field
        'avg_partnership_duration': '18 months',  # Default - could be added as model field
        'roi_partnerships': '3.5x',  # Default - could be added as model field
        
        # Leadership & Team - Mock data based on available info
        'leadership_team': [
            {
                'name': corporate.member.user.get_full_name() or corporate.member.user.username,
                'position': 'Leadership Team Member',
                'bio': f"Leadership team member at {corporate.company_name}",
                'photo': corporate.member.profile_picture if hasattr(corporate.member, 'profile_picture') else None
            }
        ] if corporate.member else [],
        'innovation_team_description': f"Our team at {corporate.company_name} comprises professionals working on innovative solutions and strategic partnerships.",
        'key_departments': support_areas_display or ['Strategic Partnerships', 'Innovation', 'Business Development'],
        'team_culture_description': f"Innovation-driven culture at {corporate.company_name} that values collaboration and continuous growth.",
        
        # News & Updates - Mock data based on company info
        'recent_news': [
            {
                'title': f'{corporate.company_name} Expands Partnership Programs',
                'summary': f'Company expands focus to include {", ".join(investment_categories_display[:3])} partnerships.' if investment_categories_display else 'Strategic expansion of partnership initiatives.',
                'date': '2024-12-01',
                'category': 'Partnership',
                'link': '#',
                'image': None
            },
            {
                'title': f'New Innovation Initiatives at {corporate.company_name}',
                'summary': f'Launching new programs in {", ".join(corporate.market_country_interests[:3]) if corporate.market_country_interests else "key markets"}.',
                'date': '2024-11-15',
                'category': 'Innovation',
                'link': '#',
                'image': None
            }
        ] if corporate.company_name else [],
        
        # Challenges & Problem Statements - Based on support areas
        'open_challenges': [
            {
                'title': f'{area} Innovation Challenge',
                'description': f'Seeking innovative solutions in {area.lower()} domain.',
                'priority': 'High' if i == 0 else 'Medium',
                'reward': f'${(i+1)*25}K',
                'deadline': f'2025-0{min(i+3, 9)}-15',
                'link': '#'
            } for i, area in enumerate(support_areas_display[:4])
        ] if support_areas_display else [
            {
                'title': 'Strategic Partnership Challenge',
                'description': 'Seeking strategic technology partnerships.',
                'priority': 'High',
                'reward': '$50K',
                'deadline': '2025-03-31',
                'link': '#'
            }
        ],
        
        # Contact & Partnership
        'partnership_message': corporate.additional_info or f'We are actively seeking strategic partnerships with innovative companies. Contact us to learn more about collaboration opportunities with {corporate.company_name}.',
        'collaboration_opportunities': support_areas_display or [
            'Strategic Technology Partnerships',
            'Innovation Programs',
            'Business Development',
            'Market Expansion Support'
        ],
        
        # Additional fields for template compatibility
        'company_type': corporate.organization_type or 'Corporate',
        'stage': 'Established',
        'industry': ', '.join(investment_categories_display[:2]) if investment_categories_display else 'Technology',
        'match_score': match_score,
        'fund_stage': '',
        'investment_focus': ', '.join(investment_categories_display) if investment_categories_display else '',
        'ticket_size': get_display_value(corporate.average_deal_size, dict(DEAL_SIZE_CHOICES)) if corporate.average_deal_size else '',
        'portfolio_size': str(len(investment_categories_display) * 5) if investment_categories_display else '',
        'geographic_reach': f"{len(corporate.market_country_interests)} countries" if corporate.market_country_interests else ''
    }
    
    return render(request, 'member/corporate_profile.html', {'corporate': corporate_data})


def onboarding_role_selection(request):
    return render(request, 'onboarding/index.html')


def onboarding_startup_step3(request):
    """Handle startup onboarding step 3 - file uploads"""
    if request.method == 'POST':
        # Handle file uploads
        uploaded_files = {}
        
        # Company profile
        if 'company_profile' in request.FILES:
            company_profile = request.FILES['company_profile']
            if company_profile.size <= 10 * 1024 * 1024:  # 10MB limit
                file_path = default_storage.save(
                    f'startup_profiles/{request.user.id}/{company_profile.name}',
                    ContentFile(company_profile.read())
                )
                uploaded_files['company_profile'] = file_path
        
        # Pitch deck
        if 'pitch_deck' in request.FILES:
            pitch_deck = request.FILES['pitch_deck']
            if pitch_deck.size <= 15 * 1024 * 1024:  # 15MB limit
                file_path = default_storage.save(
                    f'startup_profiles/{request.user.id}/{pitch_deck.name}',
                    ContentFile(pitch_deck.read())
                )
                uploaded_files['pitch_deck'] = file_path
        
        # Additional documents
        if 'additional_docs' in request.FILES:
            additional_docs = request.FILES.getlist('additional_docs')
            additional_files = []
            for doc in additional_docs:
                if doc.size <= 10 * 1024 * 1024:  # 10MB limit
                    file_path = default_storage.save(
                        f'startup_profiles/{request.user.id}/{doc.name}',
                        ContentFile(doc.read())
                    )
                    additional_files.append(file_path)
            uploaded_files['additional_docs'] = additional_files
        
        # Store file paths in session
        request.session['startup_files'] = uploaded_files
        
        # Redirect to next step
        return redirect('onboarding_startup_step4')
    
    return render(request, 'onboarding/startup_step3.html')





@login_required
def onboarding_user_profile(request):
    """User profile setup step - comes after role selection"""
    # Check if role was selected
    if 'selected_role' not in request.session:
        messages.warning(request, 'Please select your role first.')
        return redirect('onboarding_role_selection')
    
    selected_role = request.session.get('selected_role')
    
    if request.method == 'POST':
        try:
            # Get or create member
            member, created = Member.objects.get_or_create(user=request.user)
            
            # Update user profile information
            if 'profile_picture' in request.FILES:
                member.profile_picture = request.FILES['profile_picture']
            
            member.job_position = request.POST.get('job_position', '')
            member.short_bio = request.POST.get('short_bio', '')
            member.phone_number = request.POST.get('phone_number', '')
            member.linkedin_url = request.POST.get('linkedin_url', '')
            # No longer set user_type on member - will be set on company during onboarding
            member.profile_completed = True  # Mark profile as completed
            
            member.save()
            
            messages.success(request, 'Profile updated successfully!')
            
            # Redirect to role-specific onboarding (company setup)
            if selected_role == 'startup':
                return redirect('onboarding_startup_new')
            elif selected_role == 'investor':
                return redirect('onboarding_investor')
            elif selected_role == 'corporate':
                return redirect('onboarding_corporate')
                
        except Exception as e:
            messages.error(request, f'Error saving profile: {str(e)}')
    
    # Get existing member data if available
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None
    
    context = {
        'selected_role': selected_role,
        'member': member,
    }
    
    return render(request, 'onboarding/user_profile.html', context)

@login_required
def onboarding_startup_new(request):
    """New enhanced startup onboarding page - Company profile setup"""
    # Check if user has completed profile setup
    try:
        member = Member.objects.get(user=request.user)
        if not member.profile_completed:
            messages.warning(request, 'Please complete your profile first.')
            return redirect('onboarding_user_profile')
    except Member.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('onboarding_role_selection')
    
    # No longer check member user_type since companies can have different types
    # This view creates startup-type companies
    
    if request.method == 'POST':
        try:
            # Handle multiple selections for innovation_type and support_areas
            innovation_types = request.POST.getlist('innovation_type')
            support_areas = request.POST.getlist('support_areas')
            
            # Create new company profile
            company = Company.objects.create(
                member=member,
                company_type='startup',  # Set company type as startup
                company_name=request.POST.get('company_name', ''),
                website=request.POST.get('website', '') or None,
                founded_year=int(request.POST.get('founded_year')) if request.POST.get('founded_year') else None,
                team_size=request.POST.get('team_size', ''),
                primary_location=request.POST.get('primary_location', ''),
                company_description=request.POST.get('company_description', ''),
                # Innovation information
                innovation_types=innovation_types,
                solution_description=request.POST.get('solution_description', ''),
                current_stage=request.POST.get('current_stage', ''),
                funding_needed=request.POST.get('funding_needed', ''),
                # Support information
                support_areas=support_areas,
                support_details=request.POST.get('support_details', ''),
                additional_info=request.POST.get('additional_info', ''),
                # Set as primary company
                is_primary=True
            )
            
            # Handle company logo upload
            if 'company_logo' in request.FILES:
                company.company_logo = request.FILES['company_logo']
                company.save()
            
            # Update member consent and onboarding status
            member.consent_info = request.POST.get('consent_info') == 'on'
            member.consent_marketplace = request.POST.get('consent_marketplace') == 'on'
            member.onboarding_completed = True
            member.save()
            
            # Clear session
            if 'selected_role' in request.session:
                del request.session['selected_role']
            
            messages.success(request, f'Welcome to SEA-MAP, {company.company_name}! Your startup registration is complete.')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'onboarding/startup_onboarding_new.html', {'member': member})
    
    context = {
        'member': member,
    }
    return render(request, 'onboarding/startup_onboarding_new.html', context)


# Account Settings Views
@login_required
def account_settings(request):
    """Account settings dashboard"""
    member = get_object_or_404(Member, user=request.user)
    company = Company.objects.filter(member=member).first()
    
    # Get progress data for startup companies
    progress_data = None
    if company and company.company_type == 'startup':
        progress_data = company.get_startup_profile_progress()
    
    context = {
        'member': member,
        'company': company,
        'progress': progress_data,
    }
    return render(request, 'member/account_settings.html', context)


@login_required
def personal_profile_edit(request):
    """Personal profile edit form"""
    member = get_object_or_404(Member, user=request.user)
    
    if request.method == 'POST':
        try:
            # Update User model fields
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save()
            
            # Update Member model fields
            member.phone_number = request.POST.get('phone_number', '').strip()
            member.job_position = request.POST.get('job_position', '').strip()
            member.linkedin_url = request.POST.get('linkedin_url', '').strip()
            member.short_bio = request.POST.get('bio', '').strip()
            member.country = request.POST.get('country', '').strip()
            member.city = request.POST.get('city', '').strip()
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                # Validate file size (max 5MB)
                if profile_picture.size > 5 * 1024 * 1024:
                    messages.error(request, 'Profile picture must be less than 5MB.')
                    return render(request, 'member/personal_profile_edit.html', {'member': member})
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if profile_picture.content_type not in allowed_types:
                    messages.error(request, 'Profile picture must be a JPEG, PNG, or GIF image.')
                    return render(request, 'member/personal_profile_edit.html', {'member': member})
                
                member.profile_picture = profile_picture
            
            member.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('personal_profile_edit')
            
        except Exception as e:
            messages.error(request, f'An error occurred while updating your profile: {str(e)}')
            return render(request, 'member/personal_profile_edit.html', {'member': member})
    
    context = {
        'member': member,
    }
    return render(request, 'member/personal_profile_edit.html', context)


@login_required
def company_profile_edit(request):
    """Universal company profile edit form for all company types"""
    member = get_object_or_404(Member, user=request.user)
    company = Company.objects.filter(member=member).first()
    
    # Determine company type for form selection
    company_type = company.company_type if company else request.GET.get('type', 'startup')
    
    # Select appropriate form based on company type
    if company_type == 'startup':
        form_class = StartupForm
    elif company_type == 'investor':
        form_class = InvestorForm
    elif company_type == 'corporate':
        form_class = CorporateForm
    else:
        form_class = CompanyForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=company)
        
        if form.is_valid():
            company = form.save(commit=False)
            
            # Set company member and type if creating new
            if not company.pk:
                company.member = member
                company.company_type = company_type
                company.is_primary = True
            
            # Handle checkbox fields and special form data
            if company_type == 'startup':
                # Handle customer segments (multiple checkbox)
                customer_segments = request.POST.getlist('customer_segments')
                company.customer_segments = customer_segments
                
                # Handle boolean fields
                company.has_external_funding = request.POST.get('has_external_funding') == 'true'
                company.is_female_led = request.POST.get('is_female_led') == 'true'
                
            elif company_type == 'investor':
                # Handle multiple selections for investors
                company.funding_stages = request.POST.getlist('funding_stages')
                company.investment_categories = request.POST.getlist('investment_categories')
                company.market_country_interests = request.POST.getlist('market_country_interests')
                
            elif company_type == 'corporate':
                # Handle multiple selections for corporates
                company.industry_expertise = request.POST.getlist('industry_expertise')
                company.investment_categories = request.POST.getlist('investment_categories')
                company.market_country_interests = request.POST.getlist('market_country_interests')
                company.support_areas = request.POST.getlist('support_areas')
            
            company.save()
            messages.success(request, 'Your company profile has been updated successfully!')
            return redirect('company_profile_edit')
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # GET request - display form with existing data
        form = form_class(instance=company)
    
    # Prepare choices for template
    from .models import (
        TEAM_SIZE_CHOICES, LOCATION_CHOICES, CURRENT_STAGE_CHOICES,
        FUNDING_NEEDED_CHOICES, INVESTOR_TYPE_CHOICES, FUNDING_SIZE_CHOICES,
        DEAL_SIZE_CHOICES, ORGANIZATION_TYPE_CHOICES
    )
    
    # Customer segments choices for startups
    customer_segments_choices = [
        ('b2b', 'B2B (Business-to-Business)'),
        ('b2c', 'B2C (Business-to-Consumer)'),
        ('b2g', 'B2G (Business-to-Government)'),
        ('sme', 'SMEs (Small & Medium Enterprises)'),
        ('enterprise', 'Enterprise Clients'),
        ('consumers', 'Individual Consumers'),
    ]
    
    # Funding stages choices
    funding_stages_choices = [
        ('pre_seed', 'Pre-Seed'),
        ('seed', 'Seed'),
        ('series_a', 'Series A'),
        ('series_b', 'Series B'),
        ('series_c', 'Series C'),
        ('series_d', 'Series D and Above'),
    ]
    
    # Investment categories choices
    investment_categories_choices = [
        ('eliminate_redesign', 'Eliminate & Redesign Packaging'),
        ('refill_reuse', 'Refill & Reuse Solutions'),
        ('collection_sorting', 'Collection & Sorting Technologies'),
        ('advanced_recycling', 'Advanced Recycling & Upcycling'),
        ('bioplastics', 'Bioplastics & Compostable Materials'),
        ('waste_management', 'Waste Management Infrastructure'),
        ('data_monitoring', 'Data, Monitoring & Traceability'),
        ('other', 'Other'),
    ]
    
    # Industry expertise choices for corporates
    industry_expertise_choices = [
        ('technology', 'Technology'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail & Consumer Goods'),
        ('healthcare', 'Healthcare'),
        ('financial', 'Financial Services'),
        ('energy', 'Energy & Utilities'),
        ('agriculture', 'Agriculture'),
        ('education', 'Education'),
        ('transportation', 'Transportation'),
        ('real_estate', 'Real Estate'),
    ]
    
    # Support areas choices for corporates
    support_areas_choices = [
        ('branding_marketing', 'Branding & Marketing'),
        ('investment_funding', 'Investment & Funding Access'),
        ('manufacturing_supply', 'Manufacturing & Supply Chain'),
        ('market_expansion', 'Market Expansion & Customer Acquisition'),
        ('product_development', 'Product Development & R&D'),
        ('regulatory_compliance', 'Regulatory & Compliance'),
    ]
    
    context = {
        'member': member,
        'company': company,
        'form': form,
        'company_type': company_type,
        'team_size_choices': TEAM_SIZE_CHOICES,
        'location_choices': LOCATION_CHOICES,
        'current_stage_choices': CURRENT_STAGE_CHOICES,
        'funding_needed_choices': FUNDING_NEEDED_CHOICES,
        'investor_type_choices': INVESTOR_TYPE_CHOICES,
        'funding_size_choices': FUNDING_SIZE_CHOICES,
        'deal_size_choices': DEAL_SIZE_CHOICES,
        'organization_type_choices': ORGANIZATION_TYPE_CHOICES,
        'customer_segments_choices': customer_segments_choices,
        'funding_stages_choices': funding_stages_choices,
        'investment_categories_choices': investment_categories_choices,
        'industry_expertise_choices': industry_expertise_choices,
        'support_areas_choices': support_areas_choices,
    }
    
    # Add progress data for startup companies
    if company and company.company_type == 'startup':
        progress_data = company.get_startup_profile_progress()
        context['progress'] = progress_data
    
    return render(request, 'member/universal_company_profile_edit.html', context)


@login_required
def startup_company_profile_edit(request):
    """Startup-specific company profile edit form with tabs"""
    member = get_object_or_404(Member, user=request.user)
    
    # Get or create company profile
    try:
        company = Company.objects.get(member=member, is_primary=True)
    except Company.DoesNotExist:
        company = None
    
    if request.method == 'POST':
        try:
            # Get or create company
            if company:
                # Update existing company
                pass
            else:
                # Create new company
                company = Company.objects.create(
                    member=member,
                    company_type='startup',
                    is_primary=True
                )
            
            # Update basic company information
            company.company_name = request.POST.get('company_name', '').strip()
            company.company_description = request.POST.get('company_description', '').strip()
            company.website = request.POST.get('website', '').strip() or None
            company.founded_year = int(request.POST.get('founded_year')) if request.POST.get('founded_year') else None
            company.primary_location = request.POST.get('primary_location', '').strip()
            company.current_stage = request.POST.get('current_stage', '').strip()
            company.team_size = request.POST.get('team_size', '').strip()
            
            # Startup-specific fields
            # Company Information tab
            company.problem_statement = request.POST.get('problem_statement', '').strip()
            
            # Market & Traction tab
            company.target_markets = request.POST.get('target_markets', '').strip()
            customer_segments = request.POST.getlist('customer_segments')
            company.customer_segments = customer_segments
            company.active_users_count = request.POST.get('active_users_count', '').strip()
            company.paying_customers_count = request.POST.get('paying_customers_count', '').strip()
            company.annual_recurring_revenue = request.POST.get('annual_recurring_revenue', '').strip()
            
            # Financing & Funding tab
            has_external_funding = request.POST.get('has_external_funding')
            company.has_external_funding = has_external_funding == 'true'
            company.funding_history = request.POST.get('funding_history', '').strip()
            company.amount_raised = request.POST.get('amount_raised', '').strip()
            company.funding_needed = request.POST.get('funding_needed', '').strip()
            company.use_of_funds = request.POST.get('use_of_funds', '').strip()
            company.financial_projections = request.POST.get('financial_projections', '').strip()
            
            # Founders and Team tab
            is_female_led = request.POST.get('is_female_led')
            company.is_female_led = is_female_led == 'true'
            company.core_team_size = request.POST.get('core_team_size', '').strip()
            company.team_overview = request.POST.get('team_overview', '').strip()
            company.core_expertise = request.POST.get('core_expertise', '').strip()
            
            # Handle company logo upload
            if 'company_logo' in request.FILES:
                company.company_logo = request.FILES['company_logo']
            
            company.save()
            
            messages.success(request, 'Your startup profile has been updated successfully!')
            return redirect('company_profile_edit')  # Redirect to unified company profile edit
            
        except Exception as e:
            messages.error(request, f'An error occurred while updating your profile: {str(e)}')
    
    context = {
        'member': member,
        'company': company,
    }
    return render(request, 'member/universal_company_profile_edit.html', context)  # Use unified template


@login_required
def document_management(request):
    """Document management page"""
    member = get_object_or_404(Member, user=request.user)
    context = {
        'member': member,
    }
    return render(request, 'member/document_management.html', context)


@login_required
def verification_center(request):
    """Verification center page"""
    member = get_object_or_404(Member, user=request.user)
    context = {
        'member': member,
    }
    return render(request, 'member/verification_center.html', context)


def disclaimer(request):
    """Disclaimer page"""
    return render(request, 'member/disclaimer.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'member/privacy_policy.html')


def terms_and_conditions(request):
    """Terms and Conditions page"""
    return render(request, 'member/terms_and_conditions.html')