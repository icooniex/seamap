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
from .models import Member, Company
from .forms import EmailLoginForm, SignUpForm
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

def accelerator_landing(request):
    return render(request, 'accelerator_landing.html')


def startup_profile(request, startup_id):
    """Display detailed startup profile page"""
    # This is sample data - replace with actual database queries

    # In a real application, you would fetch the startup from the database
    startup = get_object_or_404(Company, pk=startup_id, company_type='startup', is_active=True)
    startup_data = {
        'id': startup.id,
        'company_name': startup.company_name,
        'description': startup.company_description,
        'short_description': startup.solution_description,
        'detailed_description': startup.company_description,
        'website': startup.website,
        'linkedin_url': getattr(startup, 'linkedin_url', ''),
        'logo': startup.company_logo if startup.company_logo else None,
        'match_percentage': calculate_match_score(startup),
        'headquarters_location': startup.primary_location,
        'founding_year': startup.founded_year,
        'team_size': startup.team_size,
        'development_stage': startup.current_stage,
        'primary_sectors': getattr(startup, 'innovation_types', []),
        'solution_categories': getattr(startup, 'solution_categories', []),
        'funding_goal': startup.funding_needed,
        'funding_raised': getattr(startup, 'funding_raised', ''),
        'funding_progress': getattr(startup, 'funding_progress', 0),
        'development_progress': getattr(startup, 'development_progress', 0),
        'problem_statement': getattr(startup, 'problem_statement', ''),
        'technology_stack': getattr(startup, 'technology_stack', []),
        'innovation_description': getattr(startup, 'solution_description', ''),
        'innovation_stage_description': getattr(startup, 'innovation_stage_description', ''),
        'intellectual_property': getattr(startup, 'intellectual_property', []),
        'target_markets': getattr(startup, 'target_markets', []),
        'customer_segments': getattr(startup, 'customer_segments', []),
        'customers_count': getattr(startup, 'customers_count', ''),
        'revenue_growth': getattr(startup, 'revenue_growth', ''),
        'annual_revenue': getattr(startup, 'annual_revenue', ''),
        'market_opportunity_description': getattr(startup, 'market_opportunity_description', ''),
        'use_of_funds': getattr(startup, 'use_of_funds', ''),
        'financial_projections': getattr(startup, 'financial_projections', ''),
        'funding_history': getattr(startup, 'funding_history', []),
        'founders': getattr(startup, 'founders', []),
        'engineering_team_size': getattr(startup, 'engineering_team_size', ''),
        'team_description': getattr(startup, 'team_description', ''),
        'core_expertise': getattr(startup, 'core_expertise', []),
        'recent_news': getattr(startup, 'recent_news', []),
        'contact_email': getattr(startup, 'contact_email', ''),
        'partnership_message': getattr(startup, 'partnership_message', ''),
        'partnership_opportunities': getattr(startup, 'partnership_opportunities', []),
        'short_summary': getattr(startup, 'short_summary', ''),
        'type_tags': getattr(startup, 'type_tags', []),
        'primary_location': startup.primary_location,
        'business_model': getattr(startup, 'business_model', ''),
        'headquarters': getattr(startup, 'headquarters', startup.primary_location),
        'deployment_sites': getattr(startup, 'deployment_sites', ''),
        'coverage_area': getattr(startup, 'coverage_area', ''),
        'founded_display': str(startup.founded_year) if startup.founded_year else '',
        'team_size_display': f"{startup.team_size} members" if startup.team_size else '',
        'industry': getattr(startup, 'industry', ''),
        'stage': startup.current_stage,
        'revenue': getattr(startup, 'annual_revenue', ''),
        'match_score': calculate_match_score(startup),
        'core_technologies': getattr(startup, 'core_technologies', []),
        'current_stage': startup.current_stage,
        'innovation_progress': getattr(startup, 'innovation_progress', 0),
        'patents_pending': getattr(startup, 'patents_pending', 0),
        'ip_description': getattr(startup, 'ip_description', ''),
        'revenue_type': getattr(startup, 'revenue_type', ''),
        'customer_count': getattr(startup, 'customer_count', ''),
        'growth_rate': getattr(startup, 'growth_rate', ''),
        'growth_period': getattr(startup, 'growth_period', ''),
        'funding_needed': startup.funding_needed,
        'funding_round': getattr(startup, 'funding_round', ''),
        'team_breakdown': getattr(startup, 'team_breakdown', {}),
        'team_experience': getattr(startup, 'team_experience', ''),
        'investment_highlights': getattr(startup, 'investment_highlights', []),
        'awards': getattr(startup, 'awards', []),
        'certifications': getattr(startup, 'certifications', []),
    }

    startup_data_temp = {
        # Basic Company Information
        'id': startup_id,
        'company_name': 'AquaTech Solutions',
        'description': 'AI-powered water quality monitoring and plastic pollution detection system for coastal communities and marine conservation efforts.',
        'short_description': 'Revolutionary marine conservation technology using AI and IoT for water quality monitoring.',
        'detailed_description': 'AquaTech Solutions is a pioneering technology company focused on revolutionizing marine conservation through advanced AI-powered monitoring systems. Founded in 2019, we develop comprehensive solutions for water quality assessment and plastic pollution detection in coastal and marine environments. Our mission is to provide actionable environmental data to governments, NGOs, and research institutions, enabling evidence-based decision making for marine conservation efforts across Southeast Asia.',
        'website': 'https://aquatech-solutions.com',
        'linkedin_url': 'https://linkedin.com/company/aquatech-solutions',
        'logo': None,  # File field - would be actual logo URL in production
        
        # Header Information
        'match_percentage': 95,
        'headquarters_location': 'Singapore',
        'founding_year': 2019,
        'team_size': '15',
        'development_stage': 'Series A',
        
        # Industry & Solution Categories
        'primary_sectors': ['Environmental Technology', 'Marine Conservation', 'IoT Solutions'],
        'solution_categories': ['Water Quality Monitoring', 'AI Detection Systems', 'Environmental Analytics', 'Pollution Tracking'],
        
        # Funding Information
        'funding_goal': '$2.5M',
        'funding_raised': '$1.8M',
        'funding_progress': 72,  # Percentage
        'development_progress': 75,  # Percentage for development stage
        
        # Problem & Solution
        'problem_statement': 'Marine ecosystems face unprecedented threats from plastic pollution and water quality degradation, yet current monitoring systems are inadequate, expensive, and provide limited real-time data for effective conservation decision-making.',
        
        # Technology & Innovation
        'technology_stack': ['Python', 'TensorFlow', 'Computer Vision', 'IoT Sensors', 'AWS Cloud', 'React', 'PostgreSQL', 'Docker'],
        'innovation_description': 'Our proprietary platform combines computer vision, IoT sensors, and machine learning algorithms to provide real-time monitoring of water quality parameters and automated detection of plastic debris in marine environments with 95% accuracy.',
        'innovation_stage_description': 'Market validation complete with proven technology deployed across 50+ sites. Ready for rapid scaling across ASEAN markets.',
        'intellectual_property': [
            'AI-Powered Plastic Detection Algorithm (Patent Pending)',
            'Water Quality Sensor Network System (Patent Filed)',
            'Real-time Environmental Data Processing (Proprietary)',
            'Marine Pollution Tracking Database (Trademark)'
        ],
        
        # Market & Traction
        'target_markets': [
            {
                'name': 'Government Environmental Agencies',
                'description': 'National and regional environmental monitoring departments'
            },
            {
                'name': 'NGOs & Research Institutions',
                'description': 'Marine conservation organizations and academic research centers'
            },
            {
                'name': 'Private Sector Partners',
                'description': 'Coastal tourism operators and sustainable fishing industries'
            }
        ],
        'customer_segments': ['Government Agencies', 'Environmental NGOs', 'Research Institutions', 'Tourism Companies', 'Fishing Industry'],
        'customers_count': '25+',
        'revenue_growth': '150%',
        'annual_revenue': '$500K',
        'market_opportunity_description': 'The global water quality monitoring market is projected to reach $4.7 billion by 2025, with the Asia-Pacific region showing the highest growth rate of 8.2% CAGR driven by increasing environmental regulations and sustainability initiatives.',
        
        # Financing Details
        'use_of_funds': '40% R&D expansion and product development, 35% market expansion across ASEAN, 15% team growth and talent acquisition, 10% operational scaling and infrastructure',
        'financial_projections': 'Projecting $2.8M ARR by end of 2025 with 200% revenue growth, expanding to 150+ deployment sites across 10 ASEAN countries, achieving break-even by Q3 2025.',
        'funding_history': [
            {
                'round_type': 'Seed Round',
                'amount': '$350K',
                'year': '2020'
            },
            {
                'round_type': 'Pre-Series A',
                'amount': '$750K', 
                'year': '2022'
            },
            {
                'round_type': 'Government Grants',
                'amount': '$180K',
                'year': '2023'
            }
        ],
        
        # Team Information
        'founders': [
            {
                'name': 'Dr. Marina Chen',
                'position': 'Co-Founder & CEO',
                'bio': 'Ph.D. in Marine Biology from NUS, 10+ years in environmental technology. Former research scientist at National University of Singapore with expertise in marine ecosystem monitoring.',
                'photo': None  # File field
            },
            {
                'name': 'Alex Liu',
                'position': 'Co-Founder & CTO', 
                'bio': 'M.S. Computer Science from MIT, AI/ML specialist with 8+ years experience. Former lead engineer at Google Singapore, expert in computer vision and IoT systems.',
                'photo': None  # File field
            }
        ],
        'engineering_team_size': '8',
        'team_description': 'Multidisciplinary team combining marine science expertise with cutting-edge AI/ML engineering capabilities, backed by experienced business development and operations professionals.',
        'core_expertise': [
            'Marine Biology & Oceanography',
            'Artificial Intelligence & Machine Learning',
            'Computer Vision & Image Processing',
            'IoT Systems & Sensor Networks',
            'Environmental Data Analytics',
            'Sustainable Technology Development'
        ],
        
        # News & Updates
        'recent_news': [
            {
                'title': 'Strategic Partnership with WWF Singapore',
                'summary': 'AquaTech Solutions announces landmark partnership with WWF Singapore to deploy AI-powered monitoring systems across 15 marine protected areas.',
                'date': '2024-12-15',  # Use string format for template
                'category': 'Partnership',
                'link': '#',
                'image': None  # File field
            },
            {
                'title': 'Series A Funding Reaches 70% Milestone',
                'summary': 'Company successfully raises $1.8M of $2.5M Series A target with participation from leading VCs including Wavemaker Partners.',
                'date': '2024-11-28',
                'category': 'Funding',
                'link': '#',
                'image': None
            },
            {
                'title': 'Winner of ASEAN Tech Innovation Award',
                'summary': 'AquaTech Solutions wins prestigious ASEAN Tech Innovation Award for outstanding contribution to environmental technology.',
                'date': '2024-10-12',
                'category': 'Award',
                'link': '#',
                'image': None
            },
            {
                'title': 'Launch of AquaVision 3.0 Platform',
                'summary': 'Next-generation monitoring platform features enhanced AI algorithms with 95% accuracy in plastic detection and real-time analysis.',
                'date': '2024-09-20',
                'category': 'Product',
                'link': '#',
                'image': None
            }
        ],
        
        # Contact & Partnership
        'contact_email': 'partnerships@aquatech.com',
        'partnership_message': 'We are actively seeking strategic partnerships, investment opportunities, and collaborative ventures to accelerate our mission of marine conservation. Join us in creating technology solutions that protect our oceans for future generations.',
        'partnership_opportunities': [
            'Series A Investment & Funding',
            'Strategic Technology Partnerships',
            'Government & NGO Collaborations',
            'Technology Licensing Opportunities',
            'Joint Research & Development',
            'Pilot Project Implementations'
        ],
        
        # Additional template fields for compatibility
        'short_summary': 'AI-powered water quality monitoring and plastic pollution detection system for coastal communities and marine conservation efforts.',
        'type_tags': ['Environmental Tech', 'Monitoring Tools', 'Data Analytics'],
        'primary_location': 'Singapore',
        'business_model': 'B2B/B2G',
        'headquarters': 'Singapore',
        'deployment_sites': '50+',
        'coverage_area': 'Across 6 ASEAN countries',
        'founded_display': '2019',
        'team_size_display': '15 members',
        'industry': 'Environmental Technology',
        'stage': 'Series A',
        'revenue': '$500K ARR',
        'match_score': 95,
        'core_technologies': ['Computer Vision', 'Machine Learning', 'IoT Sensors', 'Cloud Computing', 'Data Analytics'],
        'current_stage': 'Market Validation Complete - Scaling Phase',
        'innovation_progress': 75,
        'patents_pending': 3,
        'ip_description': '3 patents pending in AI-powered detection',
        'revenue_type': 'ARR',
        'customer_count': '25+',
        'growth_rate': '150%',
        'growth_period': 'YoY',
        'funding_needed': '$2.5M',
        'funding_round': 'Series A',
        'team_breakdown': {
            'total': 15,
            'engineers': 8,
            'scientists': 4,
            'business': 3
        },
        'team_experience': 'Combined 30+ years in marine tech and AI',
        'investment_highlights': [
            {
                'title': 'Proven Revenue Model',
                'description': 'Recurring SaaS revenue with 150% YoY growth'
            },
            {
                'title': 'Strong IP Portfolio', 
                'description': '3 patents pending in AI-powered detection'
            },
            {
                'title': 'Experienced Team',
                'description': 'Combined 30+ years in marine tech and AI'
            },
            {
                'title': 'Market Expansion Ready',
                'description': 'Validated technology ready to scale across ASEAN'
            }
        ],
        'awards': [
            'ASEAN Tech Innovation Award 2024',
            'Singapore Environmental Excellence Award 2023',
            'Climate Tech Startup of the Year 2023'
        ],
        'certifications': [
            'ISO 14001 Environmental Management',
            'Singapore Green Finance Certified',
            'ASEAN Sustainability Standards Compliant'
        ]
    }
    
    return render(request, 'member/startup_profile.html', {'startup': startup_data})

