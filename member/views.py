from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django import forms
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    template_name = 'member/login.html'

class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, label='Full Name')
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Change to your dashboard URL name
    else:
        form = SignUpForm()
    return render(request, 'member/signup.html', {'form': form})



def investor_matchmaking(request):
    # query = request.GET.get('q', '')
    # investors = Member.objects.filter(user_type='investor')
    # if query:
    #     investors = investors.filter(company_name__icontains=query)
    # # Add more filters as needed

    # # Example: Add dummy match percentage for demo
    # for idx, investor in enumerate(investors):
    #     investor.match_percent = 97 - idx * 7  # Just for demo

    # return render(request, 'member/investor_matchmaking.html', {
    #     'investors': investors,
    #     'query': query,
    # })

    return render(request, 'member/investor_matchmaking.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def problem(request):
    return render(request, 'resources/problem.html')

def challenge(request):
    return render(request, 'resources/challenge.html')

def accelerator_landing(request):
    return render(request, 'accelerator_landing.html')

def startup_detail(request):
    return render(request, 'member/startup_detail.html')

def investor_detail(request):
    return render(request, 'member/investor_detail.html')


def startup_profile(request, startup_id):
    """Display detailed startup profile page"""
    # This is sample data - replace with actual database queries
    startup_data = {
        'name': 'OceanClean Tech',
        'description': 'Developing autonomous drones that collect plastic waste from oceans and waterways with AI-powered identification technology.',
        'match_percentage': 92,
        'overview': 'Developing autonomous drones that collect plastic waste from oceans and waterways with AI-powered identification technology.',
        'solution_categories': ['Cleanup Technologies', 'Monitoring Tools'],
        'tags': ['AI', 'Robotics', 'Ocean Cleanup'],
        'development_stage': 'Early Market Entry',
        'funding_needed': '$250K - $1M',
        'sectors': ['Technology', 'Ocean Cleanup'],
        'impact_metrics': [
            {
                'title': 'Tons of plastic removed',
                'description': 'Impact measurement'
            },
            {
                'title': 'Marine wildlife protected',
                'description': 'Impact measurement'
            }
        ],
        'environmental_impact': 'OceanClean Tech is committed to creating positive environmental and social impact through sustainable marine conservation solutions. Their initiatives are designed to both address immediate environmental challenges and create long-term positive effects.',
        'team_size': '6-10',
        'team_overview': 'OceanClean Tech\'s team consists of passionate professionals dedicated to solving marine plastic pollution through innovative technologies and sustainable practices.',
        'core_expertise': ['Technology', 'Ocean Cleanup', 'AI', 'Robotics'],
        'contact_description': 'Interested in learning more about OceanClean Tech\'s innovative solutions for marine conservation? Reach out directly to discuss potential collaboration, investment opportunities, or to learn more about their technology.',
        'connection_reasons': [
            'Explore partnership opportunities',
            'Get detailed information about their solutions',
            'Request a pilot or demonstration',
            'Discuss potential investment'
        ]
    }
    
    return render(request, 'member/startup_profile.html', {'startup': startup_data})

def investor_profile(request, investor_id):
    """Display detailed investor profile page"""
    # Sample data - replace with actual database queries
    investor_data = {
        'name': 'Blue Ocean Fund',
        'description': 'Impact investment fund focused on ocean conservation',
        'match_percentage': 97,
        'location': 'Singapore',
        'founded_year': '2018',
        'team_size': '15-20 team members',
        'portfolio_count': '3 portfolio companies',
        'website': 'https://blueocanfund.com',
        'overview': 'Blue Ocean Fund is a Singapore-based impact investment fund that focuses on ocean conservation and marine technology. Founded in 2018, the fund aims to support startups and projects that address ocean plastic pollution, sustainable fishing, and marine biodiversity conservation in Southeast Asia.',
        'investment_thesis': 'Our investment thesis centers on the belief that protecting our oceans requires innovative technologies and sustainable business models. We invest in companies that demonstrably reduce marine pollution, promote sustainable use of marine resources, or help communities adapt to climate change impacts on oceanic health.',
        'investment_stages': ['Seed', 'Series A'],
        'investment_range': '$500K - $2M',
        'sectors': [
            {'name': 'Ocean Cleanup', 'percentage': 95},
            {'name': 'Sustainable Fishing', 'percentage': 85},
            {'name': 'Marine Conservation', 'percentage': 90},
            {'name': 'Coastal Management', 'percentage': 75},
            {'name': 'Plastic Alternatives', 'percentage': 80}
        ],
        'investment_type': {
            'name': 'Impact Fund',
            'description': 'Focusing on measurable social and environmental impact alongside financial returns.'
        },
        'primary_focus': {
            'name': 'Marine Tech',
            'description': 'Technologies and solutions for ocean conservation and sustainable marine resource utilization.'
        },
        'portfolio_companies': [
            {
                'name': 'OceanClean Tech',
                'description': 'Autonomous ocean cleanup drones',
                'status': 'Active',
                'investment_year': '2020'
            },
            {
                'name': 'BioPlastic Innovations',
                'description': 'Seaweed-based biodegradable packaging',
                'status': 'Active',
                'investment_year': '2019'
            },
            {
                'name': 'ReefWatch',
                'description': 'AI-powered coral reef monitoring systems',
                'status': 'Active',
                'investment_year': '2021'
            }
        ],
        'team_members': [
            {
                'name': 'Sarah Chen',
                'position': 'Managing Partner',
                'linkedin': '#'
            },
            {
                'name': 'Michael Tan',
                'position': 'Investment Director',
                'linkedin': '#'
            },
            {
                'name': 'Dr. Emma Sullivan',
                'position': 'Marine Science Advisor',
                'linkedin': '#'
            }
        ],
        'contact': {
            'email': 'info@blueocanfund.com',
            'phone': '+65 6123 4567',
            'website': 'www.blueocanfund.com'
        },
        'social': {
            'linkedin': '#',
            'twitter': '#'
        }
    }
    
    return render(request, 'member/investor_profile.html', {'investor': investor_data})

def corporate_profile(request, company_id):
    """Display detailed corporate profile page"""
    company_data = {
        'name': 'EcoRetail Group',
        'description': 'A leading retail chain committed to sustainable sourcing and plastic-free packaging across their operations throughout Southeast Asia.',
        'match_percentage': 94,
        'industry': 'Retail',
        'location': 'Singapore',
        'founded_year': '2005',
        'employee_count': '1,000-5,000',
        'revenue_range': '$10M - $50M',
        'website': 'https://ecoretailgroup.com',
        'overview': 'A leading retail chain committed to sustainable sourcing and plastic-free packaging across their operations throughout Southeast Asia.',
        'industry_info': 'EcoRetail Group operates in the Retail sector, and was established in 2005. With a company size of 1,000-5,000 employees, they have significant potential for impact in marine conservation and plastic reduction initiatives.',
        'tags': ['Retail Chain', 'Sustainability', 'Plastic-Free'],
        'sustainability_goals': [
            'Zero Plastic Packaging',
            'Carbon Neutral by 2030',
            'Sustainable Sourcing'
        ],
        'purchasing_interests': [
            'Biodegradable Packaging',
            'Plastic Alternatives',
            'Ocean-friendly Products'
        ],
        'potential_value': {
            'description': 'EcoRetail Group could achieve high-value partnerships with an annual spend of $10M - $50M in areas that align with sustainable marine solutions.',
            'purchase_items': [
                'Solutions for Biodegradable Packaging',
                'Solutions for Plastic Alternatives',
                'Solutions for Ocean-friendly Products'
            ]
        },
        'impact_potential': {
            'description': 'Working with EcoRetail Group could contribute significantly to meeting their sustainability goals while advancing marine conservation efforts.',
            'objectives': [
                'Zero Plastic Packaging',
                'Carbon Neutral by 2030',
                'Sustainable Sourcing'
            ]
        },
        'recommended_approaches': [
            {
                'title': 'Sustainability Partnership',
                'description': 'Promote collaborative sustainability initiatives that address their specific goals in Zero Plastic Packaging.'
            },
            {
                'title': 'Product Solutions',
                'description': 'Present solutions specifically tailored to their interest in biodegradable packaging with quantifiable impact metrics.'
            },
            {
                'title': 'Industry Positioning',
                'description': 'Emphasize how sustainability will position them as a leader in sustainability within the Retail sector.'
            }
        ],
        'innovation_challenges': [
            {
                'title': 'Ocean Plastic Innovation Challenge',
                'description': 'Developing solutions to reduce ocean plastic pollution',
                'timeline': 'June 15, 2025 - September 15, 2025',
                'location': 'Singapore',
                'deadline': 'June 1, 2025'
            }
        ],
        'problem_statements': [],
        'contact_description': 'Ready to explore potential collaborations with EcoRetail Group? Our platform makes it easy to establish connections and discuss how your solutions can help them meet their sustainability goals.'
    }
    
    return render(request, 'member/corporate_profile.html', {'company': company_data})

def onboarding_role_selection(request):
    return render(request, 'onboarding/index.html')



# ...existing code...

def onboarding_startup_step1(request):
    """Handle startup onboarding step 1 - company information"""
    if request.method == 'POST':
        # Get form data
        company_data = {
            'company_name': request.POST.get('company_name'),
            'website': request.POST.get('website'),
            'founded_year': request.POST.get('founded_year'),
            'team_size': request.POST.get('team_size'),
            'primary_location': request.POST.get('primary_location'),
            'company_description': request.POST.get('company_description'),
        }
        
        # Store in session
        request.session['startup_company_data'] = company_data
        
        # Redirect to next step
        return redirect('onboarding_startup_step2')
    
    return render(request, 'onboarding/startup_step1.html')

def onboarding_startup_step2(request):
    """Handle startup onboarding step 2 - innovation information"""
    if request.method == 'POST':
        # Get form data
        innovation_data = {
            'innovation_type': request.POST.getlist('innovation_type'),
            'current_stage': request.POST.get('current_stage'),
            'funding_needed': request.POST.get('funding_needed'),
        }
        
        # Store in session
        request.session['startup_innovation_data'] = innovation_data
        
        # Redirect to next step
        return redirect('onboarding_startup_step3')
    
    return render(request, 'onboarding/startup_step2.html')


import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

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

def onboarding_startup_step4(request):
    """Handle startup onboarding step 4 - final step"""
    # Get all data from session
    company_data = request.session.get('startup_company_data', {})
    innovation_data = request.session.get('startup_innovation_data', {})
    files_data = request.session.get('startup_files', {})
    
    if request.method == 'POST':
        # Create startup profile with all data
        # This would typically save to database
        startup_profile = {
            'user': request.user,
            **company_data,
            **innovation_data,
            **files_data
        }
        
        # Clear session data
        request.session.pop('startup_company_data', None)
        request.session.pop('startup_innovation_data', None)
        request.session.pop('startup_files', None)
        
        # Redirect to dashboard
        return redirect('dashboard_startup')
    
    context = {
        'company_data': company_data,
        'innovation_data': innovation_data,
        'files_data': files_data
    }
    return render(request, 'onboarding/startup_step4.html', context)
