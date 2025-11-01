// Authentication JavaScript file

// Password visibility toggle
document.addEventListener('DOMContentLoaded', function() {
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordInput = document.getElementById('password');
    
    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = passwordToggle.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        });
    }
    
    // Form submission handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = loginForm.querySelector('.login-btn');
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;
            
            // Add loading state
            submitBtn.classList.add('loading');
            submitBtn.innerHTML = '<span>Signing in...</span><i class="fas fa-spinner"></i>';
            
            try {
                // TODO: Replace with your actual login API endpoint
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password,
                        remember: remember
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Redirect to dashboard on success
                    window.location.href = '/dashboard';
                } else {
                    // Show error message
                    showError(data.message || 'Invalid email or password');
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
                }
            } catch (error) {
                console.error('Login error:', error);
                showError('An error occurred. Please try again.');
                submitBtn.classList.remove('loading');
                submitBtn.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
            }
        });
    }
    
    // Social login buttons
    const socialButtons = document.querySelectorAll('.social-btn');
    socialButtons.forEach(button => {
        button.addEventListener('click', function() {
            const provider = this.querySelector('i').classList.contains('fa-google') ? 'google' :
                           this.querySelector('i').classList.contains('fa-github') ? 'github' : 'microsoft';
            
            // TODO: Implement OAuth flow for social login
            console.log(`Login with ${provider}`);
            alert(`Social login with ${provider} - To be implemented`);
        });
    });
});

// Error message display function
function showError(message) {
    // Remove existing error message if any
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background: #fee2e2;
        color: #dc2626;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 14px;
        border: 1px solid #fecaca;
        animation: slideDown 0.3s ease-out;
    `;
    errorDiv.textContent = message;
    
    // Insert error message at the top of the form
    const form = document.getElementById('loginForm');
    form.insertBefore(errorDiv, form.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.style.animation = 'slideUp 0.3s ease-out';
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

// Add slideDown animation for error messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);
