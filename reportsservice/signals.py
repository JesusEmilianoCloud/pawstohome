from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import math
from .models import Reporte, Avistamiento, Comentario, FotoReporte
from Homeinfo.models import Notificacion
from ProfileService.models import ConfiguracionUsuario

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos usando la fórmula de Haversine
    Retorna la distancia en kilómetros
    """
    # Radio de la Tierra en kilómetros
    R = 6371.0
    
    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

@receiver(post_save, sender=Reporte)
def crear_notificaciones_nuevo_reporte(sender, instance, created, **kwargs):
    """
    Signal para crear notificaciones cuando se crea un nuevo reporte
    """
    if created:
        # Obtener usuarios con ubicación preferida configurada
        configuraciones = ConfiguracionUsuario.objects.filter(
            latitud_preferida__isnull=False,
            longitud_preferida__isnull=False
        ).exclude(usuario=instance.usuario)
        
        for config in configuraciones:
            # Calcular distancia usando Haversine
            distancia_km = calcular_distancia_haversine(
                config.latitud_preferida, 
                config.longitud_preferida,
                instance.latitud,
                instance.longitud
            )
            
            # Verificar si está en el radio y si quiere este tipo de notificación
            tipo_notificar = (
                (instance.tipo_reporte == 'perdido' and config.notificar_perdidos) or
                (instance.tipo_reporte == 'encontrado' and config.notificar_encontrados)
            )
            
            if distancia_km <= config.radio_notificaciones and tipo_notificar:
                Notificacion.objects.create(
                    usuario=config.usuario,
                    reporte=instance,
                    tipo='nuevo_reporte',
                    titulo=f"Nuevo reporte: {instance.get_tipo_reporte_display()}",
                    mensaje=f"Se ha reportado un perro {instance.tipo_reporte}: {instance.nombre_perro} en {instance.zona}",
                    url=f"/reportes/{instance.id}/"
                )

@receiver(post_save, sender=Avistamiento)
def crear_notificacion_avistamiento(sender, instance, created, **kwargs):
    """
    Signal para notificar al dueño del reporte cuando hay un nuevo avistamiento
    """
    if created:
        Notificacion.objects.create(
            usuario=instance.reporte.usuario,
            reporte=instance.reporte,
            tipo='avistamiento',
            titulo="Nuevo avistamiento reportado",
            mensaje=f"Alguien ha reportado un avistamiento de {instance.reporte.nombre_perro}",
            url=f"/reportes/{instance.reporte.id}/"
        )

@receiver(post_save, sender=Comentario)
def crear_notificacion_comentario(sender, instance, created, **kwargs):
    """
    Signal para notificar al dueño del reporte cuando hay un nuevo comentario
    """
    if created and instance.usuario != instance.reporte.usuario:
        Notificacion.objects.create(
            usuario=instance.reporte.usuario,
            reporte=instance.reporte,
            tipo='comentario',
            titulo="Nuevo comentario en tu reporte",
            mensaje=f"{instance.usuario.get_full_name() or instance.usuario.username} ha comentado en el reporte de {instance.reporte.nombre_perro}",
            url=f"/reportes/{instance.reporte.id}/"
        )

@receiver(pre_save, sender=Reporte)
def notificar_cambio_estado(sender, instance, **kwargs):
    """
    Signal para notificar cambios de estado en reportes
    """
    if instance.pk:  # Solo para actualizaciones, no creaciones
        try:
            reporte_anterior = Reporte.objects.get(pk=instance.pk)
            if reporte_anterior.estado != instance.estado:
                # El estado cambió, crear notificación
                Notificacion.objects.create(
                    usuario=instance.usuario,
                    reporte=instance,
                    tipo='estado_cambiado',
                    titulo=f"Estado del reporte actualizado",
                    mensaje=f"El estado de tu reporte de {instance.nombre_perro} ha cambiado a: {instance.get_estado_display()}",
                    url=f"/reportes/{instance.id}/"
                )
        except Reporte.DoesNotExist:
            pass

@receiver(post_save, sender=FotoReporte)
def validar_foto_principal(sender, instance, created, **kwargs):
    """
    Signal para asegurar que cada reporte tenga al menos una foto principal
    """
    if created:
        # Si es el primer foto del reporte, marcarla como principal
        if not FotoReporte.objects.filter(reporte=instance.reporte, es_principal=True).exists():
            instance.es_principal = True
            instance.save(update_fields=['es_principal'])