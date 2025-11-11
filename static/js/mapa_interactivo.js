// Mapa Interactivo - PawsToHome
class MapaInteractivo {
    constructor() {
        this.mapa = null;
        this.marcadores = L.markerClusterGroup({
            chunkedLoading: true,
            iconCreateFunction: function(cluster) {
                const childCount = cluster.getChildCount();
                let c = ' marker-cluster-';
                if (childCount < 10) {
                    c += 'small';
                } else if (childCount < 100) {
                    c += 'medium';
                } else {
                    c += 'large';
                }
                return new L.DivIcon({ 
                    html: '<div><span>' + childCount + '</span></div>', 
                    className: 'marker-cluster' + c, 
                    iconSize: new L.Point(40, 40) 
                });
            }
        });
        
        this.filtrosActivos = {
            tipo: '',  // Cambiado de 'todos' a '' para que coincida con el data-type
            raza: '',
            radio: 10,  // Cambiado de 50 a 10 (valor inicial del slider)
            fechaDesde: '',
            fechaHasta: '',
            busqueda: ''
        };
        
        this.posicionUsuario = null;
        this.reportesData = [];
        
        this.init();
    }
    
    init() {
        console.log('Inicializando mapa interactivo...');
        
        // Verificar que el contenedor del mapa existe
        const contenedorMapa = document.getElementById('mapa');
        if (!contenedorMapa) {
            console.error('Contenedor del mapa no encontrado');
            return;
        }
        
        this.crearMapa();
        
        // Configurar event listeners con un pequeño retraso para asegurar que el DOM esté completo
        setTimeout(() => {
            this.configurarEventListeners();
        }, 100);
        
        this.cargarReportes();
        console.log('Mapa inicializado correctamente');
    }
    
    crearMapa() {
        // Usar configuración inicial desde el template
        const config = window.MapConfig || {
            initialLat: 31.6904,   // Ciudad Juárez por defecto
            initialLng: -106.4245,
            initialZoom: 11
        };
        
        // Inicializar mapa
        this.mapa = L.map('mapa', {
            center: [config.initialLat, config.initialLng],
            zoom: config.initialZoom,
            zoomControl: false
        });
        
        // Agregar control de zoom en posición personalizada
        L.control.zoom({
            position: 'topright'
        }).addTo(this.mapa);
        
        // Agregar capa de tiles OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.mapa);
        
        // Agregar grupo de marcadores al mapa
        this.mapa.addLayer(this.marcadores);
        
        // Si viene desde el detalle de un reporte, agregar marcador destacado
        this.agregarMarcadorDestacado();
    }
    
