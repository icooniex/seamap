# SEA-MAP Back Office System

## Overview

The SEA-MAP Back Office is a comprehensive administrative interface designed for platform administrators to manage users, companies, and verification processes. It provides a clean, modern interface separate from the Django admin panel, specifically tailored for SEA-MAP's business needs.

## Features

### 🔐 Secure Authentication
- Dedicated login system for admin users only
- Staff/Superuser privilege verification
- Session management with security alerts

### 📊 Dashboard Overview
- Platform statistics (users, companies, pending verifications)
- Recent activity monitoring
- Quick action shortcuts

### 👥 User Management
- Complete user profile management
- Search and filter capabilities
- Profile completeness tracking
- Document verification status
- Account status management

### 🏢 Company Management
- Multi-type company profile support (Startup, Investor, Corporate)
- Advanced filtering by type and status
- Company-specific information display
- Owner relationship tracking

### ✅ Verification System (Coming Soon)
- User profile verification workflow
- Document verification and approval
- Automated verification status tracking

### 📝 Content Management (Coming Soon)
- Challenge management
- Problem statement administration
- Content publishing workflow

## Architecture

### Apps Structure
```
backoffice/
├── views.py           # Main business logic
├── forms.py           # Custom admin forms
├── urls.py            # URL routing
└── templates/backoffice/
    ├── base.html      # Base template with sidebar
    ├── login.html     # Admin login page
    ├── dashboard.html # Main dashboard
    ├── user_management.html
    ├── company_management.html
    ├── user_detail.html
    └── company_detail.html
```

### Security Features
- User privilege validation (is_staff or is_superuser)
- Session-based authentication
- CSRF protection
- Input validation and sanitization

### UI/UX Design
- Clean, minimal interface design
- Responsive layout for all devices
- Consistent color scheme and typography
- Intuitive navigation with sidebar menu
- Status badges and progress indicators

## Access Control

### Admin User Requirements
- Users must have `is_staff=True` or `is_superuser=True`
- Regular platform users cannot access the back office
- Failed login attempts are logged

### Available Admin Users
Current admin accounts in the system:
- `admin` (admin@admin.com)
- `ฟadmin` (admin@sdf.com)

## URL Structure

```
/backoffice/login/                    # Admin login
/backoffice/dashboard/                # Main dashboard
/backoffice/users/                    # User management
/backoffice/users/<id>/               # User detail page
/backoffice/companies/                # Company management
/backoffice/companies/<id>/           # Company detail page
/backoffice/logout/                   # Admin logout
```

## Development Status

### ✅ Completed Features
- [x] Admin authentication system
- [x] Dashboard with statistics
- [x] User management interface
- [x] Company management interface  
- [x] User detail pages with profile completeness
- [x] Company detail pages with type-specific information
- [x] Responsive design and UI polish
- [x] Search and filtering capabilities

### 🚧 In Development
- [ ] Document verification workflow
- [ ] Profile verification system
- [ ] Bulk actions (approve/reject multiple items)
- [ ] Email notification system
- [ ] Activity logging and audit trail

### 📋 Planned Features
- [ ] Challenge management system
- [ ] Problem statement administration
- [ ] Advanced reporting and analytics
- [ ] Role-based permissions (different admin levels)
- [ ] API endpoints for external integrations

## Technical Implementation

### Backend
- Django views with proper authentication decorators
- Pagination for large datasets
- Optimized database queries with select_related/prefetch_related
- Form validation and error handling

### Frontend
- Bootstrap 5 for responsive design
- Custom CSS for SEA-MAP branding
- JavaScript for enhanced user interactions
- Progressive enhancement principles

### Database Integration
- Leverages existing Member and Company models
- Efficient queries with proper indexing
- Foreign key relationships maintained

## Testing

### Manual Testing Checklist
- [ ] Admin login with valid credentials
- [ ] Access denied for non-admin users
- [ ] Dashboard statistics accuracy
- [ ] User search and filtering
- [ ] Company search and filtering
- [ ] Profile completeness calculations
- [ ] Navigation and responsive design
- [ ] Logout functionality

## Next Steps

1. **Implement Document Verification**
   - Add document approval/rejection workflow
   - File preview capabilities
   - Verification comments system

2. **Enhanced User Management**
   - Bulk operations
   - User messaging system
   - Account suspension/activation

3. **Content Management System**
   - Challenge CRUD operations
   - Problem statement management
   - Content scheduling and publishing

4. **Reporting and Analytics**
   - Platform usage statistics
   - User growth metrics
   - Verification completion rates

## Usage Instructions

1. **Login**: Navigate to `/backoffice/login/` and use admin credentials
2. **Dashboard**: Review platform statistics and recent activity
3. **User Management**: Search, filter, and manage user accounts
4. **Company Management**: Oversee company profiles and verification status
5. **Detail Views**: Access comprehensive user/company information

The back office system is designed to scale with SEA-MAP's growing needs while maintaining security, usability, and performance standards.
