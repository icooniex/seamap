from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets
from .upload_handlers import profile_picture_upload_to, company_logo_upload_to

# Verification Status Choices
VERIFICATION_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('under_review', 'Under Review'),
]

# Document Verification Status Choices
DOCUMENT_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('under_review', 'Under Review'),
]

# Member Document Type Choices
MEMBER_DOCUMENT_TYPE_CHOICES = [
    ('id_card', 'ID Card'),
    ('passport', 'Passport'),
    ('cv', 'CV/Resume'),
    ('certificate', 'Certificate'),
    ('portfolio', 'Portfolio'),
    ('other', 'Other'),
]

# Company Document Type Choices
COMPANY_DOCUMENT_TYPE_CHOICES = [
    ('pitch_deck', 'Pitch Deck'),
    ('business_plan', 'Business Plan'),
    ('financial_statements', 'Financial Statements'),
    ('company_registration', 'Company Registration'),
    ('technical_docs', 'Technical Documentation'),
    ('market_research', 'Market Research'),
    ('product_demo', 'Product Demo'),
    ('legal_docs', 'Legal Documents'),
    ('other', 'Other'),
]

USER_TYPE_CHOICES = [
    ('startup', 'Startup'),
    ('investor', 'Investor'),
    ('corporate', 'Corporate'),
]

TEAM_SIZE_CHOICES = [
    ('1', '1 person (Solo founder)'),
    ('2-5', '2-5 people'),
    ('6-10', '6-10 people'),
    ('11-25', '11-25 people'),
    ('26-50', '26-50 people'),
    ('51-100', '51-100 people'),
    ('100+', '100+ people'),
]

LOCATION_CHOICES = [
    ('Singapore', '🇸🇬 Singapore'),
    ('Indonesia', '🇮🇩 Indonesia'),
    ('Thailand', '🇹🇭 Thailand'),
    ('Malaysia', '🇲🇾 Malaysia'),
    ('Philippines', '🇵🇭 Philippines'),
    ('Vietnam', '🇻🇳 Vietnam'),
    ('Cambodia', '🇰🇭 Cambodia'),
    ('Laos', '🇱🇦 Laos'),
    ('Myanmar', '🇲🇲 Myanmar'),
    ('Brunei', '🇧🇳 Brunei'),
    ('Other', '🌍 Other'),
]

CURRENT_STAGE_CHOICES = [
    ('idea', '💡 Ideation – Developing an idea, no product yet'),
    ('prototype', '🔧 Prototype – Initial MVP or prototype created'),
    ('validation', '🧪 Validation – Testing with early customers'),
    ('early', '📈 Early Growth – Generating revenue'),
    ('scaling', '🚀 Scaling – Expanding with proven model'),
    ('profitable', '💰 Established – Profitable and exploring new markets'),
]

FUNDING_NEEDED_CHOICES = [
    ('under_10k', 'Under $10K'),
    ('10k_50k', '$10K - $50K'),
    ('50k_100k', '$50K - $100K'),
    ('100k_500k', '$100K - $500K'),
    ('500k_1m', '$500K - $1M'),
    ('1m_5m', '$1M - $5M'),
    ('5m_10m', '$5M - $10M'),
    ('over_10m', 'Over $10M'),
    ('not_seeking', 'Not currently seeking funding'),
]

# Investor-specific choices
INVESTOR_TYPE_CHOICES = [
    ('angel', '🦸 Angel Investor'),
    ('vc', '💼 Venture Capital (VC)'),
    ('corporate', '🏢 Corporate Investor'),
    ('family_office', '👨‍👩‍👧‍👦 Family Office'),
    ('impact_fund', '🌱 Impact Fund'),
    ('government', '🏛️ Government/Development Agency'),
    ('other', '🔎 Other'),
]

FUNDING_SIZE_CHOICES = [
    ('under_1m', 'Under $1M'),
    ('1m_50m', '$1M - $50M'),
    ('100m_200m', '$100M - $200M'),
    ('200m_500m', '$200M - $500M'),
    ('over_500m', 'Over $500M'),
]

