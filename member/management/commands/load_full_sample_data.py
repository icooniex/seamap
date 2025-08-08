from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from member.models import Member, Company


class Command(BaseCommand):
    help = 'Load full sample company data (15 companies) into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force load data even if companies already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading full sample company data (15 companies)...'))

        # Check if data already exists
        existing_sample_companies = Company.objects.filter(
            company_name__in=[
                'EcoPack Thailand', 'PlasticFree Solutions', 'OceanClean Indonesia',
                'CircularPack Malaysia', 'GreenTech Philippines', 'SEA Seed Ventures',
                'Green Impact Fund', 'Asia Climate Capital', 'Circular Ventures Asia',
                'Pacific Green Partners', 'Unilever Southeast Asia', 'Nestlé Thailand',
                'SCG (Siam Cement Group)', 'Grab Holdings', 'Charoen Pokphand Group'
            ]
        ).count()
        
        if existing_sample_companies >= 10 and not options['force']:
            self.stdout.write(self.style.WARNING(
                f'Sample companies already exist in database ({existing_sample_companies} found). Use --force to override.'
            ))
            return

        try:
            # Create startup companies
            self.stdout.write('Creating startup companies...')
            self._create_startup_companies()
            
            # Create investor companies  
            self.stdout.write('Creating investor companies...')
            self._create_investor_companies()
            
            # Create corporate companies
            self.stdout.write('Creating corporate companies...')
            self._create_corporate_companies()
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded full sample data!\n'
                f'Total Companies: {Company.objects.count()}\n'
                f'- Startups: {Company.objects.filter(company_type="startup").count()}\n'
                f'- Investors: {Company.objects.filter(company_type="investor").count()}\n'
                f'- Corporates: {Company.objects.filter(company_type="corporate").count()}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            import traceback
            traceback.print_exc()

    def _create_user_and_member(self, username, email, first_name, last_name, job_position="", bio=""):
        """Create a user and associated member profile"""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
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
        
        return user, member

    def _create_startup_companies(self):
        """Create 5 startup companies"""
        startups = [
            {
                'username': 'ecopack_founder',
                'email': 'founder@ecopack.co.th',
                'first_name': 'Siriporn',
                'last_name': 'Thanakit',
                'job_position': 'CEO & Founder',
                'bio': 'Environmental engineer turned entrepreneur.',
                'company_name': 'EcoPack Thailand',
                'website': 'https://ecopack.co.th',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'EcoPack Thailand develops biodegradable packaging solutions made from agricultural waste.',
                'innovation_types': ['plastic_alternatives', 'circular_economy'],
                'current_stage': 'early',
                'funding_needed': '500k_1m',
                'is_female_led': True,
            },
            {
                'username': 'plasticfree_ceo',
                'email': 'ceo@plasticfree.sg',
                'first_name': 'Marcus',
                'last_name': 'Lim',
                'job_position': 'Co-Founder & CEO',
                'bio': 'Former McKinsey consultant with 8 years in sustainability.',
                'company_name': 'PlasticFree Solutions',
                'website': 'https://plasticfree.sg',
                'founded_year': 2021,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'PlasticFree Solutions is a B2B platform connecting businesses with sustainable packaging alternatives.',
                'innovation_types': ['plastic_alternatives', 'waste_collection'],
                'current_stage': 'scaling',
                'funding_needed': '1m_5m',
                'is_female_led': False,
            },
            {
                'username': 'oceanclean_founder',
                'email': 'founder@oceanclean.id',
                'first_name': 'Dewi',
                'last_name': 'Kusuma',
                'job_position': 'Founder & CTO',
                'bio': 'Marine biologist and tech entrepreneur.',
                'company_name': 'OceanClean Indonesia',
                'website': 'https://oceanclean.id',
                'founded_year': 2023,
                'team_size': '2-5',
                'primary_location': 'Indonesia',
                'company_description': 'OceanClean develops autonomous marine robots that collect plastic waste from rivers and coastal areas.',
                'innovation_types': ['waste_collection', 'tracking_monitoring'],
                'current_stage': 'prototype',
                'funding_needed': '100k_500k',
                'is_female_led': True,
            },
            {
                'username': 'circularpack_ceo',
                'email': 'ceo@circularpack.my',
                'first_name': 'Ahmad',
                'last_name': 'Rahman',
                'job_position': 'CEO & Co-Founder',
                'bio': 'Former P&G executive with 12 years in packaging innovation.',
                'company_name': 'CircularPack Malaysia',
                'website': 'https://circularpack.my',
                'founded_year': 2020,
                'team_size': '26-50',
                'primary_location': 'Malaysia',
                'company_description': 'CircularPack operates a comprehensive plastic waste recycling and remanufacturing system.',
                'innovation_types': ['recycling_technologies', 'circular_economy'],
                'current_stage': 'profitable',
                'funding_needed': 'not_seeking',
                'is_female_led': False,
            },
            {
                'username': 'greentech_founder',
                'email': 'founder@greentech.ph',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'job_position': 'Founder & CEO',
                'bio': 'Chemical engineer and sustainability advocate.',
                'company_name': 'GreenTech Philippines',
                'website': 'https://greentech.ph',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Philippines',
                'company_description': 'GreenTech develops enzyme-based biodegradation technology that accelerates plastic breakdown.',
                'innovation_types': ['recycling_technologies', 'monitoring_tools'],
                'current_stage': 'validation',
                'funding_needed': '500k_1m',
                'is_female_led': True,
            }
        ]
        
        for startup_data in startups:
            user, member = self._create_user_and_member(
                startup_data['username'],
                startup_data['email'],
                startup_data['first_name'],
                startup_data['last_name'],
                startup_data['job_position'],
                startup_data['bio']
            )
            
            Company.objects.get_or_create(
                member=member,
                company_name=startup_data['company_name'],
                defaults={
                    'company_type': 'startup',
                    'website': startup_data['website'],
                    'founded_year': startup_data['founded_year'],
                    'team_size': startup_data['team_size'],
                    'primary_location': startup_data['primary_location'],
                    'company_description': startup_data['company_description'],
                    'innovation_types': startup_data['innovation_types'],
                    'current_stage': startup_data['current_stage'],
                    'funding_needed': startup_data['funding_needed'],
                    'is_female_led': startup_data['is_female_led'],
                }
            )

    def _create_investor_companies(self):
        """Create 5 investor companies"""
        investors = [
            {
                'username': 'seaseed_partner',
                'email': 'partner@seaseed.vc',
                'first_name': 'David',
                'last_name': 'Chen',
                'job_position': 'Managing Partner',
                'bio': 'Former Goldman Sachs investment banker.',
                'company_name': 'SEA Seed Ventures',
                'website': 'https://seaseed.vc',
                'founded_year': 2018,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'SEA Seed Ventures is a leading early-stage VC fund focused on sustainability and climate technology.',
                'investor_type': 'vc',
                'funding_size': '100m_200m',
                'average_deal_size': '500k_1m',
                'funding_stages': ['pre_seed', 'seed', 'series_a'],
                'investment_categories': ['eliminate_redesign', 'advanced_recycling'],
                'market_country_interests': ['Singapore', 'Indonesia', 'Thailand'],
            },
            {
                'username': 'green_impact_gp',
                'email': 'gp@greenimpact.fund',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'job_position': 'General Partner',
                'bio': 'Impact investing veteran with environmental science background.',
                'company_name': 'Green Impact Fund',
                'website': 'https://greenimpact.fund',
                'founded_year': 2015,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'Green Impact Fund is an impact investment fund dedicated to environmental sustainability.',
                'investor_type': 'impact_fund',
                'funding_size': '1m_50m',
                'average_deal_size': '1m_5m',
                'funding_stages': ['seed', 'series_a', 'series_b'],
                'investment_categories': ['waste_management', 'collection_sorting'],
                'market_country_interests': ['Thailand', 'Vietnam', 'Cambodia'],
            },
            {
                'username': 'asia_climate_md',
                'email': 'md@asiaclimate.capital',
                'first_name': 'Hiroshi',
                'last_name': 'Tanaka',
                'job_position': 'Managing Director',
                'bio': 'Former climate policy advisor to Japanese government.',
                'company_name': 'Asia Climate Capital',
                'website': 'https://asiaclimate.capital',
                'founded_year': 2019,
                'team_size': '26-50',
                'primary_location': 'Singapore',
                'company_description': 'Asia Climate Capital is a growth-stage venture capital firm investing in climate technology.',
                'investor_type': 'vc',
                'funding_size': '200m_500m',
                'average_deal_size': '5m_10m',
                'funding_stages': ['series_a', 'series_b', 'series_c'],
                'investment_categories': ['advanced_recycling', 'bioplastics'],
                'market_country_interests': ['Singapore', 'Indonesia', 'Thailand'],
            },
            {
                'username': 'circular_ventures_cio',
                'email': 'cio@circularventures.asia',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'job_position': 'Chief Investment Officer',
                'bio': 'Former McKinsey principal with circular economy expertise.',
                'company_name': 'Circular Ventures Asia',
                'website': 'https://circularventures.asia',
                'founded_year': 2020,
                'team_size': '11-25',
                'primary_location': 'Malaysia',
                'company_description': 'Circular Ventures Asia specializes in early to growth-stage investments in circular economy.',
                'investor_type': 'vc',
                'funding_size': '100m_200m',
                'average_deal_size': '1m_5m',
                'funding_stages': ['seed', 'series_a', 'series_b'],
                'investment_categories': ['eliminate_redesign', 'collection_sorting'],
                'market_country_interests': ['Malaysia', 'Singapore', 'Indonesia'],
            },
            {
                'username': 'pacific_green_lp',
                'email': 'lp@pacificgreen.partners',
                'first_name': 'Michael',
                'last_name': 'Wong',
                'job_position': 'Limited Partner & Advisor',
                'bio': 'Serial entrepreneur and angel investor.',
                'company_name': 'Pacific Green Partners',
                'website': 'https://pacificgreen.partners',
                'founded_year': 2017,
                'team_size': '2-5',
                'primary_location': 'Philippines',
                'company_description': 'Pacific Green Partners is an angel investor network focused on early-stage environmental technology.',
                'investor_type': 'angel',
                'funding_size': 'under_1m',
                'average_deal_size': '100k_500k',
                'funding_stages': ['pre_seed', 'seed'],
                'investment_categories': ['eliminate_redesign', 'refill_reuse'],
                'market_country_interests': ['Philippines', 'Indonesia', 'Malaysia'],
            }
        ]
        
        for investor_data in investors:
            user, member = self._create_user_and_member(
                investor_data['username'],
                investor_data['email'],
                investor_data['first_name'],
                investor_data['last_name'],
                investor_data['job_position'],
                investor_data['bio']
            )
            
            Company.objects.get_or_create(
                member=member,
                company_name=investor_data['company_name'],
                defaults={
                    'company_type': 'investor',
                    'website': investor_data['website'],
                    'founded_year': investor_data['founded_year'],
                    'team_size': investor_data['team_size'],
                    'primary_location': investor_data['primary_location'],
                    'company_description': investor_data['company_description'],
                    'investor_type': investor_data['investor_type'],
                    'funding_size': investor_data['funding_size'],
                    'average_deal_size': investor_data['average_deal_size'],
                    'funding_stages': investor_data['funding_stages'],
                    'investment_categories': investor_data['investment_categories'],
                    'market_country_interests': investor_data['market_country_interests'],
                }
            )

    def _create_corporate_companies(self):
        """Create 5 corporate companies"""
        corporates = [
            {
                'username': 'unilever_innovation',
                'email': 'innovation@unilever.com.sg',
                'first_name': 'Jennifer',
                'last_name': 'Lim',
                'job_position': 'Head of Sustainable Innovation',
                'bio': 'Leading Unilever\'s sustainability initiatives across SEA.',
                'company_name': 'Unilever Southeast Asia',
                'website': 'https://unilever.com.sg',
                'founded_year': 1885,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Unilever is a leading multinational consumer goods company committed to sustainable living.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['fmcg', 'consumer_goods'],
                'support_areas': ['investment_funding', 'manufacturing_supply'],
            },
            {
                'username': 'nestle_sustainability',
                'email': 'sustainability@nestle.com.th',
                'first_name': 'Ananda',
                'last_name': 'Prajak',
                'job_position': 'Sustainability Director',
                'bio': 'Driving Nestlé\'s circular economy initiatives in Thailand.',
                'company_name': 'Nestlé Thailand',
                'website': 'https://nestle.co.th',
                'founded_year': 1866,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'Nestlé is the world\'s largest food and beverage company committed to sustainable packaging.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['food_beverage', 'packaging'],
                'support_areas': ['investment_funding', 'manufacturing_supply'],
            },
            {
                'username': 'scg_innovation',
                'email': 'innovation@scg.com',
                'first_name': 'Supachai',
                'last_name': 'Wichianchai',
                'job_position': 'Innovation Director',
                'bio': 'Leading SCG\'s digital transformation and sustainability.',
                'company_name': 'SCG (Siam Cement Group)',
                'website': 'https://scg.com',
                'founded_year': 1913,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'SCG is a leading industrial conglomerate focusing on sustainable materials and chemicals.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['chemicals', 'materials'],
                'support_areas': ['manufacturing_supply', 'product_development'],
            },
            {
                'username': 'grab_sustainability',
                'email': 'sustainability@grab.com',
                'first_name': 'Rachel',
                'last_name': 'Teo',
                'job_position': 'Head of Sustainability',
                'bio': 'Leading Grab\'s environmental impact initiatives.',
                'company_name': 'Grab Holdings',
                'website': 'https://grab.com',
                'founded_year': 2012,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Grab is Southeast Asia\'s leading super-app committed to sustainable transportation.',
                'organization_type': 'private_company',
                'industry_expertise': ['technology', 'logistics'],
                'support_areas': ['market_expansion', 'branding_marketing'],
            },
            {
                'username': 'cp_innovation',
                'email': 'innovation@cpgroup.co.th',
                'first_name': 'Somsak',
                'last_name': 'Chearavanont',
                'job_position': 'Chief Innovation Officer',
                'bio': 'Driving CP Group\'s innovation strategy.',
                'company_name': 'Charoen Pokphand Group',
                'website': 'https://cpgroup.co.th',
                'founded_year': 1921,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'CP Group is one of Asia\'s largest conglomerates committed to sustainable development.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['agribusiness', 'food_processing'],
                'support_areas': ['investment_funding', 'manufacturing_supply'],
            }
        ]
        
        for corporate_data in corporates:
            user, member = self._create_user_and_member(
                corporate_data['username'],
                corporate_data['email'],
                corporate_data['first_name'],
                corporate_data['last_name'],
                corporate_data['job_position'],
                corporate_data['bio']
            )
            
            Company.objects.get_or_create(
                member=member,
                company_name=corporate_data['company_name'],
                defaults={
                    'company_type': 'corporate',
                    'website': corporate_data['website'],
                    'founded_year': corporate_data['founded_year'],
                    'team_size': corporate_data['team_size'],
                    'primary_location': corporate_data['primary_location'],
                    'company_description': corporate_data['company_description'],
                    'organization_type': corporate_data['organization_type'],
                    'industry_expertise': corporate_data['industry_expertise'],
                    'support_areas': corporate_data['support_areas'],
                }
            )
