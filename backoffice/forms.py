from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class BackOfficeLoginForm(AuthenticationForm):
    """
    Custom login form for back office users
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Username or Email',
                'autocomplete': 'username',
                'autofocus': True
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Password',
                'autocomplete': 'current-password',
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default labels
        self.fields['username'].label = ''
        self.fields['password'].label = ''
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check if user is staff/superuser
        try:
            user = User.objects.get(username=username)
            if not (user.is_staff or user.is_superuser):
                raise forms.ValidationError("Access denied. Admin privileges required.")
        except User.DoesNotExist:
            # Try with email
            try:
                user = User.objects.get(email=username)
                if not (user.is_staff or user.is_superuser):
                    raise forms.ValidationError("Access denied. Admin privileges required.")
                return user.username  # Return username for authentication
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid username or email.")
        
        return username
