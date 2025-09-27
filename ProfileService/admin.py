from django.contrib import admin
from .models import ConfiguracionUsuario

@admin.register(ConfiguracionUsuario)
class ConfiguracionUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'notificaciones_email', 'notificaciones_push', 
        'radio_notificaciones', 'notificar_perdidos', 'notificar_encontrados',
        'latitud_preferida', 'longitud_preferida'
    ]
    list_filter = [
        'notificaciones_email', 'notificaciones_push', 
        'notificar_perdidos', 'notificar_encontrados'
    ]
    search_fields = ['usuario__username', 'usuario__email']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Configuración de Notificaciones', {
            'fields': (
                'notificaciones_email', 
                'notificaciones_push', 
                'notificar_perdidos', 
                'notificar_encontrados'
            )
        }),
        ('Configuración Geográfica', {
            'fields': (
                ('latitud_preferida', 'longitud_preferida'), 
                'radio_notificaciones'
            ),
            'description': 'Configura la ubicación base y el radio para recibir notificaciones de reportes cercanos.'
        }),
    )
