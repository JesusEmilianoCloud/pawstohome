# PawsToHome - Modelos Implementados

## Resumen de Implementación

Se han implementado todos los modelos del diagrama Entidad-Relación de PawsToHome usando **PostgreSQL estándar** (sin PostGIS) y campos separados para latitud y longitud. Esto permite usar **Leaflet** en el frontend para la funcionalidad de mapas sin requerir la complejidad adicional de PostGIS.

## Modelos Implementados

### 1. Usuario (loginservice/models.py)
- **Modelo:** `CustomUser` - Extiende AbstractUser
- **Tabla:** `usuario`
- **Campos adicionales:**
  - `phone_number`: Teléfono (10 dígitos)
  - `fecha_registro`: Fecha automática de registro
  - `activo`: Boolean para activar/desactivar usuario

### 2. Configuración Usuario (ProfileService/models.py)
- **Modelo:** `ConfiguracionUsuario`
- **Tabla:** `configuracion_usuario`
- **Relación:** 1:1 con Usuario
- **Campos:**
  - `notificaciones_email`: Boolean
  - `notificaciones_push`: Boolean
  - `radio_notificaciones`: Float (km)
  - `latitud_preferida`: Float (-90 a 90)
  - `longitud_preferida`: Float (-180 a 180)
  - `notificar_perdidos`: Boolean
  - `notificar_encontrados`: Boolean

### 3. Raza (reportsservice/models.py)
- **Modelo:** `Raza`
- **Tabla:** `raza`
- **Campos:**
  - `nombre`: Único
  - `descripcion`: Texto
  - `tamano_promedio`: Choices (pequeño, mediano, grande, gigante)

### 4. Reporte (reportsservice/models.py)
- **Modelo:** `Reporte`
- **Tabla:** `reporte`
- **Campos principales:**
  - `id`: UUID (Primary Key)
  - `usuario`: FK a Usuario
  - `raza`: FK a Raza (nullable)
  - `tipo_reporte`: Choices (perdido, encontrado)
  - `estado`: Choices (activo, cerrado, en_proceso)
  - `nombre_perro`: CharField
  - `color`, `tamano`, `descripcion`
  - `latitud`, `longitud`: Coordenadas separadas
  - `direccion`, `zona`: Ubicación textual
  - Fechas, contacto, flags de verificación

### 5. FotoReporte (reportsservice/models.py)
- **Modelo:** `FotoReporte`
- **Tabla:** `foto_reporte`
- **Funcionalidades:**
  - Subida de imágenes con optimización automática
  - Solo una foto principal por reporte
  - Ordenamiento personalizable

### 6. Avistamiento (reportsservice/models.py)
- **Modelo:** `Avistamiento`
- **Tabla:** `avistamiento`
- **Campos:**
  - `reporte`: FK a Reporte
  - `usuario`: FK a Usuario (quien reporta)
  - `latitud`, `longitud`: Coordenadas del avistamiento
  - `confianza`: Integer (1-10)
  - `descripcion`, fechas, verificación

### 7. Comentario (reportsservice/models.py)
- **Modelo:** `Comentario`
- **Tabla:** `comentario`
- **Tipos:** avistamiento, información, actualización, pregunta, otro
- **Coordenadas opcionales** para avistamientos informales

### 8. Notificacion (Homeinfo/models.py)
- **Modelo:** `Notificacion`
- **Tabla:** `notificacion`
- **Sistema automático** de notificaciones por proximidad geográfica

## Configuración de Base de Datos

### SQLite (Desarrollo)
Por defecto usa SQLite si no hay variables de entorno configuradas.

### PostgreSQL (Producción)
Configura las siguientes variables de entorno en tu archivo `.env`:
```env
DB_NAME=pawstohome_db
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

## Funcionalidades Implementadas

### 1. Signals Automáticos
- **Creación de configuración** automática para nuevos usuarios
- **Notificaciones por proximidad** cuando se crean reportes
- **Notificaciones de avistamientos** y comentarios
- **Validación automática** de fotos principales

### 2. Cálculo de Distancias
Se implementó la **fórmula de Haversine** para calcular distancias entre coordenadas sin necesidad de PostGIS:

```python
def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    # Retorna distancia en kilómetros
```

### 3. Administración Django
- **Interfaces completas** para todos los modelos
- **Inlines relacionados** (fotos, avistamientos, comentarios)
- **Filtros y búsquedas** optimizadas
- **Acciones masivas** para notificaciones

## Integración con Leaflet

### 1. Instalación Frontend
```html
<!-- En tu template base -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

