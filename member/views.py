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
from .models import ORGANIZATION_TYPE_CHOICES, Member, Company, MemberDocument, CompanyDocument, INVESTOR_TYPE_CHOICES, FUNDING_SIZE_CHOICES, DEAL_SIZE_CHOICES
from .forms import EmailLoginForm, SignUpForm, CompanyForm, StartupForm, InvestorForm, CorporateForm
import json
import random
from django.views import View
from functools import wraps

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views import View


def onboarding_required(view_func):
    """
    Decorator that checks if user has completed onboarding before accessing views
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            member = Member.objects.get(user=request.user)
            onboarding_redirect = member.get_incomplete_onboarding_redirect()
            
            if onboarding_redirect:
                messages.info(request, 'Please complete your profile setup before accessing this page.')
                return redirect(onboarding_redirect)
                
        except Member.DoesNotExist:
            messages.error(request, 'Profile not found. Please complete registration.')
            return redirect('onboarding_user_profile')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


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
    
    def form_valid(self, form):
        """Override form_valid to handle 2FA check"""
        user = form.get_user()
        
        # Handle remember me functionality first
        remember_me = form.cleaned_data.get('remember_me', False)
        if remember_me:
            # Remember for 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        else:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        
        # Check if user has 2FA enabled
        try:
            member = Member.objects.get(user=user)
            if member.two_factor_enabled:
                # Store user credentials temporarily in session (don't log them in yet)
                self.request.session['pending_2fa_user_id'] = user.id
                self.request.session['pending_2fa_backend'] = form.get_user()._state.db
                
                # Generate and send OTP
                from .models import EmailOTP
                from .email_utils import send_otp_email
                
                # Clean up any existing OTPs for this user
                EmailOTP.objects.filter(user=user).delete()
                
                # Create new OTP
                otp = EmailOTP.objects.create(
                    user=user,
                    session_key=self.request.session.session_key
                )
                
                # Send OTP email
                success = send_otp_email(user, otp.otp_code)
                
                if success:
                    messages.info(self.request, f'A verification code has been sent to {user.email}. Please check your email and enter the code to complete login.')
                    return redirect('verify_2fa_login')
                else:
                    messages.error(self.request, 'Failed to send verification email. Please try again.')
                    return self.form_invalid(form)
                    
        except Member.DoesNotExist:
            pass  # User doesn't have a member profile, proceed with normal login
        
        # Normal login (no 2FA)
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect based on onboarding completion status after successful login"""
        try:
            member = Member.objects.get(user=self.request.user)
            
            # Check if user profile is complete first
            if not member.is_profile_complete():
                messages.success(self.request, 'Welcome back! Please complete your profile setup.')
                return '/onboarding/profile/'
            
            # Check if user has company profile
            if not member.has_company_profile():
                # User has profile but no company
                # Check if they have a stored role in session
                stored_role = self.request.session.get('selected_role')
                if stored_role:
                    # User has selected role before, redirect directly to company onboarding
                    messages.success(self.request, 'Welcome back! Please complete your organization setup.')
                    if stored_role == 'startup':
                        return '/onboarding/startup/new/'
                    elif stored_role == 'investor':
                        return '/onboarding/investor/'
                    elif stored_role == 'corporate':
                        return '/onboarding/corporate/'
                
                # No stored role, go to role selection
                messages.success(self.request, 'Welcome back! Please select your role and set up your organization profile.')
                return '/onboarding/'
            
            # User has completed onboarding, go to dashboard
            messages.success(self.request, 'Welcome back!')
            return '/dashboard/startups/'
            
        except Member.DoesNotExist:
            # No member profile exists, redirect to user profile creation
            messages.info(self.request, 'Welcome! Please complete your profile setup.')
            return '/onboarding/profile/'
    
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
        # Simple role selection page - no redirect loops
        return render(request, 'onboarding/index.html')

    def post(self, request):
        user_role = request.POST.get('user_role')
        if not user_role:
            messages.error(request, 'Please select a role.')
            return render(request, 'onboarding/index.html')
        if user_role not in ['startup', 'investor', 'corporate']:
            messages.error(request, 'Please select a valid role.')
            return render(request, 'onboarding/index.html')
        
        # Store the selected role
        request.session['selected_role'] = user_role
        
        # Always go to user profile first after role selection
        return redirect('onboarding_user_profile')

@onboarding_required
def dashboard(request):
    """Dashboard after successful onboarding"""
    try:
        member = Member.objects.get(user=request.user)
        # Get user's companies
        companies = Company.objects.filter(member=member)
        primary_company = companies.filter(is_primary=True).first()
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found. Please complete onboarding.')
        return redirect('onboarding_user_profile')
    
    context = {
        'member': member,
        'companies': companies,
        'primary_company': primary_company,
    }
    return render(request, 'dashboard.html', context)

# ---------------------------------------------------------------------------
# Match Score — stage mapping (startup current_stage → investor funding_stages vocab)
# ---------------------------------------------------------------------------
_STARTUP_STAGE_TO_INVESTOR_STAGES = {
    'idea':       {'pre_seed'},
    'prototype':  {'pre_seed', 'seed'},
    'validation': {'seed'},
    'early':      {'seed', 'series_a'},
    'scaling':    {'series_a', 'series_b', 'series_c'},
    'profitable': {'series_b', 'series_c', 'series_d_plus'},
}

# Startup funding_needed → compatible investor average_deal_size values
_STARTUP_FUNDING_COMPAT_DEAL = {
    'under_10k':   {'under_100k'},
    '10k_50k':     {'under_100k'},
    '50k_100k':    {'under_100k'},
    '100k_500k':   {'under_100k', '100k_500k'},
    '500k_1m':     {'100k_500k', '500k_1m'},
    '1m_5m':       {'500k_1m', '1m_5m'},
    '5m_10m':      {'1m_5m', '5m_10m'},
    'over_10m':    {'5m_10m', '10m_50m', 'over_50m'},
    'not_seeking': set(),
}


def _score_investor_startup(investor, startup):
    """
    Compute a 0-100 match score between an investor and a startup.
    Works for either viewing direction (investor views startup, or startup views investor).
    """
    score = 0

    # 1. Investment category match (40 pts)
    investor_cats = set(investor.investment_categories or [])
    startup_inno  = set(startup.innovation_types or [])
    if investor_cats and startup_inno:
        intersection = investor_cats & startup_inno
        score += round((len(intersection) / max(len(investor_cats), len(startup_inno))) * 40)
    else:
        score += 20  # neutral — one side has no preference set

    # 2. Stage match (30 pts)
    investor_stages = set(investor.funding_stages or [])
    startup_stage   = startup.current_stage or ''
    mapped_stages   = _STARTUP_STAGE_TO_INVESTOR_STAGES.get(startup_stage, set())
    if investor_stages:
        score += 30 if investor_stages & mapped_stages else 0
    else:
        score += 15  # neutral — investor has no stage preference set

    # 3. Location match (20 pts)
    investor_locations = set(investor.market_country_interests or [])
    startup_location   = startup.primary_location or ''
    if investor_locations:
        score += 20 if startup_location in investor_locations else 0
    else:
        score += 10  # neutral — investor has no location preference set

    # 4. Deal size compatibility (10 pts)
    investor_deal = investor.average_deal_size or ''
    startup_funding = startup.funding_needed or ''
    compatible_deals = _STARTUP_FUNDING_COMPAT_DEAL.get(startup_funding, set())
    if investor_deal:
        score += 10 if investor_deal in compatible_deals else 0
    else:
        score += 5  # neutral — investor has no deal size set

    return max(0, min(100, score))


