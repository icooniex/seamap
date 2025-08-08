#!/usr/bin/env python
"""
Script to create sample company profiles for SEAmap platform
Creates 5 companies each for startup, investor, and corporate types
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


def create_user_and_member(username, email, first_name, last_name, job_position="", bio=""):
    """Create a user and associated member profile"""
    try:
        # Try to get existing user first
        user = User.objects.get(username=username)
        print(f"User {username} already exists, updating...")
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password='password123'  # Simple password for demo
        )
        print(f"Created user: {username}")
    
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
        }
    )
    
    if not created:
        # Update existing member
        member.job_position = job_position
        member.short_bio = bio
        member.profile_completed = True
        member.onboarding_completed = True
        member.save()
        print(f"Updated member profile for: {username}")
    else:
        print(f"Created member profile for: {username}")
    
    return user, member


def create_startup_companies():
    """Create 5 sample startup companies"""
    startups_data = [
        {
            'user_data': {
                'username': 'ecopack_founder',
                'email': 'founder@ecopack.co.th',
                'first_name': 'Siriporn',
                'last_name': 'Thanakit',
                'job_position': 'CEO & Founder',
                'bio': 'Environmental engineer turned entrepreneur. Passionate about reducing plastic waste through innovative packaging solutions.'
            },
            'company_data': {
                'company_name': 'EcoPack Thailand',
                'website': 'https://ecopack.co.th',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'EcoPack Thailand develops biodegradable packaging solutions made from agricultural waste. Our mission is to replace single-use plastics with sustainable alternatives that decompose naturally.',
                'innovation_types': ['plastic_alternatives', 'circular_economy'],
                'solution_description': 'We create compostable packaging from rice husks and corn starch that performs as well as traditional plastics but breaks down completely in 90 days.',
                'current_stage': 'early',
                'funding_needed': '500k_1m',
                'problem_statement': 'Traditional plastic packaging takes hundreds of years to decompose, contributing to environmental pollution and harming marine ecosystems.',
                'target_markets': 'Food and beverage industry, e-commerce retailers, restaurant chains across Southeast Asia',
                'customer_segments': ['food_beverage', 'ecommerce'],
                'active_users_count': '250+ business customers',
                'paying_customers_count': '180 active paying customers',
                'annual_recurring_revenue': '$450,000',
                'has_external_funding': True,
                'funding_history': 'Received $150K seed funding from local angel investors in 2022',
                'amount_raised': '$150,000',
                'use_of_funds': 'Product development, manufacturing scale-up, and market expansion',
                'financial_projections': 'Projecting $1.2M revenue by end of 2025 with 40% gross margins',
                'is_female_led': True,
                'core_team_size': '8 people including 3 founders',
                'team_overview': 'Our team combines expertise in materials science, environmental engineering, and business development.',
                'core_expertise': 'Biodegradable materials research, sustainable manufacturing processes, B2B sales',
                'support_areas': ['manufacturing_supply', 'market_expansion', 'investment_funding'],
                'support_details': 'Looking for manufacturing partners, distribution channels, and Series A funding.',
                'additional_info': 'Our products are certified compostable and meet international food safety standards.'
            }
        },
        {
            'user_data': {
                'username': 'plasticfree_ceo',
                'email': 'ceo@plasticfree.sg',
                'first_name': 'Marcus',
                'last_name': 'Lim',
                'job_position': 'Co-Founder & CEO',
                'bio': 'Former McKinsey consultant with 8 years in sustainability. Building the future of plastic-free living.'
            },
            'company_data': {
                'company_name': 'PlasticFree Solutions',
                'website': 'https://plasticfree.sg',
                'founded_year': 2021,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'PlasticFree Solutions is a B2B platform connecting businesses with sustainable packaging alternatives. We help companies transition from plastic to eco-friendly materials.',
                'innovation_types': ['plastic_alternatives', 'waste_collection', 'education_partnerships'],
                'solution_description': 'Our platform provides end-to-end sustainable packaging solutions including material sourcing, supplier verification, and impact tracking.',
                'current_stage': 'scaling',
                'funding_needed': '1m_5m',
                'problem_statement': 'Businesses struggle to find reliable, cost-effective sustainable packaging alternatives and lack visibility into their environmental impact.',
                'target_markets': 'FMCG companies, e-commerce platforms, food delivery services across ASEAN',
                'customer_segments': ['fmcg', 'ecommerce'],
                'active_users_count': '500+ corporate users',
                'paying_customers_count': '320 enterprise customers',
                'annual_recurring_revenue': '$2,100,000',
                'has_external_funding': True,
                'funding_history': 'Series A: $3M from Temasek Holdings and Wavemaker Partners in 2023',
                'amount_raised': '$3,000,000',
                'use_of_funds': 'Regional expansion, technology development, team scaling',
                'financial_projections': 'Targeting $8M ARR by 2026 with expansion to 5 ASEAN countries',
                'is_female_led': False,
                'core_team_size': '18 people across eng, sales, operations',
                'team_overview': 'Team of ex-consultants, sustainability experts, and tech professionals from Google, Grab, and McKinsey.',
                'core_expertise': 'B2B sales, supply chain management, sustainability consulting, platform development',
                'support_areas': ['market_expansion', 'investment_funding', 'regulatory_compliance'],
                'support_details': 'Seeking Series B funding for regional expansion and partnerships with multinational corporations.',
                'additional_info': 'We have processed over $50M in sustainable packaging transactions and saved 2M kg of plastic waste.'
            }
        },
        {
            'user_data': {
                'username': 'oceanclean_founder',
                'email': 'founder@oceanclean.id',
                'first_name': 'Dewi',
                'last_name': 'Kusuma',
                'job_position': 'Founder & CTO',
                'bio': 'Marine biologist and tech entrepreneur dedicated to cleaning our oceans through innovative waste collection technology.'
            },
            'company_data': {
                'company_name': 'OceanClean Indonesia',
                'website': 'https://oceanclean.id',
                'founded_year': 2023,
                'team_size': '2-5',
                'primary_location': 'Indonesia',
                'company_description': 'OceanClean develops autonomous marine robots that collect plastic waste from rivers and coastal areas before it reaches the ocean.',
                'innovation_types': ['waste_collection', 'tracking_monitoring', 'recycling_technologies'],
                'solution_description': 'Our solar-powered robots use AI and computer vision to identify and collect plastic waste, with real-time monitoring and data analytics.',
                'current_stage': 'prototype',
                'funding_needed': '100k_500k',
                'problem_statement': '8 million tons of plastic enter our oceans annually, with 80% coming from rivers. Current collection methods are inefficient and costly.',
                'target_markets': 'Government agencies, environmental NGOs, corporate sustainability programs in Southeast Asia',
                'customer_segments': ['government', 'ngo'],
                'active_users_count': '3 pilot projects',
                'paying_customers_count': '1 paying customer (Jakarta government)',
                'annual_recurring_revenue': '$45,000',
                'has_external_funding': False,
                'funding_history': 'Self-funded with $25K personal savings',
                'amount_raised': '$0',
                'use_of_funds': 'Product development, field testing, team expansion',
                'financial_projections': 'Targeting $500K revenue in 2025 with 10 deployed units',
                'is_female_led': True,
                'core_team_size': '4 people including founder',
                'team_overview': 'Team combines marine biology expertise, robotics engineering, and environmental science.',
                'core_expertise': 'Marine robotics, AI/computer vision, environmental monitoring, sustainability',
                'support_areas': ['product_development', 'investment_funding', 'regulatory_compliance'],
                'support_details': 'Need funding for prototype development and seeking regulatory guidance for marine operations.',
                'additional_info': 'Our prototype has successfully collected 500kg of plastic waste in trials along Jakarta rivers.'
            }
        },
        {
            'user_data': {
                'username': 'circularpack_ceo',
                'email': 'ceo@circularpack.my',
                'first_name': 'Ahmad',
                'last_name': 'Rahman',
                'job_position': 'CEO & Co-Founder',
                'bio': 'Former P&G executive with 12 years in packaging innovation. Committed to creating a circular economy for packaging materials.'
            },
            'company_data': {
                'company_name': 'CircularPack Malaysia',
                'website': 'https://circularpack.my',
                'founded_year': 2020,
                'team_size': '26-50',
                'primary_location': 'Malaysia',
                'company_description': 'CircularPack operates a comprehensive plastic waste recycling and remanufacturing system, turning post-consumer plastic into high-quality packaging materials.',
                'innovation_types': ['recycling_technologies', 'circular_economy', 'tracking_monitoring'],
                'solution_description': 'We use advanced chemical recycling to break down plastic waste into virgin-quality materials, with blockchain tracking for full traceability.',
                'current_stage': 'profitable',
                'funding_needed': 'not_seeking',
                'problem_statement': 'Only 9% of plastic waste is effectively recycled. Most recycling processes degrade material quality, limiting reuse applications.',
                'target_markets': 'Packaging manufacturers, consumer goods companies, government waste management agencies across ASEAN',
                'customer_segments': ['packaging', 'fmcg'],
                'active_users_count': '150+ B2B customers',
                'paying_customers_count': '150 active customers',
                'annual_recurring_revenue': '$8,500,000',
                'has_external_funding': True,
                'funding_history': 'Series B: $12M from Khazanah Nasional and regional VCs in 2022',
                'amount_raised': '$12,000,000',
                'use_of_funds': 'Facility expansion, technology R&D, regional market entry',
                'financial_projections': 'Projecting $25M revenue by 2026 with facilities in 3 countries',
                'is_female_led': False,
                'core_team_size': '35 people across ops, R&D, business dev',
                'team_overview': 'Experienced team from P&G, Unilever, and leading chemical companies with deep packaging industry knowledge.',
                'core_expertise': 'Chemical recycling technology, polymer science, B2B sales, operations management',
                'support_areas': ['market_expansion', 'regulatory_compliance', 'manufacturing_supply'],
                'support_details': 'Looking for strategic partnerships with multinational corporations and government agencies for expansion.',
                'additional_info': 'We process 50,000 tons of plastic waste annually and have achieved 95% material recovery rate.'
            }
        },
        {
            'user_data': {
                'username': 'greentech_founder',
                'email': 'founder@greentech.ph',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'job_position': 'Founder & CEO',
                'bio': 'Chemical engineer and sustainability advocate. Former Shell executive focused on developing breakthrough green technologies.'
            },
            'company_data': {
                'company_name': 'GreenTech Philippines',
                'website': 'https://greentech.ph',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Philippines',
                'company_description': 'GreenTech develops enzyme-based biodegradation technology that accelerates the breakdown of plastic waste in natural environments.',
                'innovation_types': ['recycling_technologies', 'monitoring_tools', 'circular_economy'],
                'solution_description': 'Our proprietary enzyme formulations can break down PET plastics 6x faster than natural processes, with applications in waste treatment facilities.',
                'current_stage': 'validation',
                'funding_needed': '500k_1m',
                'problem_statement': 'Plastic waste accumulation outpaces natural degradation by thousands of years, creating persistent environmental pollution.',
                'target_markets': 'Waste management companies, municipal governments, industrial manufacturers across Asia-Pacific',
                'customer_segments': ['waste_mgmt', 'government'],
                'active_users_count': '8 pilot customers',
                'paying_customers_count': '3 paying customers',
                'annual_recurring_revenue': '$120,000',
                'has_external_funding': True,
                'funding_history': 'Pre-seed: $200K from Philippine angel investors and DOST-SETUP',
                'amount_raised': '$200,000',
                'use_of_funds': 'R&D, clinical trials, regulatory approval, market validation',
                'financial_projections': 'Targeting $2M revenue by 2026 with commercial scale deployment',
                'is_female_led': True,
                'core_team_size': '7 people including 2 co-founders',
                'team_overview': 'PhD-level scientists in biochemistry and environmental engineering with corporate R&D experience.',
                'core_expertise': 'Enzyme engineering, biochemical processes, environmental science, regulatory affairs',
                'support_areas': ['product_development', 'regulatory_compliance', 'investment_funding'],
                'support_details': 'Seeking Series A funding and partnerships with waste management companies for commercial trials.',
                'additional_info': 'Our enzyme treatment can process 10 tons of plastic waste per day with 80% degradation efficiency.'
            }
        }
    ]
    
    for startup in startups_data:
        user, member = create_user_and_member(**startup['user_data'])
        
        # Create company
        company_data = startup['company_data']
        company_data['member'] = member
        company_data['company_type'] = 'startup'
        
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
    """Create 5 sample investor companies"""
    investors_data = [
        {
            'user_data': {
                'username': 'seaseed_partner',
                'email': 'partner@seaseed.vc',
                'first_name': 'David',
                'last_name': 'Chen',
                'job_position': 'Managing Partner',
                'bio': 'Former Goldman Sachs investment banker with 15+ years in venture capital. Focus on sustainability and climate tech investments.'
            },
            'company_data': {
                'company_name': 'SEA Seed Ventures',
                'website': 'https://seaseed.vc',
                'founded_year': 2018,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'SEA Seed Ventures is a leading early-stage VC fund focused on sustainability and climate technology startups across Southeast Asia.',
                'investor_type': 'vc',
                'funding_size': '100m_200m',
                'average_deal_size': '500k_1m',
                'funding_stages': ['pre_seed', 'seed', 'series_a'],
                'investment_categories': ['eliminate_redesign', 'advanced_recycling', 'bioplastics', 'data_monitoring'],
                'market_country_interests': ['Singapore', 'Indonesia', 'Thailand', 'Malaysia', 'Philippines'],
                'investment_philosophy': 'We invest in early-stage startups that are solving critical environmental challenges with scalable technology solutions. Our focus is on companies that can achieve both significant environmental impact and strong financial returns.',
                'support_areas': ['investment_funding', 'market_expansion', 'branding_marketing'],
                'support_details': 'We provide hands-on support including business development, strategic partnerships, follow-on funding, and access to our extensive network of corporates and government agencies.',
                'additional_info': 'Portfolio includes 45 companies across cleantech, circular economy, and sustainable agriculture with total portfolio value of $500M.'
            }
        },
        {
            'user_data': {
                'username': 'green_impact_gp',
                'email': 'gp@greenimpact.fund',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'job_position': 'General Partner',
                'bio': 'Impact investing veteran with background in environmental science. 20+ years building sustainable businesses across emerging markets.'
            },
            'company_data': {
                'company_name': 'Green Impact Fund',
                'website': 'https://greenimpact.fund',
                'founded_year': 2015,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'Green Impact Fund is an impact investment fund dedicated to environmental sustainability and circular economy solutions in Southeast Asia.',
                'investor_type': 'impact_fund',
                'funding_size': '1m_50m',
                'average_deal_size': '1m_5m',
                'funding_stages': ['seed', 'series_a', 'series_b'],
                'investment_categories': ['waste_management', 'collection_sorting', 'refill_reuse', 'advanced_recycling'],
                'market_country_interests': ['Thailand', 'Vietnam', 'Cambodia', 'Laos', 'Myanmar'],
                'investment_philosophy': 'We target companies that deliver measurable environmental impact alongside financial returns. Focus on waste management, circular economy, and sustainable packaging solutions with proven business models.',
                'support_areas': ['investment_funding', 'regulatory_compliance', 'manufacturing_supply'],
                'support_details': 'Beyond capital, we provide regulatory guidance, supply chain optimization, impact measurement frameworks, and connections to government and development agencies.',
                'additional_info': 'Our portfolio has diverted 2M tons of waste from landfills and created 5,000+ green jobs across the region.'
            }
        },
        {
            'user_data': {
                'username': 'asia_climate_md',
                'email': 'md@asiaclimate.capital',
                'first_name': 'Hiroshi',
                'last_name': 'Tanaka',
                'job_position': 'Managing Director',
                'bio': 'Former climate policy advisor to Japanese government. Expert in clean technology and environmental regulation across Asia.'
            },
            'company_data': {
                'company_name': 'Asia Climate Capital',
                'website': 'https://asiaclimate.capital',
                'founded_year': 2019,
                'team_size': '26-50',
                'primary_location': 'Singapore',
                'company_description': 'Asia Climate Capital is a growth-stage venture capital firm investing in climate technology and sustainability solutions across Asia-Pacific.',
                'investor_type': 'vc',
                'funding_size': '200m_500m',
                'average_deal_size': '5m_10m',
                'funding_stages': ['series_a', 'series_b', 'series_c'],
                'investment_categories': ['advanced_recycling', 'bioplastics', 'waste_management', 'data_monitoring'],
                'market_country_interests': ['Singapore', 'Indonesia', 'Thailand', 'Malaysia', 'Vietnam', 'Philippines'],
                'investment_philosophy': 'We focus on scalable climate solutions with strong unit economics and clear paths to profitability. Target companies addressing large market opportunities with defensible technology moats.',
                'support_areas': ['investment_funding', 'market_expansion', 'manufacturing_supply'],
                'support_details': 'We offer growth capital, strategic advisory, business development support, and access to corporate partnerships for scaling operations across Asia.',
                'additional_info': 'Fund III is $400M focused on Series A-C companies. Portfolio companies have raised $2B+ in follow-on funding.'
            }
        },
        {
            'user_data': {
                'username': 'circular_ventures_cio',
                'email': 'cio@circularventures.asia',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'job_position': 'Chief Investment Officer',
                'bio': 'Former McKinsey principal with expertise in circular economy. 12 years investing in sustainability and waste management technologies.'
            },
            'company_data': {
                'company_name': 'Circular Ventures Asia',
                'website': 'https://circularventures.asia',
                'founded_year': 2020,
                'team_size': '11-25',
                'primary_location': 'Malaysia',
                'company_description': 'Circular Ventures Asia specializes in early to growth-stage investments in circular economy and waste-to-value technologies across ASEAN.',
                'investor_type': 'vc',
                'funding_size': '100m_200m',
                'average_deal_size': '1m_5m',
                'funding_stages': ['seed', 'series_a', 'series_b'],
                'investment_categories': ['eliminate_redesign', 'collection_sorting', 'advanced_recycling', 'waste_management'],
                'market_country_interests': ['Malaysia', 'Singapore', 'Indonesia', 'Thailand', 'Philippines'],
                'investment_philosophy': 'We invest in companies creating economic value from waste streams and driving transition to circular business models. Focus on proven technologies with clear commercial viability.',
                'support_areas': ['investment_funding', 'market_expansion', 'product_development'],
                'support_details': 'We provide capital, market access, technology partnerships, and operational expertise to help portfolio companies scale across multiple markets.',
                'additional_info': 'Portfolio includes 28 companies processing 500K+ tons of waste annually with combined revenue of $150M.'
            }
        },
        {
            'user_data': {
                'username': 'pacific_green_lp',
                'email': 'lp@pacificgreen.partners',
                'first_name': 'Michael',
                'last_name': 'Wong',
                'job_position': 'Limited Partner & Advisor',
                'bio': 'Serial entrepreneur and angel investor with 3 successful exits in cleantech. Active in plastic waste and ocean conservation initiatives.'
            },
            'company_data': {
                'company_name': 'Pacific Green Partners',
                'website': 'https://pacificgreen.partners',
                'founded_year': 2017,
                'team_size': '2-5',
                'primary_location': 'Philippines',
                'company_description': 'Pacific Green Partners is an angel investor network focused on early-stage environmental technology startups in the Philippines and broader Southeast Asia.',
                'investor_type': 'angel',
                'funding_size': 'under_1m',
                'average_deal_size': '100k_500k',
                'funding_stages': ['pre_seed', 'seed'],
                'investment_categories': ['eliminate_redesign', 'refill_reuse', 'collection_sorting', 'other'],
                'market_country_interests': ['Philippines', 'Indonesia', 'Malaysia', 'Thailand'],
                'investment_philosophy': 'We support passionate entrepreneurs solving environmental challenges with innovative approaches. Emphasis on strong founding teams and clear problem-solution fit.',
                'support_areas': ['investment_funding', 'branding_marketing', 'product_development'],
                'support_details': 'We offer seed capital, mentorship, network access, and ongoing strategic guidance for early-stage environmental technology companies.',
                'additional_info': 'Network of 50+ angel investors with combined investments of $25M in 80+ environmental startups across the region.'
            }
        }
    ]
    
    for investor in investors_data:
        user, member = create_user_and_member(**investor['user_data'])
        
        # Create company
        company_data = investor['company_data']
        company_data['member'] = member
        company_data['company_type'] = 'investor'
        
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
    """Create 5 sample corporate companies"""
    corporates_data = [
        {
            'user_data': {
                'username': 'unilever_innovation',
                'email': 'innovation@unilever.com.sg',
                'first_name': 'Jennifer',
                'last_name': 'Lim',
                'job_position': 'Head of Sustainable Innovation',
                'bio': 'Leading Unilever\'s sustainability initiatives across Southeast Asia. 10+ years in corporate innovation and partnerships.'
            },
            'company_data': {
                'company_name': 'Unilever Southeast Asia',
                'website': 'https://unilever.com.sg',
                'founded_year': 1885,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Unilever is a leading multinational consumer goods company committed to sustainable living and reducing environmental footprint across all operations.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['fmcg', 'consumer_goods', 'sustainability', 'supply_chain'],
                'support_areas': ['investment_funding', 'manufacturing_supply', 'market_expansion'],
                'support_details': 'We offer corporate venture capital, strategic partnerships, pilot opportunities, supply chain integration, and market access across our global distribution network.',
                'additional_info': 'Committed to making all plastic packaging reusable, recyclable, or compostable by 2025. Annual revenue of $60B+ globally with strong presence across ASEAN.'
            }
        },
        {
            'user_data': {
                'username': 'nestle_sustainability',
                'email': 'sustainability@nestle.com.th',
                'first_name': 'Ananda',
                'last_name': 'Prajak',
                'job_position': 'Sustainability Director',
                'bio': 'Driving Nestlé\'s circular economy initiatives in Thailand. Expert in sustainable packaging and regenerative agriculture.'
            },
            'company_data': {
                'company_name': 'Nestlé Thailand',
                'website': 'https://nestle.co.th',
                'founded_year': 1866,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'Nestlé is the world\'s largest food and beverage company, committed to enhancing quality of life and contributing to a healthier future through sustainable packaging solutions.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['food_beverage', 'packaging', 'sustainability', 'manufacturing'],
                'support_areas': ['investment_funding', 'manufacturing_supply', 'regulatory_compliance'],
                'support_details': 'We provide corporate partnerships, R&D collaboration, manufacturing capabilities, regulatory expertise, and access to our extensive supply chain network.',
                'additional_info': 'Investing $2B globally to shift from virgin plastics to recycled materials. Goal to achieve 100% recyclable or reusable packaging by 2025.'
            }
        },
        {
            'user_data': {
                'username': 'scg_innovation',
                'email': 'innovation@scg.com',
                'first_name': 'Supachai',
                'last_name': 'Wichianchai',
                'job_position': 'Innovation Director',
                'bio': 'Leading SCG\'s digital transformation and sustainability initiatives. 15+ years in materials science and industrial innovation.'
            },
            'company_data': {
                'company_name': 'SCG (Siam Cement Group)',
                'website': 'https://scg.com',
                'founded_year': 1913,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'SCG is a leading industrial conglomerate in ASEAN, focusing on sustainable materials, chemicals, and packaging solutions for the circular economy.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['chemicals', 'materials', 'packaging', 'manufacturing'],
                'support_areas': ['manufacturing_supply', 'product_development', 'market_expansion'],
                'support_details': 'We offer manufacturing partnerships, material science R&D, scale-up facilities, distribution networks, and corporate venture investments.',
                'additional_info': 'Revenue of $13B+ with operations across ASEAN. Committed to carbon neutrality by 2050 and leading circular economy initiatives.'
            }
        },
        {
            'user_data': {
                'username': 'grab_sustainability',
                'email': 'sustainability@grab.com',
                'first_name': 'Rachel',
                'last_name': 'Teo',
                'job_position': 'Head of Sustainability',
                'bio': 'Leading Grab\'s environmental impact initiatives across Southeast Asia. Expert in sustainable operations and green logistics.'
            },
            'company_data': {
                'company_name': 'Grab Holdings',
                'website': 'https://grab.com',
                'founded_year': 2012,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Grab is Southeast Asia\'s leading super-app, committed to sustainable transportation and reducing environmental impact through technology and partnerships.',
                'organization_type': 'private_company',
                'industry_expertise': ['technology', 'logistics', 'food_delivery', 'sustainability'],
                'support_areas': ['market_expansion', 'branding_marketing', 'investment_funding'],
                'support_details': 'We provide market access through our platform, brand partnership opportunities, corporate venture investments, and distribution channel access.',
                'additional_info': 'Platform connects 187M+ users with 5M+ driver-partners. Committed to net-zero emissions by 2040 and sustainable packaging for food delivery.'
            }
        },
        {
            'user_data': {
                'username': 'cp_innovation',
                'email': 'innovation@cpgroup.co.th',
                'first_name': 'Somsak',
                'last_name': 'Chearavanont',
                'job_position': 'Chief Innovation Officer',
                'bio': 'Driving CP Group\'s innovation strategy across agribusiness and sustainability. 20+ years in corporate strategy and venture investments.'
            },
            'company_data': {
                'company_name': 'Charoen Pokphand Group',
                'website': 'https://cpgroup.co.th',
                'founded_year': 1921,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'CP Group is one of Asia\'s largest conglomerates with businesses spanning agribusiness, food, retail, and telecommunications, committed to sustainable development.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['agribusiness', 'food_processing', 'retail', 'sustainability'],
                'support_areas': ['investment_funding', 'manufacturing_supply', 'market_expansion'],
                'support_details': 'We provide strategic investments, manufacturing capabilities, supply chain integration, market access across 20+ countries, and R&D collaboration.',
                'additional_info': 'Revenue of $65B+ with 400,000+ employees globally. Committed to sustainable agriculture and circular economy across food value chain.'
            }
        }
    ]
    
    for corporate in corporates_data:
        user, member = create_user_and_member(**corporate['user_data'])
        
        # Create company
        company_data = corporate['company_data']
        company_data['member'] = member
        company_data['company_type'] = 'corporate'
        
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


def main():
    """Main function to create all sample data"""
    print("Creating sample company profiles...")
    print("=" * 50)
    
    print("\n🚀 Creating Startup Companies...")
    create_startup_companies()
    
    print("\n💰 Creating Investor Companies...")
    create_investor_companies()
    
    print("\n🏢 Creating Corporate Companies...")
    create_corporate_companies()
    
    print("\n" + "=" * 50)
    print("✅ Sample data creation completed!")
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Members: {Member.objects.count()}")
    print(f"Total Companies: {Company.objects.count()}")
    print(f"- Startups: {Company.objects.filter(company_type='startup').count()}")
    print(f"- Investors: {Company.objects.filter(company_type='investor').count()}")
    print(f"- Corporates: {Company.objects.filter(company_type='corporate').count()}")


if __name__ == "__main__":
    main()