    configurarEventListeners() {
        console.log('Configurando event listeners...');
        
        // Filtros de tipo
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remover clase active de otros botones del mismo grupo
                const grupo = e.target.closest('.filter-buttons');
                if (grupo) {
                    grupo.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                }
                
                // Agregar clase active al botón clickeado
                e.target.classList.add('active');
                
                // Actualizar filtro - el data-type puede ser '', 'perdido' o 'encontrado'
                const tipoSeleccionado = e.target.dataset.type || '';
                this.filtrosActivos.tipo = tipoSeleccionado;
                
                this.aplicarFiltros();
            });
        });
        
        // Filtro de raza
        const razaFilter = document.getElementById('filtro-raza');
        if (razaFilter) {
            razaFilter.addEventListener('change', (e) => {
                this.filtrosActivos.raza = e.target.value;
                this.aplicarFiltros();
            });
        } else {
            console.warn('Elemento filtro-raza no encontrado');
        }
        
        // Control de radio
        const radioSlider = document.getElementById('radio-slider');
        const radioDisplay = document.getElementById('radio-value');
        
        if (radioSlider && radioDisplay) {
            radioSlider.addEventListener('input', (e) => {
                const valor = e.target.value;
                this.filtrosActivos.radio = parseInt(valor);
                radioDisplay.textContent = valor;
                this.aplicarFiltros();
            });
        } else {
            console.warn('Elementos de radio no encontrados:', { radioSlider, radioDisplay });
        }
        
        // Búsqueda
        const searchBtn = document.getElementById('btn-buscar');
        const searchInput = document.getElementById('busqueda');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                const termino = searchInput ? searchInput.value : '';
                this.filtrosActivos.busqueda = termino;
                this.aplicarFiltros();
            });
        } else {
            console.warn('Botón de búsqueda no encontrado');
        }
        
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.filtrosActivos.busqueda = e.target.value;
                    this.aplicarFiltros();
                }
            });
        } else {
            console.warn('Input de búsqueda no encontrado');
        }
        
        // Botón de ubicación
        const ubicacionBtn = document.getElementById('btn-ubicacion');
        if (ubicacionBtn) {
            ubicacionBtn.addEventListener('click', (e) => {
                console.log('Botón de ubicación clickeado');
                e.preventDefault();
                this.obtenerUbicacionUsuario();
            });
        } else {
            console.error('Botón de ubicación no encontrado en el DOM');
        }
        
        // Botones de fecha
        document.querySelectorAll('.date-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const grupo = e.target.closest('.date-buttons');
                if (grupo) {
                    grupo.querySelectorAll('.date-btn').forEach(b => b.classList.remove('active'));
                }
                e.target.classList.add('active');
                
                const period = e.target.dataset.period;
                const hoy = new Date();
                
                if (period === 'today') {
                    // Hoy
                    this.filtrosActivos.fechaDesde = hoy.toISOString().split('T')[0];
                    this.filtrosActivos.fechaHasta = hoy.toISOString().split('T')[0];
                } else if (period === 'week') {
                    // Esta semana (últimos 7 días)
                    const desde = new Date(hoy.getTime() - (7 * 24 * 60 * 60 * 1000));
                    this.filtrosActivos.fechaDesde = desde.toISOString().split('T')[0];
                    this.filtrosActivos.fechaHasta = hoy.toISOString().split('T')[0];
                } else if (period === 'month') {
                    // Este mes (últimos 30 días)
                    const desde = new Date(hoy.getTime() - (30 * 24 * 60 * 60 * 1000));
                    this.filtrosActivos.fechaDesde = desde.toISOString().split('T')[0];
                    this.filtrosActivos.fechaHasta = hoy.toISOString().split('T')[0];
                } else {
                    // Todos (limpiar filtros de fecha)
                    this.filtrosActivos.fechaDesde = '';
                    this.filtrosActivos.fechaHasta = '';
                }
                
                this.aplicarFiltros();
            });
        });
        
        // Inputs de fecha personalizados
        const fechaDesde = document.getElementById('fecha-desde');
        const fechaHasta = document.getElementById('fecha-hasta');
        
        if (fechaDesde) {
            fechaDesde.addEventListener('change', (e) => {
                this.filtrosActivos.fechaDesde = e.target.value;
                this.aplicarFiltros();
            });
        } else {
            console.warn('Input fecha-desde no encontrado');
        }
        
        if (fechaHasta) {
            fechaHasta.addEventListener('change', (e) => {
                this.filtrosActivos.fechaHasta = e.target.value;
                this.aplicarFiltros();
            });
        } else {
            console.warn('Input fecha-hasta no encontrado');
        }
        
        // Modal
        const modal = document.getElementById('modal-reporte');
        const closeBtn = document.querySelector('.modal-close');
        
        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
            
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        } else {
            console.warn('Modal o botón de cerrar no encontrado:', { modal, closeBtn });
        }
        
        console.log('Event listeners configurados');
    }
    
    async cargarReportes() {
        try {
            const response = await fetch('/maps/api/reportes/');
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            this.reportesData = data.reportes || [];
            this.mostrarReportesEnMapa();
            this.actualizarListaReportesCercanos();
        } catch (error) {
            console.error('Error al cargar reportes:', error);
            this.mostrarError(`Error al cargar los reportes: ${error.message}`);
        }
    }
    
    mostrarReportesEnMapa() {
        // Limpiar marcadores existentes
        this.marcadores.clearLayers();
        
        // Filtrar reportes según criterios activos
        const reportesFiltrados = this.filtrarReportes();
        
        reportesFiltrados.forEach(reporte => {
            if (reporte.latitud && reporte.longitud) {
                const marcador = this.crearMarcador(reporte);
                this.marcadores.addLayer(marcador);
            }
        });
    }
    
    filtrarReportes() {
        let reportesFiltrados = [...this.reportesData];
        
        // Filtro por tipo (perdido/encontrado/todos)
        if (this.filtrosActivos.tipo && this.filtrosActivos.tipo.trim() !== '') {
            reportesFiltrados = reportesFiltrados.filter(r => r.tipo_reporte === this.filtrosActivos.tipo);
        }
        
        // Filtro por raza
        if (this.filtrosActivos.raza) {
            reportesFiltrados = reportesFiltrados.filter(r => {
                // Comparar por ID si es un número, sino por nombre
                if (!isNaN(this.filtrosActivos.raza)) {
                    return r.raza_id == this.filtrosActivos.raza;
                }
                return r.raza && r.raza.toLowerCase().includes(this.filtrosActivos.raza.toLowerCase());
            });
        }
        
        // Filtro por radio (solo si hay posición del usuario)
        if (this.posicionUsuario) {
            reportesFiltrados = reportesFiltrados.filter(r => {
                if (!r.latitud || !r.longitud) return false;
                const distancia = this.calcularDistancia(
                    this.posicionUsuario.lat, 
                    this.posicionUsuario.lng, 
                    r.latitud, 
                    r.longitud
                );
                return distancia <= this.filtrosActivos.radio;
            });
        }
        
        // Filtro por fechas
        if (this.filtrosActivos.fechaDesde) {
            const fechaDesde = new Date(this.filtrosActivos.fechaDesde);
            reportesFiltrados = reportesFiltrados.filter(r => {
                const fechaReporte = new Date(r.fecha_reporte);
                return fechaReporte >= fechaDesde;
            });
        }
        
        if (this.filtrosActivos.fechaHasta) {
            const fechaHasta = new Date(this.filtrosActivos.fechaHasta + 'T23:59:59');
            reportesFiltrados = reportesFiltrados.filter(r => {
                const fechaReporte = new Date(r.fecha_reporte);
                return fechaReporte <= fechaHasta;
            });
        }
        
        // Filtro por búsqueda
        if (this.filtrosActivos.busqueda) {
            const termino = this.filtrosActivos.busqueda.toLowerCase();
            reportesFiltrados = reportesFiltrados.filter(r => 
                (r.nombre_perro && r.nombre_perro.toLowerCase().includes(termino)) ||
                (r.raza && r.raza.toLowerCase().includes(termino)) ||
                (r.descripcion && r.descripcion.toLowerCase().includes(termino)) ||
                (r.zona && r.zona.toLowerCase().includes(termino))
            );
        }
        
        return reportesFiltrados;
    }
    
    crearMarcador(reporte) {
        // Determinar color del marcador según el tipo
        const color = reporte.tipo_reporte === 'perdido' ? '#dc3545' : '#28a745';
        const icono = reporte.tipo_reporte === 'perdido' ? '🐕' : '🏠';
        
        // Crear icono personalizado
        const iconoMarcador = L.divIcon({
            className: 'custom-marker',
            html: `<div class="marker-pin" style="background-color: ${color};">
                     <div class="marker-icon">${icono}</div>
                   </div>`,
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        });
        
        const marcador = L.marker([reporte.latitud, reporte.longitud], {
            icon: iconoMarcador
        });
        
        // Crear contenido del popup
        const popupContent = this.crearPopupContent(reporte);
        marcador.bindPopup(popupContent);
        
        return marcador;
    }
    
    crearPopupContent(reporte) {
        const fechaFormateada = new Date(reporte.fecha_reporte).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        const imagenUrl = reporte.foto_url || '/static/images/default-pet.jpg';
        
        return `
            <div class="popup-content">
                <div class="popup-header">
                    <span class="popup-status ${reporte.tipo_reporte}">${reporte.tipo_reporte.toUpperCase()}</span>
                </div>
                <h3 class="popup-name">${reporte.nombre_perro || 'Sin nombre'}</h3>
                <img src="${imagenUrl}" alt="${reporte.nombre_perro}" class="popup-image" 
                     onerror="this.src='/static/images/default-pet.jpg'">
                <div class="popup-details">
                    <strong>Raza:</strong> ${reporte.raza || 'No especificada'}<br>
                    <strong>Fecha:</strong> ${fechaFormateada}<br>
                    <strong>Contacto:</strong> ${reporte.telefono_contacto || 'No disponible'}
                </div>
                <div class="popup-actions">
                    <button class="popup-btn popup-btn-primary" onclick="mapaApp.verDetalleReporte('${reporte.id}')">
                        Ver Detalles
                    </button>
                    <button class="popup-btn popup-btn-secondary" onclick="mapaApp.contactarReporte('${reporte.id}')">
                        Contactar
                    </button>
                </div>
            </div>
        `;
    }
    
    aplicarFiltros() {
        this.mostrarReportesEnMapa();
        this.actualizarListaReportesCercanos();
    }
    
    actualizarListaReportesCercanos() {
        const reportesFiltrados = this.filtrarReportes();
        const lista = document.getElementById('reports-list');
        const contador = document.getElementById('reports-count');
        
        contador.textContent = reportesFiltrados.length;
        lista.innerHTML = '';
        
        // Mostrar solo los primeros 10 reportes más cercanos
        const reportesCercanos = this.posicionUsuario ? 
            this.ordenarPorDistancia(reportesFiltrados).slice(0, 10) : 
            reportesFiltrados.slice(0, 10);
        
        reportesCercanos.forEach(reporte => {
            const item = this.crearItemReporte(reporte);
            lista.appendChild(item);
        });
    }
    
    crearItemReporte(reporte) {
        const div = document.createElement('div');
        div.className = 'report-item';
        div.onclick = () => this.centrarEnReporte(reporte);
        
        const distancia = this.posicionUsuario && reporte.latitud && reporte.longitud ?
            this.calcularDistancia(
                this.posicionUsuario.lat, 
                this.posicionUsuario.lng, 
                reporte.latitud, 
                reporte.longitud
            ).toFixed(1) + ' km' : '';
        
        const fechaFormateada = new Date(reporte.fecha_reporte).toLocaleDateString('es-ES', {
            day: 'numeric',
            month: 'short'
        });
        
        div.innerHTML = `
            <div class="report-status ${reporte.tipo_reporte}"></div>
            <div class="report-info">
                <div class="report-name">${reporte.nombre_perro || 'Sin nombre'}</div>
                <div class="report-details">
                    ${reporte.raza || 'Raza no especificada'} • ${fechaFormateada}
                    ${distancia ? ` • ${distancia}` : ''}
                </div>
            </div>
        `;
        
        return div;
    }
    
    centrarEnReporte(reporte) {
        if (reporte.latitud && reporte.longitud) {
            this.mapa.setView([reporte.latitud, reporte.longitud], 15);
            
            // Buscar el marcador y abrir su popup
            this.marcadores.eachLayer(layer => {
                const pos = layer.getLatLng();
                if (Math.abs(pos.lat - reporte.latitud) < 0.0001 && 
                    Math.abs(pos.lng - reporte.longitud) < 0.0001) {
                    layer.openPopup();
                }
            });
        }
    }
    
    ordenarPorDistancia(reportes) {
        if (!this.posicionUsuario) return reportes;
        
        return reportes.sort((a, b) => {
            const distA = this.calcularDistancia(
                this.posicionUsuario.lat, 
                this.posicionUsuario.lng, 
                a.latitud, 
                a.longitud
            );
            const distB = this.calcularDistancia(
                this.posicionUsuario.lat, 
                this.posicionUsuario.lng, 
                b.latitud, 
                b.longitud
            );
            return distA - distB;
        });
    }
    
    calcularDistancia(lat1, lon1, lat2, lon2) {
        const R = 6371; // Radio de la Tierra en km
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) * 
                Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    toRad(valor) {
        return valor * Math.PI / 180;
    }
    
    obtenerUbicacionUsuario() {
        if (!navigator.geolocation) {
            this.mostrarError('Geolocalización no soportada por este navegador');
            return;
        }
        
        const btn = document.getElementById('btn-ubicacion');
        if (!btn) {
            console.error('Botón de ubicación no encontrado');
            return;
        }
        
        const textoOriginal = btn.textContent;
        btn.textContent = 'Obteniendo ubicación...';
        btn.disabled = true;
        
        const opciones = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 minutos
        };
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log('Ubicación obtenida:', position.coords);
                this.posicionUsuario = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                // Centrar mapa en la ubicación del usuario
                this.mapa.setView([this.posicionUsuario.lat, this.posicionUsuario.lng], 14);
                
                // Agregar marcador de usuario
                this.agregarMarcadorUsuario();
                
                // Actualizar filtros y lista
                this.aplicarFiltros();
                
                btn.textContent = 'Ubicación obtenida ✓';
                btn.disabled = false;
                
                this.mostrarNotificacion('Ubicación obtenida correctamente', 'success');
                
                // Restaurar texto original después de 2 segundos
                setTimeout(() => {
                    btn.textContent = textoOriginal;
                }, 2000);
            },
            (error) => {
                console.error('Error obteniendo ubicación:', error);
                let mensajeError = 'No se pudo obtener la ubicación';
                
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        mensajeError = 'Permiso de ubicación denegado. Por favor, permite el acceso a tu ubicación en la configuración del navegador.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        mensajeError = 'Información de ubicación no disponible.';
                        break;
                    case error.TIMEOUT:
                        mensajeError = 'Tiempo de espera agotado al obtener la ubicación.';
                        break;
                    default:
                        mensajeError = 'Error desconocido al obtener la ubicación.';
                        break;
                }
                
                this.mostrarError(mensajeError);
                btn.textContent = textoOriginal;
                btn.disabled = false;
            },
            opciones
        );
    }
    
    agregarMarcadorUsuario() {
        if (this.marcadorUsuario) {
            this.mapa.removeLayer(this.marcadorUsuario);
        }
        
        const iconoUsuario = L.divIcon({
            className: 'user-marker',
            html: '<div class="user-marker-pin">📍</div>',
            iconSize: [25, 25],
            iconAnchor: [12, 25]
        });
        
        this.marcadorUsuario = L.marker([this.posicionUsuario.lat, this.posicionUsuario.lng], {
            icon: iconoUsuario
        }).bindPopup('Tu ubicación').addTo(this.mapa);
    }
    
    async verDetalleReporte(reporteId) {
        try {
            const response = await fetch(`/reports/detalle/${reporteId}/`);
            if (!response.ok) throw new Error('Error al cargar detalles');
            
            const html = await response.text();
            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('modal-reporte').style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error al cargar los detalles del reporte');
        }
    }
    
    contactarReporte(reporteId) {
        const reporte = this.reportesData.find(r => r.id === reporteId);
        if (reporte && reporte.telefono_contacto) {
            const mensaje = `Hola! Vi tu reporte sobre ${reporte.nombre_perro || 'la mascota'} en PawsToHome. ¿Podrías darme más información?`;
            const url = `https://wa.me/${reporte.telefono_contacto}?text=${encodeURIComponent(mensaje)}`;
            window.open(url, '_blank');
        } else {
            this.mostrarError('No hay información de contacto disponible');
        }
    }
    
    mostrarError(mensaje) {
        this.mostrarNotificacion(mensaje, 'error');
    }
    
    mostrarNotificacion(mensaje, tipo = 'info') {
        // Crear notificación
        const notif = document.createElement('div');
        notif.className = `notification notification-${tipo}`;
        notif.textContent = mensaje;
        
        let backgroundColor = '#17a2b8'; // info
        if (tipo === 'error') backgroundColor = '#dc3545';
        if (tipo === 'success') backgroundColor = '#28a745';
        if (tipo === 'warning') backgroundColor = '#ffc107';
        
        notif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        document.body.appendChild(notif);
        
        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (notif.parentNode) {
                    notif.remove();
                }
            }, 300);
        }, tipo === 'error' ? 5000 : 3000);
    }
    
    // Método para agregar marcador destacado cuando viene desde detalle del reporte
    agregarMarcadorDestacado() {
        const config = window.MapConfig || {};
        
        // Solo agregar marcador si tenemos coordenadas específicas y información del reporte
        if (config.initialLat && config.initialLng && config.initialNombre) {
            // Determinar color del marcador (rojo para perdido por defecto)
            const color = '#dc3545';
            const icono = '📍';
            
            // Crear icono usando el mismo estilo que los marcadores normales
            const iconoDestacado = L.divIcon({
                className: 'custom-marker',
                html: `<div class="marker-pin" style="background-color: ${color}; transform: rotate(-45deg) scale(1.2); box-shadow: 0 4px 12px rgba(0,0,0,0.4), 0 0 0 3px rgba(220, 53, 69, 0.3); animation: pulse-marcador 2s infinite;">
                         <div class="marker-icon" style="transform: rotate(45deg);">${icono}</div>
                       </div>`,
                iconSize: [36, 50],
                iconAnchor: [18, 50],
                popupAnchor: [0, -50]
            });
            
            // Crear marcador
            const marcadorDestacado = L.marker([config.initialLat, config.initialLng], {
                icon: iconoDestacado,
                zIndexOffset: 1000 // Asegurar que esté encima de otros marcadores
            }).addTo(this.mapa);
            
            // Crear contenido del popup usando el mismo formato que los popups normales
            const popupContent = `
                <div class="popup-content">
                    <div class="popup-header">
                        <span class="popup-status perdido">UBICACIÓN</span>
                    </div>
                    <h3 class="popup-name">${config.initialNombre}</h3>
                    ${config.initialZona || config.initialDireccion ? `
                        <div class="popup-details">
                            ${config.initialZona ? `<strong>Zona:</strong> ${config.initialZona}<br>` : ''}
                            ${config.initialDireccion ? `<strong>Dirección:</strong> ${config.initialDireccion}<br>` : ''}
                            <strong>Coordenadas:</strong> ${parseFloat(config.initialLat).toFixed(4)}, ${parseFloat(config.initialLng).toFixed(4)}
                        </div>
                    ` : ''}
                    <div class="popup-actions">
                        <button class="popup-btn popup-btn-primary" onclick="window.history.back()">
                            ← Volver al Detalle
                        </button>
                    </div>
                </div>
            `;
            
            marcadorDestacado.bindPopup(popupContent);
            
            // Abrir popup automáticamente
            setTimeout(() => {
                marcadorDestacado.openPopup();
            }, 500);
        }
    }
}

