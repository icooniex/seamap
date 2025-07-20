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

class Member(models.Model):
    # Basic user information
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    # Company Information (Step 1)
    company_name = models.CharField(max_length=255, blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    team_size = models.CharField(max_length=10, choices=TEAM_SIZE_CHOICES, blank=True)
    primary_location = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True)
    company_description = models.TextField(blank=True)
    
    # Innovation Information (Step 2)
    innovation_types = models.JSONField(default=list, blank=True)  # Store multiple selections
    solution_description = models.TextField(blank=True)
    current_stage = models.CharField(max_length=20, choices=CURRENT_STAGE_CHOICES, blank=True)
    funding_needed = models.CharField(max_length=20, choices=FUNDING_NEEDED_CHOICES, blank=True)
    
    # Support Information (Step 3)
    support_areas = models.JSONField(default=list, blank=True)  # Store multiple selections
    support_details = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    
    # Consent fields
    consent_info = models.BooleanField(default=False)
    consent_marketplace = models.BooleanField(default=False)
    
    # Registration tracking
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type}) - {self.company_name}"

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

class MemberDocument(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # e.g. pitch deck, company profile, etc.

    def __str__(self):
        return f"{self.name} for {self.member.user.username}"