"""
Management command to setup Cloudflare R2 bucket and test connection
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Setup and test Cloudflare R2 bucket connection'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-bucket',
            action='store_true',
            help='Create bucket if it does not exist',
        )
        parser.add_argument(
            '--test-upload',
            action='store_true',
            help='Test file upload to bucket',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Setting up Cloudflare R2...'))
        
        # Check if R2 is configured
        if not getattr(settings, 'USE_CLOUDFLARE_R2', False):
            self.stdout.write(
                self.style.ERROR('Cloudflare R2 is not enabled. Set USE_CLOUDFLARE_R2=True')
            )
            return
        
        # Check required settings
        required_settings = [
            'CLOUDFLARE_R2_ACCESS_KEY_ID',
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
            'CLOUDFLARE_R2_BUCKET_NAME',
            'CLOUDFLARE_R2_ENDPOINT_URL',
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing_settings.append(setting)
        
        if missing_settings:
            self.stdout.write(
                self.style.ERROR(f'Missing required settings: {", ".join(missing_settings)}')
            )
            return
        
        # Initialize R2 client
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=settings.CLOUDFLARE_R2_ENDPOINT_URL,
                aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
                region_name='auto'
            )
            self.stdout.write(self.style.SUCCESS('✓ R2 client initialized'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to initialize R2 client: {e}'))
            return
        
        # Test bucket access
        bucket_name = settings.CLOUDFLARE_R2_BUCKET_NAME
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(self.style.SUCCESS(f'✓ Bucket "{bucket_name}" exists and is accessible'))
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.stdout.write(self.style.WARNING(f'Bucket "{bucket_name}" does not exist'))
                if options['create_bucket']:
                    try:
                        s3_client.create_bucket(Bucket=bucket_name)
                        self.stdout.write(self.style.SUCCESS(f'✓ Created bucket "{bucket_name}"'))
                    except Exception as create_error:
                        self.stdout.write(self.style.ERROR(f'Failed to create bucket: {create_error}'))
                        return
                else:
                    self.stdout.write(self.style.ERROR('Use --create-bucket to create the bucket'))
                    return
            else:
                self.stdout.write(self.style.ERROR(f'Error accessing bucket: {e}'))
                return
        
        # Test file upload
        if options['test_upload']:
            self.stdout.write('Testing file upload...')
            try:
                test_content = b'This is a test file for Cloudflare R2 setup'
                test_key = 'test/setup_test.txt'
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content,
                    ContentType='text/plain'
                )
                self.stdout.write(self.style.SUCCESS('✓ Test file uploaded successfully'))
                
                # Test file access
                response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
                if response['Body'].read() == test_content:
                    self.stdout.write(self.style.SUCCESS('✓ Test file retrieved successfully'))
                
                # Clean up test file
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
                self.stdout.write(self.style.SUCCESS('✓ Test file cleaned up'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'File upload test failed: {e}'))
                return
        
        # Display configuration summary
        self.stdout.write('\n' + self.style.SUCCESS('Cloudflare R2 Setup Complete!'))
        self.stdout.write(f'Bucket: {bucket_name}')
        self.stdout.write(f'Endpoint: {settings.CLOUDFLARE_R2_ENDPOINT_URL}')
        if hasattr(settings, 'CLOUDFLARE_R2_CUSTOM_DOMAIN') and settings.CLOUDFLARE_R2_CUSTOM_DOMAIN:
            self.stdout.write(f'Custom Domain: {settings.CLOUDFLARE_R2_CUSTOM_DOMAIN}')
        self.stdout.write(f'Media URL: {settings.MEDIA_URL}')