def investor_profile(request, investor_id):
    """Display detailed investor profile page"""
    # This is sample data - replace with actual database queries
    investor_data = {
        # Basic Company Information
        'id': investor_id,
        'company_name': 'Southeast Asia Growth Capital',
        'investor_type': 'Venture Capital',
        'description': 'Leading venture capital firm focused on high-growth technology startups across Southeast Asia, with expertise in fintech, healthtech, and sustainability solutions.',
        'short_description': 'Leading VC firm investing in high-growth tech startups across SEA.',
        'website': 'https://seagrowthcapital.com',
        'linkedin_url': 'https://linkedin.com/company/sea-growth-capital',
        'logo': None,  # File field
        
        # Header Information
        'match_percentage': 92,
        'headquarters_location': 'Singapore',
        'founded_year': 2015,
        'team_size': '25',
        'aum': '$500M',  # Assets Under Management
        
        # Investment Categories
        'investment_sectors': ['FinTech', 'HealthTech', 'EdTech', 'Sustainability', 'AI/ML'],
        'investment_types': ['Series A', 'Series B', 'Growth Equity'],
        'geographic_focus': ['Singapore', 'Malaysia', 'Thailand', 'Indonesia', 'Philippines', 'Vietnam'],
        
        # Investment Information
        'total_fund_size': '$500M',
        'average_deal_size': '$2-8M',
        'min_investment': '$1M',
        'max_investment': '$15M',
        'preferred_stages': ['Series A', 'Series B', 'Growth Stage'],
        'investment_timeline': '3-6 months',
        'board_participation': 'Active',
        'follow_on_strategy': 'Yes',
        
        # About Company
        'detailed_description': 'Southeast Asia Growth Capital is a premier venture capital firm dedicated to identifying and nurturing the next generation of technology leaders in Southeast Asia. Founded in 2015, we have built a reputation for backing exceptional entrepreneurs who are solving real problems with innovative technology solutions. Our team combines deep regional expertise with global investment experience, providing portfolio companies with strategic guidance, operational support, and access to our extensive network.',
        'investment_philosophy': 'We believe in backing exceptional entrepreneurs who are building category-defining companies that can scale across the Southeast Asian region. Our investment approach focuses on companies with strong unit economics, clear paths to profitability, and the potential for significant market impact.',
        'value_proposition': 'Beyond capital, we provide hands-on support in areas including strategic planning, business development, talent acquisition, and follow-on funding. Our team has operational experience in building and scaling technology companies.',
        
        # Market Interest
        'sector_focus': [
            {
                'name': 'Financial Technology',
                'percentage': 35,
                'description': 'Digital banking, payments, lending, insurtech'
            },
            {
                'name': 'Healthcare Technology',
                'percentage': 25,
                'description': 'Telemedicine, health data, medical devices'
            },
            {
                'name': 'Education Technology',
                'percentage': 20,
                'description': 'Online learning, workforce development, skills training'
            },
            {
                'name': 'Sustainability',
                'percentage': 15,
                'description': 'Clean energy, waste management, sustainable agriculture'
            },
            {
                'name': 'Enterprise Software',
                'percentage': 5,
                'description': 'B2B SaaS, productivity tools, analytics platforms'
            }
        ],
        'target_markets': ['Singapore', 'Malaysia', 'Thailand', 'Indonesia', 'Philippines', 'Vietnam'],
        'market_opportunity_focus': 'We focus on markets with strong digital adoption, growing middle class, and regulatory support for innovation. Southeast Asia represents one of the fastest-growing digital economies globally.',
        
        # Portfolio Information
        'portfolio_companies': [
            {
                'name': 'PayLink Solutions',
                'sector': 'FinTech',
                'stage': 'Series B',
                'description': 'Digital payment platform for SMEs',
                'logo': None,
                'status': 'Active',
                'investment_year': '2022'
            },
            {
                'name': 'HealthMate',
                'sector': 'HealthTech',
                'stage': 'Series A',
                'description': 'Telemedicine and health monitoring app',
                'logo': None,
                'status': 'Active',
                'investment_year': '2023'
            },
            {
                'name': 'EduFlow',
                'sector': 'EdTech',
                'stage': 'Series A',
                'description': 'Corporate learning and development platform',
                'logo': None,
                'status': 'Active',
                'investment_year': '2023'
            },
            {
                'name': 'GreenEnergy Tech',
                'sector': 'Sustainability',
                'stage': 'Growth',
                'description': 'Solar energy solutions for commercial buildings',
                'logo': None,
                'status': 'Active',
                'investment_year': '2021'
            },
            {
                'name': 'LogiTech Systems',
                'sector': 'Enterprise',
                'stage': 'Series B',
                'description': 'Supply chain optimization software',
                'logo': None,
                'status': 'Exited',
                'investment_year': '2019'
            },
            {
                'name': 'FoodDelivery Pro',
                'sector': 'Marketplace',
                'stage': 'Series A',
                'description': 'B2B food delivery platform',
                'logo': None,
                'status': 'Active',
                'investment_year': '2022'
            }
        ],
        'total_investments': 45,
        'active_portfolio': 32,
        'successful_exits': 8,
        'portfolio_valuation': '$2.8B',
        
        # Team Information
        'partners': [
            {
                'name': 'David Chen',
                'position': 'Managing Partner',
                'bio': 'Former investment banker at Goldman Sachs with 15+ years in Southeast Asian markets. Led Series A-C rounds for 25+ companies.',
                'photo': None,
                'linkedin': '#'
            },
            {
                'name': 'Sarah Lim',
                'position': 'Investment Partner',
                'bio': 'Ex-McKinsey consultant and former startup founder. Specialist in FinTech and digital transformation with deep operational experience.',
                'photo': None,
                'linkedin': '#'
            },
            {
                'name': 'Michael Rodriguez',
                'position': 'Principal',
                'bio': 'Former product manager at Google and Grab. Focuses on early-stage investments in mobility and logistics technology.',
                'photo': None,
                'linkedin': '#'
            }
        ],
        'investment_team_size': '12',
        'total_team_size': '25',
        'team_description': 'Our investment team combines deep sector expertise with operational experience. We have former entrepreneurs, consultants, and industry experts who understand the challenges of building companies in Southeast Asia.',
        'advisory_board': [
            'Former CEO of leading Southeast Asian bank',
            'Founder of successful fintech unicorn',
            'Former government minister of digital economy'
        ],
        
        # Investment Criteria
        'investment_criteria': [
            'Strong founding team with relevant experience',
            'Large addressable market opportunity',
            'Differentiated technology or business model',
            'Clear path to profitability and scale',
            'Regional expansion potential'
        ],
        'due_diligence_process': 'Our investment process typically takes 8-12 weeks from initial meeting to term sheet. We conduct thorough market research, technical due diligence, and reference checks.',
        
        # News & Updates
        'recent_news': [
            {
                'title': 'Southeast Asia Growth Capital Closes $500M Fund III',
                'summary': 'Successfully raised largest fund to date with strong LP support, focusing on Series A and B investments across the region.',
                'date': '2024-11-15',
                'category': 'Funding',
                'link': '#',
                'image': None
            },
            {
                'title': 'Investment in HealthMate Telemedicine Platform',
                'summary': 'Led Series A round of $5M in Malaysian healthtech startup expanding across Southeast Asia.',
                'date': '2024-10-28',
                'category': 'Investment',
                'link': '#',
                'image': None
            },
            {
                'title': 'Portfolio Company PayLink Achieves Profitability',
                'summary': 'Digital payment platform reaches break-even milestone with 500K+ active merchants across 4 countries.',
                'date': '2024-09-20',
                'category': 'Portfolio',
                'link': '#',
                'image': None
            },
            {
                'title': 'Partnership with Singapore FinTech Association',
                'summary': 'Strategic partnership to support early-stage fintech startups through mentorship and funding programs.',
                'date': '2024-08-15',
                'category': 'Partnership',
                'link': '#',
                'image': None
            }
        ],
        
        # Contact & Partnership
        'contact_email': 'investments@seagrowthcapital.com',
        'partnership_message': 'We are actively seeking investment opportunities in high-growth technology startups across Southeast Asia. If you are building something meaningful and looking for a partner who can help you scale, we would love to hear from you.',
        'pitch_requirements': [
            'Executive Summary (1-2 pages)',
            'Business Plan or Pitch Deck',
            'Financial Projections (3 years)',
            'Team Backgrounds and References',
            'Product Demo or Prototype'
        ],
        
        # Additional fields for template compatibility
        'company_type': 'Venture Capital',
        'stage': 'Established',
        'industry': 'Investment Management',
        'match_score': 92,
        'fund_stage': 'Fund III',
        'investment_focus': 'Series A & B Technology Companies',
        'ticket_size': '$2-8M',
        'portfolio_size': '45+ companies',
        'geographic_reach': '6 SEA countries'
    }
    
    return render(request, 'member/investor_profile.html', {'investor': investor_data})

