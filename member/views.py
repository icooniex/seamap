from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout
from django import forms
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Member, Company
from .forms import EmailLoginForm, SignUpForm
import json
from django.views import View


class CustomLoginView(LoginView):
    """
    Custom login view with email authentication and remember me functionality
    """
    template_name = 'member/login.html'
    form_class = EmailLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after successful login"""
        return '/dashboard/'
    
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

def onboarding_investor(request):
    """Placeholder for investor onboarding"""
    # messages.info(request, 'Investor onboarding coming soon!')
    # return redirect('onboarding_role_selection')
    context = {
        'message': 'Investor onboarding coming soon!'
    }

    return render(request, 'onboarding/investor_onboarding.html', context)

def onboarding_corporate(request):
    """Placeholder for corporate onboarding"""
    messages.info(request, 'Corporate onboarding coming soon!')
    return redirect('onboarding_role_selection')

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

def dashboard2(request):
    return render(request, 'dash2.html')

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
from django.views import View

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
    
    return render(request, 'onboarding/startup_step4.html')

def onboarding_startup_step5(request):
    return render(request, 'onboarding/startup_step5.html')
def onboarding_startup_step6(request):
    return render(request, 'onboarding/startup_step6.html')

def onboarding_startup_single_page(request):
    """Handle single-page startup onboarding flow with all 3 steps"""
    if request.method == 'POST':
        # Process all form data from the single-page form
        step1_data = {
            'company_name': request.POST.get('company_name'),
            'website': request.POST.get('website'),
            'founded_year': request.POST.get('founded_year'),
            'team_size': request.POST.get('team_size'),
            'primary_location': request.POST.get('primary_location'),
            'company_description': request.POST.get('company_description'),
        }
        
        step2_data = {
            'innovation_type': request.POST.getlist('innovation_type'),
            'solution_description': request.POST.get('solution_description'),
            'current_stage': request.POST.get('current_stage'),
            'funding_needed': request.POST.get('funding_needed'),
        }
        
        step3_data = {
            'support_areas': request.POST.getlist('support_areas'),
            'support_details': request.POST.get('support_details'),
            'additional_info': request.POST.get('additional_info'),
            'consent_info': request.POST.get('consent_info') == 'on',
            'consent_marketplace': request.POST.get('consent_marketplace') == 'on',
        }
        
        # Store in session
        request.session['startup_onboarding'] = {
            'step1': step1_data,
            'step2': step2_data,
            'step3': step3_data,
        }
        
        # Redirect to success page or dashboard
        return redirect('dashboard')
    
    return render(request, 'onboarding/startup_single_page.html')

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
            member.user_type = selected_role
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
    
    # Check if role was selected and is startup
    if member.user_type != 'startup':
        messages.warning(request, 'This onboarding is for startups only.')
        return redirect('onboarding_role_selection')
    
    if request.method == 'POST':
        try:
            # Handle multiple selections for innovation_type and support_areas
            innovation_types = request.POST.getlist('innovation_type')
            support_areas = request.POST.getlist('support_areas')
            
            # Create new company profile
            company = Company.objects.create(
                member=member,
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