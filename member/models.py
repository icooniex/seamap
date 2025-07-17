from django.db import models
from django.contrib.auth.models import User

USER_TYPE_CHOICES = [
    ('startup', 'Startup'),
    ('investor', 'Investor'),
    ('corporate', 'Corporate'),
]

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True)

    # Add more fields as needed

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

class MemberDocument(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # e.g. pitch deck, company profile, etc.

    def __str__(self):
        return f"{self.name} for {self.member.user.username}"