def _score_corporate_startup(corporate, startup):
    """
    Compute a 0-100 match score between a corporate and a startup.
    Works for either viewing direction.
    """
    score = 0

    # 1. Support areas match (50 pts)
    corp_support    = set(corporate.support_areas or [])
    startup_support = set(startup.support_areas or [])
    if corp_support and startup_support:
        intersection = corp_support & startup_support
        score += round((len(intersection) / max(len(corp_support), len(startup_support))) * 50)
    else:
        score += 25  # neutral

    # 2. Innovation type match (30 pts)
    corp_inno    = set(corporate.innovation_types or [])
    startup_inno = set(startup.innovation_types or [])
    if corp_inno and startup_inno:
        intersection = corp_inno & startup_inno
        score += round((len(intersection) / max(len(corp_inno), len(startup_inno))) * 30)
    else:
        score += 15  # neutral

    # 3. Location match (20 pts)
    if corporate.primary_location and startup.primary_location:
        score += 20 if corporate.primary_location == startup.primary_location else 0
    else:
        score += 10  # neutral

    return max(0, min(100, score))


def calculate_real_match_score(viewer_company, subject_company):
    """
    Return a 0-100 match score between viewer_company and subject_company.
    Returns None when the pair has no applicable algorithm (same type, or
    investor↔corporate which is unsupported).
    """
    if viewer_company is None or subject_company is None:
        return None

    vtype = viewer_company.company_type
    stype = subject_company.company_type

    if vtype == stype:
        return None  # same type — no score shown

    # investor ↔ startup (both directions)
    if vtype == 'investor' and stype == 'startup':
        return _score_investor_startup(viewer_company, subject_company)
    if vtype == 'startup' and stype == 'investor':
        return _score_investor_startup(subject_company, viewer_company)

    # corporate ↔ startup (both directions)
    if vtype == 'corporate' and stype == 'startup':
        return _score_corporate_startup(viewer_company, subject_company)
    if vtype == 'startup' and stype == 'corporate':
        return _score_corporate_startup(subject_company, viewer_company)

    # investor ↔ corporate — unsupported
    return None

@onboarding_required
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
    filter_female_led = request.GET.get('is_female_led', '')
    
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
    
    # Apply female-led filter
    if filter_female_led == 'true':
        startups = startups.filter(member__is_female_led=True)
    
    # Determine current user's company and whether scores apply
    try:
        user_company = request.user.member.companies.filter(is_active=True).first()
    except Exception:
        user_company = None
    # Scores shown only when viewer is NOT a startup (investor or corporate viewing startups)
    show_match_score = user_company is not None and user_company.company_type != 'startup'

    startups_with_scores = []
    for startup in startups:
        if show_match_score:
            match_score = calculate_real_match_score(user_company, startup)
            if match_score is None:
                match_score = 0
        else:
            match_score = None

        # Only apply score filter when scores are shown
        if show_match_score and int(filter_match_score) > 0:
            if match_score < int(filter_match_score):
                continue

        startup.match_score = match_score
        startups_with_scores.append(startup)

    # Sort by match score (descending) when scores are visible and filter active
    if show_match_score and int(filter_match_score) > 0:
        startups_with_scores.sort(key=lambda x: x.match_score or 0, reverse=True)

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
        'filter_female_led': filter_female_led,
        'available_locations': sorted(set(locations)),
        'available_stages': sorted(set(stages)),
        'available_team_sizes': sorted(set(team_sizes)),
        'total_startups': len(startups_with_scores),
        'show_match_score': show_match_score,
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
            
            messages.success(request, 'Thank you for your submission! Your profile has been received and will be reviewed by our team. Once verification is successful, your profile will be published. This process typically takes up to 48 hours. We appreciate your patience.')
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
                    'industry_expertise': industry_expertise,  # Store industry expertise
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
                company.industry_expertise = industry_expertise
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
            
            messages.success(request, 'Thank you for your submission! Your profile has been received and will be reviewed by our team. Once verification is successful, your profile will be published. This process typically takes up to 48 hours. We appreciate your patience.')
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



@onboarding_required
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
    
    # Determine current user's company and whether scores apply
    try:
        user_company = request.user.member.companies.filter(is_active=True).first()
    except Exception:
        user_company = None
    # Scores shown only when viewer is a startup (not an investor viewing investors)
    show_match_score = user_company is not None and user_company.company_type != 'investor'

    investors_with_scores = []
    for investor in investors:
        if show_match_score:
            match_score = calculate_real_match_score(user_company, investor)
            if match_score is None:
                match_score = 0
        else:
            match_score = None

        # Only apply score filter when scores are shown
        if show_match_score and int(filter_match_score) > 0:
            if match_score < int(filter_match_score):
                continue

        investor.match_score = match_score
        investor.preferred_stages = investor.funding_stages or []
        investors_with_scores.append(investor)

    # Sort by match score (descending) when scores are visible and filter active
    if show_match_score and int(filter_match_score) > 0:
        investors_with_scores.sort(key=lambda x: x.match_score or 0, reverse=True)

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
        'show_match_score': show_match_score,
    }

    return render(request, 'matchmaking/investor_matchmaking.html', context)

@onboarding_required
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
    
    # Determine current user's company and whether scores apply
    try:
        user_company = request.user.member.companies.filter(is_active=True).first()
    except Exception:
        user_company = None
    # Scores shown only for startups viewing corporates (investor↔corporate unsupported)
    show_match_score = user_company is not None and user_company.company_type == 'startup'

    corporates_with_scores = []
    for corporate in corporates:
        if show_match_score:
            match_score = calculate_real_match_score(user_company, corporate)
            if match_score is None:
                match_score = 0
        else:
            match_score = None

        # Only apply score filter when scores are shown
        if show_match_score and int(filter_match_score) > 0:
            if match_score < int(filter_match_score):
                continue

        corporate.match_score = match_score
        corporates_with_scores.append(corporate)

    # Sort by match score (descending) when scores are visible and filter active
    if show_match_score and int(filter_match_score) > 0:
        corporates_with_scores.sort(key=lambda x: x.match_score or 0, reverse=True)

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
        'show_match_score': show_match_score,
    }

    return render(request, 'matchmaking/corporate_matchmaking.html', context)




@onboarding_required
def problem(request):
    from .models import ProblemStatement
    from django.db.models import Q
    
    try:
        problems = ProblemStatement.objects.filter(status='published').select_related('company').order_by('-created_at')
        
        # Handle search functionality
        search_query = request.GET.get('q', '').strip()
        if search_query:
            problems = problems.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(company__company_name__icontains=search_query)
            )
        
        # Check if user is a corporate user
        is_corporate_user = False
        if request.user.is_authenticated:
            try:
                is_corporate_user = request.user.member.companies.filter(company_type='corporate').exists()
            except:
                is_corporate_user = False
        
        context = {
            'problems': problems,
            'total_problems': problems.count(),
            'is_corporate_user': is_corporate_user,
            'search_query': search_query,
        }
    except:
        context = {'problems': [], 'total_problems': 0, 'is_corporate_user': False}
    return render(request, 'resources/problem.html', context)

@onboarding_required
def challenge(request):
    from .models import Challenge
    try:
        challenges = Challenge.objects.filter(status='published').order_by('-created_at')
        context = {
            'challenges': challenges,
            'total_challenges': challenges.count(),
        }
    except:
        context = {'challenges': [], 'total_challenges': 0}
    return render(request, 'resources/challenge.html', context)

