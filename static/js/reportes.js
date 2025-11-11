// Reportes JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeReports();
    initFilterFormValidation();
});

function initializeReports() {
    // Inicializar toggle de filtros
    initFilterToggle();
    
    // Inicializar efectos de las cards
    initCardEffects();
    
    // Inicializar animaciones de carga
    initLoadingAnimations();
}

// Toggle de filtros
function initFilterToggle() {
    const toggleBtn = document.getElementById('toggle-filters');
    const filtersPanel = document.getElementById('filters-panel');
    
    if (toggleBtn && filtersPanel) {
        toggleBtn.addEventListener('click', function() {
            filtersPanel.classList.toggle('active');
            
            // Cambiar texto del botón
            const isActive = filtersPanel.classList.contains('active');
            const icon = toggleBtn.querySelector('span');
            const text = toggleBtn.childNodes[2]; // Texto después del span
            
            if (isActive) {
                icon.textContent = '✕';
                toggleBtn.innerHTML = icon.outerHTML + ' Cerrar Filtros';
                toggleBtn.classList.add('active');
            } else {
                icon.textContent = '🔍';
                toggleBtn.innerHTML = icon.outerHTML + ' Filtros';
                toggleBtn.classList.remove('active');
            }
        });
        
        // Cerrar filtros si se hace clic fuera
        document.addEventListener('click', function(e) {
            if (!toggleBtn.contains(e.target) && !filtersPanel.contains(e.target)) {
                filtersPanel.classList.remove('active');
                const icon = toggleBtn.querySelector('span');
                icon.textContent = '🔍';
                toggleBtn.innerHTML = icon.outerHTML + ' Filtros';
                toggleBtn.classList.remove('active');
            }
        });
    }
}

// Efectos de las cards
function initCardEffects() {
    const reportCards = document.querySelectorAll('.report-card');
    
    reportCards.forEach(card => {
        // Efecto hover mejorado
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
        
        // Efecto de loading en el botón "Ver Detalle"
        const detailBtn = card.querySelector('a[href*="detalle"]');
        if (detailBtn) {
            detailBtn.addEventListener('click', function(e) {
                // Agregar loading state
                this.classList.add('loading');
                this.innerHTML = '<span>⏳</span> Cargando...';
                
                // Simular delay para mejor UX
                setTimeout(() => {
                    // El navegador seguirá con la navegación
                }, 300);
            });
        }
    });
}

// Animaciones de carga
function initLoadingAnimations() {
    // Animar estadísticas al hacer scroll
    const statsCards = document.querySelectorAll('.stat-card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'bounceIn 0.6s ease-out';
                animateCounter(entry.target);
            }
        });
    }, observerOptions);
    
    statsCards.forEach(card => {
        statsObserver.observe(card);
    });
    
    // Animar cards de reportes
    const reportCards = document.querySelectorAll('.report-card');
    
    const reportsObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.animation = `slideInUp 0.6s ease-out forwards`;
                    entry.target.style.opacity = '1';
                }, index * 100); // Staggered animation
            }
        });
    }, observerOptions);
    
    reportCards.forEach(card => {
        card.style.opacity = '0';
        reportsObserver.observe(card);
    });
}

// Animar contadores en las estadísticas
function animateCounter(card) {
    const counter = card.querySelector('h3');
    const target = parseInt(counter.textContent);
    let current = 0;
    const increment = target / 30; // 30 frames de animación
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            counter.textContent = target;
            clearInterval(timer);
        } else {
            counter.textContent = Math.floor(current);
        }
    }, 50);
}

// Funciones de utilidad
function showNotification(message, type = 'info') {
    // Crear notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: { bg: '#d4edda', border: '#c3e6cb', text: '#155724' },
        error: { bg: '#f8d7da', border: '#f5c6cb', text: '#721c24' },
        info: { bg: '#d1ecf1', border: '#bee5eb', text: '#0c5460' },
        warning: { bg: '#fff3cd', border: '#ffeaa7', text: '#856404' }
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
    
    // Auto remove después de 5 segundos
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

// Manejo de formularios de filtros
document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('filters-form')) {
        let valid = true;
        const requiredFields = e.target.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                showFieldError(field, 'Este campo es obligatorio');
                field.style.borderColor = '#dc3545';
                valid = false;
            } else {
                clearFieldError(field);
                field.style.borderColor = '#28a745';
            }
        });
        if (!valid) {
            e.preventDefault();
            showNotification('Por favor, completa todos los campos requeridos', 'error');
            return;
        }
        // Mostrar loading en el botón de aplicar filtros
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.classList.add('loading');
            submitBtn.innerHTML = '<span>⏳</span> Aplicando...';
        }
    }
});

function showFieldError(field, message) {
    clearFieldError(field);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.95rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.style.borderColor = '';
}

function initFilterFormValidation() {
    const filterForms = document.querySelectorAll('.filters-form');
    filterForms.forEach(form => {
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('input', function() {
                if (!this.value.trim()) {
                    showFieldError(this, 'Este campo es obligatorio');
                    this.style.borderColor = '#dc3545';
                } else {
                    clearFieldError(this);
                    this.style.borderColor = '#28a745';
                }
            });
        });
    });
}

// Manejo de enlaces de paginación
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('page-link')) {
        e.target.style.opacity = '0.7';
        e.target.innerHTML = '⏳ Cargando...';
    }
});

// Agregamos las animaciones CSS que faltan
const style = document.createElement('style');
style.textContent = `
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
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
    
    .btn.loading {
        pointer-events: none;
        opacity: 0.7;
    }
    
    .btn.loading::after {
        content: '';
        width: 16px;
        height: 16px;
        border: 2px solid transparent;
        border-top: 2px solid currentColor;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-left: 0.5rem;
    }
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
    
    .btn-outline.active {
        background: #e67e22;
        color: white;
    }
`;

document.head.appendChild(style);

// Funciones para mejorar la experiencia de usuario
function debounce(func, wait) {
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

// Búsqueda en tiempo real (si se implementa después)
function initLiveSearch() {
    const searchInput = document.querySelector('input[name="buscar"]');
    if (searchInput) {
        const debouncedSearch = debounce(function(e) {
            // Aquí se implementaría la búsqueda AJAX
            console.log('Buscando:', e.target.value);
        }, 300);
        
        searchInput.addEventListener('input', debouncedSearch);
    }
}

// Lazy loading para imágenes
function initLazyLoading() {
    const images = document.querySelectorAll('.report-image img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('fade-in');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Inicializar funciones adicionales si es necesario
// initLiveSearch();
// initLazyLoading();