# Investor Onboarding Flow Documentation

## Complete Flow Path

```
signup → role selection (investor) → user profile → investor onboarding → dashboard
```

## Step-by-Step Process

### 1. User Registration (`/signup/`)
- User creates account with email, password, first name, last name
- After successful signup, redirects to role selection

### 2. Role Selection (`/onboarding/`)  
- User selects "Investor" role
- Role stored in session and Member model
- Redirects to user profile setup

### 3. User Profile (`/onboarding/profile/`)
- User completes personal profile:
  - Profile picture (optional)
  - Job position
  - Short bio  
  - Phone number
  - LinkedIn URL
- Sets `profile_completed = True`
- Redirects to investor-specific onboarding

### 4. Investor Onboarding (`/onboarding/investor/`)
- **Step 1: Organization Information**
  - Company name (required)
  - Investor type (Angel, VC, Corporate, etc.) (required)  
  - Company logo (optional)
  - Website, founded year
  - Team size (required)
  - Primary location (required)
  - Company description

- **Step 2: Investment Approach**
  - Fund size (required)
  - Average deal size (required)
  - Preferred funding stages (checkboxes, at least 1 required)
  - Investment category interests (checkboxes, at least 1 required) 
  - Market country interests (checkboxes, at least 1 required)
  - Investment philosophy (required)

- **Step 3: Support & Consent**
  - Additional information (optional)
  - Privacy consent checkboxes (both required)

### 5. Dashboard (`/dashboard/`)
- Successful completion redirects to dashboard
- Sets `onboarding_completed = True`

## Database Fields

### Member Model
- `user_type = 'investor'`
- `profile_completed = True`  
- `onboarding_completed = True`
- `consent_info = True`
- `consent_marketplace = True`

### Company Model (Investor Organization)
**Basic Info:**
- `company_name`, `investor_type`, `company_logo`
- `website`, `founded_year`, `team_size`, `primary_location`
- `company_description`

**Investment Fields:**
- `funding_size`, `average_deal_size`, `investment_philosophy`
- `funding_stages` (JSONField) - Pre-Seed, Seed, Series A/B/C/D
- `investment_categories` (JSONField) - Packaging, Recycling, etc.
- `market_country_interests` (JSONField) - Countries of interest

**Status:**
- `is_primary = True`
- `is_active = True`

## View Functions

### `onboarding_investor(request)`
**Location:** `member/views.py`

**Functionality:**
- Validates user profile completion
- Validates investor role  
- Handles GET requests (show form)
- Handles POST requests (process form data)
- Creates Company record with investor data
- Sets onboarding completion flags
- Redirects to dashboard on success

## Templates

### `templates/onboarding/investor_onboarding_complete.html`
- Complete 3-step form with independent JavaScript
- Step flow management and validation
- Checkbox cards for multi-select fields
- File upload for logo
- Bootstrap modal validation

## URL Routing

```python
path('onboarding/investor/', views.onboarding_investor, name='onboarding_investor'),
```

## Form Validation

**Step 1:**
- Company name, investor type, team size, primary location (required)
- Website URL format validation (if provided)

**Step 2:**
- Fund size, average deal size, investment philosophy (required)
- At least one funding stage must be selected
- At least one investment category must be selected  
- At least one market country must be selected

**Step 3:**
- Both consent checkboxes must be checked

## Success Messages

```
"Welcome to SEA-MAP, {company_name}! Your investor registration is complete."
```

## Error Handling

- Profile incomplete → redirect to profile setup
- Wrong user type → redirect to role selection  
- Form validation errors → stay on form with error messages
- Database errors → stay on form with error message

## Session Management

- `selected_role` cleared after successful onboarding
- Form data preserved during validation errors

## File Upload

- Company logo stored in `media/company_logos/`
- File size and type validation in JavaScript
- Optional field, form processes without logo

This flow provides a complete, validated investor onboarding experience that matches the startup onboarding pattern while capturing investor-specific data.
