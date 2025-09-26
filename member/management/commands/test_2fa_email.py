"""
Management command to test email configuration and 2FA OTP sending
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from member.email_utils import send_otp_email
from member.models import EmailOTP
import sys


class Command(BaseCommand):
    help = 'Test email configuration and 2FA OTP functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
            required=False
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to test OTP email with',
            required=False
        )
        parser.add_argument(
            '--basic',
            action='store_true',
            help='Send basic test email only',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔧 Testing Email Configuration...\n')
        
        # Check email settings
        self.stdout.write(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"📧 Email Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"📧 Email Port: {settings.EMAIL_PORT}")
        self.stdout.write(f"📧 Use TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"📧 From Email: {settings.DEFAULT_FROM_EMAIL}")
        
        host_user = getattr(settings, 'EMAIL_HOST_USER', None)
        if host_user:
            # Mask email for security
            masked_email = f"{host_user[:3]}***{host_user[host_user.find('@'):]}"
            self.stdout.write(f"📧 Host User: {masked_email}")
        else:
            self.stdout.write("❌ EMAIL_HOST_USER not configured!")
            return

        host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        if host_password:
            self.stdout.write(f"📧 Host Password: {'*' * len(host_password[:4])}***")
        else:
            self.stdout.write("❌ EMAIL_HOST_PASSWORD not configured!")
            return

        self.stdout.write('\n' + '='*50)
        
        # Test basic email
        if options['basic']:
            self.test_basic_email(options['email'])
            return

        # Test OTP email
        if options['user']:
            self.test_otp_email(options['user'])
        elif options['email']:
            self.test_email_with_dummy_user(options['email'])
        else:
            # Interactive mode
            self.interactive_test()

    def test_basic_email(self, email):
        """Test basic email sending"""
        if not email:
            email = input("Enter email address to test: ").strip()
            
        if not email:
            self.stdout.write(self.style.ERROR("❌ No email address provided"))
            return

        try:
            self.stdout.write(f"📤 Sending basic test email to {email}...")
            
            send_mail(
                subject='SeaMap - Email Configuration Test',
                message='This is a test email to verify your SeaMap email configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Basic email sent successfully to {email}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send basic email: {str(e)}"))

    def test_otp_email(self, username):
        """Test OTP email with existing user"""
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"👤 Found user: {user.username} ({user.email})")
            
            # Create OTP
            otp = EmailOTP.objects.create(user=user)
            self.stdout.write(f"🔐 Generated OTP: {otp.otp_code}")
            
            # Send OTP email
            self.stdout.write(f"📤 Sending OTP email to {user.email}...")
            success = send_otp_email(user, otp.otp_code)
            
            if success:
                self.stdout.write(self.style.SUCCESS(f"✅ OTP email sent successfully!"))
                self.stdout.write(f"🔍 Check your email ({user.email}) for the verification code.")
                self.stdout.write(f"🕐 OTP expires at: {otp.expires_at}")
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to send OTP email"))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User '{username}' not found"))
            self.stdout.write("Available users:")
            for user in User.objects.all()[:5]:
                self.stdout.write(f"  - {user.username} ({user.email})")

    def test_email_with_dummy_user(self, email):
        """Test OTP email with dummy user data"""
        try:
            # Create a temporary user object (not saved to DB)
            from django.contrib.auth.models import User
            dummy_user = User(
                username='test_user',
                email=email,
                first_name='Test'
            )
            
            # Generate OTP code manually
            import secrets
            otp_code = f"{secrets.randbelow(1000000):06d}"
            
            self.stdout.write(f"👤 Testing with dummy user data")
            self.stdout.write(f"📧 Email: {email}")
            self.stdout.write(f"🔐 Generated OTP: {otp_code}")
            
            # Send OTP email
            self.stdout.write(f"📤 Sending OTP email to {email}...")
            success = send_otp_email(dummy_user, otp_code)
            
            if success:
                self.stdout.write(self.style.SUCCESS(f"✅ OTP email sent successfully!"))
                self.stdout.write(f"🔍 Check your email ({email}) for the verification code.")
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to send OTP email"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))

    def interactive_test(self):
        """Interactive testing mode"""
        self.stdout.write("\n🔧 Interactive Email Test Mode")
        self.stdout.write("Choose an option:")
        self.stdout.write("1. Test with existing user")
        self.stdout.write("2. Test with email address")
        self.stdout.write("3. Send basic test email")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Show available users
            users = User.objects.all()[:10]
            if users:
                self.stdout.write("\nAvailable users:")
                for i, user in enumerate(users, 1):
                    self.stdout.write(f"{i}. {user.username} ({user.email})")
                    
                username = input("\nEnter username: ").strip()
                if username:
                    self.test_otp_email(username)
            else:
                self.stdout.write(self.style.ERROR("❌ No users found in database"))
                
        elif choice == '2':
            email = input("Enter email address: ").strip()
            if email:
                self.test_email_with_dummy_user(email)
                
        elif choice == '3':
            email = input("Enter email address: ").strip()
            if email:
                self.test_basic_email(email)
                
        else:
            self.stdout.write(self.style.ERROR("❌ Invalid choice"))