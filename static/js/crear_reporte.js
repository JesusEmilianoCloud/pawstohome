// Crear Reporte JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeCreateReport();
});

let currentStep = 1;
const totalSteps = 5;
let uploadedFiles = [];

function initializeCreateReport() {
    // Inicializar navegación de pasos
    initStepNavigation();
    
    // Inicializar selección de tipo
    initTypeSelection();
    
    // Inicializar subida de fotos
    initPhotoUpload();
    
    // Inicializar geolocalización
    initGeolocation();
    
    // Inicializar validación
    initFormValidation();
}

// Navegación entre pasos
function initStepNavigation() {
    const nextBtn = document.getElementById('next-step');
    const prevBtn = document.getElementById('prev-step');
    const submitBtn = document.getElementById('submit-report');
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (validateCurrentStep()) {
                nextStep();
            }
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            prevStep();
        });
    }
    
    // Navegación con indicadores de paso
    const stepDots = document.querySelectorAll('.step-dot');
    stepDots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            const targetStep = index + 1;
            if (canNavigateToStep(targetStep)) {
                goToStep(targetStep);
            }
        });
    });
}

function nextStep() {
    if (currentStep < totalSteps) {
        currentStep++;
        updateStepDisplay();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

function goToStep(step) {
    if (step >= 1 && step <= totalSteps) {
        currentStep = step;
        updateStepDisplay();
    }
}

function updateStepDisplay() {
    // Ocultar todos los pasos
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Mostrar paso actual
    const activeStep = document.querySelector(`[data-step="${currentStep}"]`);
    if (activeStep) {
        activeStep.classList.add('active');
    }
    
    // Actualizar indicadores
    document.querySelectorAll('.step-dot').forEach((dot, index) => {
        dot.classList.remove('active', 'completed');
        if (index + 1 === currentStep) {
            dot.classList.add('active');
        } else if (index + 1 < currentStep) {
            dot.classList.add('completed');
        }
    });
    
    // Actualizar botones de navegación
    const nextBtn = document.getElementById('next-step');
    const prevBtn = document.getElementById('prev-step');
    const submitBtn = document.getElementById('submit-report');
    
    if (prevBtn) {
        prevBtn.style.display = currentStep > 1 ? 'inline-flex' : 'none';
    }
    
    if (nextBtn && submitBtn) {
        if (currentStep === totalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-flex';
        } else {
            nextBtn.style.display = 'inline-flex';
            submitBtn.style.display = 'none';
        }
    }
}

// Selección de tipo de reporte
function initTypeSelection() {
    const typeCards = document.querySelectorAll('.report-type-card');
    
    typeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remover selección previa
            typeCards.forEach(c => c.classList.remove('selected'));
            
            // Seleccionar esta card
            this.classList.add('selected');
            
            // Marcar el radio button correspondiente
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
            }
            
            // Actualizar texto dinámico si es necesario
            updateDynamicText(radio.value);
        });
    });
}

function updateDynamicText(tipoReporte) {
    // Actualizar textos que cambian según el tipo
    const stepDescriptions = document.querySelectorAll('[data-dynamic-text]');
    
    stepDescriptions.forEach(element => {
        const textType = element.dataset.dynamicText;
        
        if (textType === 'fecha-incidente') {
            if (tipoReporte === 'perdido') {
                element.textContent = '¿Cuándo se perdió la mascota?';
            } else {
                element.textContent = '¿Cuándo encontraste la mascota?';
            }
        }
    });
}

// Subida de fotos
function initPhotoUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('fotos');
    const photoPreview = document.getElementById('photo-preview');
    
    if (!uploadArea || !fileInput) return;
    
    // Click en área de subida
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });
    
    // Cambio en input de archivos
    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
}

function handleFiles(files) {
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    const maxSize = 5 * 1024 * 1024; // 5MB
    const maxFiles = 6;
    
    files.forEach(file => {
        // Validaciones
        if (!validTypes.includes(file.type)) {
            showNotification('Solo se permiten archivos JPG, PNG y WebP', 'error');
            return;
        }
        
        if (file.size > maxSize) {
            showNotification('El archivo es demasiado grande (máximo 5MB)', 'error');
            return;
        }
        
        if (uploadedFiles.length >= maxFiles) {
            showNotification(`Máximo ${maxFiles} fotos permitidas`, 'warning');
            return;
        }
        
        // Agregar archivo
        uploadedFiles.push(file);
        createPreviewItem(file);
    });
}

