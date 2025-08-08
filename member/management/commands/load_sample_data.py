from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from member.models import Member, Company
import json
import os


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

        # Path to the backup file
        backup_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sample_companies_backup.json')
        
        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f'Backup file not found: {backup_file}'))
            return

        # Check if data already exists
        if Company.objects.count() > 5 and not options['force']:
            self.stdout.write(self.style.WARNING(
                'Companies already exist in database. Use --force to override.'
            ))
            return

        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)

            # First, create users for members
            user_data = {}
            for item in data:
                if item['model'] == 'member.member':
                    member_id = item['pk']
                    user_id = item['fields']['user']
                    
                    # Create user if doesn't exist
                    if user_id not in user_data:
                        # Extract user info from our script data
                        username = self._get_username_for_member(member_id)
                        if username:
                            user, created = User.objects.get_or_create(
                                id=user_id,
                                defaults={
                                    'username': username,
                                    'email': f'{username}@example.com',
                                    'first_name': 'Sample',
                                    'last_name': 'User',
                                }
                            )
                            user_data[user_id] = user
                            if created:
                                self.stdout.write(f'Created user: {username}')

            # Load the JSON data
            from django.core.management import call_command
            from io import StringIO
            
            # Save to temp file and load
            temp_file = '/tmp/sample_data.json'
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            
            call_command('loaddata', temp_file)
            
            # Clean up
            os.remove(temp_file)
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded sample data!\n'
                f'Total Companies: {Company.objects.count()}\n'
                f'- Startups: {Company.objects.filter(company_type="startup").count()}\n'
                f'- Investors: {Company.objects.filter(company_type="investor").count()}\n'
                f'- Corporates: {Company.objects.filter(company_type="corporate").count()}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))

    def _get_username_for_member(self, member_id):
        """Get username based on member ID - simplified mapping"""
        username_map = {
            # This would need to be updated based on actual member IDs
            # For now, we'll use a simple pattern
        }
        return username_map.get(member_id, f'user_{member_id}')
