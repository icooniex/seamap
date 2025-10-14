from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from member.models import Member, Company


class Command(BaseCommand):
    help = 'Load sample data for SEAmap platform (6 users: 2 startups, 2 investors, 2 corporates) focused on plastic circularity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force load data even if companies already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading plastic circularity focused sample data (6 companies)...'))

        # Check if data already exists (updated company names)
        existing_sample_companies = Company.objects.filter(
            company_name__in=[
                'EcoPack Solutions', 'PlasticFree Innovations', 
                'Circular Ventures Asia', 'Ocean Impact Fund',
                'Unilever Southeast Asia', 'SCG Circular Economy Solutions'
            ]
        ).count()
        
        if existing_sample_companies >= 3 and not options['force']:
            self.stdout.write(self.style.WARNING(
                f'Sample companies already exist in database ({existing_sample_companies} found). Use --force to override.'
            ))
            return

        try:
            # Create startup companies (2)
            self.stdout.write('Creating startup companies...')
            self._create_startup_companies()
            
            # Create investor companies (2)
            self.stdout.write('Creating investor companies...')
            self._create_investor_companies()
            
            # Create corporate companies (2)
            self.stdout.write('Creating corporate companies...')
            self._create_corporate_companies()
            
            # Print login credentials
            self._print_login_credentials()
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded plastic circularity sample data!\n'
                f'Total Companies: {Company.objects.count()}\n'
                f'- Startups: {Company.objects.filter(company_type="startup").count()}\n'
                f'- Investors: {Company.objects.filter(company_type="investor").count()}\n'
                f'- Corporates: {Company.objects.filter(company_type="corporate").count()}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
            import traceback
            traceback.print_exc()

    def _create_user_and_member(self, username, email, first_name, last_name, job_position="", bio="", password="seamap2025"):
        """Create a user and associated member profile"""
        try:
            # Try to get existing user first
            user = User.objects.get(username=username)
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
        
        return user, member

    def _create_startup_companies(self):
        """Create 2 startup companies focused on plastic circularity"""
        startups = [
            {
                'username': 'ecopack_founder',
                'email': 'founder@ecopack.asia',
                'first_name': 'Siriporn',
                'last_name': 'Thanakit',
                'job_position': 'CEO & Founder',
                'bio': 'Environmental engineer turned entrepreneur. 8 years developing biodegradable packaging solutions from agricultural waste. Passionate about replacing single-use plastics across Southeast Asia.',
                'password': 'seamap2025',
                'company_name': 'EcoPack Solutions',
                'website': 'https://ecopack.asia',
                'founded_year': 2022,
                'team_size': '6-10',
                'primary_location': 'Thailand',
                'company_description': 'EcoPack Solutions develops biodegradable packaging materials from agricultural waste, specifically rice husks and corn starch. Our mission is to replace single-use plastics with sustainable alternatives that decompose naturally within 90 days.',
                'innovation_types': ['Eliminate & Redesign Packaging', 'Upcycling Plastic Waste', 'Reusable Packaging Collection/Drop Off'],
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
                'support_areas': ['Manufacturing & Supply Chain', 'Market Expansion & Customer Acquisition', 'Investment & Funding Access'],
                'support_details': 'Seeking manufacturing partners for scale-up, distribution channels across ASEAN, and Series A funding of $800K-1.2M.',
                'additional_info': 'Our products are certified compostable (ASTM D6400, EN 13432) and meet international food safety standards. Processed 50 tons of agricultural waste in 2024.'
            },
            {
                'username': 'plasticfree_ceo',
                'email': 'ceo@plasticfree.sg',
                'first_name': 'Marcus',
                'last_name': 'Lim',
                'job_position': 'Co-Founder & CEO',
                'bio': 'Former McKinsey consultant with 10 years in sustainability consulting. Built 2 previous cleantech companies. Expert in circular economy business models and corporate sustainability transformation.',
                'password': 'seamap2025',
                'company_name': 'PlasticFree Innovations',
                'website': 'https://plasticfree.sg',
                'founded_year': 2021,
                'team_size': '11-25',
                'primary_location': 'Singapore',
                'company_description': 'PlasticFree Innovations operates a B2B platform connecting businesses with verified sustainable packaging alternatives. We help companies transition from plastic to eco-friendly materials with full supply chain integration.',
                'innovation_types': ['Eliminate & Redesign Packaging', 'Tracking & Monitoring Waste', 'Education & Industry Partnerships'],
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
                'support_areas': ['Market Expansion & Customer Acquisition', 'Investment & Funding Access', 'Manufacturing & Supply Chain'],
                'support_details': 'Seeking Series B funding for regional expansion and partnerships with multinational corporations and government agencies.',
                'additional_info': 'Platform has processed over $35M in sustainable packaging transactions and helped customers save 1.5M kg of plastic waste annually.'
            }
        ]
        
        for startup_data in startups:
            user, member = self._create_user_and_member(
                startup_data['username'],
                startup_data['email'],
                startup_data['first_name'],
                startup_data['last_name'],
                startup_data['job_position'],
                startup_data['bio'],
                startup_data['password']
            )
            
            company, created = Company.objects.get_or_create(
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
                    'solution_description': startup_data['solution_description'],
                    'current_stage': startup_data['current_stage'],
                    'funding_needed': startup_data['funding_needed'],
                    'problem_statement': startup_data['problem_statement'],
                    'target_markets': startup_data['target_markets'],
                    'customer_segments': startup_data['customer_segments'],
                    'active_users_count': startup_data['active_users_count'],
                    'paying_customers_count': startup_data['paying_customers_count'],
                    'annual_recurring_revenue': startup_data['annual_recurring_revenue'],
                    'has_external_funding': startup_data['has_external_funding'],
                    'funding_history': startup_data['funding_history'],
                    'amount_raised': startup_data['amount_raised'],
                    'use_of_funds': startup_data['use_of_funds'],
                    'financial_projections': startup_data['financial_projections'],
                    'is_female_led': startup_data['is_female_led'],
                    'core_team_size': startup_data['core_team_size'],
                    'team_overview': startup_data['team_overview'],
                    'core_expertise': startup_data['core_expertise'],
                    'support_areas': startup_data['support_areas'],
                    'support_details': startup_data['support_details'],
                    'additional_info': startup_data['additional_info'],
                    'verification_status': 'approved',  # Pre-approve for demo
                }
            )
            
            if not created:
                # Update existing company with new data
                for key, value in startup_data.items():
                    if key not in ['username', 'email', 'first_name', 'last_name', 'job_position', 'bio', 'password']:
                        setattr(company, key, value)
                company.verification_status = 'approved'
                company.save()

    def _create_investor_companies(self):
        """Create 2 investor companies focused on plastic circularity"""
        investors = [
            {
                'username': 'circular_vc_partner',
                'email': 'partner@circularvc.asia',
                'first_name': 'David',
                'last_name': 'Chen',
                'job_position': 'Managing Partner',
                'bio': 'Former Goldman Sachs investment banker with 15+ years in venture capital. Specialized in sustainability and circular economy investments across Asia-Pacific. Led 40+ investments in cleantech startups.',
                'password': 'seamap2025',
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
                                                                'investment_categories': ['Bioplastics & Compostable Materials', 'Advanced Recycling & Upcycling', 'Collection & Sorting Technologies', 'Data, Monitoring & Traceability'],
                'market_country_interests': ['Singapore', 'Indonesia', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam'],
                'investment_philosophy': 'We invest in early-stage startups solving plastic waste challenges with scalable technology solutions. Focus on companies that can achieve both significant environmental impact and strong financial returns in the circular economy.',
                'support_areas': ['Investment & Funding Access', 'Market Expansion & Customer Acquisition', 'Manufacturing & Supply Chain'],
                'support_details': 'We provide hands-on support including business development, strategic partnerships, follow-on funding, and access to our extensive network of corporates, government agencies, and manufacturing partners.',
                'additional_info': 'Portfolio includes 35 companies across plastic alternatives, waste management, and circular economy with total portfolio value of $400M. Combined portfolio impact: 800K tons plastic waste diverted annually.'
            },
            {
                'username': 'ocean_impact_gp',
                'email': 'gp@oceanimpact.fund',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'job_position': 'General Partner',
                'bio': 'Impact investing veteran with PhD in Marine Biology. 18+ years building sustainable businesses across emerging markets. Former World Bank consultant on ocean plastic pollution initiatives.',
                'password': 'seamap2025',
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
                'investment_categories': ['Collection & Sorting Technologies', 'Advanced Recycling & Upcycling', 'Data, Monitoring & Traceability', 'Waste Management Infrastructure'],
                'market_country_interests': ['Thailand', 'Indonesia', 'Philippines', 'Vietnam', 'Malaysia'],
                'investment_philosophy': 'We target companies delivering measurable ocean plastic reduction alongside financial returns. Focus on waste collection, advanced recycling, and monitoring technologies with proven impact metrics.',
                'support_areas': ['Investment & Funding Access', 'Regulatory & Compliance', 'Branding & Marketing'],
                'support_details': 'Beyond capital, we provide impact measurement frameworks, regulatory guidance, connections to government and NGO partners, and access to scientific research networks.',
                'additional_info': 'Portfolio has prevented 1.2M tons of plastic from entering oceans, created 3,000+ green jobs, and operates in 8 countries across Southeast Asia and Pacific.'
            }
        ]
        
        for investor_data in investors:
            user, member = self._create_user_and_member(
                investor_data['username'],
                investor_data['email'],
                investor_data['first_name'],
                investor_data['last_name'],
                investor_data['job_position'],
                investor_data['bio'],
                investor_data['password']
            )
            
            company, created = Company.objects.get_or_create(
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
                    'investment_philosophy': investor_data['investment_philosophy'],
                    'support_areas': investor_data['support_areas'],
                    'support_details': investor_data['support_details'],
                    'additional_info': investor_data['additional_info'],
                    'verification_status': 'approved',  # Pre-approve for demo
                }
            )
            
            if not created:
                # Update existing company with new data
                for key, value in investor_data.items():
                    if key not in ['username', 'email', 'first_name', 'last_name', 'job_position', 'bio', 'password']:
                        setattr(company, key, value)
                company.verification_status = 'approved'
                company.save()

    def _create_corporate_companies(self):
        """Create 2 corporate companies focused on plastic circularity"""
        corporates = [
            {
                'username': 'unilever_sustainability',
                'email': 'sustainability@unilever.com.sg',
                'first_name': 'Jennifer',
                'last_name': 'Lim',
                'job_position': 'Head of Sustainable Innovation',
                'bio': 'Leading Unilever\'s plastic circularity initiatives across Southeast Asia. 12+ years in corporate sustainability and open innovation. Expert in sustainable packaging and supply chain transformation.',
                'password': 'seamap2025',
                'company_name': 'Unilever Southeast Asia',
                'website': 'https://unilever.com.sg',
                'founded_year': 1885,
                'team_size': '100+',
                'primary_location': 'Singapore',
                'company_description': 'Unilever is a leading multinational consumer goods company committed to sustainable living. We are transforming our packaging to be 100% reusable, recyclable, or compostable while reducing plastic waste across our value chain.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['Retail & Consumer Goods', 'Energy & Sustainability', 'Industrial & Manufacturing'],
                'investment_categories': ['Eliminate & Redesign Packaging', 'Sustainable Alternative Materials', 'Upcycling Plastic Waste'],
                'innovation_types': ['plastic_alternatives', 'refill_reuse', 'recycling_technologies'],
                'support_areas': ['Co-Development – Collaborating on tailored solutions', 'Financial Support – Funding startups and projects', 'Mentorship & Expertise – Guiding startups with knowledge'],
                'support_details': 'We offer corporate venture capital through Unilever Ventures, strategic partnerships, pilot opportunities, manufacturing scale-up support, and market access across our global distribution network.',
                'additional_info': 'Committed to halving virgin plastic use by 2025. Annual revenue of $60B+ globally. Operating plastic waste collection programs in Indonesia, Philippines, and Thailand reaching 100,000+ households.'
            },
            {
                'username': 'scg_circular_director',
                'email': 'circular@scg.com',
                'first_name': 'Supachai',
                'last_name': 'Wichianchai',
                'job_position': 'Director, Circular Economy',
                'bio': 'Leading SCG\'s circular economy transformation across ASEAN. 15+ years in materials science and industrial innovation. Expert in chemical recycling and advanced materials development.',
                'password': 'seamap2025',
                'company_name': 'SCG Circular Economy Solutions',
                'website': 'https://scg.com/circular',
                'founded_year': 1913,
                'team_size': '100+',
                'primary_location': 'Thailand',
                'company_description': 'SCG is a leading industrial conglomerate pioneering circular economy solutions across ASEAN. We develop advanced recycling technologies, sustainable materials, and circular business models for plastic waste valorization.',
                'organization_type': 'multinational_corporation',
                'industry_expertise': ['Industrial & Manufacturing', 'Food Production & Service', 'Retail & Consumer Goods'],
                'investment_categories': ['Upcycling Plastic Waste', 'Enhancing Plastic Recycling Systems', 'Sustainable Alternative Materials'],
                'innovation_types': ['recycling_technologies', 'plastic_alternatives', 'tracking_monitoring'],
                'support_areas': ['Pilot Programs – Testing innovative solution', 'Co-Development – Collaborating on tailored solutions', 'Financial Support – Funding startups and projects'],
                'support_details': 'We provide manufacturing partnerships, chemical recycling R&D, scale-up facilities, distribution networks, corporate venture investments, and access to circular economy expertise.',
                'additional_info': 'Revenue of $15B+ with operations across ASEAN. Operates 3 chemical recycling plants processing 30,000 tons annually. Committed to carbon neutrality by 2050 and leading regional circular economy initiatives.'
            }
        ]
        
        for corporate_data in corporates:
            user, member = self._create_user_and_member(
                corporate_data['username'],
                corporate_data['email'],
                corporate_data['first_name'],
                corporate_data['last_name'],
                corporate_data['job_position'],
                corporate_data['bio'],
                corporate_data['password']
            )
            
            company, created = Company.objects.get_or_create(
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
                    'investment_categories': corporate_data['investment_categories'],
                    'innovation_types': corporate_data['innovation_types'],
                    'support_areas': corporate_data['support_areas'],
                    'support_details': corporate_data['support_details'],
                    'additional_info': corporate_data['additional_info'],
                    'verification_status': 'approved',  # Pre-approve for demo
                }
            )
            
            if not created:
                # Update existing company with new data
                for key, value in corporate_data.items():
                    if key not in ['username', 'email', 'first_name', 'last_name', 'job_position', 'bio', 'password']:
                        setattr(company, key, value)
                company.verification_status = 'approved'
                company.save()

    def _print_login_credentials(self):
        """Print all login credentials for easy testing"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🔐 LOGIN CREDENTIALS FOR TESTING"))
        self.stdout.write("="*60)
        
        # Login info for each user type
        startup_logins = [
            ("Siriporn Thanakit (CEO & Founder)", "founder@ecopack.asia", "seamap2025"),
            ("Marcus Lim (Co-Founder & CEO)", "ceo@plasticfree.sg", "seamap2025")
        ]
        
        investor_logins = [
            ("David Chen (Managing Partner)", "partner@circularvc.asia", "seamap2025"),
            ("Sarah Williams (General Partner)", "gp@oceanimpact.fund", "seamap2025")
        ]
        
        corporate_logins = [
            ("Jennifer Lim (Head of Sustainable Innovation)", "sustainability@unilever.com.sg", "seamap2025"),
            ("Supachai Wichianchai (Director, Circular Economy)", "circular@scg.com", "seamap2025")
        ]
        
        self.stdout.write("\n🚀 STARTUP USERS:")
        for name, email, password in startup_logins:
            self.stdout.write(f"  Name: {name}")
            self.stdout.write(f"  Email: {email}")
            self.stdout.write(f"  Password: {password}")
            self.stdout.write("  ---")
        
        self.stdout.write("\n💰 INVESTOR USERS:")
        for name, email, password in investor_logins:
            self.stdout.write(f"  Name: {name}")
            self.stdout.write(f"  Email: {email}")
            self.stdout.write(f"  Password: {password}")
            self.stdout.write("  ---")
        
        self.stdout.write("\n🏢 CORPORATE USERS:")
        for name, email, password in corporate_logins:
            self.stdout.write(f"  Name: {name}")
            self.stdout.write(f"  Email: {email}")
            self.stdout.write(f"  Password: {password}")
            self.stdout.write("  ---")
        
        self.stdout.write("\n💡 QUICK LOGIN TIPS:")
        self.stdout.write("  - All accounts are pre-verified for immediate access")
        self.stdout.write("  - Use email address as username for login")
        self.stdout.write("  - All profiles are complete with sample data")
        self.stdout.write("  - Companies have realistic plastic circularity focus")
        self.stdout.write("="*60)
