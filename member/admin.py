from django.contrib import admin
from .models import Member, Company, MemberDocument, CompanyDocument

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'job_position', 'profile_completed', 'onboarding_completed', 'created_at')
    list_filter = ('profile_completed', 'onboarding_completed', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'job_position', 'short_bio')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user',)
        }),
        ('User Profile', {
            'fields': ('profile_picture', 'job_position', 'short_bio', 'phone_number', 'linkedin_url')
        }),
        ('Consent & Privacy', {
            'fields': ('consent_info', 'consent_marketplace')
        }),
        ('Status', {
            'fields': ('profile_completed', 'onboarding_completed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CompanyDocumentInline(admin.TabularInline):
    model = CompanyDocument
    extra = 0
    fields = ('name', 'document_type', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'get_member_name', 'get_company_type', 'get_organization_type', 'primary_location', 'current_stage', 'investor_type', 'is_primary', 'is_active', 'created_at')
    list_filter = ('company_type', 'organization_type', 'primary_location', 'current_stage', 'investor_type', 'is_primary', 'is_active', 'team_size', 'created_at')
    search_fields = ('company_name', 'member__user__username', 'member__user__email', 'company_description', 'solution_description', 'investment_philosophy')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CompanyDocumentInline]
    
    def get_member_name(self, obj):
        return obj.member.user.get_full_name() or obj.member.user.username
    get_member_name.short_description = 'Member'
    
    def get_company_type(self, obj):
        return obj.get_company_type_display()
    get_company_type.short_description = 'Company Type'
    
    def get_organization_type(self, obj):
        """Display organization type for corporate companies"""
        return obj.get_organization_type_display_readable()
    get_organization_type.short_description = 'Organization Type'
    
    def get_investor_type_display(self, obj):
        return obj.get_investor_type_display() if obj.investor_type else '-'
    get_investor_type_display.short_description = 'Investor Type'
    
    def get_funding_stages_list(self, obj):
        stages = obj.get_funding_stages_display() if obj.funding_stages else []
        return ', '.join(stages) if stages else '-'
    get_funding_stages_list.short_description = 'Funding Stages'
    
    def get_investment_categories_list(self, obj):
        categories = obj.get_investment_categories_display() if obj.investment_categories else []
        return ', '.join(categories) if categories else '-'
    get_investment_categories_list.short_description = 'Investment Categories'
    
    def get_industry_expertise_list(self, obj):
        """Display industry expertise for corporate users"""
        # For corporate users, we store industry expertise in support_areas or a custom field
        # Let's check investment_categories first, then support_areas
        if obj.investment_categories:
            return ', '.join(obj.investment_categories) if obj.investment_categories else '-'
        elif obj.support_areas:
            return ', '.join(obj.support_areas) if obj.support_areas else '-'
        return '-'
    get_industry_expertise_list.short_description = 'Industry Expertise'
    
    def get_technological_areas_list(self, obj):
        """Display technological areas for corporate users"""
        # For corporate users, technological areas are stored in investment_categories
        categories = obj.investment_categories if obj.investment_categories else []
        return ', '.join(categories) if categories else '-'
    get_technological_areas_list.short_description = 'Technological Areas'
    
    def get_collaboration_methods_list(self, obj):
        """Display collaboration methods for corporate users"""  
        # For corporate users, collaboration methods are stored in support_areas
        methods = obj.support_areas if obj.support_areas else []
        return ', '.join(methods) if methods else '-'
    get_collaboration_methods_list.short_description = 'Collaboration Methods'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('member', 'company_type', 'company_name', 'company_logo', 'website')
        }),
        ('Company Details', {
            'fields': ('founded_year', 'team_size', 'primary_location', 'organization_type', 'company_description')
        }),
        ('Innovation & Solution (For Startups)', {
            'fields': ('innovation_types', 'solution_description', 'current_stage', 'funding_needed'),
            'classes': ('collapse',)
        }),
        ('Investor Profile (For Investors)', {
            'fields': ('investor_type', 'funding_size', 'average_deal_size', 'funding_stages'),
            'classes': ('collapse',)
        }),
        ('Investment & Technology Focus', {
            'fields': ('investment_categories', 'market_country_interests', 'investment_philosophy'),
            'classes': ('collapse',),
            'description': 'Investment categories, market interests, and philosophy/goals'
        }),
        ('Support & Collaboration', {
            'fields': ('support_areas', 'support_details', 'additional_info'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_primary', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MemberDocument)
class MemberDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'member', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('name', 'member__user__username', 'member__user__email')

@admin.register(CompanyDocument)
class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('name', 'company__company_name', 'company__member__user__username')
