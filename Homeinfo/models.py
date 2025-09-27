from django.db import models
from django.conf import settings
from django.utils import timezone

class Notificacion(models.Model):
    """
    Modelo de Notificación basado en el ER de PawsToHome
    Representa la entidad NOTIFICACION del diagrama
    """
    
    TIPO_NOTIFICACION_CHOICES = [
        ('nuevo_reporte', 'Nuevo Reporte'),
        ('avistamiento', 'Nuevo Avistamiento'),
        ('comentario', 'Nuevo Comentario'),
        ('estado_cambiado', 'Estado Cambiado'),
        ('sistema', 'Notificación del Sistema'),
        ('recordatorio', 'Recordatorio'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name="Usuario"
    )
    
    # Relación opcional con reporte (puede ser notificación del sistema)
    reporte = models.ForeignKey(
        'reportsservice.Reporte',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name="Reporte Relacionado"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_NOTIFICACION_CHOICES,
        verbose_name="Tipo de Notificación"
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    
    mensaje = models.TextField(
        verbose_name="Mensaje"
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Creación"
    )
    
    leida = models.BooleanField(
        default=False,
        verbose_name="Leída"
    )
    
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Lectura"
    )
    
    url = models.URLField(
        blank=True,
        verbose_name="URL de Referencia"
    )
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        db_table = "notificacion"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.titulo}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])