def corporate_profile(request, corporate_id):
    """Display detailed corporate profile page"""
    # This is sample data - replace with actual database queries
    corporate_data = {
        # Basic Company Information
        'id': corporate_id,
        'company_name': 'TechCorp Asia',
        'description': 'Leading multinational technology corporation driving digital transformation across Southeast Asia with focus on sustainable innovation and strategic partnerships.',
        'detailed_description': 'TechCorp Asia is a premier technology corporation with over 25 years of experience in delivering innovative solutions across multiple industries. We specialize in digital transformation, cloud computing, AI/ML, and sustainable technology solutions. Our mission is to empower businesses and communities through cutting-edge technology while maintaining our commitment to environmental sustainability and social responsibility.',
        'website': 'https://techcorp-asia.com',
        'linkedin_url': 'https://linkedin.com/company/techcorp-asia',
        'logo': None,  # File field
        
        # Header Information
        'match_percentage': 88,
        'headquarters_location': 'Singapore',
        'founded_year': '1998',
        'company_size': '15,000+ employees',
        'organization_type': 'Multinational Corporation',
        'contact_email': 'partnerships@techcorp-asia.com',
        
        # Financial & Scale Metrics
        'annual_revenue': '$2.8B',
        'market_cap': '$15B',
        'employee_count': '15,000+',
        'global_presence': '25+',
        'rd_team_size': '1,200+',
        
        # Business Information
        'mission_vision': 'To create technology solutions that drive sustainable growth and positive impact across Southeast Asia, while fostering innovation partnerships that benefit society and the environment.',
        'business_model': 'B2B Technology Solutions and Strategic Partnerships',
        'growth_strategy': 'Digital Transformation & Sustainability',
        'innovation_focus': 'AI/ML, IoT, and Green Technology',
        'esg_rating': 'A+',
        
        # Organization & Industry
        'business_focus_areas': [
            'Digital Transformation',
            'Cloud Computing Solutions',
            'Artificial Intelligence',
            'Sustainable Technology',
            'IoT and Smart Systems',
            'Cybersecurity Solutions'
        ],
        'industry_expertise': [
            'Technology',
            'Finance',
            'Healthcare',
            'Education',
            'Energy',
            'Real Estate'
        ],
        
        # Market Interest & Innovation
        'innovation_interest_description': 'We actively seek partnerships with innovative startups and technology companies that align with our strategic focus areas. Our innovation interests span across emerging technologies that can drive digital transformation and sustainability.',
        'innovation_interest_categories': [
            'Artificial Intelligence & Machine Learning',
            'Internet of Things (IoT)',
            'Blockchain Technology',
            'Green Technology Solutions',
            'Fintech Innovations',
            'Healthcare Technology',
            'Smart City Solutions',
            'Cybersecurity',
            'Cloud Computing',
            'Data Analytics'
        ],
        'technology_scouting_areas': [
            'Computer Vision',
            'Natural Language Processing',
            'Edge Computing',
            'Quantum Computing',
            'Renewable Energy Tech',
            'Carbon Capture Technology',
            'Autonomous Systems',
            'Digital Health Solutions'
        ],
        'target_markets': [
            'Singapore',
            'Malaysia',
            'Thailand',
            'Indonesia',
            'Philippines',
            'Vietnam',
            'Cambodia',
            'Myanmar'
        ],
        'innovation_timeline': [
            'Q1 2025: Launch AI Innovation Lab',
            'Q2 2025: Green Tech Partnership Program',
            'Q3 2025: Southeast Asia Expansion',
            'Q4 2025: Sustainability Innovation Hub'
        ],
        'strategic_market_focus': 'Our strategic focus is on emerging markets in Southeast Asia where digital adoption is accelerating. We prioritize markets with strong regulatory support for innovation and growing demand for sustainable technology solutions.',
        
        # Collaboration & Support
        'collaboration_overview': 'TechCorp Asia believes in the power of strategic partnerships to drive innovation and create meaningful impact. We offer comprehensive collaboration programs designed to accelerate startup growth while advancing our mutual goals in technology advancement and sustainability.',
        'active_partnerships': '45+',
        'innovation_budget': '$120M',
        'collaboration_types': [
            {
                'type': 'Co-Development',
                'description': 'Joint product development initiatives combining our enterprise expertise with startup innovation.'
            },
            {
                'type': 'Financial Support',
                'description': 'Strategic investments and funding support for promising startups aligned with our focus areas.'
            },
            {
                'type': 'Mentorship',
                'description': 'Expert guidance from our senior leadership team and industry specialists.'
            },
            {
                'type': 'Pilot Program',
                'description': 'Opportunity to test and validate solutions within our enterprise environment.'
            }
        ],
        'collaboration_goals': [
            'Accelerate digital transformation initiatives',
            'Develop sustainable technology solutions',
            'Expand market reach across Southeast Asia',
            'Foster innovation ecosystem development',
            'Create positive environmental and social impact',
            'Drive technological advancement in key sectors'
        ],
        'partnership_success_rate': '94%',
        'avg_partnership_duration': '24 months',
        'roi_partnerships': '4.2x',
        
        # Leadership & Team
        'leadership_team': [
            {
                'name': 'James Wong',
                'position': 'Chief Executive Officer',
                'bio': 'Visionary leader with 20+ years in technology industry. Former VP at Microsoft Asia-Pacific, driving strategic growth and innovation initiatives.',
                'photo': None
            },
            {
                'name': 'Dr. Sarah Chen',
                'position': 'Chief Technology Officer',
                'bio': 'Technology pioneer with Ph.D. in Computer Science. Leading AI/ML research and development with 15+ years of experience in enterprise solutions.',
                'photo': None
            },
            {
                'name': 'Michael Rodriguez',
                'position': 'Chief Innovation Officer',
                'bio': 'Innovation strategist focused on emerging technologies and startup partnerships. Former venture capital partner with deep Southeast Asia expertise.',
                'photo': None
            },
            {
                'name': 'Lisa Tan',
                'position': 'VP of Strategic Partnerships',
                'bio': 'Partnership expert driving collaboration initiatives with startups and technology companies across the region.',
                'photo': None
            }
        ],
        'innovation_team_description': 'Our innovation team comprises 200+ engineers, researchers, and strategists working on cutting-edge technology solutions. We maintain dedicated R&D centers in Singapore, Malaysia, and Thailand, focusing on AI/ML, IoT, and sustainable technology development.',
        'key_departments': [
            'Research & Development',
            'Artificial Intelligence Lab',
            'IoT Solutions Center',
            'Sustainability Innovation Hub',
            'Strategic Partnerships',
            'Digital Transformation Services',
            'Cybersecurity Division',
            'Cloud Solutions Team'
        ],
        'team_culture_description': 'Innovation-driven culture that values collaboration, sustainability, and continuous learning. We foster an environment where diverse teams work together to solve complex challenges.',
        
        # News & Updates
        'recent_news': [
            {
                'title': 'TechCorp Asia Launches $50M Sustainability Innovation Fund',
                'summary': 'New fund dedicated to supporting startups developing green technology solutions across Southeast Asia.',
                'date': '2024-12-10',
                'category': 'Investment',
                'link': '#',
                'image': None
            },
            {
                'title': 'Strategic Partnership with Singapore Green Finance Centre',
                'summary': 'Collaboration to accelerate development of sustainable fintech solutions in the region.',
                'date': '2024-11-25',
                'category': 'Partnership',
                'link': '#',
                'image': None
            },
            {
                'title': 'AI Innovation Lab Opens in Kuala Lumpur',
                'summary': 'State-of-the-art facility focusing on AI/ML research and development for Southeast Asian markets.',
                'date': '2024-10-15',
                'category': 'Expansion',
                'link': '#',
                'image': None
            },
            {
                'title': 'TechCorp Achieves Carbon Neutral Certification',
                'summary': 'Company reaches milestone in sustainability journey with verified carbon neutral operations.',
                'date': '2024-09-30',
                'category': 'Sustainability',
                'link': '#',
                'image': None
            }
        ],
        
        # Challenges & Problem Statements
        'open_challenges': [
            {
                'title': 'Smart City IoT Solutions Challenge',
                'description': 'Seeking innovative IoT solutions for urban sustainability and smart city development.',
                'priority': 'High',
                'reward': '$100K',
                'deadline': '2025-03-31',
                'link': '#'
            },
            {
                'title': 'AI-Powered Healthcare Innovation',
                'description': 'Developing AI solutions for healthcare accessibility and diagnostic accuracy in rural areas.',
                'priority': 'Medium',
                'reward': '$75K',
                'deadline': '2025-04-15',
                'link': '#'
            },
            {
                'title': 'Green Technology Integration Challenge',
                'description': 'Solutions for integrating renewable energy technologies into existing enterprise infrastructure.',
                'priority': 'High',
                'reward': '$120K',
                'deadline': '2025-05-20',
                'link': '#'
            },
            {
                'title': 'Cybersecurity for SMEs',
                'description': 'Affordable cybersecurity solutions designed specifically for small and medium enterprises.',
                'priority': 'Medium',
                'reward': '$60K',
                'deadline': '2025-06-10',
                'link': '#'
            }
        ],
        
        # Contact & Partnership
        'partnership_message': 'We are actively seeking strategic partnerships with innovative startups and technology companies. Our comprehensive collaboration programs are designed to accelerate mutual growth while creating positive impact across Southeast Asia.',
        'collaboration_opportunities': [
            'Joint Product Development',
            'Strategic Technology Partnerships',
            'Pilot Program Participation',
            'Innovation Challenge Participation',
            'Research & Development Collaboration',
            'Market Expansion Support',
            'Mentorship and Advisory Programs',
            'Investment and Funding Opportunities'
        ],
        
        # Additional template compatibility fields
        'short_description': 'Leading multinational technology corporation driving digital transformation across Southeast Asia.',
        'type_tags': ['Technology', 'Innovation', 'Sustainability'],
        'primary_location': 'Singapore',
        'business_type': 'Multinational Corporation',
        'headquarters': 'Singapore',
        'global_offices': '25+ countries',
        'founded_display': '1998',
        'industry': 'Technology',
        'stage': 'Established Corporation',
        'market_cap_display': '$15B',
        'revenue_display': '$2.8B annually',
        'match_score': 88,
        'core_technologies': [
            'Artificial Intelligence',
            'Cloud Computing',
            'IoT Solutions',
            'Blockchain',
            'Cybersecurity',
            'Data Analytics'
        ],
        'sustainability_initiatives': [
            'Carbon Neutral Operations',
            'Green Technology Development',
            'Sustainable Supply Chain',
            'Environmental Impact Reduction'
        ],
        'innovation_metrics': {
            'rd_investment': '$300M annually',
            'patents_portfolio': '500+',
            'innovation_projects': '150+ active',
            'startup_partnerships': '45+ active'
        },
        'market_leadership': [
            'Top 3 Technology Provider in SEA',
            'Leading Digital Transformation Partner',
            'Premier Sustainability Innovation Hub',
            'Largest Enterprise Cloud Provider'
        ],
        'awards_recognition': [
            'ASEAN Corporate Excellence Award 2024',
            'Singapore Sustainability Leadership Award 2023',
            'Technology Innovation Partner of the Year 2023',
            'Best Employer in Technology Sector 2024'
        ],
        'certifications': [
            'ISO 27001 Information Security',
            'ISO 14001 Environmental Management',
            'Carbon Trust Certification',
            'Singapore Green Finance Certified'
        ]
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
    context = {
        'member': member,
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
    """Company profile edit form"""
    member = get_object_or_404(Member, user=request.user)
    company = None
    if hasattr(member, 'company'):
        company = member.company
    
    # Sample industry expertise choices for template
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
    
    context = {
        'member': member,
        'company': company,
        'industry_expertise_choices': industry_expertise_choices,
    }
    return render(request, 'member/company_profile_edit.html', context)


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