@onboarding_required
def challenge_detail(request, challenge_id):
    """Display detailed challenge page"""
    # Try to fetch actual challenge data from database
    try:
        from .models import Challenge
        challenge = get_object_or_404(Challenge, pk=challenge_id, status='published')
        
        # Get related challenges (same categories or same organizer, excluding current)
        related_challenges = Challenge.objects.filter(
            status='published'
        ).exclude(pk=challenge_id)
        
        # Try to find challenges with similar categories
        if challenge.categories:
            # If current challenge has categories, find others with similar categories
            related_challenges = related_challenges.filter(
                categories__overlap=challenge.categories
            )[:3]
        else:
            # If no categories, get recent challenges from same organizer or random
            related_challenges = related_challenges.filter(
                organizer=challenge.organizer
            )[:3]
            if not related_challenges.exists():
                related_challenges = Challenge.objects.filter(
                    status='published'
                ).exclude(pk=challenge_id).order_by('-created_at')[:3]
        
        context = {
            'challenge': challenge,
            'challenge_id': challenge_id,
            'related_challenges': related_challenges,
        }
    except:
        # Fallback to static data if model not ready
        context = {
            'challenge_id': challenge_id,
            'related_challenges': [],
        }
    return render(request, 'resources/challenge_detail.html', context)

@onboarding_required
def problem_detail(request, problem_id):
    """Display detailed problem statement page"""
    # Try to fetch actual problem data from database
    try:
        from .models import ProblemStatement
        problem = get_object_or_404(ProblemStatement, pk=problem_id, status='published')
        
        # Prefetch documents to avoid N+1 queries
        problem = ProblemStatement.objects.prefetch_related('documents').get(pk=problem_id, status='published')
        
        # Get related problems (same company, excluding current)
        related_problems = ProblemStatement.objects.filter(
            status='published',
            company=problem.company
        ).exclude(pk=problem_id)[:3]
        
        if not related_problems.exists():
            related_problems = ProblemStatement.objects.filter(
                status='published'
            ).exclude(pk=problem_id).order_by('-created_at')[:3]
        
        context = {
            'problem': problem,
            'problem_id': problem_id,
            'related_problems': related_problems,
        }
    except Exception as e:
        # If problem not found or any other error, try to get it with different status
        try:
            from .models import ProblemStatement
            problem = ProblemStatement.objects.prefetch_related('documents').get(pk=problem_id)
            related_problems = ProblemStatement.objects.filter(
                company=problem.company
            ).exclude(pk=problem_id)[:3] if problem.company else []
            
            context = {
                'problem': problem,
                'problem_id': problem_id,
                'related_problems': related_problems,
            }
        except:
            # Fallback with None problem
            context = {
                'problem': None,
                'problem_id': problem_id,
                'related_problems': [],
            }
    return render(request, 'resources/problem_detail.html', context)


@onboarding_required
def create_challenge(request):
    """Create a new challenge (Corporate users only)"""
    # Check if user is corporate
    try:
        member = request.user.member
        if not member.companies.filter(company_type='corporate').exists():
            messages.error(request, 'Only corporate users can create challenges.')
            return redirect('challenge')
    except Member.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile_completion')
    
    if request.method == 'POST':
        from .models import Challenge
        from django.utils.dateparse import parse_datetime
        
        try:
            # Get basic information
            title = request.POST.get('title', '').strip()
            subtitle = request.POST.get('subtitle', '').strip()
            description = request.POST.get('description', '').strip()
            requirements_content = request.POST.get('requirements_content', '').strip()
            organizer_contact = request.POST.get('organizer_contact', '').strip()
            
            # Get timeline
            application_deadline = request.POST.get('application_deadline')
            if application_deadline:
                application_deadline = parse_datetime(application_deadline)
            else:
                application_deadline = None
            
            # Get categories
            categories = request.POST.getlist('categories')
            
            # Get location & scope
            location = request.POST.get('location', '').strip()
            scope = request.POST.get('scope', '').strip()
            innovation_category = request.POST.get('innovation_category', '').strip()
            
            # Get prize information
            has_prizes = request.POST.get('has_prizes') == 'on'
            main_prize_amount = None
            main_prize_currency = 'USD'
            prizes_content = ''
            
            if has_prizes:
                try:
                    main_prize_amount = float(request.POST.get('main_prize_amount', 0))
                except (ValueError, TypeError):
                    main_prize_amount = None
                main_prize_currency = request.POST.get('main_prize_currency', 'USD')
                prizes_content = request.POST.get('prizes_content', '').strip()
            
            # Validation
            if not title:
                messages.error(request, 'Challenge title is required.')
                return render(request, 'resources/create_challenge.html')
            
            if not description:
                messages.error(request, 'Challenge description is required.')
                return render(request, 'resources/create_challenge.html')
            
            if not requirements_content:
                messages.error(request, 'Requirements content is required.')
                return render(request, 'resources/create_challenge.html')
            
            if not organizer_contact:
                messages.error(request, 'Contact email is required.')
                return render(request, 'resources/create_challenge.html')
            
            if not categories:
                messages.error(request, 'Please select at least one category.')
                return render(request, 'resources/create_challenge.html')
            
            # Create challenge
            challenge = Challenge.objects.create(
                title=title,
                subtitle=subtitle,
                description=description,
                requirements_content=requirements_content,
                organizer_contact=organizer_contact,
                application_deadline=application_deadline,
                categories=categories,
                location=location,
                scope=scope,
                innovation_category=innovation_category,
                has_prizes=has_prizes,
                main_prize_amount=main_prize_amount,
                main_prize_currency=main_prize_currency,
                prizes_content=prizes_content,
                created_by=member,
                organizer=member.companies.filter(company_type='corporate').first(),
                status='pending'
            )
            
            # Handle file uploads
            if 'challenge_brief' in request.FILES:
                challenge.challenge_brief = request.FILES['challenge_brief']
            
            if 'featured_image' in request.FILES:
                challenge.featured_image = request.FILES['featured_image']
            
            challenge.save()
            
            messages.success(request, 'Thank you for submitting your innovation challenge! It will be reviewed by our team and published upon successful verification. This process typically takes up to 48 hours. We appreciate your patience.')
            return redirect('challenge')
            
        except Exception as e:
            messages.error(request, f'Error creating challenge: {str(e)}')
            return render(request, 'resources/create_challenge.html')
    
    return render(request, 'resources/create_challenge.html')


