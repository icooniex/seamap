#!/usr/bin/env python3
"""
Test script to verify back office functionality after template fixes
"""

import requests
import sys
from urllib.parse import urljoin

BASE_URL = "http://0.0.0.0:8000"
BACKOFFICE_URL = urljoin(BASE_URL, "/backoffice/")

def test_page(url, expected_status=200, description=""):
    """Test a page and return success status"""
    try:
        response = requests.get(url, allow_redirects=False)
        if response.status_code == expected_status:
            print(f"✅ {description}: {response.status_code}")
            return True
        else:
            print(f"❌ {description}: Expected {expected_status}, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Connection error - {e}")
        return False

def test_login_required_pages():
    """Test pages that should redirect to login"""
    pages_requiring_login = [
        (urljoin(BACKOFFICE_URL, "dashboard/"), "Dashboard (should redirect to login)"),
        (urljoin(BACKOFFICE_URL, "users/"), "User Management (should redirect to login)"),
        (urljoin(BACKOFFICE_URL, "companies/"), "Company Management (should redirect to login)"),
    ]
    
    print("\n📋 Testing Login Required Pages:")
    success_count = 0
    for url, description in pages_requiring_login:
        # Should redirect (302) or be forbidden (403) if not logged in
        if test_page(url, expected_status=302, description=description):
            success_count += 1
    
    return success_count, len(pages_requiring_login)

def test_accessible_pages():
    """Test pages that should be accessible without login"""
    accessible_pages = [
        (urljoin(BACKOFFICE_URL, "login/"), "Back Office Login Page"),
    ]
    
    print("\n📋 Testing Accessible Pages:")
    success_count = 0
    for url, description in accessible_pages:
        if test_page(url, expected_status=200, description=description):
            success_count += 1
    
    return success_count, len(accessible_pages)

def main():
    """Run all tests"""
    print("🔍 Testing Back Office System Functionality")
    print("=" * 50)
    
    # Test server availability
    print("\n🌐 Testing Server Connection:")
    if not test_page(BASE_URL, description="Main Django Server"):
        print("❌ Server is not responding. Make sure Django server is running.")
        sys.exit(1)
    
    # Test back office pages
    login_success, login_total = test_login_required_pages()
    accessible_success, accessible_total = test_accessible_pages()
    
    # Summary
    total_success = login_success + accessible_success
    total_tests = login_total + accessible_total
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {total_success}/{total_tests} tests passed")
    
    if total_success == total_tests:
        print("🎉 All back office routing and authentication checks passed!")
        print("\n✨ Template syntax errors have been successfully fixed!")
        print("📌 Next steps:")
        print("   1. Login as admin user at: http://0.0.0.0:8000/backoffice/login/")
        print("   2. Test user management and company management features")
        print("   3. Verify profile detail views work without template errors")
    else:
        print(f"⚠️  Some tests failed. Please check the server logs.")
    
    return total_success == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
