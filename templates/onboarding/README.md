# SEA-MAP Onboarding Shared Templates & Assets

This document explains how to use the shared templates, CSS, and JavaScript for the SEA-MAP onboarding system.

## File Structure

```
templates/onboarding/
├── onboarding_base.html          # Base template for all onboarding pages
├── index.html                    # Role selection page (uses base template)
├── startup_onboarding_shared.html # Example startup onboarding form
└── [other onboarding pages]

static/css/
└── onboarding.css                # Shared CSS for all onboarding pages

static/js/
└── onboarding-shared.js          # Shared JavaScript utilities
```

## Base Template Usage

### Extending the Base Template

```django
{% extends 'onboarding/onboarding_base.html' %}
{% load static %}

{% block title %}Your Page Title - SEA-MAP{% endblock %}

{% block content %}
<!-- Your page content here -->
{% endblock %}
```

### Available Blocks

- `title`: Page title (defaults to "SEA-MAP Onboarding")
- `extra_css`: Additional CSS files or inline styles
- `header_content`: Customize the header section (logo, title, subtitle)
- `mobile_breadcrumb`: Mobile breadcrumb/progress indicator
- `content`: Main page content
- `modals`: Any modals used by the page
- `extra_js`: Additional JavaScript files or inline scripts

### Header Customization

```django
{% block header_content %}
<div class="logo-icon small">
    <i class="bi bi-rocket-takeoff"></i>
</div>
<h1 class="onboarding-title">Startup Registration</h1>
<p class="onboarding-subtitle">Join our community of innovative startups</p>
{% endblock %}
```

## CSS Classes Reference

### Layout Classes

- `.main-container`: Main wrapper with gradient background
- `.onboarding-wrapper`: White card container
- `.onboarding-header`: Header section with gradient background
- `.form-content`: Main form content area
- `.navigation-section`: Bottom navigation with buttons
- `.continue-section`: Single button section (for role selection)

### Navigation Classes

- `.top-navbar`: Top navigation bar
- `.navbar-brand`: Brand/logo section
- `.navbar-logo`: Logo container with gradient
- `.navbar-text-content`: Text content (title & tagline)
- `.navbar-title`: SEA-MAP title
- `.navbar-tagline`: Subtitle text

### Progress Indicator Classes

- `.progress-section`: Progress indicator container
- `.step-indicator`: Step circles and connectors
- `.step-item`: Individual step container
- `.step-number`: Step circle (states: `.active`, `.completed`, `.pending`)
- `.step-connector`: Line between steps (states: `.completed`)
- `.progress-bar-container`: Progress bar background
- `.progress-bar-fill`: Progress bar fill

### Form Classes

- `.form-group`: Form field container
- `.form-label`: Field labels
- `.form-control`: Text inputs and textareas
- `.form-select`: Select dropdowns
- `.section-title`: Main section headings
- `.section-subtitle`: Section descriptions
- `.form-title`: Step titles (in multi-step forms)
- `.form-subtitle`: Step descriptions

### Card & Selection Classes

- `.role-options`: Grid container for role cards
- `.role-card`: Individual role/option card
- `.role-icon`: Icon container with gradients
- `.role-title`: Card titles
- `.role-description`: Card descriptions
- `.selection-indicator`: Check mark for selected cards
- `.startup-icon`: Orange gradient
- `.investor-icon`: Green gradient
- `.corporate-icon`: Blue gradient

### Checkbox Components

- `.checkbox-grid`: Grid for checkbox cards
- `.checkbox-card`: Clickable checkbox container
- `.checkbox-card-content`: Checkbox content layout
- `.checkbox-icon`: Checkbox visual indicator
- `.checkbox-label`: Checkbox text

### Button Classes

- `.btn`: Base button class
- `.btn-primary`: Primary action button (SEA-MAP blue)
- `.btn-outline-secondary`: Secondary button
- `.btn:disabled`: Disabled state styling

### Consent Section

- `.consent-section`: Consent container
- `.consent-title`: Consent section title
- `.consent-item`: Individual consent item
- `.consent-checkbox`: Checkbox layout
- `.consent-text`: Consent text styling

### Responsive Classes

All components are responsive by default. Key breakpoints:
- `992px`: Role cards switch to single column
- `768px`: Mobile optimizations, reduced padding, single column layouts

## JavaScript Utilities

### OnboardingUtils

```javascript
// Initialize checkbox cards
OnboardingUtils.initCheckboxCards();

// Initialize role cards with callback
OnboardingUtils.initRoleCards(function(selectedCard) {
    console.log('Role selected:', selectedCard.dataset.role);
});

// Show validation modal
OnboardingUtils.showValidationModal('Please fill in all required fields');

// Validate form fields
const isValid = OnboardingUtils.validateFields(containerElement);
```