function createPreviewItem(file) {
    const photoPreview = document.getElementById('photo-preview');
    
    const previewItem = document.createElement('div');
    previewItem.className = 'preview-item';
    
    const img = document.createElement('img');
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-photo';
    removeBtn.textContent = '×';
    removeBtn.type = 'button';
    
    // Crear preview de la imagen
    const reader = new FileReader();
    reader.onload = function(e) {
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    // Función para remover foto
    removeBtn.addEventListener('click', function() {
        const index = uploadedFiles.indexOf(file);
        if (index > -1) {
            uploadedFiles.splice(index, 1);
        }
        previewItem.remove();
    });
    
    previewItem.appendChild(img);
    previewItem.appendChild(removeBtn);
    photoPreview.appendChild(previewItem);
}

// Geolocalización
function initGeolocation() {
    const getLocationBtn = document.getElementById('get-location');
    const latInput = document.getElementById('latitud');
    const lonInput = document.getElementById('longitud');
    
    if (getLocationBtn && latInput && lonInput) {
        getLocationBtn.addEventListener('click', function() {
            getCurrentLocation(latInput, lonInput, getLocationBtn);
        });
    }
}

function getCurrentLocation(latInput, lonInput, button) {
    if (!navigator.geolocation) {
        showNotification('La geolocalización no es compatible con este navegador', 'error');
        return;
    }
    
    // Estado de carga
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
            
            // Efecto de éxito
            latInput.classList.add('success');
            lonInput.classList.add('success');
            
            setTimeout(() => {
                latInput.classList.remove('success');
                lonInput.classList.remove('success');
            }, 3000);
            
            showNotification('Ubicación obtenida exitosamente', 'success');
            
            // Restaurar botón
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = originalText;
        },
        function(error) {
            let errorMessage = 'Error al obtener la ubicación';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = 'Permiso de ubicación denegado';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = 'Información de ubicación no disponible';
                    break;
                case error.TIMEOUT:
                    errorMessage = 'Tiempo de espera agotado';
                    break;
            }
            
            showNotification(errorMessage, 'error');
            
            // Restaurar botón
            button.classList.remove('loading');
            button.disabled = false;
            button.innerHTML = originalText;
        },
        options
    );
}

// Validación de formulario
function initFormValidation() {
    const form = document.getElementById('report-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateAllSteps()) {
                e.preventDefault();
                showNotification('Por favor completa todos los campos requeridos', 'error');
                return false;
            }
            
            // Preparar archivos para envío
            prepareFilesForSubmission();
            
            // Estado de carga en botón submit
            const submitBtn = document.getElementById('submit-report');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<span>📝</span> Creando reporte...';
            }
        });
    }
}

function validateCurrentStep() {
    const currentStepElement = document.querySelector(`[data-step="${currentStep}"]`);
    const requiredFields = currentStepElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Validaciones específicas por paso
    if (currentStep === 1) {
        const selectedType = document.querySelector('input[name="tipo_reporte"]:checked');
        if (!selectedType) {
            showNotification('Por favor selecciona el tipo de reporte', 'error');
            isValid = false;
        }
    }
    
    if (currentStep === 4) {
        if (!validateCoordinates()) {
            isValid = false;
        }
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    
    // Limpiar estilos previos
    field.classList.remove('error', 'success');
    
    // Validar campo requerido
    if (field.hasAttribute('required') && !value) {
        field.classList.add('error');
        showFieldError(field, 'Este campo es requerido');
        return false;
    }
    
    // Validaciones específicas por tipo
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.classList.add('error');
            showFieldError(field, 'Ingresa un email válido');
            return false;
        }
    }
    
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\d\s\-\(\)\+]{10,}$/;
        if (!phoneRegex.test(value)) {
            field.classList.add('error');
            showFieldError(field, 'Ingresa un teléfono válido');
            return false;
        }
    }
    
    // Campo válido
    field.classList.add('success');
    clearFieldError(field);
    return true;
}

function validateCoordinates() {
    const latInput = document.getElementById('latitud');
    const lonInput = document.getElementById('longitud');
    
    if (!latInput || !lonInput) return true;
    
    const lat = parseFloat(latInput.value);
    const lon = parseFloat(lonInput.value);
    
    if (isNaN(lat) || lat < -90 || lat > 90) {
        latInput.classList.add('error');
        showFieldError(latInput, 'Latitud debe estar entre -90 y 90');
        return false;
    }
    
    if (isNaN(lon) || lon < -180 || lon > 180) {
        lonInput.classList.add('error');
        showFieldError(lonInput, 'Longitud debe estar entre -180 y 180');
        return false;
    }
    
    return true;
}

function validateAllSteps() {
    let allValid = true;
    
    for (let step = 1; step <= totalSteps; step++) {
        const stepElement = document.querySelector(`[data-step="${step}"]`);
        const requiredFields = stepElement.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                allValid = false;
            }
        });
    }
    
    return allValid;
}

function canNavigateToStep(targetStep) {
    // Permitir navegación solo a pasos completados o el siguiente
    return targetStep <= currentStep + 1;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `⚠️ ${message}`;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function prepareFilesForSubmission() {
    // Crear inputs ocultos para las fotos si es necesario
    const form = document.getElementById('report-form');
    const photosContainer = document.getElementById('photos-container') || 
                           document.createElement('div');
    
    if (!document.getElementById('photos-container')) {
        photosContainer.id = 'photos-container';
        form.appendChild(photosContainer);
    }
    
    // Limpiar inputs previos
    photosContainer.innerHTML = '';
    
    // Agregar archivos seleccionados
    uploadedFiles.forEach((file, index) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.name = `foto_${index}`;
        input.style.display = 'none';
        
        // Crear un nuevo FileList con este archivo
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        
        photosContainer.appendChild(input);
    });
}

// Utilidades
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

// Validación en tiempo real
document.addEventListener('blur', function(e) {
    if (e.target.matches('.form-control[required]')) {
        validateField(e.target);
    }
}, true);

// Navegación con teclado
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        if (e.key === 'ArrowRight' && currentStep < totalSteps) {
            e.preventDefault();
            if (validateCurrentStep()) {
                nextStep();
            }
        } else if (e.key === 'ArrowLeft' && currentStep > 1) {
            e.preventDefault();
            prevStep();
        }
    }
});