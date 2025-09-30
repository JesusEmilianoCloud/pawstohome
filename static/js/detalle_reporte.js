// Detalle Reporte JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeReportDetail();
});

function initializeReportDetail() {
    // Inicializar galería de fotos
    initPhotoGallery();
    
    // Inicializar formulario de comentarios
    initCommentForm();
    
    // Inicializar scroll suave
    initSmoothScrolling();
    
    // Inicializar animaciones
    initAnimations();
}

// Galería de fotos
function initPhotoGallery() {
    const mainImage = document.getElementById('main-image');
    const thumbnails = document.querySelectorAll('.thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        // Función para cambiar imagen principal
        window.changeMainImage = function(imageSrc, thumbnailElement) {
            mainImage.style.opacity = '0.7';
            
            setTimeout(() => {
                mainImage.src = imageSrc;
                mainImage.style.opacity = '1';
                
                // Actualizar thumbnails activos
                thumbnails.forEach(thumb => thumb.classList.remove('active'));
                thumbnailElement.classList.add('active');
            }, 200);
        };
        
        // Navegación con teclado
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                const currentActive = document.querySelector('.thumbnail.active');
                const currentIndex = Array.from(thumbnails).indexOf(currentActive);
                
                let newIndex;
                if (e.key === 'ArrowLeft') {
                    newIndex = currentIndex > 0 ? currentIndex - 1 : thumbnails.length - 1;
                } else {
                    newIndex = currentIndex < thumbnails.length - 1 ? currentIndex + 1 : 0;
                }
                
                const newThumbnail = thumbnails[newIndex];
                const newImageSrc = newThumbnail.querySelector('img').src;
                changeMainImage(newImageSrc, newThumbnail);
            }
        });
        
        // Zoom en la imagen principal
        mainImage.addEventListener('click', function() {
            openImageModal(this.src);
        });
    }
}

// Modal para imagen en pantalla completa
function openImageModal(imageSrc) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    const img = document.createElement('img');
    img.src = imageSrc;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 30px;
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        font-size: 2rem;
        padding: 0.5rem 1rem;
        border-radius: 50%;
        cursor: pointer;
        transition: background 0.3s ease;
    `;
    
    closeBtn.addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', escHandler);
        }
    });
    
    modal.appendChild(img);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);
}

// Formulario de comentarios
function initCommentForm() {
    const commentForm = document.querySelector('.comment-form form');
    
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const contenido = this.querySelector('#contenido');
            
            // Validación básica
            if (!contenido.value.trim()) {
                e.preventDefault();
                showNotification('Por favor escribe un comentario', 'error');
                contenido.focus();
                return;
            }
            
            // Agregar loading state
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<span>📝</span> Enviando comentario...';
            }
        });
        
        // Auto-resize del textarea
        const textarea = commentForm.querySelector('textarea');
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        }
        
        // Contador de caracteres
        addCharacterCounter(textarea);
    }
}

// Contador de caracteres para textarea
function addCharacterCounter(textarea) {
    if (!textarea) return;
    
    const maxLength = 500; // Límite de caracteres
    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.style.cssText = `
        text-align: right;
        font-size: 0.8rem;
        color: #7f8c8d;
        margin-top: 0.25rem;
    `;
    
    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${remaining} caracteres restantes`;
        
        if (remaining < 50) {
            counter.style.color = '#e74c3c';
        } else if (remaining < 100) {
            counter.style.color = '#f39c12';
        } else {
            counter.style.color = '#7f8c8d';
        }
    }
    
    textarea.setAttribute('maxlength', maxLength);
    textarea.addEventListener('input', updateCounter);
    updateCounter();
    
    textarea.parentNode.appendChild(counter);
}

// Scroll suave
function initSmoothScrolling() {
    // Scroll suave para enlaces internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animaciones al hacer scroll
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    // Animar secciones al entrar en viewport
    const sections = document.querySelectorAll('.pet-info-section, .description-section, .comments-section');
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                entry.target.style.opacity = '1';
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        section.style.opacity = '0';
        sectionObserver.observe(section);
    });
    
    // Animar sidebar cards
    const sidebarCards = document.querySelectorAll('.sidebar-card');
    
    const sidebarObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.animation = 'slideInRight 0.6s ease-out forwards';
                    entry.target.style.opacity = '1';
                }, index * 100);
            }
        });
    }, observerOptions);
    
    sidebarCards.forEach(card => {
        card.style.opacity = '0';
        sidebarObserver.observe(card);
    });
}

// Funciones de utilidad
function showNotification(message, type = 'info') {
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

// Funcionalidad de compartir (si se implementa después)
function initShareFunctionality() {
    const shareBtn = document.querySelector('.share-btn');
    
    if (shareBtn && navigator.share) {
        shareBtn.addEventListener('click', async function() {
            try {
                await navigator.share({
                    title: document.title,
                    text: 'Ayuda a encontrar esta mascota',
                    url: window.location.href
                });
            } catch (err) {
                console.log('Error sharing:', err);
            }
        });
    }
}

// Función para copiar enlace al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Enlace copiado al portapapeles', 'success');
    }).catch(() => {
        showNotification('Error al copiar enlace', 'error');
    });
}

// Manejo de enlaces de contacto
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="tel:"]') || e.target.matches('a[href^="mailto:"]')) {
        // Agregar confirmación para llamadas
        if (e.target.href.startsWith('tel:')) {
            const phoneNumber = e.target.textContent;
            if (!confirm(`¿Deseas llamar a ${phoneNumber}?`)) {
                e.preventDefault();
            }
        }
    }
});

// Agregar estilos CSS dinámicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
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
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
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
    
    .main-photo img {
        cursor: zoom-in;
        transition: transform 0.3s ease;
    }
    
    .main-photo img:hover {
        transform: scale(1.05);
    }
    
    .thumbnail {
        transition: all 0.3s ease;
    }
    
    .thumbnail:hover {
        transform: scale(1.1);
        border-color: #e67e22 !important;
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
        to { transform: rotate(360deg); }
    }
    
    .char-counter {
        transition: color 0.3s ease;
    }
`;

document.head.appendChild(style);