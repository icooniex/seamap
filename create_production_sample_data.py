#!/usr/bin/env python
"""
Simple script to create sample data for Railway deployment
This script will be run after migration in production
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seamap.settings')

try:
    django.setup()
    print("Django setup successful")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from member.models import Member, Company

def create_sample_data():
    """Create basic sample data if database is empty"""
    
    try:
        # Check database connection
        print(f"Checking database connection...")
        company_count = Company.objects.count()
        print(f"Current company count: {company_count}")
        
        # Only create if no companies exist
        if company_count > 0:
            print("Sample data already exists, skipping...")
            return
        
        print("Creating sample data for production...")
        
        # Create sample startup
        print("Creating startup user and company...")
        user1, created = User.objects.get_or_create(
            username='ecopack_demo',
            defaults={
                'email': 'demo@ecopack.com',
                'first_name': 'Demo',
                'last_name': 'Founder',
            }
        )
        print(f"Startup user created: {created}")
        
        member1, created = Member.objects.get_or_create(
            user=user1,
            defaults={
                'job_position': 'CEO',
                'short_bio': 'Demo startup founder',
                'consent_info': True,
                'consent_marketplace': True,
                'profile_completed': True,
                'onboarding_completed': True,
            }
        )
        print(f"Startup member created: {created}")
        
        company1, created = Company.objects.get_or_create(
            member=member1,
            company_name='EcoPack Demo',
            defaults={
                'company_type': 'startup',
                'website': 'https://ecopack-demo.com',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'Demo eco-friendly packaging startup',
                'innovation_types': ['plastic_alternatives'],
                'current_stage': 'early',
                'funding_needed': '500k_1m',
            }
        )
        print(f"Startup company created: {created}")
        
        # Create sample investor
        print("Creating investor user and company...")
        user2, created = User.objects.get_or_create(
            username='investor_demo',
            defaults={
                'email': 'demo@investor.com',
                'first_name': 'Demo',
                'last_name': 'Investor',
            }
        )
        print(f"Investor user created: {created}")
        
        member2, created = Member.objects.get_or_create(
            user=user2,
            defaults={
                'job_position': 'Managing Partner',
                'short_bio': 'Demo investor',
                'consent_info': True,
                'consent_marketplace': True,
                'profile_completed': True,
                'onboarding_completed': True,
            }
        )
        print(f"Investor member created: {created}")
        
        company2, created = Company.objects.get_or_create(
            member=member2,
            company_name='Demo Ventures',
            defaults={
                'company_type': 'investor',
                'website': 'https://demo-ventures.com',
                'founded_year': 2020,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'Demo venture capital fund',
                'investor_type': 'vc',
                'funding_size': '100m_200m',
                'average_deal_size': '1m_5m',
                'funding_stages': ['seed', 'series_a'],
                'investment_categories': ['eliminate_redesign', 'advanced_recycling'],
                'market_country_interests': ['Singapore', 'Thailand'],
            }
        )
        print(f"Investor company created: {created}")
        
        # Create sample corporate
        print("Creating corporate user and company...")
        user3, created = User.objects.get_or_create(
            username='corporate_demo',
            defaults={
                'email': 'demo@corporate.com',
                'first_name': 'Demo',
                'last_name': 'Corporate',
            }
        )
        print(f"Corporate user created: {created}")
        
        member3, created = Member.objects.get_or_create(
            user=user3,
            defaults={
                'job_position': 'Innovation Director',
                'short_bio': 'Demo corporate representative',
                'consent_info': True,
                'consent_marketplace': True,
                'profile_completed': True,
                'onboarding_completed': True,
            }
        )
        print(f"Corporate member created: {created}")
        
        company3, created = Company.objects.get_or_create(
            member=member3,
            company_name='Demo Corporation',
            defaults={
                'company_type': 'corporate',
                'website': 'https://demo-corp.com',
                'founded_year': 2000,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Demo multinational corporation',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['manufacturing', 'sustainability'],
                'support_areas': ['investment_funding', 'manufacturing_supply'],
            }
        )
        print(f"Corporate company created: {created}")
        
        # Final count
        final_count = Company.objects.count()
        startup_count = Company.objects.filter(company_type='startup').count()
        investor_count = Company.objects.filter(company_type='investor').count()
        corporate_count = Company.objects.filter(company_type='corporate').count()
        
        print(f"Sample data creation completed!")
        print(f"Total companies: {final_count}")
        print(f"- Startups: {startup_count}")
        print(f"- Investors: {investor_count}")  
        print(f"- Corporates: {corporate_count}")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_sample_data()