@onboarding_required
def create_problem_statement(request):
    """Create a new problem statement (Corporate users only)"""
    # Check if user is corporate
    try:
        member = request.user.member
        if not member.companies.filter(company_type='corporate').exists():
            messages.error(request, 'Only corporate users can create problem statements.')
            return redirect('problem')
    except Member.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile_completion')
    
    if request.method == 'POST':
        from .models import ProblemStatement
        
        try:
            # Get basic information
            title = request.POST.get('title', '').strip()
            subtitle = request.POST.get('subtitle', '').strip()
            description = request.POST.get('description', '').strip()
            current_challenges = request.POST.get('current_challenges', '').strip()
            contact_email = request.POST.get('contact_email', '').strip()
            
            # Get new form fields
            preferred_asean_countries = request.POST.getlist('preferred_asean_countries')
            innovation_type = request.POST.getlist('innovation_type')
            startup_stage = request.POST.getlist('startup_stage')
            
            # Get solution & technical requirements
            solution_requirements = request.POST.get('solution_requirements', '').strip()
            technical_requirements = request.POST.get('technical_requirements', '').strip()
            
            # Get collaboration details
            timeline = request.POST.get('timeline', '').strip()
            implementation_support = request.POST.get('implementation_support', '').strip()
            
            # Validation - Basic Information
            if not title:
                messages.error(request, 'Problem title is required.')
                return render(request, 'resources/create_problem.html')
            
            if not description:
                messages.error(request, 'Problem description is required.')
                return render(request, 'resources/create_problem.html')
            
            if not current_challenges:
                messages.error(request, 'Current challenges description is required.')
                return render(request, 'resources/create_problem.html')
            
            if not contact_email:
                messages.error(request, 'Contact email is required.')
                return render(request, 'resources/create_problem.html')
            
            if not solution_requirements:
                messages.error(request, 'Solution requirements are required.')
                return render(request, 'resources/create_problem.html')
            
            # Validation - Checkbox fields (at least one required each)
            if not innovation_type:
                messages.error(request, 'Please select at least one Type of Innovation.')
                return render(request, 'resources/create_problem.html')
            
            if not startup_stage:
                messages.error(request, 'Please select at least one Preferred Startup Stage.')
                return render(request, 'resources/create_problem.html')
            
            if not preferred_asean_countries:
                messages.error(request, 'Please select at least one Preferred ASEAN Country.')
                return render(request, 'resources/create_problem.html')
            
            # Validation - Collaboration Details
            if not timeline:
                messages.error(request, 'Implementation timeline is required.')
                return render(request, 'resources/create_problem.html')
            
            if not implementation_support:
                messages.error(request, 'Implementation support description is required.')
                return render(request, 'resources/create_problem.html')
            
            # Create problem statement
            problem = ProblemStatement.objects.create(
                title=title,
                subtitle=subtitle,
                description=description,
                current_challenges=current_challenges,
                contact_email=contact_email,
                preferred_asean_countries=preferred_asean_countries,
                innovation_type=innovation_type,
                startup_stage=startup_stage,
                solution_requirements=solution_requirements,
                technical_requirements=technical_requirements,
                timeline=timeline,
                implementation_support=implementation_support,
                created_by=member,
                company=member.companies.filter(company_type='corporate').first(),
                status='pending'
            )
            
            # Handle file uploads
            if 'technical_specifications' in request.FILES:
                # Create ProblemDocument for technical specifications
                from .models import ProblemDocument
                tech_spec_file = request.FILES['technical_specifications']
                ProblemDocument.objects.create(
                    problem=problem,
                    name='Technical Specifications',
                    file=tech_spec_file,
                    document_type='specifications'
                )
            
            if 'featured_image' in request.FILES:
                problem.featured_image = request.FILES['featured_image']
            
            problem.save()
            
            messages.success(request, 'Problem statement submitted successfully! It will be reviewed before publication.')
            return redirect('problem')
            
        except Exception as e:
            messages.error(request, f'Error creating problem statement: {str(e)}')
            return render(request, 'resources/create_problem.html')
    
    return render(request, 'resources/create_problem.html')

@onboarding_required
def accelerator_landing(request):
    return render(request, 'accelerator_landing.html')

