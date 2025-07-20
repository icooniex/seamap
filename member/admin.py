from django.contrib import admin
from .models import Member, MemberDocument

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'user_type', 'primary_location', 'onboarding_completed', 'created_at')
    list_filter = ('user_type', 'primary_location', 'onboarding_completed', 'current_stage', 'created_at')
    search_fields = ('company_name', 'user__username', 'user__email', 'solution_description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'user_type', 'onboarding_completed')
        }),
        ('Company Information', {
            'fields': ('company_name', 'website', 'founded_year', 'team_size', 'primary_location', 'company_description')
        }),
        ('Innovation & Solution', {
            'fields': ('innovation_types', 'solution_description', 'current_stage', 'funding_needed')
        }),
        ('Support Requirements', {
            'fields': ('support_areas', 'support_details', 'additional_info')
        }),
        ('Consent & Privacy', {
            'fields': ('consent_info', 'consent_marketplace')
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
    search_fields = ('name', 'member__company_name', 'member__user__username')
