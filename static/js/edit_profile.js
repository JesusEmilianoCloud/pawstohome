// Edit Profile JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeEditProfile();
});

function initializeEditProfile() {
    // Initialize range slider
    initRangeSlider();
    
    // Initialize location functionality
    initLocationHandler();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize toggle animations
    initToggleAnimations();
}

// Range Slider Handler
function initRangeSlider() {
    const rangeSlider = document.getElementById('radio_notificaciones');
    const rangeValue = document.querySelector('.range-value');
    
    if (rangeSlider && rangeValue) {
        // Update value display
        rangeSlider.addEventListener('input', function() {
            rangeValue.textContent = this.value + ' km';
        });
        
        // Add visual feedback
        rangeSlider.addEventListener('mouseover', function() {
            this.style.cursor = 'pointer';
        });
    }
}

// Location Handler
function initLocationHandler() {
    const getLocationBtn = document.getElementById('get-location-btn');
    const latInput = document.getElementById('latitud_preferida');
    const lonInput = document.getElementById('longitud_preferida');
    
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', function() {
            getCurrentLocation(latInput, lonInput, getLocationBtn);
        });
    }
}

// Get Current Location
function getCurrentLocation(latInput, lonInput, button) {
    if (!navigator.geolocation) {
        showNotification('La geolocalización no es compatible con este navegador.', 'error');
        return;
    }
    
    // Add loading state
    button.classList.add('loading');
    button.disabled = true;
    const originalText = button.innerHTML;
    button.innerHTML = '<span>📍</span> Obteniendo ubicación...';
    
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    };
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude.toFixed(6);
            const lon = position.coords.longitude.toFixed(6);
            
            latInput.value = lat;
            lonInput.value = lon;
            
            // Add success animation
            latInput.style.borderColor = '#27ae60';
            lonInput.style.borderColor = '#27ae60';
            
            setTimeout(() => {
                latInput.style.borderColor = '';
                lonInput.style.borderColor = '';
            }, 2000);
            
            showNotification('Ubicación obtenida exitosamente', 'success');
            
            // Remove loading state
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = originalText;
        },
        function(error) {
            let errorMessage = 'Error al obtener la ubicación.';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = 'Permiso de ubicación denegado.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = 'Información de ubicación no disponible.';
                    break;
                case error.TIMEOUT:
                    errorMessage = 'Tiempo de espera agotado para obtener la ubicación.';
                    break;
            }
            
            showNotification(errorMessage, 'error');
            
            // Remove loading state
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = originalText;
        },
        options
    );
}

// Form Validation
function initFormValidation() {
    const form = document.querySelector('.profile-form');
    const latInput = document.getElementById('latitud_preferida');
    const lonInput = document.getElementById('longitud_preferida');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
            
            // Add loading state to submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    }
    
    // Real-time validation for coordinates
    if (latInput) {
        latInput.addEventListener('blur', function() {
            validateLatitude(this);
        });
    }
    
    if (lonInput) {
        lonInput.addEventListener('blur', function() {
            validateLongitude(this);
        });
    }
}

// Validate Form
function validateForm() {
    const latInput = document.getElementById('latitud_preferida');
    const lonInput = document.getElementById('longitud_preferida');
    const emailInput = document.getElementById('email');
    
    let isValid = true;
    
    // Validate email
    if (emailInput && !validateEmail(emailInput.value)) {
        showFieldError(emailInput, 'Por favor ingresa un email válido');
        isValid = false;
    } else {
        clearFieldError(emailInput);
    }
    
    // Validate coordinates if provided
    if (latInput && latInput.value && !validateLatitude(latInput)) {
        isValid = false;
    }
    
    if (lonInput && lonInput.value && !validateLongitude(lonInput)) {
        isValid = false;
    }
    
    return isValid;
}

// Validate Latitude
function validateLatitude(input) {
    const value = parseFloat(input.value);
    
    if (input.value && (isNaN(value) || value < -90 || value > 90)) {
        showFieldError(input, 'La latitud debe estar entre -90 y 90');
        return false;
    } else {
        clearFieldError(input);
        return true;
    }
}

// Validate Longitude
function validateLongitude(input) {
    const value = parseFloat(input.value);
    
    if (input.value && (isNaN(value) || value < -180 || value > 180)) {
        showFieldError(input, 'La longitud debe estar entre -180 y 180');
        return false;
    } else {
        clearFieldError(input);
        return true;
    }
}

// Validate Email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show Field Error
function showFieldError(input, message) {
    clearFieldError(input);
    
    input.style.borderColor = '#e74c3c';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#e74c3c';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    
    input.parentNode.appendChild(errorDiv);
}

// Clear Field Error
function clearFieldError(input) {
    if (input) {
        input.style.borderColor = '';
        const errorDiv = input.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

// Toggle Animations
function initToggleAnimations() {
    const toggleItems = document.querySelectorAll('.toggle-item');
    
    toggleItems.forEach(item => {
        const input = item.querySelector('input[type="checkbox"]');
        
        if (input) {
            input.addEventListener('change', function() {
                if (this.checked) {
                    item.style.background = '#e8f5e8';
                    item.style.borderColor = '#27ae60';
                } else {
                    item.style.background = '#f8f9fa';
                    item.style.borderColor = '#e9ecef';
                }
            });
            
            // Set initial state
            if (input.checked) {
                item.style.background = '#e8f5e8';
                item.style.borderColor = '#27ae60';
            }
        }
    });
}

// Show Notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: { bg: '#d4edda', border: '#c3e6cb', text: '#155724' },
        error: { bg: '#f8d7da', border: '#f5c6cb', text: '#721c24' },
        info: { bg: '#d1ecf1', border: '#bee5eb', text: '#0c5460' }
    };
    
    const color = colors[type] || colors.info;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${color.bg};
        border: 1px solid ${color.border};
        color: ${color.text};
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
        font-weight: 500;
    `;
    
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);