// CSS adicional para marcadores personalizados
const estilosMarcadores = `
    <style>
        .custom-marker {
            background: none;
            border: none;
        }
        
        .marker-pin {
            width: 30px;
            height: 30px;
            border-radius: 50% 50% 50% 0;
            position: relative;
            transform: rotate(-45deg);
            left: 50%;
            top: 50%;
            margin: -15px 0 0 -15px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .marker-icon {
            transform: rotate(45deg);
            font-size: 16px;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }
        
        .user-marker {
            background: none;
            border: none;
        }
        
        .user-marker-pin {
            font-size: 25px;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }
        
        .marker-cluster {
            background-color: rgba(102, 126, 234, 0.8);
            border-radius: 50%;
            text-align: center;
            color: white;
            font-weight: bold;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .marker-cluster div {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .marker-cluster-small {
            background-color: rgba(102, 126, 234, 0.8);
        }
        
        .marker-cluster-medium {
            background-color: rgba(102, 126, 234, 0.9);
        }
        
        .marker-cluster-large {
            background-color: rgba(102, 126, 234, 1);
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        

    </style>
`;

// Agregar estilos al head
document.head.insertAdjacentHTML('beforeend', estilosMarcadores);

// Inicializar aplicación cuando se carga la página
let mapaApp;

function inicializarMapa() {
    console.log('DOM cargado, iniciando aplicación...');
    try {
        mapaApp = new MapaInteractivo();
        console.log('Mapa inicializado exitosamente');
    } catch (error) {
        console.error('Error al inicializar el mapa:', error);
    }
}

// Verificar si el DOM ya está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarMapa);
} else {
    // DOM ya está listo
    inicializarMapa();
}