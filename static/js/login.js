/**
 * JavaScript específico para el login de PawsToHome
 * Maneja la funcionalidad de pestañas, validación y efectos visuales
 */

// Función para cambiar entre pestañas de login y registro
function showTab(tabName) {
    // Ocultar todas las pestañas
    const contents = document.querySelectorAll('.form-content');
    contents.forEach(content => content.classList.remove('active'));
    
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));
    
    // Mostrar la pestaña seleccionada
    document.getElementById(tabName).classList.add('active');
    
    // Activar el botón correspondiente
    const activeButton = tabName === 'login' ? 
        document.querySelectorAll('.tab-button')[0] : 
        document.querySelectorAll('.tab-button')[1];
    activeButton.classList.add('active');
}

// Configuración inicial cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay errores de registro para mostrar esa pestaña
    // Esta funcionalidad se manejará desde Django
    
    // Animar elementos de entrada
    initializePageAnimations();
    
    // Configurar efectos de hover para campos de entrada
    setupInputEffects();
    
    // Configurar validación de formularios
    setupFormValidation();
    
    // Configurar eventos de pestañas
    setupTabEvents();
});

/**
 * Inicializa las animaciones de entrada de la página
 */
function initializePageAnimations() {
    const authMain = document.querySelector('.auth-main');
    if (authMain) {
        authMain.style.opacity = '0';
        authMain.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            authMain.style.transition = 'all 0.6s ease';
            authMain.style.opacity = '1';
            authMain.style.transform = 'translateY(0)';
        }, 100);
    }
}

/**
 * Configura los efectos visuales para los campos de entrada
 */
function setupInputEffects() {
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        input.addEventListener('focus', function() {
            const parent = this.parentElement;
            if (parent) {
                parent.style.transform = 'translateY(-1px)';
            }
        });
        
        input.addEventListener('blur', function() {
            const parent = this.parentElement;
            if (parent) {
                parent.style.transform = 'translateY(0)';
            }
        });
    });
}

/**
 * Configura la validación y efectos de envío de formularios
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.btn');
            if (submitBtn) {
                // Efectos visuales durante el envío
                submitBtn.style.opacity = '0.7';
                
                // Determinar el tipo de formulario
                const formTypeInput = this.querySelector('input[name="form_type"]');
                const isLogin = formTypeInput && formTypeInput.value === 'login';
                const originalText = isLogin ? 'Iniciar Sesión' : 'Crear Cuenta';
                
                submitBtn.innerHTML = '<span>Procesando...</span>';
                
                // Validación básica antes del envío
                if (!validateForm(this)) {
                    e.preventDefault();
                    restoreButton(submitBtn, originalText);
                    return false;
                }
                
                // Restaurar botón después de un tiempo si hay error
                setTimeout(() => {
                    restoreButton(submitBtn, originalText);
                }, 3000);
            }
        });
    });
}

/**
 * Restaura el botón a su estado original
 */
function restoreButton(button, originalText) {
    if (button) {
        button.style.opacity = '1';
        button.innerHTML = originalText;
    }
}

/**
 * Valida un formulario antes del envío
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('input[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        // Limpiar errores previos
        clearFieldError(field);
        
        if (!field.value.trim()) {
            showFieldError(field, 'Este campo es obligatorio');
            isValid = false;
        } else {
            // Validaciones específicas por tipo de campo
            if (field.type === 'email' && !isValidEmail(field.value)) {
                showFieldError(field, 'Ingrese un correo electrónico válido');
                isValid = false;
            } else if (field.type === 'password' && field.value.length < 8) {
                showFieldError(field, 'La contraseña debe tener al menos 8 caracteres');
                isValid = false;
            }
        }
    });
    
    // Validar confirmación de contraseña en registro
    const password1 = form.querySelector('input[name="password1"]');
    const password2 = form.querySelector('input[name="password2"]');
    
    if (password1 && password2 && password1.value !== password2.value) {
        showFieldError(password2, 'Las contraseñas no coinciden');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Muestra un error en un campo específico
 */
function showFieldError(field, message) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        // Crear elemento de error si no existe
        let errorElement = formGroup.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.style.cssText = `
                color: #e53e3e;
                font-size: 0.875rem;
                margin-top: 0.5rem;
                font-family: 'Inter', sans-serif;
            `;
            formGroup.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        field.style.borderColor = '#e53e3e';
        field.style.boxShadow = '0 0 0 4px rgba(229, 62, 62, 0.1)';
    }
}

/**
 * Limpia los errores de un campo
 */
function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        const errorElement = formGroup.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    // Restaurar estilos originales
    field.style.borderColor = '';
    field.style.boxShadow = '';
}

/**
 * Valida el formato de un correo electrónico
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Configura los eventos de las pestañas
 */
function setupTabEvents() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const tabName = index === 0 ? 'login' : 'register';
            showTab(tabName);
        });
    });
}

/**
 * Función para mostrar notificaciones temporales
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#e53e3e' : type === 'success' ? '#27ae60' : '#3182ce'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        font-family: 'Inter', sans-serif;
        animation: slideInRight 0.3s ease;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

/**
 * Función para manejar errores de Django mostrados en la página
 */
function handleDjangoMessages() {
    // Esta función puede ser llamada desde el template de Django
    // para mostrar la pestaña correcta basada en errores del servidor
    const registerError = document.querySelector('.error-message');
    const registerSuccess = document.querySelector('.success-message');
    
    if (registerError || registerSuccess) {
        showTab('register');
    }
}

// Agregar estilos CSS para las animaciones de notificaciones
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(300px);
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
            transform: translateX(300px);
        }
    }
`;
document.head.appendChild(notificationStyles);