### 2. Ejemplo de Mapa de Reportes
```javascript
// Inicializar mapa
const map = L.map('map').setView([19.4326, -99.1332], 13); // Ciudad de México

// Agregar tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Cargar reportes desde API
fetch('/api/reportes/')
    .then(response => response.json())
    .then(reportes => {
        reportes.forEach(reporte => {
            const marker = L.marker([reporte.latitud, reporte.longitud])
                .bindPopup(`
                    <strong>${reporte.nombre_perro}</strong><br>
                    ${reporte.tipo_reporte}: ${reporte.descripcion}<br>
                    <a href="/reportes/${reporte.id}/">Ver detalles</a>
                `)
                .addTo(map);
        });
    });
```

### 3. Formulario con Selector de Ubicación
```javascript
// Mapa para seleccionar ubicación en formularios
const formMap = L.map('form-map').setView([19.4326, -99.1332], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(formMap);

let marker;

formMap.on('click', function(e) {
    const { lat, lng } = e.latlng;
    
    // Actualizar marker
    if (marker) {
        formMap.removeLayer(marker);
    }
    marker = L.marker([lat, lng]).addTo(formMap);
    
    // Actualizar campos del formulario
    document.getElementById('id_latitud').value = lat;
    document.getElementById('id_longitud').value = lng;
    
    // Reverse geocoding (opcional)
    reverseGeocode(lat, lng);
});
```

## API Views Sugeridas

### 1. Vista de Reportes para Mapa
```python
from django.http import JsonResponse
from .models import Reporte

def reportes_api(request):
    reportes = Reporte.objects.filter(
        visible=True, 
        estado='activo'
    ).select_related('usuario', 'raza')
    
    data = [{
        'id': str(r.id),
        'nombre_perro': r.nombre_perro,
        'tipo_reporte': r.tipo_reporte,
        'latitud': r.latitud,
        'longitud': r.longitud,
        'descripcion': r.descripcion,
        'fecha_reporte': r.fecha_reporte.isoformat(),
        'zona': r.zona,
    } for r in reportes]
    
    return JsonResponse(data, safe=False)
```

### 2. Búsqueda por Proximidad
```python
from django.db.models import Q
import math

def reportes_cercanos(request):
    lat = float(request.GET.get('lat'))
    lng = float(request.GET.get('lng'))
    radio_km = float(request.GET.get('radio', 5))
    
    # Filtro aproximado por bounding box (más eficiente)
    lat_delta = radio_km / 111.0  # Aprox 111 km por grado
    lng_delta = radio_km / (111.0 * math.cos(math.radians(lat)))
    
    reportes = Reporte.objects.filter(
        latitud__range=[lat - lat_delta, lat + lat_delta],
        longitud__range=[lng - lng_delta, lng + lng_delta],
        visible=True,
        estado='activo'
    )
    
    # Filtro preciso con Haversine (en Python para pocos resultados)
    reportes_cercanos = []
    for reporte in reportes:
        distancia = calcular_distancia_haversine(
            lat, lng, reporte.latitud, reporte.longitud
        )
        if distancia <= radio_km:
            reportes_cercanos.append({
                'reporte': reporte,
                'distancia': round(distancia, 2)
            })
    
    # Ordenar por distancia
    reportes_cercanos.sort(key=lambda x: x['distancia'])
    
    return render(request, 'reportes/cercanos.html', {
        'reportes': reportes_cercanos
    })
```

## Próximos Pasos

1. **Crear vistas y templates** para mostrar mapas con Leaflet
2. **Implementar API REST** (usar Django REST Framework)
3. **Agregar funcionalidad de búsqueda** por proximidad
4. **Implementar sistema de notificaciones** push (usar Django Channels)
5. **Optimizar consultas** con select_related y prefetch_related
6. **Agregar tests unitarios** para todos los modelos

## Comandos Útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver

# Shell de Django para probar modelos
python manage.py shell

# Verificar estructura de la base de datos
python manage.py dbshell
```

## Migración a PostGIS (Opcional)

Si más adelante quieres migrar a PostGIS para funcionalidades geoespaciales avanzadas:

1. Instalar PostGIS en PostgreSQL
2. Cambiar el ENGINE a `django.contrib.gis.db.backends.postgis`
3. Agregar `django.contrib.gis` a INSTALLED_APPS
4. Convertir campos Float a PointField
5. Recrear migraciones