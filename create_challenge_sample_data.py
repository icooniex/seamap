#!/usr/bin/env python3
"""
Create sample challenge and problem statement data for testing the back office system.
Run this script with: python create_challenge_sample_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seamap.settings')
django.setup()

from member.models import Challenge, ProblemStatement, Company

def create_sample_challenges():
    """Create sample challenges for testing"""
    
    # Get some companies for testing
    companies = Company.objects.filter(company_type='corporate')[:3]
    
    if not companies.exists():
        print("No corporate companies found. Please create some companies first.")
        return
    
    # Get the first member to use as creator
    from member.models import Member
    creator = Member.objects.first()
    
    if not creator:
        print("No members found. Please create some members first.")
        return
    
    challenges_data = [
        {
            'title': 'Smart Logistics Challenge',
            'subtitle': 'Revolutionize supply chain with AI and IoT',
            'description': '''We are seeking innovative solutions to optimize our logistics operations using artificial intelligence and Internet of Things technologies. The challenge is to develop a comprehensive system that can predict delivery times, optimize routes, and reduce operational costs while maintaining high customer satisfaction.

Key areas to address:
- Real-time tracking and monitoring
- Predictive analytics for demand forecasting
- Route optimization algorithms
- Integration with existing systems
- Cost reduction strategies''',
            'organizer_contact': 'logistics@company.com',
            'requirements_content': '''Technical Requirements:
- AI/ML capabilities for predictive analytics
- IoT integration for real-time monitoring  
- Scalable cloud-based architecture
- API integration capabilities
- Mobile-friendly interface

Business Requirements:
- Reduce operational costs by 15-20%
- Improve delivery accuracy by 30%
- Enhanced customer tracking experience
- Compliance with industry standards''',
            'has_prizes': True,
            'main_prize_amount': 50000,
            'prizes_content': '''1st Place: $50,000 + 6-month pilot program
2nd Place: $25,000 + 3-month collaboration
3rd Place: $10,000 + Mentorship program

Additional Benefits:
- Access to our logistics network
- Technical mentorship from industry experts
- Potential for long-term partnership''',
            'innovation_category': 'logistics',
            'location': 'Bangkok, Thailand',
            'scope': 'Southeast Asia',
            'status': 'pending',
            'application_deadline': timezone.now() + timedelta(days=45),
            'created_by': creator,
        },
        {
            'title': 'Sustainable Energy Solutions',
            'subtitle': 'Green technology for industrial applications',
            'description': '''Our manufacturing facilities are looking for innovative renewable energy solutions that can be integrated into our existing industrial operations. We need practical, scalable, and cost-effective solutions that will help us achieve carbon neutrality by 2030.

Focus Areas:
- Solar and wind energy integration
- Energy storage solutions
- Smart grid technologies
- Energy efficiency optimization
- Carbon footprint reduction''',
            'organizer_contact': 'sustainability@company.com',
            'requirements_content': '''Solution Requirements:
- Minimum 30% reduction in energy costs
- Scalable for multiple facility locations  
- Integration with current infrastructure
- ROI within 3-5 years
- Compliance with environmental regulations

Technical Specifications:
- Industrial-grade reliability
- Remote monitoring capabilities
- Predictive maintenance features
- Safety compliance standards''',
            'has_prizes': True,
            'main_prize_amount': 75000,
            'prizes_content': '''Grand Prize: $75,000 + Implementation contract
Runner-up: $35,000 + Pilot testing opportunity
Innovation Award: $15,000 + Technology incubation

Partnership Opportunities:
- Joint development agreements
- Access to testing facilities
- Market expansion support''',
            'innovation_category': 'energy',
            'location': 'Multiple locations',
            'scope': 'Global',
            'status': 'approved',
            'application_deadline': timezone.now() + timedelta(days=30),
            'created_by': creator,
        },
        {
            'title': 'Digital Customer Experience Platform',
            'subtitle': 'Next-gen customer engagement solutions',
            'description': '''We are transforming our customer experience and need innovative digital solutions that can provide personalized, seamless interactions across all touchpoints. The goal is to create a unified platform that enhances customer satisfaction and drives business growth.

Challenge Objectives:
- Omnichannel customer experience
- Personalization at scale
- Real-time customer insights
- Automated customer service
- Enhanced mobile experience''',
            'organizer_contact': 'digital@company.com',
            'requirements_content': '''Platform Requirements:
- Multi-channel integration (web, mobile, social)
- AI-powered personalization engine
- Real-time analytics dashboard
- Customer journey mapping
- Scalable architecture

Performance Metrics:
- Improve customer satisfaction by 25%
- Increase engagement rates by 40%
- Reduce response time by 50%
- Support 10x traffic growth''',
            'has_prizes': True,
            'main_prize_amount': 60000,
            'prizes_content': '''Winner: $60,000 + 12-month development contract
Second Place: $30,000 + Proof-of-concept funding
Third Place: $15,000 + Accelerator program access

Additional Benefits:
- Customer base for testing
- Marketing co-promotion
- Technology partnership opportunities''',
            'innovation_category': 'technology',
            'location': 'Bangkok, Thailand',
            'scope': 'Asia-Pacific',
            'status': 'published',
            'application_deadline': timezone.now() + timedelta(days=60),
            'published_at': timezone.now() - timedelta(days=5),
            'created_by': creator,
        },
    ]
    
    created_challenges = []
    
    for i, challenge_data in enumerate(challenges_data):
        company = companies[i % len(companies)]
        challenge_data['organizer'] = company
        
        challenge = Challenge.objects.create(**challenge_data)
        created_challenges.append(challenge)
        print(f"Created challenge: {challenge.title} (Status: {challenge.status})")
    
    return created_challenges

def create_sample_problems():
    """Create sample problem statements for testing"""
    
    # Get some companies for testing
    companies = Company.objects.filter(company_type='corporate')[:3]
    
    if not companies.exists():
        print("No corporate companies found. Please create some companies first.")
        return
    
    # Get the first member to use as creator
    from member.models import Member
    creator = Member.objects.first()
    
    if not creator:
        print("No members found. Please create some members first.")
        return
    
    problems_data = [
        {
            'title': 'Manufacturing Process Optimization',
            'subtitle': 'Reduce waste and improve efficiency in production',
            'description': '''Our manufacturing processes generate significant waste and operate at suboptimal efficiency levels. We need innovative solutions to optimize our production line, reduce material waste by at least 25%, and improve overall operational efficiency.

Current Challenges:
- High material waste rates (15-20%)
- Inconsistent product quality
- Manual monitoring processes
- Energy inefficiency
- Limited real-time visibility

We are looking for technology solutions that can integrate with our existing machinery and provide actionable insights for continuous improvement.''',
            'current_challenges': '''Current Problems:
- High material waste rates (15-20%)
- Inconsistent product quality
- Manual monitoring processes
- Energy inefficiency
- Limited real-time visibility''',
            'contact_email': 'manufacturing@company.com',
            'solution_requirements': '''Required Capabilities:
- IoT sensors for real-time monitoring
- Machine learning for predictive analytics
- Integration with existing ERP systems
- Automated quality control systems
- Energy consumption optimization

Expected Outcomes:
- 25% reduction in material waste
- 20% improvement in energy efficiency
- 30% faster quality issue detection
- Real-time production monitoring
- Predictive maintenance capabilities''',
            'technical_requirements': '''Technical Deliverables:
- Comprehensive monitoring system
- Predictive analytics dashboard
- Automated alert systems
- Integration with existing infrastructure
- Training and documentation''',
            'collaboration_type': 'Joint Development',
            'budget_range': '200,000 - 500,000',
            'timeline': '6-12 months implementation',
            'implementation_support': '''Support Provided:
- Access to manufacturing facilities
- Technical team collaboration
- Implementation funding
- Testing environment
- Ongoing maintenance contract''',
            'region': 'Southeast Asia',
            'status': 'pending',
            'created_by': creator,
        },
        {
            'title': 'Cybersecurity Enhancement for Financial Services',
            'subtitle': 'Advanced threat detection and prevention',
            'description': '''As a financial services company, we face increasing cybersecurity threats and need advanced solutions to protect our systems and customer data. We require a comprehensive cybersecurity framework that can detect, prevent, and respond to sophisticated cyber attacks.

Security Challenges:
- Advanced persistent threats (APT)
- Phishing and social engineering attacks
- Data breach prevention
- Compliance with financial regulations
- Zero-day vulnerability protection

The solution should provide real-time threat detection, automated response capabilities, and comprehensive security monitoring across our entire IT infrastructure.''',
            'current_challenges': '''Security Challenges:
- Advanced persistent threats (APT)
- Phishing and social engineering attacks
- Data breach prevention
- Compliance with financial regulations
- Zero-day vulnerability protection''',
            'contact_email': 'security@financecompany.com',
            'solution_requirements': '''Security Requirements:
- AI-powered threat detection
- Real-time monitoring and alerting
- Automated incident response
- Compliance reporting capabilities
- Integration with existing security tools

Technical Specifications:
- Support for cloud and on-premise environments
- Scalable architecture for growth
- Low false positive rates (<1%)
- 24/7 monitoring capabilities
- Advanced analytics and reporting''',
            'technical_requirements': '''Expected Results:
- 90% reduction in security incidents
- Faster threat detection (< 5 minutes)
- Automated response to 80% of threats
- Full regulatory compliance
- Enhanced customer trust''',
            'collaboration_type': 'Implementation Partnership',
            'budget_range': '500,000 - 1,000,000',
            'timeline': '12-18 months implementation',
            'implementation_support': '''Partnership Benefits:
- Complete security framework
- 24/7 monitoring system
- Incident response procedures
- Staff training programs
- Regular security assessments''',
            'region': 'Asia-Pacific',
            'status': 'approved',
            'created_by': creator,
        },
        {
            'title': 'Smart Healthcare Patient Management',
            'subtitle': 'Digital transformation for patient care',
            'description': '''We are seeking innovative digital solutions to transform our patient management processes and improve healthcare delivery. The goal is to create an integrated system that enhances patient experience, improves clinical outcomes, and optimizes operational efficiency.

Current Pain Points:
- Fragmented patient data across systems
- Long wait times and scheduling issues
- Manual administrative processes
- Limited patient engagement tools
- Inefficient resource allocation

We need a comprehensive digital platform that can unify patient data, streamline operations, and provide better tools for both patients and healthcare providers.''',
            'current_challenges': '''Current Pain Points:
- Fragmented patient data across systems
- Long wait times and scheduling issues
- Manual administrative processes
- Limited patient engagement tools
- Inefficient resource allocation''',
            'contact_email': 'digital@healthcare.com',
            'solution_requirements': '''Platform Requirements:
- Electronic health record (EHR) integration
- Patient portal and mobile app
- Appointment scheduling system
- Telemedicine capabilities
- Real-time analytics dashboard

Compliance Requirements:
- HIPAA compliance mandatory
- HL7 FHIR standards support
- Data encryption and security
- Audit trail capabilities
- Privacy protection measures''',
            'technical_requirements': '''Expected Improvements:
- 50% reduction in patient wait times
- 40% increase in patient satisfaction
- 30% improvement in operational efficiency
- Better clinical decision making
- Enhanced patient engagement''',
            'collaboration_type': 'Technology Partnership',
            'budget_range': '300,000 - 750,000',
            'timeline': '9-15 months implementation',
            'implementation_support': '''System Features:
- Unified patient dashboard
- Automated scheduling system
- Mobile health tracking
- Predictive analytics for care
- Integrated communication tools''',
            'region': 'Thailand',
            'status': 'published',
            'published_at': timezone.now() - timedelta(days=10),
            'created_by': creator,
        },
    ]
    
    created_problems = []
    
    for i, problem_data in enumerate(problems_data):
        company = companies[i % len(companies)]
        problem_data['company'] = company
        
        problem = ProblemStatement.objects.create(**problem_data)
        created_problems.append(problem)
        print(f"Created problem statement: {problem.title} (Status: {problem.status})")
    
    return created_problems

def main():
    """Main function to create sample data"""
    print("Creating sample challenge and problem statement data...")
    print("-" * 60)
    
    # Create challenges
    print("\nCreating Challenges:")
    challenges = create_sample_challenges()
    print(f"Created {len(challenges)} challenges")
    
    # Create problem statements  
    print("\nCreating Problem Statements:")
    problems = create_sample_problems()
    print(f"Created {len(problems)} problem statements")
    
    print("-" * 60)
    print("Sample data creation completed!")
    print(f"Total created: {len(challenges)} challenges, {len(problems)} problem statements")
    print("\nYou can now test the back office system at:")
    print("- Challenges: /backoffice/challenges/")
    print("- Problem Statements: /backoffice/problems/")

if __name__ == "__main__":
    main()
