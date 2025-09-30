from django.contrib import admin
from django.utils.html import format_html
from .models import Raza, Reporte, FotoReporte, Avistamiento, Comentario

@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tamano_promedio']
    list_filter = ['tamano_promedio']
    search_fields = ['nombre']
    ordering = ['nombre']

class FotoReporteInline(admin.TabularInline):
    model = FotoReporte
    extra = 1
    fields = ['imagen', 'descripcion', 'es_principal', 'orden']
    readonly_fields = ['fecha_subida']

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    fields = ['usuario', 'tipo', 'contenido']
    readonly_fields = ['fecha_comentario']

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_perro', 'tipo_reporte', 'estado', 'usuario', 
        'zona', 'fecha_reporte', 'visible', 'verificado'
    ]
    list_filter = [
        'tipo_reporte', 'estado', 'tamano', 'visible', 
        'verificado', 'fecha_reporte', 'raza__tamano_promedio'
    ]
    search_fields = [
        'nombre_perro', 'color', 'zona', 'direccion', 
        'usuario__username', 'usuario__email'
    ]
    readonly_fields = ['fecha_reporte', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'usuario', 'tipo_reporte', 'estado', 'nombre_perro', 
                'raza', 'color', 'tamano'
            )
        }),
        ('Descripción', {
            'fields': ('descripcion', 'caracteristicas_distintivas')
        }),
        ('Ubicación', {
            'fields': (('latitud', 'longitud'), 'direccion', 'zona')
        }),
        ('Fechas', {
            'fields': (
                'fecha_incidente', 'fecha_reporte', 
                'fecha_actualizacion', 'fecha_cierre'
            )
        }),
        ('Contacto', {
            'fields': ('telefono_contacto', 'email_contacto')
        }),
        ('Estado', {
            'fields': ('visible', 'verificado')
        }),
    )
    
    inlines = [FotoReporteInline, ComentarioInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'raza')

@admin.register(FotoReporte)
class FotoReporteAdmin(admin.ModelAdmin):
    list_display = ['reporte', 'descripcion', 'es_principal', 'orden', 'fecha_subida']
    list_filter = ['es_principal', 'fecha_subida']
    search_fields = ['reporte__nombre_perro', 'descripcion']
    readonly_fields = ['fecha_subida']
    
    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" height="100" />', obj.imagen.url)
        return "Sin imagen"
    imagen_thumbnail.short_description = "Vista previa"

@admin.register(Avistamiento)
class AvistamientoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'fecha_avistamiento', 
        'confianza', 'verificado', 'fecha_reporte_avistamiento'
    ]
    
    list_filter = ['confianza', 'verificado', 'fecha_avistamiento']
    
    search_fields = [
        'usuario__username',
        'descripcion', 'direccion'
    ]
    
    readonly_fields = ['fecha_reporte_avistamiento']
    
    fieldsets = (
        ('Información del Avistamiento', {
            'fields': ('usuario', 'fecha_avistamiento', 'confianza')
        }),
        ('Ubicación', {
            'fields': (('latitud', 'longitud'), 'direccion')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'verificado')
        }),
        ('Fechas', {
            'fields': ('fecha_reporte_avistamiento',)
        }),
    )

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['reporte', 'usuario', 'tipo', 'fecha_comentario']
    list_filter = ['tipo', 'fecha_comentario']
    search_fields = [
        'reporte__nombre_perro', 'usuario__username', 'contenido'
    ]
    readonly_fields = ['fecha_comentario']
    
    fieldsets = (
        ('Información del Comentario', {
            'fields': ('reporte', 'usuario', 'tipo')
        }),
        ('Contenido', {
            'fields': ('contenido',)
        }),
        ('Ubicación (Opcional)', {
            'fields': (('latitud', 'longitud'),),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_comentario',)
        }),
    )
