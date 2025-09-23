# Estructura de Archivos Estáticos - PawsToHome

Esta carpeta contiene todos los archivos estáticos del proyecto PawsToHome, incluyendo CSS, JavaScript e imágenes.

## Estructura de Carpetas

```
static/
├── css/
│   ├── style.css          # Estilos principales del sitio
│   └── components.css     # Estilos para componentes específicos
├── js/
│   └── main.js           # JavaScript principal del sitio
├── images/
│   └── (archivos de imágenes)
└── README.md             # Este archivo
```

## Configuración de Django

Los archivos estáticos están configurados en `settings.py`:

```python
# URL para servir archivos estáticos
STATIC_URL = '/static/'

# Directorio donde se recopilarán los archivos estáticos en producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Directorios donde Django buscará archivos estáticos durante desarrollo
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

## Uso en Templates

Para usar archivos estáticos en los templates de Django:

```django
{% load static %}

<!-- CSS -->
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<link rel="stylesheet" href="{% static 'css/components.css' %}">

<!-- JavaScript -->
<script src="{% static 'js/main.js' %}"></script>

<!-- Imágenes -->
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

## Archivos CSS

### style.css
- Estilos base del sitio
- Layout y componentes principales
- Sistema de colores y tipografía
- Estilos responsivos

### components.css
- Estilos para componentes específicos
- Efectos y animaciones
- Utilidades CSS
- Estados de formularios

## JavaScript

### main.js
- Funcionalidades principales del sitio
- Validación de formularios
- Sistema de notificaciones
- Funciones utilitarias

## Comandos Útiles

### Desarrollo
Durante el desarrollo, Django sirve los archivos estáticos automáticamente.

### Producción
Para recopilar todos los archivos estáticos en producción:

```bash
python manage.py collectstatic
```

## Mejores Prácticas

1. **Organización**: Mantener archivos organizados en subcarpetas por tipo
2. **Nombres descriptivos**: Usar nombres claros y descriptivos para archivos
3. **Minificación**: En producción, considerar minificar CSS y JS
4. **Optimización de imágenes**: Optimizar imágenes para web
5. **Versionado**: Usar el sistema de versionado de Django para cache busting

## Navegación

- `/static/css/` - Archivos de estilos CSS
- `/static/js/` - Archivos JavaScript
- `/static/images/` - Imágenes y recursos gráficos

## Template Base

El archivo `base.html` proporciona la estructura común para todas las páginas:
- Carga automática de CSS y JS
- Navegación común
- Bloques extensibles para contenido específico
