from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from .models import Company, Member

User = get_user_model()

class EmailLoginForm(AuthenticationForm):
    """
    Custom login form that uses email instead of username
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'id': 'email',
            'name': 'email'
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password',
            'name': 'password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'id': 'remember',
            'name': 'remember'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the username field's help text
        self.fields['username'].help_text = None
        # Update field labels
        self.fields['username'].label = 'Email'

    def clean_username(self):
        """Validate email field"""
        email = self.cleaned_data.get('username')
        if not email:
            raise forms.ValidationError("Email is required")
        
        # Check if user with this email exists
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address")
        
        return email

    def clean(self):
        """Custom authentication with email"""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class SignUpForm(UserCreationForm):
    """
    Custom signup form for user registration with enhanced styling
    """
    first_name = forms.CharField(
        max_length=150, 
        label='First Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=150, 
        label='Last Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help texts
        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CompanyForm(forms.ModelForm):
    """Base form for company information"""
    
    class Meta:
        model = Company
        fields = [
            'company_name', 'company_logo', 'website', 'founded_year',
            'team_size', 'primary_location', 'company_description'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company name'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.yourcompany.com'
            }),
            'founded_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2020',
                'min': '1900',
                'max': '2025'
            }),
            'team_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'primary_location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your company, what you do, and your mission...'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class StartupForm(CompanyForm):
    """Form for startup-specific information"""
    
    class Meta(CompanyForm.Meta):
        fields = CompanyForm.Meta.fields + [
            'problem_statement', 'current_stage', 'target_markets',
            'customer_segments', 'active_users_count', 'paying_customers_count',
            'annual_recurring_revenue', 'has_external_funding', 'funding_history',
            'amount_raised', 'funding_needed', 'use_of_funds', 
            'financial_projections', 'is_female_led', 'core_team_size',
            'team_overview', 'core_expertise'
        ]
        widgets = {
            **CompanyForm.Meta.widgets,
            'problem_statement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What problem does your startup solve?'
            }),
            'current_stage': forms.Select(attrs={
                'class': 'form-select'
            }),
            'target_markets': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your target markets...'
            }),
            'active_users_count': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10,000'
            }),
            'paying_customers_count': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1,500'
            }),
            'annual_recurring_revenue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $500,000'
            }),
            'funding_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your funding history...'
            }),
            'amount_raised': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $1,000,000'
            }),
            'funding_needed': forms.Select(attrs={
                'class': 'form-select'
            }),
            'use_of_funds': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'How will you use the funding?'
            }),
            'financial_projections': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your financial projections...'
            }),
            'core_team_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 5 people'
            }),
            'team_overview': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your core team...'
            }),
            'core_expertise': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What are your team\'s core competencies?'
            })
        }


class InvestorForm(CompanyForm):
    """Form for investor-specific information"""
    
    class Meta(CompanyForm.Meta):
        fields = CompanyForm.Meta.fields + [
            'investor_type', 'funding_size', 'average_deal_size',
            'funding_stages', 'investment_categories', 'market_country_interests',
            'investment_philosophy'
        ]
        widgets = {
            **CompanyForm.Meta.widgets,
            'investor_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'funding_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'average_deal_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'investment_philosophy': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your investment philosophy and approach...'
            })
        }


class CorporateForm(CompanyForm):
    """Form for corporate-specific information"""
    
    class Meta(CompanyForm.Meta):
        fields = CompanyForm.Meta.fields + [
            'organization_type', 'funding_size', 'average_deal_size',
            'industry_expertise', 'investment_categories', 'market_country_interests',
            'support_areas', 'investment_philosophy'
        ]
        widgets = {
            **CompanyForm.Meta.widgets,
            'organization_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'funding_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'average_deal_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'investment_philosophy': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your investment philosophy and corporate goals...'
            })
        }


class ProblemStatementForm(forms.ModelForm):
    """Form for creating and editing problem statements"""
    
    # Additional fields for documents
    technical_specifications = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        }),
        help_text='Upload technical specifications document (PDF, DOC, DOCX)'
    )
    
    requirements_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        }),
        help_text='Upload detailed requirements document (PDF, DOC, DOCX)'
    )
    
    additional_documents = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        }),
        help_text='Upload additional documents (images, PDFs, etc.)'
    )

    class Meta:
        model = None  # Will be imported dynamically to avoid circular import
        fields = [
            'title', 'subtitle', 'description', 'contact_person', 'contact_email',
            'current_challenges', 'impact_categories', 'solution_requirements',
            'technical_requirements', 'collaboration_type', 'budget_range',
            'timeline', 'implementation_support', 'region', 'industry_focus',
            'priority', 'featured_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter problem statement title...'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subtitle describing the problem...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed problem description...'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact person name'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@company.com'
            }),
            'current_challenges': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe current challenges and pain points...'
            }),
            'solution_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Detailed requirements for the solution (supports rich text formatting)...'
            }),
            'technical_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Technical specifications and requirements (supports rich text formatting)...'
            }),
            'collaboration_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Partnership, Licensing, Joint Development, etc.'
            }),
            'budget_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '$10K - $100K, Negotiable, etc.'
            }),
            'timeline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3-6 months, 1 year, etc.'
            }),
            'implementation_support': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Support offered for implementation...'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Southeast Asia, Global, etc.'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        # Import here to avoid circular import
        from .models import ProblemStatement
        self._meta.model = ProblemStatement
        super().__init__(*args, **kwargs)
