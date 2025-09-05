"""
Quick test script for the back office system
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/sikharincholpratin/Desktop/GIZ/project/seamap')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seamap.settings')
django.setup()

from django.contrib.auth.models import User
from member.models import Member, Company

def test_backoffice_data():
    """Test data availability for back office"""
    
    print("=== SEA-MAP Back Office System Test ===\n")
    
    # Test admin users
    admin_users = User.objects.filter(is_staff=True)
    print(f"👨‍💼 Admin Users: {admin_users.count()}")
    for user in admin_users:
        print(f"  - {user.username} ({user.email})")
    
    print()
    
    # Test regular members
    members = Member.objects.all()
    print(f"👥 Total Members: {members.count()}")
    if members.exists():
        recent_members = members.order_by('-created_at')[:3]
        print("Recent members:")
        for member in recent_members:
            print(f"  - {member.user.get_full_name() or member.user.username} ({member.user.email})")
    
    print()
    
    # Test companies
    companies = Company.objects.all()
    print(f"🏢 Total Companies: {companies.count()}")
    if companies.exists():
        by_type = {}
        for company in companies:
            by_type[company.company_type] = by_type.get(company.company_type, 0) + 1
        
        print("Companies by type:")
        for comp_type, count in by_type.items():
            print(f"  - {comp_type.title()}: {count}")
    
    print()
    
    # Test documents
    from member.models import MemberDocument, CompanyDocument
    
    member_docs = MemberDocument.objects.all()
    company_docs = CompanyDocument.objects.all()
    total_docs = member_docs.count() + company_docs.count()
    
    print(f"📄 Total Documents: {total_docs}")
    if total_docs > 0:
        print(f"  - Member documents: {member_docs.count()}")
        print(f"  - Company documents: {company_docs.count()}")
        
        # Only check status for member documents
        pending_member = member_docs.filter(status='pending').count()
        
        if pending_member > 0:
            print(f"  - Pending verification: {pending_member}")
    
    print()
    print("✅ Back Office System Ready!")
    print("📍 Login at: http://127.0.0.1:8000/backoffice/login/")
    print("🔑 Use admin credentials to access the system")

if __name__ == "__main__":
    test_backoffice_data()
