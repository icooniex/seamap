from django.contrib import admin
from .models import Member, Company, MemberDocument, CompanyDocument, Challenge, ChallengeDocument, ProblemStatement, ProblemDocument

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'job_position', 'verification_status', 'profile_completed', 'onboarding_completed', 'created_at')
    list_filter = ('verification_status', 'profile_completed', 'onboarding_completed', 'created_at')
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
        ('Verification', {
            'fields': ('verification_status', 'verified_at', 'verified_by', 'verification_notes')
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
    list_display = ('company_name', 'get_member_name', 'get_company_type', 'verification_status', 'get_organization_type', 'primary_location', 'current_stage', 'is_primary', 'is_active', 'created_at')
    list_filter = ('company_type', 'verification_status', 'organization_type', 'primary_location', 'current_stage', 'investor_type', 'is_primary', 'is_active', 'team_size', 'created_at')
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
        ('Verification', {
            'fields': ('verification_status', 'verified_at', 'verified_by', 'verification_notes')
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
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        ('Document Information', {
            'fields': ('member', 'name', 'file')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(CompanyDocument)
class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('name', 'company__company_name', 'company__member__user__username')


class ChallengeDocumentInline(admin.TabularInline):
    model = ChallengeDocument
    extra = 0
    fields = ('name', 'document_type', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_organizer_name', 'get_status_display', 'innovation_category', 'has_prizes', 'main_prize_amount', 'application_deadline', 'created_at')
    list_filter = ('status', 'innovation_category', 'has_prizes', 'scope', 'main_prize_currency', 'created_at')
    search_fields = ('title', 'subtitle', 'description', 'organizer__company_name', 'created_by__user__username', 'organizer_contact', 'location')
    readonly_fields = ('created_at', 'updated_at', 'applicant_count', 'view_count', 'published_at')
    inlines = [ChallengeDocumentInline]
    date_hierarchy = 'created_at'
    
    def get_organizer_name(self, obj):
        return obj.organizer.company_name if obj.organizer else '-'
    get_organizer_name.short_description = 'Organizer'
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Status'
    
    def get_categories_display(self, obj):
        if obj.categories:
            return ', '.join(obj.categories)
        return '-'
    get_categories_display.short_description = 'Categories'
    
    def get_prize_display(self, obj):
        if obj.has_prizes and obj.main_prize_amount:
            return f"{obj.main_prize_amount} {obj.main_prize_currency}"
        return 'No prizes' if not obj.has_prizes else 'Prizes available'
    get_prize_display.short_description = 'Prize'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'description', 'organizer', 'organizer_contact', 'created_by')
        }),
        ('Challenge Details', {
            'fields': ('requirements_content', 'categories', 'innovation_category', 'status')
        }),
        ('Timeline', {
            'fields': ('application_deadline', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Location & Scope', {
            'fields': ('location', 'scope'),
            'classes': ('collapse',)
        }),
        ('Prizes & Rewards', {
            'fields': ('has_prizes', 'main_prize_amount', 'main_prize_currency', 'prizes_content'),
            'classes': ('collapse',)
        }),
        ('Media & Documents', {
            'fields': ('featured_image', 'challenge_brief'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('applicant_count', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_challenges', 'reject_challenges', 'publish_challenges']
    
    def approve_challenges(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} challenges were approved.')
    approve_challenges.short_description = "Approve selected challenges"
    
    def reject_challenges(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} challenges were rejected.')
    reject_challenges.short_description = "Reject selected challenges"
    
    def publish_challenges(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='approved').update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} approved challenges were published.')
    publish_challenges.short_description = "Publish approved challenges"


@admin.register(ChallengeDocument)
class ChallengeDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_challenge_title', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('name', 'challenge__title', 'challenge__organizer__company_name')
    readonly_fields = ('uploaded_at',)
    
    def get_challenge_title(self, obj):
        return obj.challenge.title
    get_challenge_title.short_description = 'Challenge'


class ProblemDocumentInline(admin.TabularInline):
    model = ProblemDocument
    extra = 0
    fields = ('name', 'document_type', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(ProblemStatement)
class ProblemStatementAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_company_name', 'get_status_display', 'get_preferred_countries', 'timeline', 'created_at')
    list_filter = ('status', 'timeline', 'created_at')
    search_fields = ('title', 'subtitle', 'description', 'company__company_name', 'created_by__user__username', 'contact_email', 'current_challenges')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProblemDocumentInline]
    date_hierarchy = 'created_at'
    
    def get_company_name(self, obj):
        return obj.company.company_name if obj.company else '-'
    get_company_name.short_description = 'Company'
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'Status'
    
    def get_preferred_countries(self, obj):
        if obj.preferred_asean_countries:
            return ', '.join([country.title() for country in obj.preferred_asean_countries])
        return '-'
    get_preferred_countries.short_description = 'Preferred ASEAN Countries'
    
    def get_innovation_types(self, obj):
        if obj.innovation_type:
            return ', '.join([itype.title() for itype in obj.innovation_type])
        return '-'
    get_innovation_types.short_description = 'Innovation Types'
    
    def get_startup_stages(self, obj):
        if obj.startup_stage:
            return ', '.join([stage.title() for stage in obj.startup_stage])
        return '-'
    get_startup_stages.short_description = 'Startup Stages'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'description', 'company', 'contact_email', 'created_by')
        }),
        ('Problem Details', {
            'fields': ('current_challenges', 'status')
        }),
        ('Preferences & Requirements', {
            'fields': ('preferred_asean_countries', 'innovation_type', 'startup_stage'),
            'classes': ('collapse',)
        }),
        ('Solution Requirements', {
            'fields': ('solution_requirements', 'technical_requirements'),
            'classes': ('collapse',)
        }),
        ('Collaboration Details', {
            'fields': ('timeline', 'implementation_support'),
            'classes': ('collapse',)
        }),
        ('Media & Documents', {
            'fields': ('featured_image', 'technical_specifications'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_problems', 'reject_problems', 'publish_problems']
    
    def approve_problems(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} problem statements were approved.')
    approve_problems.short_description = "Approve selected problem statements"
    
    def reject_problems(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} problem statements were rejected.')
    reject_problems.short_description = "Reject selected problem statements"
    
    def publish_problems(self, request, queryset):
        from django.utils import timezone
        # Update status and set published_at timestamp for approved problems
        approved_problems = queryset.filter(status='approved')
        updated = approved_problems.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} approved problem statements were published.')
    publish_problems.short_description = "Publish approved problem statements"


@admin.register(ProblemDocument)
class ProblemDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_problem_title', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('name', 'problem__title', 'problem__company__company_name')
    readonly_fields = ('uploaded_at',)
    
    def get_problem_title(self, obj):
        return obj.problem.title
    get_problem_title.short_description = 'Problem Statement'
