from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from member.models import Member, Company


class Command(BaseCommand):
    help = 'Load sample company data into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force load data even if companies already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading sample company data...'))

        # Check if data already exists
        company_count = Company.objects.count()
        if company_count > 0 and not options['force']:
            self.stdout.write(self.style.WARNING(
                f'Companies already exist in database ({company_count} found). Use --force to override.'
            ))
            return

        try:
            # Create sample startup
            self.stdout.write('Creating startup...')
            user1, created = User.objects.get_or_create(
                username='ecopack_demo',
                defaults={
                    'email': 'demo@ecopack.com',
                    'first_name': 'Demo',
                    'last_name': 'Founder',
                }
            )
            
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
            
            Company.objects.get_or_create(
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
            
            # Create sample investor
            self.stdout.write('Creating investor...')
            user2, created = User.objects.get_or_create(
                username='investor_demo',
                defaults={
                    'email': 'demo@investor.com',
                    'first_name': 'Demo',
                    'last_name': 'Investor',
                }
            )
            
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
            
            Company.objects.get_or_create(
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
            
            # Create sample corporate
            self.stdout.write('Creating corporate...')
            user3, created = User.objects.get_or_create(
                username='corporate_demo',
                defaults={
                    'email': 'demo@corporate.com',
                    'first_name': 'Demo',
                    'last_name': 'Corporate',
                }
            )
            
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
            
            Company.objects.get_or_create(
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
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded sample data!\n'
                f'Total Companies: {Company.objects.count()}\n'
                f'- Startups: {Company.objects.filter(company_type="startup").count()}\n'
                f'- Investors: {Company.objects.filter(company_type="investor").count()}\n'
                f'- Corporates: {Company.objects.filter(company_type="corporate").count()}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            import traceback
            traceback.print_exc()