### MultiStepForm

```javascript
// Initialize multi-step form
MultiStepForm.init({
    totalSteps: 3,
    startStep: 1,
    formId: 'onboardingForm',
    backBtnId: 'backBtn',
    nextBtnId: 'nextBtn',
    submitBtnId: 'submitBtn'
});

// Navigate to specific step
MultiStepForm.showStep(2);

// Validate current step
const isValid = MultiStepForm.validateCurrentStep();
```

## Creating New Onboarding Pages

### 1. Simple Single-Page Form

```django
{% extends 'onboarding/onboarding_base.html' %}
{% load static %}

{% block title %}New Page - SEA-MAP{% endblock %}

{% block content %}
<form method="POST">
    {% csrf_token %}
    <div class="form-content">
        <h2 class="section-title">Page Title</h2>
        <p class="section-subtitle">Page description</p>
        
        <!-- Form fields here -->
        
    </div>
    
    <div class="continue-section">
        <button type="submit" class="btn btn-primary">
            Continue
        </button>
    </div>
</form>
{% endblock %}
```

### 2. Multi-Step Form

```django
{% extends 'onboarding/onboarding_base.html' %}
{% load static %}

{% block title %}Multi-Step Form - SEA-MAP{% endblock %}

{% block mobile_breadcrumb %}
<div class="onboarding-breadcrumb">
    <span id="mobile-step-indicator">Step 1 of 3</span>
</div>
{% endblock %}

{% block content %}
<!-- Progress Section -->
<div class="progress-section">
    <div class="step-indicator">
        <!-- Step indicators -->
    </div>
    <div class="progress-bar-container">
        <div class="progress-bar-fill" id="progressBar" style="width: 33.33%"></div>
    </div>
</div>

<form id="onboardingForm" method="POST">
    {% csrf_token %}
    
    <div class="form-content">
        <div class="step-content active" data-step="1">
            <!-- Step 1 content -->
        </div>
        
        <div class="step-content" data-step="2">
            <!-- Step 2 content -->
        </div>
    </div>
    
    <div class="navigation-section">
        <button type="button" class="btn btn-outline-secondary" id="backBtn" disabled>
            Back
        </button>
        <div>
            <button type="button" class="btn btn-primary" id="nextBtn">
                Next Step
            </button>
            <button type="submit" class="btn btn-primary" id="submitBtn" style="display: none;">
                Complete
            </button>
        </div>
    </div>
</form>
{% endblock %}
```

## Customization

### Colors

The CSS uses CSS custom properties for easy theming:

```css
:root {
    --bs-primary: #2c59a7;        /* SEA-MAP Blue */
    --bs-success: #58946e;        /* Success Green */
    --bs-warning: #EBCA38;        /* Warning Yellow */
    --bs-danger: #C73834;         /* Danger Red */
}
```

### Adding New Components

1. Add styles to `static/css/onboarding.css`
2. Follow existing naming conventions
3. Ensure responsive design
4. Test across different screen sizes

### JavaScript Extensions

Add custom functionality by extending the shared utilities:

```javascript
// Custom validation
MultiStepForm.validateCurrentStep = function() {
    // Your custom validation logic
    return true;
};

// Custom step change handler
MultiStepForm.showStep = function(stepNumber) {
    // Your custom step change logic
    // Call original method
    MultiStepForm.constructor.prototype.showStep.call(this, stepNumber);
};
```

## Best Practices

1. **Always extend the base template** for consistency
2. **Use semantic HTML** and proper form elements
3. **Follow responsive design** patterns established in the CSS
4. **Test on mobile devices** regularly
5. **Use the provided JavaScript utilities** instead of duplicating functionality
6. **Keep custom CSS minimal** by leveraging existing classes
7. **Follow accessibility guidelines** (proper labels, keyboard navigation, etc.)

## Browser Support

- Modern browsers (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- Bootstrap 5.3.0 compatibility
- Mobile browsers on iOS and Android

## Troubleshooting

### Common Issues

1. **Styles not loading**: Ensure `{% load static %}` is at the top of your template
2. **JavaScript not working**: Check browser console for errors
3. **Mobile layout issues**: Test responsive breakpoints
4. **Form validation not working**: Ensure proper field names and required attributes

### Debug Mode

Add this to your template for debugging:

```html
<script>
console.log('OnboardingUtils:', window.OnboardingUtils);
console.log('MultiStepForm:', window.MultiStepForm);
</script>
```
