from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Create default media files and directories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default media structure...'))
        
        try:
            # Create media directories if they don't exist
            media_dirs = [
                'profile_pictures',
                'company_logos', 
                'challenges',
                'problems',
                'documents',
                'company_documents',
                'challenge_documents',
                'problem_documents'
            ]
            
            for dir_name in media_dirs:
                dir_path = os.path.join(settings.MEDIA_ROOT, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                self.stdout.write(f'Created directory: {dir_path}')
            
            # Copy default images to media directory as fallbacks
            static_images_path = os.path.join(settings.BASE_DIR, 'static', 'images')
            default_files = {
                'logo.webp': [
                    'profile_pictures/default-profile.png',
                    'company_logos/default-company-logo.png',
                    'company_logos/default-startup-logo.png', 
                    'company_logos/default-investor-logo.png',
                    'company_logos/default-corporate-logo.png',
                    'challenges/default-challenge.png',
                    'problems/default-problem.png'
                ]
            }
            
            source_logo = os.path.join(static_images_path, 'logo.webp')
            if os.path.exists(source_logo):
                for default_file in default_files['logo.webp']:
                    dest_path = os.path.join(settings.MEDIA_ROOT, default_file)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(source_logo, dest_path)
                    self.stdout.write(f'Created default file: {dest_path}')
            
            self.stdout.write(self.style.SUCCESS('Media structure created successfully!'))
            self.stdout.write(f'Media root: {settings.MEDIA_ROOT}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating media structure: {str(e)}'))