DEAL_SIZE_CHOICES = [
    ('under_100k', 'Under $100K'),
    ('100k_500k', '$100K - $500K'),
    ('500k_1m', '$500K - $1M'),
    ('1m_5m', '$1M - $5M'),
    ('5m_10m', '$5M - $10M'),
    ('10m_50m', '$10M - $50M'),
    ('over_50m', 'Over $50M'),
]

# Corporate-specific choices
ORGANIZATION_TYPE_CHOICES = [
    ('private_company', '🏢 Private Company'),
    ('multinational_corporation', '🌐 Multinational Corporation'),
    ('sme', '🏭 Small or Medium-sized Enterprise (SME)'),
    ('startup_subsidiary', '🚀 Startup Subsidiary'),
    ('other', 'Other'),
]

class Member(models.Model):
    """User Profile Model - stores individual user information"""
    # Basic user information
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # User Profile Information
    profile_picture = models.ImageField(upload_to=profile_picture_upload_to, blank=True, null=True)
    job_position = models.CharField(max_length=255, blank=True)
    short_bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Consent fields
    consent_info = models.BooleanField(default=False)
    consent_marketplace = models.BooleanField(default=False)
    
    # Registration tracking
    profile_completed = models.BooleanField(default=False)
    
    # 2FA Settings
    two_factor_enabled = models.BooleanField(default=False, help_text="Enable two-factor authentication via email")
    onboarding_completed = models.BooleanField(default=False)
    
    # Verification fields
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending',
        help_text="Profile verification status by admin"
    )
    verified_at = models.DateTimeField(blank=True, null=True, help_text="When the profile was verified")
    verified_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_members',
        help_text="Admin user who verified this profile"
    )
    verification_notes = models.TextField(
        blank=True, 
        help_text="Admin notes about verification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def get_verification_status_color(self):
        """Get Bootstrap color class for verification status"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'under_review': 'info',
        }
        return colors.get(self.verification_status, 'secondary')

    def can_be_verified(self):
        """Check if profile has enough information to be verified"""
        required_fields = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.job_position,
            self.short_bio,
        ]
        return all(field for field in required_fields)

    def get_profile_picture_url(self):
        """Get profile picture URL with fallback to default image"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            try:
                # Import settings here to avoid circular imports
                from django.conf import settings
                
                # For R2 storage, always return the URL (cloud storage handles existence)
                if getattr(settings, 'USE_CLOUDFLARE_R2', False):
                    return self.profile_picture.url
                elif settings.DEBUG:
                    # Local development - check file existence
                    import os
                    file_path = os.path.join(settings.MEDIA_ROOT, str(self.profile_picture))
                    if os.path.exists(file_path):
                        return self.profile_picture.url
                else:
                    # Production with local storage
                    return self.profile_picture.url
            except:
                pass
        
        # Return default profile picture
        return '/static/images/default-profile.png'

    def is_profile_complete(self):
        """Check if user profile is complete"""
        required_fields = [
            self.user.first_name,
            self.user.last_name, 
            self.user.email,
            self.job_position,
            self.short_bio,
        ]
        return all(field and str(field).strip() for field in required_fields) and self.profile_completed

    def has_company_profile(self):
        """Check if user has at least one company profile"""
        return self.companies.filter(is_active=True).exists()

    def get_onboarding_status(self):
        """Get detailed onboarding status and next step"""
        if not self.is_profile_complete():
            return {
                'completed': False,
                'next_step': 'user_profile',
                'redirect_url': '/onboarding/profile/'
            }
        
        if not self.has_company_profile():
            # Check if user has selected a role in session - this will need to be handled in views
            # For now, assume they need to select company type
            return {
                'completed': False,
                'next_step': 'company_profile',
                'redirect_url': '/onboarding/'
            }
        
        return {
            'completed': True,
            'next_step': None,
            'redirect_url': None
        }

    def get_incomplete_onboarding_redirect(self):
        """Get redirect URL for incomplete onboarding"""
        status = self.get_onboarding_status()
        return status.get('redirect_url') if not status['completed'] else None

    class Meta:
        verbose_name = "Member Profile"
        verbose_name_plural = "Member Profiles"


class Company(models.Model):
    """Company/Organization Profile Model - stores company/organization information"""
    # Link to member (founder/representative)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='companies')
    
    # Company Type - moved from Member model
    company_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    # Basic Company Information (Step 1)
    company_name = models.CharField(max_length=255)
    company_logo = models.ImageField(upload_to=company_logo_upload_to, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    team_size = models.CharField(max_length=10, choices=TEAM_SIZE_CHOICES, blank=True)
    primary_location = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True)
    company_description = models.TextField(blank=True)
    organization_type = models.CharField(max_length=30, choices=ORGANIZATION_TYPE_CHOICES, blank=True)
    
    # Investor-specific fields
    investor_type = models.CharField(max_length=20, choices=INVESTOR_TYPE_CHOICES, blank=True)
    funding_size = models.CharField(max_length=20, choices=FUNDING_SIZE_CHOICES, blank=True)
    average_deal_size = models.CharField(max_length=20, choices=DEAL_SIZE_CHOICES, blank=True)
    funding_stages = models.JSONField(default=list, blank=True)  # Store multiple selections
    investment_categories = models.JSONField(default=list, blank=True)  # Store multiple selections  
    market_country_interests = models.JSONField(default=list, blank=True)  # Store multiple selections
    investment_philosophy = models.TextField(blank=True)
    
    # Corporate-specific fields
    industry_expertise = models.JSONField(default=list, blank=True)  # Store multiple industry expertise selections
    
    # Innovation Information (Step 2) - Mainly for startups
    innovation_types = models.JSONField(default=list, blank=True)  # Store multiple selections
    solution_description = models.TextField(blank=True)
    current_stage = models.CharField(max_length=20, choices=CURRENT_STAGE_CHOICES, blank=True)
    funding_needed = models.CharField(max_length=20, choices=FUNDING_NEEDED_CHOICES, blank=True)
    
    # Startup-specific fields
    # Company Information tab
    problem_statement = models.TextField(blank=True, help_text="Problem statement for startup")
    
    # Market & Traction tab
    target_markets = models.TextField(blank=True, help_text="Target markets description")
    customer_segments = models.JSONField(default=list, blank=True, help_text="Customer segments")
    active_users_count = models.CharField(max_length=100, blank=True, help_text="Number of active users")
    paying_customers_count = models.CharField(max_length=100, blank=True, help_text="Number of paying customers")
    annual_recurring_revenue = models.CharField(max_length=100, blank=True, help_text="Annual recurring revenue in USD")
    
    # Financing & Funding tab
    has_external_funding = models.BooleanField(default=False, help_text="Has secured external funding")
    funding_history = models.TextField(blank=True, help_text="Funding history details")
    amount_raised = models.CharField(max_length=100, blank=True, help_text="Amount raised in USD")
    use_of_funds = models.TextField(blank=True, help_text="Use of funds description")
    financial_projections = models.TextField(blank=True, help_text="Financial projections")
    
    # Founders and Team tab
    is_female_led = models.BooleanField(default=False, help_text="Led or co-led by female founder")
    core_team_size = models.CharField(max_length=50, blank=True, help_text="Core team size including founders")
    team_overview = models.TextField(blank=True, help_text="Team overview description")
    core_expertise = models.TextField(blank=True, help_text="Core expertise description")
    
    # Support Information (Step 3)
    support_areas = models.JSONField(default=list, blank=True)  # Store multiple selections
    support_details = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    
    # Company Status
    is_primary = models.BooleanField(default=True)  # User's main company
    is_active = models.BooleanField(default=True)
    
    # Verification fields
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending',
        help_text="Company verification status by admin"
    )
    verified_at = models.DateTimeField(blank=True, null=True, help_text="When the company was verified")
    verified_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_companies',
        help_text="Admin user who verified this company"
    )
    verification_notes = models.TextField(
        blank=True, 
        help_text="Admin notes about verification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.get_company_type_display()}) - by {self.member.user.get_full_name() or self.member.user.username}"

    def get_verification_status_color(self):
        """Get Bootstrap color class for verification status"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'under_review': 'info',
        }
        return colors.get(self.verification_status, 'secondary')

    def can_be_verified(self):
        """Check if company has enough information to be verified"""
        required_fields = [
            self.company_name,
            self.company_description,
            self.primary_location,
            self.company_type,
        ]
        return all(field for field in required_fields)

    def get_company_logo_url(self):
        """Get company logo URL with fallback to default image"""
        if self.company_logo and hasattr(self.company_logo, 'url'):
            try:
                # Import settings here to avoid circular imports
                from django.conf import settings
                
                # For R2 storage, always return the URL (cloud storage handles existence)
                if getattr(settings, 'USE_CLOUDFLARE_R2', False):
                    return self.company_logo.url
                elif settings.DEBUG:
                    # Local development - check file existence
                    import os
                    file_path = os.path.join(settings.MEDIA_ROOT, str(self.company_logo))
                    if os.path.exists(file_path):
                        return self.company_logo.url
                else:
                    # Production with local storage
                    return self.company_logo.url
            except:
                pass
        
        # Return default logo based on company type
        default_logos = {
            'startup': '/static/images/default-startup-logo.png',
            'investor': '/static/images/default-investor-logo.png', 
            'corporate': '/static/images/default-corporate-logo.png',
        }
        return default_logos.get(self.company_type, '/static/images/default-company-logo.png')

    def get_startup_profile_progress(self):
        """Calculate startup profile completion progress"""
        if self.company_type != 'startup':
            return {'total': 100, 'completed': 100, 'tabs': {}}
        
        tabs_progress = {
            'company_info': self._get_company_info_progress(),
            'innovation_info': self._get_innovation_info_progress(),
            'market_traction': self._get_market_traction_progress(),
            'financing': self._get_financing_progress(),
            'team': self._get_team_progress()
        }
        
        total_fields = sum(tab['total'] for tab in tabs_progress.values())
        completed_fields = sum(tab['completed'] for tab in tabs_progress.values())
        
        return {
            'total': total_fields,
            'completed': completed_fields,
            'percentage': round((completed_fields / total_fields * 100) if total_fields > 0 else 0),
            'tabs': tabs_progress
        }
    
    def _get_company_info_progress(self):
        """Calculate company information tab progress"""
        required_fields = [
            'company_name', 'company_description', 'website', 'founded_year',
            'team_size', 'primary_location', 'problem_statement', 'current_stage'
        ]
        
        completed = 0
        for field in required_fields:
            value = getattr(self, field, None)
            if value and str(value).strip():
                completed += 1
        
        # Check company logo
        if self.company_logo:
            completed += 1
            
        return {
            'completed': completed,
            'total': len(required_fields) + 1,  # +1 for logo
            'percentage': round((completed / (len(required_fields) + 1)) * 100),
            'status': 'complete' if completed == len(required_fields) + 1 else 'incomplete'
        }
    
    def _get_market_traction_progress(self):
        """Calculate market & traction tab progress"""
        required_fields = ['target_markets']
        completed = 0
        
        # Check text fields
        for field in required_fields:
            value = getattr(self, field, None)
            if value and str(value).strip():
                completed += 1
                
        # Check customer segments (JSON field)
        if self.customer_segments and len(self.customer_segments) > 0:
            completed += 1
            
        # Optional but counted fields
        optional_fields = ['active_users_count', 'paying_customers_count', 'annual_recurring_revenue']
        for field in optional_fields:
            value = getattr(self, field, None)
            if value and str(value).strip():
                completed += 1
        
        total_fields = len(required_fields) + 1 + len(optional_fields)  # +1 for customer_segments
        return {
            'completed': completed,
            'total': total_fields,
            'percentage': round((completed / total_fields) * 100),
            'status': 'complete' if completed >= len(required_fields) + 1 else 'incomplete'
        }
    
    def _get_financing_progress(self):
        """Calculate financing & funding tab progress"""
        completed = 0
        total_fields = 6
        
        # Always check external funding status (boolean field)
        if hasattr(self, 'has_external_funding'):
            completed += 1
            
        # If has external funding, check related fields
        if self.has_external_funding:
            if self.funding_history and self.funding_history.strip():
                completed += 1
            if self.amount_raised and self.amount_raised.strip():
                completed += 1
        else:
            # If no external funding, auto-complete these fields
            completed += 2
            
        # Check other funding fields
        if self.funding_needed and self.funding_needed.strip():
            completed += 1
        if self.use_of_funds and self.use_of_funds.strip():
            completed += 1
        if self.financial_projections and self.financial_projections.strip():
            completed += 1
            
        return {
            'completed': completed,
            'total': total_fields,
            'percentage': round((completed / total_fields) * 100),
            'status': 'complete' if completed >= 4 else 'incomplete'  # At least 4 out of 6 fields
        }
    
    def _get_team_progress(self):
        """Calculate team tab progress"""
        required_fields = ['core_team_size', 'team_overview', 'core_expertise']
        completed = 0
        
        # Check if female-led status is set (boolean field)
        if hasattr(self, 'is_female_led'):
            completed += 1
            
        # Check text fields
        for field in required_fields:
            value = getattr(self, field, None)
            if value and str(value).strip():
                completed += 1
        
        total_fields = len(required_fields) + 1  # +1 for is_female_led
        return {
            'completed': completed,
            'total': total_fields,
            'percentage': round((completed / total_fields) * 100),
            'status': 'complete' if completed == total_fields else 'incomplete'
        }

    def _get_innovation_info_progress(self):
        """Calculate innovation information tab progress"""
        required_fields = ['problem_statement', 'solution_description']
        completed = 0
        
        # Check text fields
        for field in required_fields:
            value = getattr(self, field, None)
            if value and str(value).strip():
                completed += 1
        
        # Check innovation types (JSON array field)
        if self.innovation_types and len(self.innovation_types) > 0:
            completed += 1
            
        total_fields = len(required_fields) + 1  # +1 for innovation_types
        return {
            'completed': completed,
            'total': total_fields,
            'percentage': round((completed / total_fields) * 100),
            'status': 'complete' if completed == total_fields else 'incomplete'
        }

    def get_innovation_types_display(self):
        """Return human-readable innovation types"""
        type_mapping = {
            'plastic_alternatives': 'Eliminate & Redesign Packaging',
            'recycling_technologies': 'Refill & Reuse Solutions',
            'waste_collection': 'Reusable Packaging Collection/Drop Off',
            'circular_economy': 'Upcycling Plastic Waste',
            'monitoring_tools': 'Sustainable Alternative Materials',
            'education_partnerships': 'Education & Industry Partnerships',
            'tracking_monitoring': 'Tracking & Monitoring Waste',
            'other': 'Other Innovation',
        }
        return [type_mapping.get(t, t) for t in self.innovation_types]

    def get_support_areas_display(self):
        """Return human-readable support areas"""
        area_mapping = {
            'branding_marketing': 'Branding & Marketing',
            'investment_funding': 'Investment & Funding Access',
            'manufacturing_supply': 'Manufacturing & Supply Chain',
            'market_expansion': 'Market Expansion & Customer Acquisition',
            'product_development': 'Product Development & R&D',
            'regulatory_compliance': 'Regulatory & Compliance',
        }
        return [area_mapping.get(a, a) for a in self.support_areas]

    def get_funding_stages_display(self):
        """Return human-readable funding stages"""
        stage_mapping = {
            'pre_seed': 'Pre-Seed',
            'seed': 'Seed',
            'series_a': 'Series A',
            'series_b': 'Series B',
            'series_c': 'Series C',
            'series_d': 'Series D and Above',
        }
        return [stage_mapping.get(s, s) for s in self.funding_stages]

    def get_investment_categories_display(self):
        """Return human-readable investment categories"""
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
        return [category_mapping.get(c, c) for c in self.investment_categories]

    def get_market_country_interests_display(self):
        """Return human-readable market countries"""
        country_mapping = {
            'Singapore': '🇸🇬 Singapore',
            'Indonesia': '🇮🇩 Indonesia',
            'Thailand': '🇹🇭 Thailand',
            'Malaysia': '🇲🇾 Malaysia',
            'Philippines': '🇵🇭 Philippines',
            'Vietnam': '🇻🇳 Vietnam',
            'Cambodia': '🇰🇭 Cambodia',
            'Laos': '🇱🇦 Laos',
            'Myanmar': '🇲🇲 Myanmar',
            'Brunei': '🇧🇳 Brunei',
            'Other': '🌍 Other',
        }
        return [country_mapping.get(c, c) for c in self.market_country_interests]

    def get_organization_type_display_readable(self):
        """Return human-readable organization type"""
        if self.organization_type:
            return dict(ORGANIZATION_TYPE_CHOICES).get(self.organization_type, self.organization_type)
        return '-'

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"
        unique_together = ['member', 'company_name']  # Prevent duplicate company names per member


class MemberDocument(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Brief description of the document")
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Document verification fields
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_member_documents')
    review_notes = models.TextField(blank=True)
    document_type = models.CharField(max_length=50, choices=MEMBER_DOCUMENT_TYPE_CHOICES, default='other')

    def __str__(self):
        return f"{self.name} for {self.member.user.username}"
    
    def get_status_color(self):
        """Return Bootstrap color class for status"""
        colors = {
            'pending': 'warning',
            'approved': 'success', 
            'rejected': 'danger',
            'under_review': 'info'
        }
        return colors.get(self.status, 'secondary')
        
    def get_file_size_mb(self):
        """Return file size in MB"""
        if self.file and hasattr(self.file, 'size'):
            return round(self.file.size / (1024 * 1024), 2)
        return 0
        
    def get_file_extension(self):
        """Return file extension"""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ''

    class Meta:
        verbose_name = "Member Document"
        verbose_name_plural = "Member Documents"
        ordering = ['-uploaded_at']


class CompanyDocument(models.Model):
    """Documents related to a specific company"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Brief description of the document")
    file = models.FileField(upload_to='company_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(max_length=50, choices=COMPANY_DOCUMENT_TYPE_CHOICES, default='other')
    
    # Document verification fields
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES, default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_company_documents')
    review_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} for {self.company.company_name}"
        
    def get_status_color(self):
        """Return Bootstrap color class for status"""
        colors = {
            'pending': 'warning',
            'approved': 'success', 
            'rejected': 'danger',
            'under_review': 'info'
        }
        return colors.get(self.status, 'secondary')
        
    def get_file_size_mb(self):
        """Return file size in MB"""
        if self.file and hasattr(self.file, 'size'):
            return round(self.file.size / (1024 * 1024), 2)
        return 0
        
    def get_file_extension(self):
        """Return file extension"""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ''

    class Meta:
        verbose_name = "Company Document"
        verbose_name_plural = "Company Documents"
        ordering = ['-uploaded_at']


