/**
 * SEA-MAP Onboarding Shared JavaScript
 * Common functionality for all onboarding pages
 */

// Utility functions
const OnboardingUtils = {
    /**
     * Fix Bootstrap modal backdrop issues
     * Call this to prevent overlay from staying after modal is closed
     */
    fixModalBackdrop: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('hidden.bs.modal', function () {
                // Remove any remaining modal backdrops
                document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                    backdrop.remove();
                });
                // Remove modal-open class from body
                document.body.classList.remove('modal-open');
                // Reset body styles
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            });
        }
    },

    /**
     * Initialize validation modal with backdrop fix
     */
    initValidationModal: function(modalId = 'validationModal') {
        this.fixModalBackdrop(modalId);
        return new bootstrap.Modal(document.getElementById(modalId));
    },

    /**
     * Initialize checkbox card interactions
     */
    initCheckboxCards: function() {
        document.querySelectorAll('.checkbox-card').forEach(card => {
            card.addEventListener('click', function() {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                this.classList.toggle('selected', checkbox.checked);
            });
        });
    },

    /**
     * Initialize role card interactions
     */
    initRoleCards: function(callback) {
        const roleCards = document.querySelectorAll('.role-card');
        
        roleCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove selected class from all cards
                roleCards.forEach(c => c.classList.remove('selected'));
                
                // Add selected class to clicked card
                this.classList.add('selected');
                
                // Check the corresponding radio button
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                }
                
                // Execute callback if provided
                if (callback) {
                    callback(this);
                }
            });

            // Add hover effects for better UX
            card.addEventListener('mouseenter', function() {
                if (!this.classList.contains('selected')) {
                    this.style.transform = 'translateY(-5px)';
                }
            });

            card.addEventListener('mouseleave', function() {
                if (!this.classList.contains('selected')) {
                    this.style.transform = 'translateY(0)';
                }
            });
        });
    },

    /**
     * Remove invalid styling when user starts typing
     */
    initFieldValidation: function() {
        document.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                }
            });
        });
    },

    /**
     * Show validation modal with custom message
     */
    showValidationModal: function(message, modalId = 'validationModal') {
        const modal = document.getElementById(modalId);
        const modalBody = document.getElementById(`${modalId.replace('Modal', 'ModalBody')}`);
        
        if (modal && modalBody) {
            modalBody.innerHTML = `<p class="mb-0">${message}</p>`;
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    },

    /**
     * Validate form fields
     */
    validateFields: function(container = document) {
        const requiredFields = container.querySelectorAll('[required]');
        let isValid = true;
        
        // Reset previous errors
        document.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        // Validate required fields
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            }
        });
        
        return isValid;
    },

    /**
     * Smooth scroll to element
     */
    scrollToElement: function(element, offset = 0) {
        if (element) {
            const elementTop = element.offsetTop - offset;
            window.scrollTo({
                top: elementTop,
                behavior: 'smooth'
            });
        }
    },

    /**
     * Debounce function for performance optimization
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Multi-step form functionality
const MultiStepForm = {
    currentStep: 1,
    totalSteps: 3,

    init: function(config = {}) {
        this.totalSteps = config.totalSteps || 3;
        this.currentStep = config.startStep || 1;
        this.form = document.getElementById(config.formId || 'onboardingForm');
        this.backBtn = document.getElementById(config.backBtnId || 'backBtn');
        this.nextBtn = document.getElementById(config.nextBtnId || 'nextBtn');
        this.submitBtn = document.getElementById(config.submitBtnId || 'submitBtn');
        this.progressBar = document.getElementById(config.progressBarId || 'progressBar');
        this.mobileIndicator = document.getElementById(config.mobileIndicatorId || 'mobile-step-indicator');
        
        this.setupEventListeners();
        this.updateStepIndicators();
    },

    setupEventListeners: function() {
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                if (this.validateCurrentStep() && this.currentStep < this.totalSteps) {
                    this.showStep(this.currentStep + 1);
                }
            });
        }

        if (this.backBtn) {
            this.backBtn.addEventListener('click', () => {
                if (this.currentStep > 1) {
                    this.showStep(this.currentStep - 1);
                }
            });
        }

        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                if (!this.validateCurrentStep()) {
                    e.preventDefault();
                }
            });
        }
    },

    showStep: function(stepNumber) {
        const stepContents = document.querySelectorAll('.step-content');
        
        stepContents.forEach(content => {
            content.classList.remove('active');
            if (parseInt(content.dataset.step) === stepNumber) {
                content.classList.add('active');
            }
        });
        
        this.currentStep = stepNumber;
        this.updateStepIndicators();
    },

    updateStepIndicators: function() {
        // Update step numbers and titles
        for (let i = 1; i <= this.totalSteps; i++) {
            const indicator = document.getElementById(`step-${i}-indicator`);
            const title = document.getElementById(`step-${i}-title`);
            
            if (indicator && title) {
                if (i < this.currentStep) {
                    indicator.className = 'step-number completed';
                    indicator.innerHTML = '<i class="bi bi-check-lg"></i>';
                    title.className = 'step-title';
                } else if (i === this.currentStep) {
                    indicator.className = 'step-number active';
                    indicator.textContent = i;
                    title.className = 'step-title active';
                } else {
                    indicator.className = 'step-number pending';
                    indicator.textContent = i;
                    title.className = 'step-title';
                }
            }
        }
        
        // Update connectors
        for (let i = 1; i < this.totalSteps; i++) {
            const connector = document.getElementById(`connector-${i}`);
            if (connector) {
                connector.className = i < this.currentStep ? 'step-connector completed' : 'step-connector';
            }
        }
        
        // Update progress bar
        if (this.progressBar) {
            const progressWidth = (this.currentStep / this.totalSteps) * 100;
            this.progressBar.style.width = progressWidth + '%';
        }
        
        // Update mobile indicator
        if (this.mobileIndicator) {
            this.mobileIndicator.textContent = `Step ${this.currentStep} of ${this.totalSteps}`;
        }
        
        // Update buttons
        if (this.backBtn) {
            this.backBtn.disabled = this.currentStep === 1;
        }
        
        if (this.nextBtn && this.submitBtn) {
            if (this.currentStep === this.totalSteps) {
                this.nextBtn.style.display = 'none';
                this.submitBtn.style.display = 'inline-flex';
            } else {
                this.nextBtn.style.display = 'inline-flex';
                this.submitBtn.style.display = 'none';
            }
        }
    },

    validateCurrentStep: function() {
        const currentStepElement = document.querySelector(`[data-step="${this.currentStep}"]`);
        let isValid = OnboardingUtils.validateFields(currentStepElement);
        
        // Custom validation for specific steps
        if (this.currentStep === 2) {
            const innovationTypes = currentStepElement.querySelectorAll('input[name="innovation_type"]:checked');
            if (innovationTypes.length === 0) {
                OnboardingUtils.showValidationModal('Please select at least one type of innovation that describes your startup\'s focus area.');
                return false;
            }
        }
        
        if (this.currentStep === 3) {
            const consentCheckboxes = currentStepElement.querySelectorAll('input[type="checkbox"][required]');
            const uncheckedRequired = Array.from(consentCheckboxes).filter(cb => !cb.checked);
            
            if (uncheckedRequired.length > 0) {
                OnboardingUtils.showValidationModal('Please accept all required consent agreements to complete your registration.');
                return false;
            }
        }
        
        if (!isValid) {
            OnboardingUtils.showValidationModal('Please fill in all required fields marked with * before continuing to the next step.');
        }
        
        return isValid;
    }
};

// Form submission handling
const FormHandler = {
    init: function() {
        this.setupFormSubmission();
    },

    setupFormSubmission: function() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Processing...';
                    
                    // Re-enable button after 5 seconds as fallback
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
                    }, 5000);
                }
            });
        });
    }
};

// Animation utilities
const AnimationUtils = {
    fadeIn: function(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        function fade(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            element.style.opacity = Math.min(progress / duration, 1);
            
            if (progress < duration) {
                requestAnimationFrame(fade);
            }
        }
        
        requestAnimationFrame(fade);
    },

    slideIn: function(element, direction = 'up', duration = 300) {
        const translations = {
            up: 'translateY(20px)',
            down: 'translateY(-20px)',
            left: 'translateX(20px)',
            right: 'translateX(-20px)'
        };
        
        element.style.transform = translations[direction];
        element.style.opacity = '0';
        element.style.display = 'block';
        
        setTimeout(() => {
            element.style.transition = `transform ${duration}ms ease, opacity ${duration}ms ease`;
            element.style.transform = 'translate(0)';
            element.style.opacity = '1';
        }, 10);
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize common utilities
    OnboardingUtils.initCheckboxCards();
    OnboardingUtils.initFieldValidation();
    FormHandler.init();
    
    // Initialize role cards if they exist
    const continueBtn = document.getElementById('continueBtn');
    if (continueBtn) {
        OnboardingUtils.initRoleCards(function() {
            continueBtn.disabled = false;
        });
    }
    
    // Initialize multi-step form if step indicators exist
    if (document.querySelector('.step-indicator')) {
        MultiStepForm.init();
    }
    
    // Store original button text for form submission
    document.querySelectorAll('[type="submit"]').forEach(btn => {
        btn.dataset.originalText = btn.innerHTML;
    });
});

// Export for use in other scripts
window.OnboardingUtils = OnboardingUtils;
window.MultiStepForm = MultiStepForm;
window.FormHandler = FormHandler;
window.AnimationUtils = AnimationUtils;
