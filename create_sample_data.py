#!/usr/bin/env python
"""
Script to create sample data for SEAmap platform
Creates 6 users with profiles and companies (2 startups, 2 investors, 2 corporates)
All focused on plastic circularity and waste management
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seamap.settings')
django.setup()

from django.contrib.auth.models import User
from member.models import Member, Company

# Store login credentials for display
login_credentials = []


def create_user_and_member(username, email, first_name, last_name, job_position="", bio="", password="seamap2025"):
    """Create a user and associated member profile"""
    global login_credentials
    
    try:
        # Try to get existing user first
        user = User.objects.get(username=username)
        print(f"User {username} already exists, updating...")
        # Update password in case it changed
        user.set_password(password)
        user.save()
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        print(f"Created user: {username}")
    
    # Store credentials for display
    login_credentials.append({
        'username': username,
        'email': email,
        'password': password,
        'name': f"{first_name} {last_name}",
        'role': job_position
    })
    
    # Create or get member profile
    member, created = Member.objects.get_or_create(
        user=user,
        defaults={
            'job_position': job_position,
            'short_bio': bio,
            'consent_info': True,
            'consent_marketplace': True,
            'profile_completed': True,
            'onboarding_completed': True,
            'verification_status': 'approved',  # Pre-approve for demo
        }
    )
    
    if not created:
        # Update existing member
        member.job_position = job_position
        member.short_bio = bio
        member.profile_completed = True
        member.onboarding_completed = True
        member.verification_status = 'approved'
        member.save()
        print(f"Updated member profile for: {username}")
    else:
        print(f"Created member profile for: {username}")
    
    return user, member


def create_startup_companies():
    """Create 2 sample startup companies focused on plastic circularity"""
    startups_data = [
        {
            'user_data': {
                'username': 'ecopack_founder',
                'email': 'founder@ecopack.asia',
                'first_name': 'Siriporn',
                'last_name': 'Thanakit',
                'job_position': 'CEO & Founder',
                'bio': 'Environmental engineer turned entrepreneur. 8 years developing biodegradable packaging solutions from agricultural waste. Passionate about replacing single-use plastics across Southeast Asia.',
                'password': 'ecopack2024'
            },
            'company_data': {
                'company_name': 'EcoPack Solutions',
                'website': 'https://ecopack.asia',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'EcoPack Solutions develops biodegradable packaging materials from agricultural waste, specifically rice husks and corn starch. Our mission is to replace single-use plastics with sustainable alternatives that decompose naturally within 90 days.',
                'innovation_types': ['plastic_alternatives', 'circular_economy', 'waste_collection'],
                'solution_description': 'We create compostable packaging from agricultural waste that performs as well as traditional plastics but breaks down completely in 90 days in industrial composting facilities.',
                'current_stage': 'early',
                'funding_needed': '500k_1m',
                'problem_statement': 'Traditional plastic packaging takes hundreds of years to decompose, contributing to environmental pollution and harming marine ecosystems, especially in Southeast Asia where plastic waste management is inadequate.',
                'target_markets': 'Food and beverage industry, e-commerce retailers, restaurant chains across Southeast Asia',
                'customer_segments': ['food_beverage', 'ecommerce', 'retail'],
                'active_users_count': '180+ business customers',
                'paying_customers_count': '120 active paying customers',
                'annual_recurring_revenue': '$320,000',
                'has_external_funding': True,
                'funding_history': 'Received $150K seed funding from Thai government innovation fund and local angel investors in 2023',
                'amount_raised': '$150,000',
                'use_of_funds': 'Product development, manufacturing scale-up, market expansion to Malaysia and Philippines',
                'financial_projections': 'Projecting $800K revenue by end of 2025 with 45% gross margins',
                'is_female_led': True,
                'core_team_size': '7 people including 2 co-founders',
                'team_overview': 'Our team combines expertise in materials science, environmental engineering, and business development with experience from Dow Chemical and CP Group.',
                'core_expertise': 'Biodegradable materials research, sustainable manufacturing processes, B2B sales, regulatory compliance',
                'support_areas': ['manufacturing_supply', 'market_expansion', 'investment_funding'],
                'support_details': 'Seeking manufacturing partners for scale-up, distribution channels across ASEAN, and Series A funding of $800K-1.2M.',
                'additional_info': 'Our products are certified compostable (ASTM D6400, EN 13432) and meet international food safety standards. Processed 50 tons of agricultural waste in 2024.'
            }
        },
        {
            'user_data': {
                'username': 'plasticfree_ceo',
                'email': 'ceo@plasticfree.sg',
                'first_name': 'Marcus',
                'last_name': 'Lim',
                'job_position': 'Co-Founder & CEO',
                'bio': 'Former McKinsey consultant with 10 years in sustainability consulting. Built 2 previous cleantech companies. Expert in circular economy business models and corporate sustainability transformation.',
                'password': 'plasticfree2024'
            },
            'company_data': {
                'company_name': 'PlasticFree Innovations',
                'website': 'https://plasticfree.sg',
                'founded_year': 2021,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'PlasticFree Innovations operates a B2B platform connecting businesses with verified sustainable packaging alternatives. We help companies transition from plastic to eco-friendly materials with full supply chain integration.',
                'innovation_types': ['plastic_alternatives', 'tracking_monitoring', 'education_partnerships'],
                'solution_description': 'Our SaaS platform provides end-to-end sustainable packaging solutions including material sourcing, supplier verification, impact tracking, and carbon footprint measurement.',
                'current_stage': 'scaling',
                'funding_needed': '1m_5m',
                'problem_statement': 'Businesses struggle to find reliable, cost-effective sustainable packaging alternatives and lack visibility into their environmental impact and supply chain sustainability.',
                'target_markets': 'FMCG companies, e-commerce platforms, food delivery services, retail chains across ASEAN',
                'customer_segments': ['fmcg', 'ecommerce', 'retail'],
                'active_users_count': '450+ corporate users',
                'paying_customers_count': '280 enterprise customers',
                'annual_recurring_revenue': '$1,800,000',
                'has_external_funding': True,
                'funding_history': 'Series A: $2.5M from Temasek Holdings, Wavemaker Partners, and Sequoia Capital India in 2023',
                'amount_raised': '$2,500,000',
                'use_of_funds': 'Regional expansion to Indonesia, Thailand, Malaysia; technology development; team scaling',
                'financial_projections': 'Targeting $6M ARR by 2026 with expansion to 5 ASEAN countries and 1000+ customers',
                'is_female_led': False,
                'core_team_size': '16 people across engineering, sales, operations',
                'team_overview': 'Team of ex-consultants, sustainability experts, and tech professionals from Google, Grab, McKinsey, and Unilever.',
                'core_expertise': 'B2B SaaS development, supply chain management, sustainability consulting, enterprise sales',
                'support_areas': ['market_expansion', 'investment_funding', 'manufacturing_supply'],
                'support_details': 'Seeking Series B funding for regional expansion and partnerships with multinational corporations and government agencies.',
                'additional_info': 'Platform has processed over $35M in sustainable packaging transactions and helped customers save 1.5M kg of plastic waste annually.'
            }
        }
    ]
    
    for startup in startups_data:
        user, member = create_user_and_member(**startup['user_data'])
        
        # Create company
        company_data = startup['company_data']
        company_data['member'] = member
        company_data['company_type'] = 'startup'
        company_data['verification_status'] = 'approved'  # Pre-approve for demo
        
        company, created = Company.objects.get_or_create(
            member=member,
            company_name=company_data['company_name'],
            defaults=company_data
        )
        
        if not created:
            # Update existing company
            for key, value in company_data.items():
                if key != 'member':
                    setattr(company, key, value)
            company.save()
            print(f"Updated startup company: {company.company_name}")
        else:
            print(f"Created startup company: {company.company_name}")


def create_investor_companies():
    """Create 2 sample investor companies focused on plastic circularity"""
    investors_data = [
        {
            'user_data': {
                'username': 'circular_vc_partner',
                'email': 'partner@circularvc.asia',
                'first_name': 'David',
                'last_name': 'Chen',
                'job_position': 'Managing Partner',
                'bio': 'Former Goldman Sachs investment banker with 15+ years in venture capital. Specialized in sustainability and circular economy investments across Asia-Pacific. Led 40+ investments in cleantech startups.',
                'password': 'circularvc2024'
            },
            'company_data': {
                'company_name': 'Circular Ventures Asia',
                'website': 'https://circularvc.asia',
                'founded_year': 2019,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'Circular Ventures Asia is a leading early-stage VC fund focused exclusively on circular economy and plastic waste solutions across Southeast Asia. We invest in companies transforming waste into value.',
                'investor_type': 'vc',
                'funding_size': '100m_200m',
                'average_deal_size': '500k_1m',
                'funding_stages': ['pre_seed', 'seed', 'series_a'],
                'investment_categories': ['plastic_alternatives', 'recycling_technologies', 'waste_collection', 'tracking_monitoring'],
                'market_country_interests': ['Singapore', 'Indonesia', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam'],
                'investment_philosophy': 'We invest in early-stage startups solving plastic waste challenges with scalable technology solutions. Focus on companies that can achieve both significant environmental impact and strong financial returns in the circular economy.',
                'support_areas': ['investment_funding', 'market_expansion', 'manufacturing_supply'],
                'support_details': 'We provide hands-on support including business development, strategic partnerships, follow-on funding, and access to our extensive network of corporates, government agencies, and manufacturing partners.',
                'additional_info': 'Portfolio includes 35 companies across plastic alternatives, waste management, and circular economy with total portfolio value of $400M. Combined portfolio impact: 800K tons plastic waste diverted annually.'
            }
        },
        {
            'user_data': {
                'username': 'ocean_impact_gp',
                'email': 'gp@oceanimpact.fund',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'job_position': 'General Partner',
                'bio': 'Impact investing veteran with PhD in Marine Biology. 18+ years building sustainable businesses across emerging markets. Former World Bank consultant on ocean plastic pollution initiatives.',
                'password': 'oceanimpact2024'
            },
            'company_data': {
                'company_name': 'Ocean Impact Fund',
                'website': 'https://oceanimpact.fund',
                'founded_year': 2018,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'Ocean Impact Fund is a specialized impact investment fund dedicated to marine plastic pollution solutions and ocean conservation across Southeast Asia. We target scalable solutions with measurable environmental impact.',
                'investor_type': 'impact_fund',
                'funding_size': '1m_50m',
                'average_deal_size': '1m_5m',
                'funding_stages': ['seed', 'series_a', 'series_b'],
                'investment_categories': ['waste_collection', 'recycling_technologies', 'tracking_monitoring', 'education_partnerships'],
                'market_country_interests': ['Thailand', 'Indonesia', 'Philippines', 'Vietnam', 'Malaysia'],
                'investment_philosophy': 'We target companies delivering measurable ocean plastic reduction alongside financial returns. Focus on waste collection, advanced recycling, and monitoring technologies with proven impact metrics.',
                'support_areas': ['investment_funding', 'regulatory_compliance', 'impact_measurement'],
                'support_details': 'Beyond capital, we provide impact measurement frameworks, regulatory guidance, connections to government and NGO partners, and access to scientific research networks.',
                'additional_info': 'Portfolio has prevented 1.2M tons of plastic from entering oceans, created 3,000+ green jobs, and operates in 8 countries across Southeast Asia and Pacific.'
            }
        }
    ]
    
    for investor in investors_data:
        user, member = create_user_and_member(**investor['user_data'])
        
        # Create company
        company_data = investor['company_data']
        company_data['member'] = member
        company_data['company_type'] = 'investor'
        company_data['verification_status'] = 'approved'  # Pre-approve for demo
        
        company, created = Company.objects.get_or_create(
            member=member,
            company_name=company_data['company_name'],
            defaults=company_data
        )
        
        if not created:
            # Update existing company
            for key, value in company_data.items():
                if key != 'member':
                    setattr(company, key, value)
            company.save()
            print(f"Updated investor company: {company.company_name}")
        else:
            print(f"Created investor company: {company.company_name}")


def create_corporate_companies():
    """Create 2 sample corporate companies focused on plastic circularity"""
    corporates_data = [
        {
            'user_data': {
                'username': 'unilever_sustainability',
                'email': 'sustainability@unilever.com.sg',
                'first_name': 'Jennifer',
                'last_name': 'Lim',
                'job_position': 'Head of Sustainable Innovation',
                'bio': 'Leading Unilever\'s plastic circularity initiatives across Southeast Asia. 12+ years in corporate sustainability and open innovation. Expert in sustainable packaging and supply chain transformation.',
                'password': 'unilever2024'
            },
            'company_data': {
                'company_name': 'Unilever Southeast Asia',
                'website': 'https://unilever.com.sg',
                'founded_year': 1885,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Unilever is a leading multinational consumer goods company committed to sustainable living. We are transforming our packaging to be 100% reusable, recyclable, or compostable while reducing plastic waste across our value chain.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['consumer_goods', 'sustainable_packaging', 'supply_chain', 'circular_economy'],
                'innovation_types': ['plastic_alternatives', 'refill_reuse', 'recycling_technologies'],
                'support_areas': ['investment_funding', 'manufacturing_supply', 'market_expansion'],
                'support_details': 'We offer corporate venture capital through Unilever Ventures, strategic partnerships, pilot opportunities, manufacturing scale-up support, and market access across our global distribution network.',
                'additional_info': 'Committed to halving virgin plastic use by 2025. Annual revenue of $60B+ globally. Operating plastic waste collection programs in Indonesia, Philippines, and Thailand reaching 100,000+ households.'
            }
        },
        {
            'user_data': {
                'username': 'scg_circular_director',
                'email': 'circular@scg.com',
                'first_name': 'Supachai',
                'last_name': 'Wichianchai',
                'job_position': 'Director, Circular Economy',
                'bio': 'Leading SCG\'s circular economy transformation across ASEAN. 15+ years in materials science and industrial innovation. Expert in chemical recycling and advanced materials development.',
                'password': 'scgcircular2024'
            },
            'company_data': {
                'company_name': 'SCG Circular Economy Solutions',
                'website': 'https://scg.com/circular',
                'founded_year': 1913,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'SCG is a leading industrial conglomerate pioneering circular economy solutions across ASEAN. We develop advanced recycling technologies, sustainable materials, and circular business models for plastic waste valorization.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['chemicals', 'advanced_materials', 'recycling_technology', 'manufacturing'],
                'innovation_types': ['recycling_technologies', 'plastic_alternatives', 'tracking_monitoring'],
                'support_areas': ['manufacturing_supply', 'product_development', 'investment_funding'],
                'support_details': 'We provide manufacturing partnerships, chemical recycling R&D, scale-up facilities, distribution networks, corporate venture investments, and access to circular economy expertise.',
                'additional_info': 'Revenue of $15B+ with operations across ASEAN. Operates 3 chemical recycling plants processing 30,000 tons annually. Committed to carbon neutrality by 2050 and leading regional circular economy initiatives.'
            }
        }
    ]
    
    for corporate in corporates_data:
        user, member = create_user_and_member(**corporate['user_data'])
        
        # Create company
        company_data = corporate['company_data']
        company_data['member'] = member
        company_data['company_type'] = 'corporate'
        company_data['verification_status'] = 'approved'  # Pre-approve for demo
        
        company, created = Company.objects.get_or_create(
            member=member,
            company_name=company_data['company_name'],
            defaults=company_data
        )
        
        if not created:
            # Update existing company
            for key, value in company_data.items():
                if key != 'member':
                    setattr(company, key, value)
            company.save()
            print(f"Updated corporate company: {company.company_name}")
        else:
            print(f"Created corporate company: {company.company_name}")


def print_login_credentials():
    """Print all login credentials for easy testing"""
    print("\n" + "="*60)
    print("🔐 LOGIN CREDENTIALS FOR TESTING")
    print("="*60)
    
    # Group by company type
    startups = [cred for cred in login_credentials if 'founder' in cred['username'] or 'ceo' in cred['username']]
    investors = [cred for cred in login_credentials if 'vc' in cred['username'] or 'impact' in cred['username']]
    corporates = [cred for cred in login_credentials if 'unilever' in cred['username'] or 'scg' in cred['username']]
    
    print("\n🚀 STARTUP USERS:")
    for cred in startups:
        print(f"  Name: {cred['name']} ({cred['role']})")
        print(f"  Email: {cred['email']}")
        print(f"  Password: {cred['password']}")
        print(f"  ---")
    
    print("\n💰 INVESTOR USERS:")
    for cred in investors:
        print(f"  Name: {cred['name']} ({cred['role']})")
        print(f"  Email: {cred['email']}")
        print(f"  Password: {cred['password']}")
        print(f"  ---")
    
    print("\n🏢 CORPORATE USERS:")
    for cred in corporates:
        print(f"  Name: {cred['name']} ({cred['role']})")
        print(f"  Email: {cred['email']}")
        print(f"  Password: {cred['password']}")
        print(f"  ---")
    
    print("\n💡 QUICK LOGIN TIPS:")
    print("  - All accounts are pre-verified for immediate access")
    print("  - Use email address as username for login")
    print("  - All profiles are complete with sample data")
    print("  - Companies have realistic plastic circularity focus")
    print("="*60)


def main():
    """Main function to create all sample data"""
    print("Creating sample company profiles focused on plastic circularity...")
    print("=" * 60)
    
    print("\n🚀 Creating 2 Startup Companies...")
    create_startup_companies()
    
    print("\n💰 Creating 2 Investor Companies...")
    create_investor_companies()
    
    print("\n🏢 Creating 2 Corporate Companies...")
    create_corporate_companies()
    
    print("\n" + "=" * 60)
    print("✅ Sample data creation completed!")
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Members: {Member.objects.count()}")
    print(f"Total Companies: {Company.objects.count()}")
    print(f"- Startups: {Company.objects.filter(company_type='startup').count()}")
    print(f"- Investors: {Company.objects.filter(company_type='investor').count()}")
    print(f"- Corporates: {Company.objects.filter(company_type='corporate').count()}")
    
    # Print login credentials
    print_login_credentials()


if __name__ == "__main__":
    main()