# Challenge and Problem Statement Status Choices
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('published', 'Published'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

INNOVATION_CATEGORY_CHOICES = [
    ('', 'Select category'),
    ('Innovation', 'Innovation'),
    ('Technology', 'Technology'),
    ('Sustainability', 'Sustainability'),
    ('Social Impact', 'Social Impact'),
    ('Digital Transformation', 'Digital Transformation'),
    ('Healthcare', 'Healthcare'),
    ('Education', 'Education'),
    ('Finance', 'Finance'),
    ('Environment', 'Environment'),
    ('Agriculture', 'Agriculture'),
]


class Challenge(models.Model):
    """Innovation Challenge Model"""
    # Basic Information
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(help_text="Main challenge description and overview")
    
    # Organization Information
    organizer = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='challenges')
    organizer_contact = models.EmailField()
    
    # Challenge Details
    requirements_content = models.TextField(help_text="Rich text content for requirements and criteria")
    categories = models.JSONField(default=list, blank=True, help_text="Challenge category tags")
    
    # Timeline & Status
    application_deadline = models.DateTimeField(null=True, blank=True)
    
    # Prize Information
    has_prizes = models.BooleanField(default=False)
    main_prize_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    main_prize_currency = models.CharField(max_length=3, default='USD')
    prizes_content = models.TextField(blank=True, help_text="Rich text content for prizes and rewards")
    
    # Location & Scope
    location = models.CharField(max_length=100, blank=True)
    scope = models.CharField(max_length=100, blank=True)
    innovation_category = models.CharField(
        max_length=100, 
        choices=INNOVATION_CATEGORY_CHOICES,
        blank=True, 
        help_text="Innovation category for the challenge"
    )
    
    # Additional Resources
    challenge_brief = models.FileField(upload_to='challenge_briefs/', blank=True, null=True, help_text="Challenge brief document")
    featured_image = models.ImageField(upload_to='challenges/', blank=True, null=True)
    
    # Meta Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Statistics
    applicant_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.organizer.company_name}"
    
    def get_status_display_color(self):
        colors = {
            'draft': 'secondary',
            'pending': 'warning',
            'approved': 'info',
            'rejected': 'danger',
            'published': 'success',
        }
        return colors.get(self.status, 'secondary')
    
    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"
        ordering = ['-created_at']


