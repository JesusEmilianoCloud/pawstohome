from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class ConfiguracionUsuario(models.Model):
    """
    Modelo de Configuración de Usuario basado en el ER de PawsToHome
    Representa la entidad CONFIGURACION_USUARIO del diagrama
    Relación 1:1 con Usuario
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='configuracion',
        verbose_name="Usuario"
    )
    
    # Configuraciones de notificaciones
    notificaciones_email = models.BooleanField(
        default=True,
        verbose_name="Notificaciones por Email"
    )
    
    notificaciones_push = models.BooleanField(
        default=True,
        verbose_name="Notificaciones Push"
    )
    
    # Radio de notificaciones en kilómetros
    radio_notificaciones = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(50.0)],
        verbose_name="Radio de Notificaciones (km)",
        help_text="Radio en kilómetros para recibir notificaciones de reportes cercanos"
    )
    
    # Ubicación preferida del usuario (coordenadas separadas)
    latitud_preferida = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name="Latitud Preferida",
        help_text="Latitud de la ubicación base para notificaciones (-90 a 90)"
    )
    
    longitud_preferida = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name="Longitud Preferida", 
        help_text="Longitud de la ubicación base para notificaciones (-180 a 180)"
    )
    
    # Tipos de reportes a notificar
    notificar_perdidos = models.BooleanField(
        default=True,
        verbose_name="Notificar Mascotas Perdidas"
    )
    
    notificar_encontrados = models.BooleanField(
        default=True,
        verbose_name="Notificar Mascotas Encontradas"
    )
    
    class Meta:
        verbose_name = "Configuración de Usuario"
        verbose_name_plural = "Configuraciones de Usuario"
        db_table = "configuracion_usuario"
    
    def __str__(self):
        return f"Configuración de {self.usuario.username}"
    
    def tiene_ubicacion_preferida(self):
        """Verifica si el usuario tiene ubicación preferida configurada"""
        return self.latitud_preferida is not None and self.longitud_preferida is not None
    
    def set_ubicacion_preferida(self, latitud, longitud):
        """Establece la ubicación preferida del usuario"""
        if latitud is not None and longitud is not None:
            # Validar rangos
            if -90 <= latitud <= 90 and -180 <= longitud <= 180:
                self.latitud_preferida = latitud
                self.longitud_preferida = longitud
            else:
                raise ValueError("Coordenadas fuera de rango válido")
        else:
            self.latitud_preferida = None
            self.longitud_preferida = None