@onboarding_required
def startup_profile(request, startup_id):
    """Display detailed startup profile page"""
    # Fetch the actual startup from the database
    startup = get_object_or_404(Company, pk=startup_id, company_type='startup', is_active=True)

    # Calculate real match score based on the viewer's company preferences
    try:
        viewer_company = request.user.member.companies.filter(is_active=True).first()
    except Exception:
        viewer_company = None
    match_score = calculate_real_match_score(viewer_company, startup)
    
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
        'funding_raised': startup.amount_raised or '-',  # Could be added as model field
        'funding_progress': 0,  # Could be calculated based on funding data
        'development_progress': 75 if startup.current_stage else 50,  # Default based on stage
        
        # Problem & Solution
        'problem_statement': startup.problem_statement or '',
        'innovation_description': startup.solution_description or '',
        'solution_description': startup.solution_description or '',
        'innovation_stage_description': f"Currently in {startup.current_stage} stage" if startup.current_stage else '',
        
        # Technology & Innovation
        'technology_stack': innovation_types_display or ['Technology Solutions'],
        'core_technologies': innovation_types_display or [],
        'intellectual_property': [],  # Could be added as model field
        
        # Market & Traction
        'target_markets': startup.target_markets or '',
        'market_country_interests': startup.market_country_interests or [],
        'customer_segments': startup.customer_segments or [],
        'customers_count': startup.active_users_count or '-',  # Could be added as model field
        'paying_customers': startup.paying_customers_count or '-',  # Could be added as model field
        'revenue_growth': '',  # Could be added as model field
        'annual_revenue': startup.annual_recurring_revenue or '-',  # Could be added as model field
        'market_opportunity_description': startup.investment_philosophy or '',
        
        # Financing Details
        'use_of_funds': startup.use_of_funds or '',
        'financial_projections': startup.financial_projections or '',  # Could be added as model field
        'funding_history': startup.funding_history or '',  # Could be added as model field or separate model
        'funding_round': startup.current_stage or '',
        
        # Team Information
        'founders': [
            {
                'name': startup.member.user.get_full_name() or startup.member.user.username,
                'position': startup.member.job_position or 'Founder',
                'bio': startup.member.short_bio or f"Founder of {startup.company_name}",
                'photo': startup.member.profile_picture if hasattr(startup.member, 'profile_picture') else None
            }
        ] if startup.member else [],
        
        'core_team_size': str(max(1, int(startup.core_team_size or '1') // 4)) if startup.core_team_size and startup.core_team_size.isdigit() else '',
        'team_description': f"Our team at {startup.company_name} is dedicated to {', '.join(innovation_types_display[:2])}." if innovation_types_display else f"Dedicated team at {startup.company_name}.",
        'core_expertise': startup.core_expertise or f"Expertise in {', '.join(innovation_types_display[:2])}" if innovation_types_display else 'Diverse expertise',
        'team_breakdown': {
            'total': int(startup.team_size or '1') if startup.team_size and startup.team_size.isdigit() else 1,
            'engineers': max(1, int(startup.team_size or '1') // 3) if startup.team_size and startup.team_size.isdigit() else 1,
            'business': max(1, int(startup.team_size or '1') // 4) if startup.team_size and startup.team_size.isdigit() else 1,
        },
        'team_overview': startup.team_overview or f"Our team is passionate about driving innovation in {', '.join(innovation_types_display[:2])}." if innovation_types_display else "Our team is passionate about innovation.",
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
    
    # Get published documents
    published_documents = startup.documents.filter(status='approved', is_published=True).order_by('-uploaded_at')
    
    show_match_score = match_score is not None
    return render(request, 'member/startup_profile.html', {
        'startup': startup_data,
        'published_documents': published_documents,
        'show_match_score': show_match_score,
    })
@onboarding_required
def investor_profile(request, investor_id):
    """Display detailed investor profile page"""
    # Fetch the actual investor from the database
    investor = get_object_or_404(Company, pk=investor_id, company_type='investor', is_active=True)

    # Calculate real match score based on the viewer's company preferences
    try:
        viewer_company = request.user.member.companies.filter(is_active=True).first()
    except Exception:
        viewer_company = None
    match_score = calculate_real_match_score(viewer_company, investor)
    
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
            'series_d': 'Series D+',
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
        
        'preferred_stages': funding_stages_display,
        
        # About Company
        'investment_philosophy': investor.investment_philosophy or '',
        'value_proposition': investor.investment_philosophy or '',  # Using same field for now
        
        # Market Interest
        'sector_focus': [
            {
                'name': cat,
                'percentage': 100 // len(investment_categories_display) if investment_categories_display else 0,
                'description': cat
            } for cat in investment_categories_display
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
                'position': investor.member.job_position or 'Partner',
                'bio': investor.member.short_bio or f"Partner at {investor.company_name}",
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
        
        # Contact & Partnership
        'contact_email': investor.member.user.email if investor.member else '',
        'partnership_message': investor.additional_info or f'We are actively seeking investment opportunities. Contact us to learn more about partnership with {investor.company_name}.',
        
        # Additional fields for template compatibility
        'company_type': get_display_value(investor.investor_type, dict(INVESTOR_TYPE_CHOICES)),
        'stage': 'Established',
        'industry': 'Investment Management',
        'match_score': match_score,
        'investment_focus': ', '.join(funding_stages_display) if funding_stages_display else '',
        'ticket_size': get_display_value(investor.average_deal_size, dict(DEAL_SIZE_CHOICES)) if investor.average_deal_size else '',
        'portfolio_size': '',
        'geographic_reach': f"{len(investor.market_country_interests)} countries" if investor.market_country_interests else ''
    }
    
    # Get published documents
    published_documents = investor.documents.filter(status='approved', is_published=True).order_by('-uploaded_at')
    
    show_match_score = match_score is not None
    return render(request, 'member/investor_profile.html', {
        'investor': investor_data,
        'published_documents': published_documents,
        'show_match_score': show_match_score,
    })
@onboarding_required
def corporate_profile(request, corporate_id):
    """Display detailed corporate profile page"""
    # Fetch the actual corporate from the database
    corporate = get_object_or_404(Company, pk=corporate_id, company_type='corporate', is_active=True)

    # Calculate real match score based on the viewer's company preferences
    try:
        viewer_company = request.user.member.companies.filter(is_active=True).first()
    except Exception:
        viewer_company = None
    match_score = calculate_real_match_score(viewer_company, corporate)
    
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
    

    # Collaboration types based on support areas (from corporate onboarding)
    collaboration_types = []
    if corporate.support_areas:
        # Map the actual collaboration methods from onboarding to the template structure
        collaboration_mapping = {
            'Co-Development – Collaborating on tailored solutions': {
                'type': 'Co-Development',
                'description': 'Collaborating on tailored solutions and joint product development.'
            },
            'Financial Support – Funding startups and projects': {
                'type': 'Financial Support',
                'description': 'Funding startups and projects through various financial instruments.'
            },
            'Mentorship & Expertise – Guiding startups with knowledge': {
                'type': 'Mentorship',
                'description': 'Guiding startups with industry knowledge and expertise.'
            },
            'Pilot Programs – Testing innovative solution': {
                'type': 'Pilot Program',
                'description': 'Testing innovative solutions through structured pilot programs.'
            }
        }
        
        collaboration_types = []
        for area in corporate.support_areas:
            if area in collaboration_mapping:
                collaboration_types.append(collaboration_mapping[area])
            else:
                # Fallback for any unmapped values
                collaboration_types.append({
                    'type': area.split('–')[0].strip() if '–' in area else area,
                    'description': area.split('–')[1].strip() if '–' in area else f'Support through {area.lower()}.'
                })

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
        'company_size': f"{corporate.team_size}" if corporate.team_size else '',
        'team_size': corporate.team_size or '',
        # 'organization_type': corporate.organization_type or '',
        'organization_type': get_display_value(corporate.organization_type, dict(ORGANIZATION_TYPE_CHOICES)),
        'contact_email': corporate.member.user.email if corporate.member else '',
        
        # Financial & Scale Metrics - Enhanced with defaults based on team size
        'annual_revenue': '',  # Could be added as model field later
        'market_cap': '',  # Not in model - could be added as field
        'employee_count': corporate.team_size or '',
        'global_presence': f"{len(corporate.market_country_interests)} countries" if corporate.market_country_interests else '',
        
        
        # Business Information
        'mission_vision': corporate.investment_philosophy or corporate.company_description or '',
        
        # Organization & Industry
        'business_focus_areas': investment_categories_display or ['Technology Solutions'],
        'industry_expertise': corporate.industry_expertise or '',
        
        # Market Interest & Innovation
        'innovation_interest_description': corporate.investment_philosophy or corporate.company_description or 'We actively seek partnerships with innovative companies that align with our strategic focus areas.',
        'innovation_interest_categories': investment_categories_display or ['Technology Solutions'],
        
        'target_markets': corporate.market_country_interests or [],
        
        'strategic_market_focus': f"Our strategic focus is on {', '.join(corporate.market_country_interests[:3])} markets" if corporate.market_country_interests else 'Regional market expansion',
        

        
        # Leadership & Team - Mock data based on available info
        'leadership_team': [
            {
                'name': corporate.member.user.get_full_name() or corporate.member.user.username,
                'position': corporate.member.job_position or 'Leadership Team Member',
                'bio': corporate.member.short_bio or f"Leadership team member at {corporate.company_name}",
                'photo': corporate.member.profile_picture if hasattr(corporate.member, 'profile_picture') else None
            }
        ] if corporate.member else [],
        'innovation_team_description': f"Our team at {corporate.company_name} comprises professionals working on innovative solutions and strategic partnerships.",
        
        # Contact & Partnership
        'partnership_message': corporate.additional_info or f'We are actively seeking strategic partnerships with innovative companies. Contact us to learn more about collaboration opportunities with {corporate.company_name}.',

        'collaboration_types': collaboration_types or [
            {
                'type': 'Strategic Partnership',
                'description': 'Various forms of strategic collaboration and business partnership opportunities.'
            }
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
    
    # Get published documents
    published_documents = corporate.documents.filter(status='approved', is_published=True).order_by('-uploaded_at')
    
    show_match_score = match_score is not None
    return render(request, 'member/corporate_profile.html', {
        'corporate': corporate_data,
        'published_documents': published_documents,
        'show_match_score': show_match_score,
    })


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
    # Get selected role from session
    selected_role = request.session.get('selected_role')
    
    # If no role selected, redirect to role selection BUT don't create another message
    # to avoid infinite loop messages
    if not selected_role:
        return redirect('onboarding_role_selection')
    
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
            
            # messages.success(request, 'Profile updated successfully!')
            
            # Redirect to role-specific onboarding (company setup)
            if selected_role == 'startup':
                return redirect('onboarding_startup_new')
            elif selected_role == 'investor':
                return redirect('onboarding_investor')
            elif selected_role == 'corporate':
                return redirect('onboarding_corporate')
            else:
                # Fallback - should not happen
                return redirect('onboarding_role_selection')
                
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
                # Female-led status
                is_female_led=request.POST.get('is_female_led') == 'on',
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
            
            messages.success(request, 'Thank you for your submission! Your profile has been received and will be reviewed by our team. Once verification is successful, your profile will be published. This process typically takes up to 48 hours. We appreciate your patience.')
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
        # Initialize form for all cases
        form = form_class(request.POST, request.FILES, instance=company)
        
        # Handle JSON field validation separately for startup forms
        if company_type == 'startup':
            # Remove JSON fields from form validation to handle them manually
            temp_post = request.POST.copy()
            json_fields = ['customer_segments', 'innovation_types']
            for field in json_fields:
                if field in temp_post:
                    del temp_post[field]
            
            # Create a modified form without JSON fields
            form_without_json = form_class(temp_post, request.FILES, instance=company)
            form_without_json.fields = {k: v for k, v in form.fields.items() if k not in json_fields}
            
            # Use the modified form for validation
            if form_without_json.is_valid():
                company = form_without_json.save(commit=False)
                
                # Set company member and type if creating new
                if not company.pk:
                    company.member = member
                    company.company_type = company_type
                    company.is_primary = True
                
                # Handle JSON fields manually for startups
                innovation_types = request.POST.getlist('innovation_type') or []
                company.innovation_types = innovation_types
                
                customer_segments = request.POST.getlist('customer_segments') or []
                company.customer_segments = customer_segments
                
                # Handle boolean fields
                company.has_external_funding = request.POST.get('has_external_funding') == 'true'
                company.is_female_led = request.POST.get('is_female_led') == 'true'
                
                company.save()
                messages.success(request, 'Your company profile has been updated successfully!')
                return redirect('company_profile_edit')
            else:
                # Form validation failed - use original form for displaying errors
                form = form_without_json
        
        elif company_type == 'corporate':
            # Remove JSON fields from form validation to handle them manually
            temp_post = request.POST.copy()
            json_fields = ['industry_expertise', 'investment_categories', 'market_country_interests', 'support_areas']
            for field in json_fields:
                if field in temp_post:
                    del temp_post[field]
            
            # Create a modified form without JSON fields
            form_without_json = form_class(temp_post, request.FILES, instance=company)
            form_without_json.fields = {k: v for k, v in form.fields.items() if k not in json_fields}
            
            # Use the modified form for validation
            if form_without_json.is_valid():
                company = form_without_json.save(commit=False)
                
                # Set company member and type if creating new
                if not company.pk:
                    company.member = member
                    company.company_type = company_type
                    company.is_primary = True
                
                # Handle JSON fields manually for corporates
                company.industry_expertise = request.POST.getlist('industry_expertise') or []
                company.investment_categories = request.POST.getlist('investment_categories') or []
                company.market_country_interests = request.POST.getlist('market_country_interests') or []
                company.support_areas = request.POST.getlist('support_areas') or []
                
                company.save()
                messages.success(request, 'Your company profile has been updated successfully!')
                return redirect('company_profile_edit')
            else:
                # Form validation failed - use original form for displaying errors
                form = form_without_json
        
        elif company_type == 'investor':
            # Remove JSON fields from form validation to handle them manually
            temp_post = request.POST.copy()
            json_fields = ['funding_stages', 'investment_categories', 'market_country_interests']
            for field in json_fields:
                if field in temp_post:
                    del temp_post[field]
            
            # Create a modified form without JSON fields
            form_without_json = form_class(temp_post, request.FILES, instance=company)
            form_without_json.fields = {k: v for k, v in form.fields.items() if k not in json_fields}
            
            # Use the modified form for validation
            if form_without_json.is_valid():
                company = form_without_json.save(commit=False)
                
                # Set company member and type if creating new
                if not company.pk:
                    company.member = member
                    company.company_type = company_type
                    company.is_primary = True
                
                # Handle JSON fields manually for investors
                company.funding_stages = request.POST.getlist('funding_stages') or []
                company.investment_categories = request.POST.getlist('investment_categories') or []
                company.market_country_interests = request.POST.getlist('market_country_interests') or []
                
                company.save()
                messages.success(request, 'Your company profile has been updated successfully!')
                return redirect('company_profile_edit')
            else:
                # Form validation failed - use original form for displaying errors
                form = form_without_json
        
        elif form.is_valid():
            company = form.save(commit=False)
            
            # Set company member and type if creating new
            if not company.pk:
                company.member = member
                company.company_type = company_type
                company.is_primary = True
            
            company.save()
            messages.success(request, 'Your company profile has been updated successfully!')
            return redirect('company_profile_edit')
        
        # If we reach here, form validation failed
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
            
            # Innovation Information tab
            innovation_types = request.POST.getlist('innovation_type')
            company.innovation_types = innovation_types
            company.solution_description = request.POST.get('solution_description', '').strip()
            
            # Startup-specific fields
            # Company Information tab (moved problem_statement to Innovation tab)
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
    return render(request, 'member/startup_company_profile_edit.html', context)


@login_required
def document_management(request):
    """Document management page"""
    member = get_object_or_404(Member, user=request.user)
    
    # Get all member documents
    member_documents = member.documents.all().order_by('-uploaded_at')
    
    # Get company documents for all user's companies
    company_documents = []
    for company in member.companies.all():
        company_documents.extend(company.documents.all())
    
    # Combine all documents
    all_documents = list(member_documents) + list(company_documents)
    all_documents.sort(key=lambda x: x.uploaded_at, reverse=True)
    
    context = {
        'member': member,
        'documents': all_documents,
        'member_documents': member_documents,
        'company_documents': company_documents,
    }
    return render(request, 'member/document_management.html', context)


@login_required
def upload_document(request):
    """Handle document upload via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        member = get_object_or_404(Member, user=request.user)
        
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'})
        
        file = request.FILES['file']
        document_category = request.POST.get('document_category', 'member')
        document_title = request.POST.get('document_title', '').strip()
        document_description = request.POST.get('document_description', '').strip()
        document_type = request.POST.get('document_type', '')
        company_id = request.POST.get('company_id')

        # Validate required fields
        if not document_title:
            return JsonResponse({'success': False, 'error': 'Document title is required'})
        
        if not document_type:
            return JsonResponse({'success': False, 'error': 'Document type is required'})

        # Validate file size (10MB max)
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False, 
                'error': f'File {file.name} is too large. Maximum size is 10MB.'
            })
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'File type {file_extension} is not allowed.'
            })

        # Create document based on category
        if document_category == 'company':
            # Validate company selection
            if not company_id:
                return JsonResponse({'success': False, 'error': 'Company selection is required for company documents'})
            
            try:
                company = Company.objects.get(id=company_id, member=member)
            except Company.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid company selection'})
            
            # Create company document
            document = CompanyDocument.objects.create(
                company=company,
                name=document_title,
                description=document_description,
                file=file,
                document_type=document_type
            )
            
            success_message = f'Your document "{document_title}" has been uploaded successfully and is pending review. Our team will verify it and make it available shortly. Thank you.'
            
        else:
            # Create member document
            document = MemberDocument.objects.create(
                member=member,
                name=document_title,
                description=document_description,
                file=file,
                document_type=document_type
            )
            
            success_message = f'Your document "{document_title}" has been uploaded successfully and is pending review. Our team will verify it and make it available shortly. Thank you.'

        return JsonResponse({
            'success': True,
            'message': success_message,
            'document': {
                'id': document.id,
                'name': document.name,
                'description': document.description,
                'type': document.get_document_type_display() if hasattr(document, 'get_document_type_display') else document.document_type,
                'size': document.file.size,
                'uploaded_at': document.uploaded_at.strftime('%b %d, %Y %H:%M'),
                'url': document.file.url if document.file else None,
                'category': document_category
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        })


@login_required
def toggle_document_publish(request, doc_id):
    """Toggle publish status of a company document"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        member = get_object_or_404(Member, user=request.user)
        
        # Find the document in user's companies
        document = None
        for company in member.companies.all():
            try:
                document = CompanyDocument.objects.get(id=doc_id, company=company)
                break
            except CompanyDocument.DoesNotExist:
                continue
        
        if not document:
            return JsonResponse({
                'success': False,
                'error': 'Document not found or access denied'
            })
        
        # Only approved documents can be published
        if document.status != 'approved' and request.POST.get('action') == 'publish':
            return JsonResponse({
                'success': False,
                'error': 'Only approved documents can be published'
            })
        
        # Toggle publish status
        action = request.POST.get('action')
        if action == 'publish':
            document.is_published = True
            message = 'Document published successfully'
        elif action == 'unpublish':
            document.is_published = False
            message = 'Document unpublished successfully'
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid action'
            })
        
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'is_published': document.is_published
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to update document: {str(e)}'
        })


@login_required 
def delete_document(request, doc_id):
    """Delete a document"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        member = get_object_or_404(Member, user=request.user)
        
        # Try to find in member documents first
        try:
            document = MemberDocument.objects.get(id=doc_id, member=member)
            document_name = document.name
            
            # Delete file from storage
            if document.file:
                document.file.delete(save=False)
            
            # Delete database record
            document.delete()
            
        except MemberDocument.DoesNotExist:
            # Try company documents
            company_doc = None
            for company in member.companies.all():
                try:
                    company_doc = CompanyDocument.objects.get(id=doc_id, company=company)
                    break
                except CompanyDocument.DoesNotExist:
                    continue
            
            if not company_doc:
                return JsonResponse({'success': False, 'error': 'Document not found'})
            
            document_name = company_doc.name
            
            # Delete file from storage
            if company_doc.file:
                company_doc.file.delete(save=False)
            
            # Delete database record
            company_doc.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Document "{document_name}" deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Delete failed: {str(e)}'
        })


@login_required
def view_document(request, doc_id):
    """View/download a document"""
    try:
        member = get_object_or_404(Member, user=request.user)
        
        # Try to find in member documents first
        document = None
        try:
            document = MemberDocument.objects.get(id=doc_id, member=member)
        except MemberDocument.DoesNotExist:
            # Try company documents
            for company in member.companies.all():
                try:
                    document = CompanyDocument.objects.get(id=doc_id, company=company)
                    break
                except CompanyDocument.DoesNotExist:
                    continue
        
        if not document or not document.file:
            return JsonResponse({'success': False, 'error': 'Document not found'})
        
        # Return file response
        from django.http import FileResponse
        import mimetypes
        
        response = FileResponse(
            document.file.open('rb'),
            content_type=mimetypes.guess_type(document.file.name)[0]
        )
        response['Content-Disposition'] = f'inline; filename="{document.name}"'
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'View failed: {str(e)}'
        })


def _calculate_verification_data(member):
    """Calculate verification progress data for verification center"""
    
    # Personal profile checks
    personal_checks = {
        'email_verified': member.user.is_active,  # Assuming email verification via activation
        'profile_complete': (
            bool(member.profile_picture) and 
            bool(member.job_position) and 
            bool(member.short_bio) and 
            bool(member.phone_number)
        ),
        'linkedin_verified': bool(member.linkedin_url),  # Optional
    }
    
    # Count personal profile completion
    personal_completed = sum([
        personal_checks['email_verified'],
        personal_checks['profile_complete']
    ])
    personal_total = 2  # Email and profile completion are required
    
    # Company profile checks
    company_exists = member.companies.filter(is_active=True).exists()
    company_checks = {
        'company_exists': company_exists,
        'company_info_complete': False,
        'documents_uploaded': False,
        'documents_verified': False,
    }
    
    company_completed = 0
    company_total = 4  # Company creation, info completion, document upload, document verification
    
    if company_exists:
        company = member.companies.filter(is_active=True).first()
        
        # Check if company info is complete
        company_info_complete = (
            bool(company.company_name) and
            bool(company.company_description) and
            bool(company.website) and
            bool(company.founded_year) and
            bool(company.team_size) and
            bool(company.primary_location)
        )
        company_checks['company_info_complete'] = company_info_complete
        
        # Check documents
        company_documents = company.documents.all()
        company_checks['documents_uploaded'] = company_documents.exists()
        company_checks['documents_verified'] = (
            company_documents.exists() and 
            company_documents.filter(status='approved').count() > 0
        )
        
        # Count completed company steps
        if company_exists:
            company_completed += 1
        if company_info_complete:
            company_completed += 1
        if company_checks['documents_uploaded']:
            company_completed += 1
        if company_checks['documents_verified']:
            company_completed += 1
    
    # Calculate overall progress
    total_steps = personal_total + company_total
    completed_steps = personal_completed + company_completed
    remaining_steps = total_steps - completed_steps
    
    # Calculate document stats for display
    document_stats = {
        'pending_documents': 0,
        'approved_documents': 0,
        'total_documents': 0,
    }
    
    if company_exists:
        company = member.companies.filter(is_active=True).first()
        if company:
            documents = company.documents.all()
            document_stats['total_documents'] = documents.count()
            document_stats['pending_documents'] = documents.filter(status='pending').count()
            document_stats['approved_documents'] = documents.filter(status='approved').count()
    
    return {
        'overall': {
            'percentage': round((completed_steps / total_steps * 100) if total_steps > 0 else 0),
            'completed_steps': completed_steps,
            'remaining_steps': remaining_steps,
            'total_steps': total_steps,
        },
        'personal': {
            'completed_steps': personal_completed,
            'total_steps': personal_total,
            'checks': personal_checks,
        },
        'company': {
            'completed_steps': company_completed,
            'total_steps': company_total,
            'checks': company_checks,
        },
        'document_stats': document_stats,
    }


@login_required
def verification_center(request):
    """Verification center page"""
    member = get_object_or_404(Member, user=request.user)
    
    # Calculate verification data
    verification_data = _calculate_verification_data(member)
    
    context = {
        'member': member,
        'verification_data': verification_data,
    }
    return render(request, 'member/verification_center.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_two_factor_auth(request):
    """Toggle two-factor authentication for user"""
    try:
        data = json.loads(request.body)
        enable = data.get('enable', False)
        
        member = Member.objects.get(user=request.user)
        
        if enable:
            # Enable 2FA
            member.two_factor_enabled = True
            member.save(update_fields=['two_factor_enabled'])
            
            # Send notification email
            from .email_utils import send_2fa_enabled_notification
            send_2fa_enabled_notification(request.user)
            
            return JsonResponse({
                'success': True,
                'message': 'Two-factor authentication has been enabled successfully. You will now receive verification codes via email when logging in.',
                'enabled': True
            })
        else:
            # Disable 2FA
            member.two_factor_enabled = False
            member.save(update_fields=['two_factor_enabled'])
            
            # Clean up any existing OTPs for this user
            from .models import EmailOTP
            EmailOTP.objects.filter(user=request.user).delete()
            
            # Send notification email
            from .email_utils import send_2fa_disabled_notification
            send_2fa_disabled_notification(request.user)
            
            return JsonResponse({
                'success': True,
                'message': 'Two-factor authentication has been disabled. Your account security level has been reduced.',
                'enabled': False
            })
            
    except Member.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User profile not found.'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


def verify_2fa_login(request):
    """Handle 2FA OTP verification during login"""
    # Check if there's a pending 2FA user
    user_id = request.session.get('pending_2fa_user_id')
    if not user_id:
        messages.error(request, 'No pending authentication found. Please log in again.')
        return redirect('login')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid authentication session. Please log in again.')
        return redirect('login')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter the verification code.')
            return render(request, 'member/verify_2fa_login.html', {'user': user})
        
        # Find valid OTP for this user
        from .models import EmailOTP
        try:
            otp = EmailOTP.objects.get(
                user=user,
                otp_code=otp_code,
                is_used=False
            )
            
            if not otp.is_valid():
                messages.error(request, 'The verification code has expired. Please request a new one.')
                return render(request, 'member/verify_2fa_login.html', {'user': user})
            
            # Mark OTP as used
            otp.mark_as_used()
            
            # Complete the login process
            from django.contrib.auth import login
            login(request, user, backend='member.backends.EmailBackend')
            
            # Clean up session
            if 'pending_2fa_user_id' in request.session:
                del request.session['pending_2fa_user_id']
            if 'pending_2fa_backend' in request.session:
                del request.session['pending_2fa_backend']
            
            messages.success(request, 'Login successful! Two-factor authentication verified.')
            
            # Redirect to original success URL
            try:
                member = Member.objects.get(user=user)
                
                # Check if user profile is complete first
                if not member.is_profile_complete():
                    return redirect('onboarding_user_profile')
                
                # Check if user has company profile
                if not member.has_company_profile():
                    # Check if they have a stored role in session
                    stored_role = request.session.get('selected_role')
                    if stored_role:
                        if stored_role == 'startup':
                            return redirect('onboarding_startup_new')
                        elif stored_role == 'investor':
                            return redirect('onboarding_investor')
                        elif stored_role == 'corporate':
                            return redirect('onboarding_corporate')
                    
                    # No stored role, go to role selection
                    return redirect('onboarding_role_selection')
                
                # User has completed onboarding, go to dashboard
                return redirect('dashboard')
                
            except Member.DoesNotExist:
                return redirect('onboarding_user_profile')
            
        except EmailOTP.DoesNotExist:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'member/verify_2fa_login.html', {'user': user})
    
    # GET request - show OTP input form
    return render(request, 'member/verify_2fa_login.html', {'user': user})


def resend_2fa_otp(request):
    """Resend OTP for 2FA login"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    user_id = request.session.get('pending_2fa_user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'No pending authentication found'}, status=400)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Clean up existing OTPs
        from .models import EmailOTP
        EmailOTP.objects.filter(user=user).delete()
        
        # Create new OTP
        otp = EmailOTP.objects.create(
            user=user,
            session_key=request.session.session_key
        )
        
        # Send OTP email
        from .email_utils import send_otp_email
        success = send_otp_email(user, otp.otp_code)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'A new verification code has been sent to {user.email}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send verification email. Please try again.'
            })
            
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid session'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


