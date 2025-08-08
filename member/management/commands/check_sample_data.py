from django.core.management.base import BaseCommand
from member.models import Company


class Command(BaseCommand):
    help = 'Check sample data status'

    def handle(self, *args, **options):
        try:
            total_companies = Company.objects.count()
            startups = Company.objects.filter(company_type='startup').count()
            investors = Company.objects.filter(company_type='investor').count()
            corporates = Company.objects.filter(company_type='corporate').count()
            
            self.stdout.write(self.style.SUCCESS(f'Database Status:'))
            self.stdout.write(f'Total Companies: {total_companies}')
            self.stdout.write(f'- Startups: {startups}')
            self.stdout.write(f'- Investors: {investors}')
            self.stdout.write(f'- Corporates: {corporates}')
            
            if total_companies == 0:
                self.stdout.write(self.style.WARNING('No companies found in database!'))
                self.stdout.write('Run: python manage.py load_sample_data')
            else:
                self.stdout.write(self.style.SUCCESS('Sample data exists!'))
                
                # Show sample companies
                for company in Company.objects.all()[:5]:
                    self.stdout.write(f'• {company.company_name} ({company.company_type})')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking data: {str(e)}'))