class ProblemStatement(models.Model):
    """Corporate Problem Statement Model"""
    # Basic Information
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(help_text="Main problem statement description")
    
    # Company Information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='problem_statements')
    contact_email = models.EmailField()
    
    # Problem Details
    current_challenges = models.TextField(help_text="Current challenges and pain points")
    
    # New fields for enhanced problem filtering
    preferred_asean_countries = models.JSONField(default=list, blank=True, help_text="Preferred ASEAN countries for solutions")
    innovation_type = models.JSONField(default=list, blank=True, help_text="Types of innovation sought")
    startup_stage = models.JSONField(default=list, blank=True, help_text="Preferred startup maturity levels")
    
    # Solution Requirements
    solution_requirements = models.TextField(help_text="Rich text content for what they're looking for")
    technical_requirements = models.TextField(blank=True, help_text="Rich text content for technical specifications")
    
    # Collaboration Details
    timeline = models.CharField(max_length=100, blank=True)
    implementation_support = models.TextField(blank=True)
    
    # Additional Resources
    technical_specifications = models.FileField(upload_to='problem_specifications/', blank=True, null=True, help_text="Technical specifications document")
    featured_image = models.ImageField(upload_to='problems/', blank=True, null=True)
    
    # Meta Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Statistics
    solution_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_problems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.company.company_name}"
    
    def get_status_display_color(self):
        colors = {
            'draft': 'secondary',
            'pending': 'warning',
            'approved': 'info',
            'rejected': 'danger',
            'published': 'success',
        }
        return colors.get(self.status, 'secondary')
    
    class Meta:
        verbose_name = "Problem Statement"
        verbose_name_plural = "Problem Statements"
        ordering = ['-created_at']


class ChallengeDocument(models.Model):
    """Documents related to a challenge"""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='challenge_documents/')
    document_type = models.CharField(max_length=50, blank=True)  # e.g., 'brief', 'guidelines', 'template'
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} for {self.challenge.title}"
    
    class Meta:
        verbose_name = "Challenge Document"
        verbose_name_plural = "Challenge Documents"


class ProblemDocument(models.Model):
    """Documents related to a problem statement"""
    problem = models.ForeignKey(ProblemStatement, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='problem_documents/')
    document_type = models.CharField(max_length=50, blank=True)  # e.g., 'specifications', 'requirements', 'examples'
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} for {self.problem.title}"
    
    class Meta:
        verbose_name = "Problem Document"
        verbose_name_plural = "Problem Documents"


class EmailOTP(models.Model):
    """Model for storing email-based OTP for 2FA"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    session_key = models.CharField(max_length=40, blank=True, null=True)  # To associate with login session
    
    def save(self, *args, **kwargs):
        if not self.otp_code:
            # Generate 6-digit OTP
            self.otp_code = f"{secrets.randbelow(1000000):06d}"
        if not self.expires_at:
            # OTP expires in 10 minutes
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"