def disclaimer(request):
    """Disclaimer page"""
    return render(request, 'member/disclaimer.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'member/privacy_policy.html')


def match_score_explanation(request):
    """Match Score Explanation page"""
    return render(request, 'member/match_score_explanation.html')


def terms_and_conditions(request):
    """Terms and Conditions page"""
    return render(request, 'member/terms_and_conditions.html')

def environment_agreement(request):
    return render(request, 'member/environment_agreement.html')


def contact_us(request):
    """Contact Us page"""
    return render(request, 'member/contact_us.html')

@login_required
def test_2fa_email(request):
    """Test view for 2FA email functionality"""
    if request.method == 'POST':
        try:
            # Create test OTP
            from .models import EmailOTP
            otp = EmailOTP.objects.create(user=request.user)
            
            # Send test email
            from .email_utils import send_otp_email
            success = send_otp_email(request.user, otp.otp_code)
            
            if success:
                messages.success(request, f'✅ Test OTP email sent successfully to {request.user.email}! Check your email for verification code: {otp.otp_code}')
            else:
                messages.error(request, '❌ Failed to send test email. Please check your email configuration.')
                
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            
        return redirect('test_2fa_email')
    
    # Check email configuration
    from django.conf import settings
    email_config = {
        'backend': settings.EMAIL_BACKEND,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'host_user': getattr(settings, 'EMAIL_HOST_USER', 'Not configured'),
        'host_password': '***' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'Not configured'
    }
    
    # Get logo for preview
    from .email_assets import get_logo_url, get_logo_base64
    logo_url = get_logo_url(request)
    
    return render(request, 'member/test_2fa_email.html', {
        'email_config': email_config,
        'logo_url': logo_url
    })


@login_required
@require_http_methods(["POST"])
def toggle_2fa(request):
    """Toggle 2FA setting for user"""
    try:
        member = Member.objects.get(user=request.user)
        
        # Toggle the 2FA status
        member.two_factor_enabled = not member.two_factor_enabled
        member.save()
        
        if member.two_factor_enabled:
            message = "Two-factor authentication has been enabled successfully!"
            messages.success(request, message)
        else:
            message = "Two-factor authentication has been disabled."
            messages.info(request, message)
        
        return JsonResponse({
            'success': True,
            'enabled': member.two_factor_enabled,
            'message': message
        })
        
    except Member.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Member profile not found'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def send_2fa_verification(request):
    """Send verification code before enabling/disabling 2FA"""
    try:
        data = json.loads(request.body)
        action = data.get('action', '')  # 'enable' or 'disable'
        
        if action not in ['enable', 'disable']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action specified.'
            }, status=400)
        
        user = request.user
        
        # Generate and send OTP
        from .models import EmailOTP
        from .email_utils import send_otp_email
        
        # Clean up any existing OTPs for this user
        EmailOTP.objects.filter(user=user).delete()
        
        # Create new OTP
        otp = EmailOTP.objects.create(user=user)
        
        # Send OTP email with context about the action
        context_message = f"to {action} Two-Factor Authentication on your account"
        success = send_otp_email(user, otp.otp_code, context=context_message)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Verification code sent to {user.email}. Please check your email.',
                'action': action
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send verification email. Please try again.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def verify_and_toggle_2fa(request):
    """Verify code and toggle 2FA setting"""
    try:
        data = json.loads(request.body)
        enable = data.get('enable', False)
        verification_code = data.get('verification_code', '').strip()
        
        if not verification_code:
            return JsonResponse({
                'success': False,
                'message': 'Verification code is required.',
                'error_type': 'missing_code'
            }, status=400)
        
        user = request.user
        
        # Verify the OTP
        from .models import EmailOTP
        try:
            otp = EmailOTP.objects.get(
                user=user,
                otp_code=verification_code,
                is_used=False
            )
            
            if not otp.is_valid():
                return JsonResponse({
                    'success': False,
                    'message': 'The verification code has expired. Please request a new code.',
                    'error_type': 'expired_code'
                }, status=400)
            
            # Mark OTP as used
            otp.mark_as_used()
            
        except EmailOTP.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Invalid verification code. Please check and try again.',
                'error_type': 'invalid_code'
            }, status=400)
        
        # Now toggle the 2FA setting
        try:
            member = Member.objects.get(user=user)
            
            if enable:
                # Enable 2FA
                member.two_factor_enabled = True
                member.save(update_fields=['two_factor_enabled'])
                
                # Send notification email
                from .email_utils import send_2fa_enabled_notification
                send_2fa_enabled_notification(user)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Two-factor authentication has been enabled successfully. You will now receive verification codes via email when logging in.',
                    'enabled': True
                })
            else:
                # Disable 2FA
                member.two_factor_enabled = False
                member.save(update_fields=['two_factor_enabled'])
                
                # Clean up any remaining OTPs for this user
                EmailOTP.objects.filter(user=user).delete()
                
                # Send notification email
                from .email_utils import send_2fa_disabled_notification
                send_2fa_disabled_notification(user)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Two-factor authentication has been disabled. Your account security level has been reduced.',
                    'enabled': False
                })
                
        except Member.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User profile not found.'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)
