from django.db import models
from django.contrib.auth.models import User

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
    ('private_company', 'Private Company'),
    ('multinational_corporation', 'Multinational Corporation'),
    ('sme', 'Small or Medium-sized Enterprise (SME)'),
    ('startup_subsidiary', 'Startup Subsidiary'),
    ('other', 'Other'),
]

class Member(models.Model):
    """User Profile Model - stores individual user information"""
    # Basic user information
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # User Profile Information
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    job_position = models.CharField(max_length=255, blank=True)
    short_bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Consent fields
    consent_info = models.BooleanField(default=False)
    consent_marketplace = models.BooleanField(default=False)
    
    # Registration tracking
    profile_completed = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

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
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.get_company_type_display()}) - by {self.member.user.get_full_name() or self.member.user.username}"

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
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # e.g. pitch deck, company profile, etc.

    def __str__(self):
        return f"{self.name} for {self.member.user.username}"


class CompanyDocument(models.Model):
    """Documents related to a specific company"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='company_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(max_length=50, blank=True)  # e.g., 'pitch_deck', 'business_plan'

    def __str__(self):
        return f"{self.name} for {self.company.company_name}"

    class Meta:
        verbose_name = "Company Document"
        verbose_name_plural = "Company Documents"