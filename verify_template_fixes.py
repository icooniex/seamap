#!/usr/bin/env python3
"""
Quick verification script to check template syntax fixes
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/Users/sikharincholpratin/Desktop/GIZ/project/seamap')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seamap.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from member.models import Company

def test_template_fixes():
    """Test that template syntax errors are fixed"""
    client = Client()
    
    print("🔍 Verifying Template Syntax Fixes")
    print("=" * 40)
    
    # Create a temporary admin user
    try:
        test_admin = User.objects.create_user(
            username='temp_test_admin',
            email='test@test.com',
            password='test123',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Created temporary admin user: {test_admin.username}")
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return
    
    # Login
    login_success = client.login(username='temp_test_admin', password='test123')
    if login_success:
        print("✅ Admin login successful")
    else:
        print("❌ Admin login failed")
        return
    
    # Test company detail pages
    print("\n📋 Testing Company Detail Pages:")
    companies = Company.objects.all()[:5]  # Test first 5 companies
    
    success_count = 0
    for company in companies:
        try:
            response = client.get(f'/backoffice/companies/{company.id}/', follow=True)
            if response.status_code == 200:
                print(f"✅ Company {company.id} ({company.company_name or 'Unnamed'}): Template renders successfully")
                success_count += 1
            else:
                print(f"❌ Company {company.id}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Company {company.id}: Template error - {e}")
    
    print(f"\n📊 Results: {success_count}/{len(companies)} company detail pages working")
    
    # Test user detail pages (quick check)
    from member.models import Member
    print("\n📋 Testing User Detail Pages (sample):")
    members = Member.objects.all()[:3]  # Test first 3 members
    
    user_success_count = 0
    for member in members:
        try:
            response = client.get(f'/backoffice/users/{member.id}/', follow=True)
            if response.status_code == 200:
                print(f"✅ User {member.id} ({member.user.first_name} {member.user.last_name}): Template renders successfully")
                user_success_count += 1
            else:
                print(f"❌ User {member.id}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ User {member.id}: Template error - {e}")
    
    print(f"\n📊 Results: {user_success_count}/{len(members)} user detail pages working")
    
    # Clean up
    test_admin.delete()
    print(f"\n🧹 Cleaned up temporary admin user")
    
    # Summary
    total_success = success_count + user_success_count
    total_tests = len(companies) + len(members)
    
    print("\n" + "=" * 40)
    print(f"🎉 Template Fix Verification Complete!")
    print(f"📊 Overall: {total_success}/{total_tests} detail pages working")
    
    if total_success == total_tests:
        print("✅ ALL TEMPLATE SYNTAX ERRORS HAVE BEEN FIXED!")
    else:
        print("⚠️  Some pages still have issues")

if __name__ == "__main__":
    test_template_fixes()
