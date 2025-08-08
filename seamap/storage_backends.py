"""
Custom storage backends for Cloudflare R2
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class PublicMediaStorage(S3Boto3Storage):
    """
    Storage for media files (user uploads) with public read access
    """
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'bucket_name': settings.CLOUDFLARE_R2_BUCKET_NAME,
            'location': 'media',
            'default_acl': 'public-read',
            'file_overwrite': False,
            'custom_domain': getattr(settings, 'CLOUDFLARE_R2_CUSTOM_DOMAIN', None),
            'access_key': settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            'secret_key': settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            'endpoint_url': settings.CLOUDFLARE_R2_ENDPOINT_URL,
            'region_name': 'auto',
        })
        super().__init__(*args, **kwargs)


class PrivateMediaStorage(S3Boto3Storage):
    """
    Storage for private files (documents) with private access
    """
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'bucket_name': settings.CLOUDFLARE_R2_BUCKET_NAME,
            'location': 'private',
            'default_acl': 'private',
            'file_overwrite': False,
            'access_key': settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            'secret_key': settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            'endpoint_url': settings.CLOUDFLARE_R2_ENDPOINT_URL,
            'region_name': 'auto',
        })
        super().__init__(*args, **kwargs)
