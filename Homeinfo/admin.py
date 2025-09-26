from django.contrib import admin
from .models import Notificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'tipo', 'titulo', 'leida', 
        'fecha_creacion', 'fecha_lectura'
    ]
    list_filter = ['tipo', 'leida', 'fecha_creacion']
    search_fields = [
        'usuario__username', 'titulo', 'mensaje', 
        'reporte__nombre_perro'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_lectura']
    
    fieldsets = (
        ('Destinatario', {
            'fields': ('usuario',)
        }),
        ('Contenido', {
            'fields': ('tipo', 'titulo', 'mensaje', 'url')
        }),
        ('Relación', {
            'fields': ('reporte',)
        }),
        ('Estado', {
            'fields': ('leida', 'fecha_creacion', 'fecha_lectura')
        }),
    )
    
    actions = ['marcar_como_leidas', 'marcar_como_no_leidas']
    
    def marcar_como_leidas(self, request, queryset):
        updated = 0
        for notificacion in queryset:
            if not notificacion.leida:
                notificacion.marcar_como_leida()
                updated += 1
        
        self.message_user(
            request, 
            f'{updated} notificación(es) marcada(s) como leída(s).'
        )
    marcar_como_leidas.short_description = "Marcar seleccionadas como leídas"
    
    def marcar_como_no_leidas(self, request, queryset):
        updated = queryset.filter(leida=True).update(
            leida=False, 
            fecha_lectura=None
        )
        self.message_user(
            request, 
            f'{updated} notificación(es) marcada(s) como no leída(s).'
        )
    marcar_como_no_leidas.short_description = "Marcar seleccionadas como no leídas"
