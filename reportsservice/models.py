import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os

class Raza(models.Model):
    """
    Modelo de Raza basado en el ER de PawsToHome
    Representa la entidad RAZA del diagrama
    """
    
    TAMANO_CHOICES = [
        ('pequeño', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
        ('gigante', 'Gigante'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Raza"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    tamano_promedio = models.CharField(
        max_length=10,
        choices=TAMANO_CHOICES,
        verbose_name="Tamaño Promedio"
    )
    
    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        db_table = "raza"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Reporte(models.Model):
    """
    Modelo de Reporte basado en el ER de PawsToHome
    Representa la entidad REPORTE del diagrama
    """
    
    TIPO_REPORTE_CHOICES = [
        ('perdido', 'Perdido'),
        ('encontrado', 'Encontrado'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('cerrado', 'Cerrado'),
        ('en_proceso', 'En Proceso'),
    ]
    
    TAMANO_CHOICES = [
        ('pequeño', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
        ('gigante', 'Gigante'),
    ]
    
    # Primary Key UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID Reporte"
    )
    
    # Foreign Keys
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes',
        verbose_name="Usuario"
    )
    
    raza = models.ForeignKey(
        Raza,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes',
        verbose_name="Raza"
    )
    
    # Campos principales
    tipo_reporte = models.CharField(
        max_length=12,
        choices=TIPO_REPORTE_CHOICES,
        verbose_name="Tipo de Reporte"
    )
    
    estado = models.CharField(
        max_length=12,
        choices=ESTADO_CHOICES,
        default='activo',
        verbose_name="Estado"
    )
    
    nombre_perro = models.CharField(
        max_length=100,
        verbose_name="Nombre del Perro"
    )
    
    color = models.CharField(
        max_length=100,
        verbose_name="Color"
    )
    
    tamano = models.CharField(
        max_length=10,
        choices=TAMANO_CHOICES,
        verbose_name="Tamaño"
    )
    
    descripcion = models.TextField(
        verbose_name="Descripción"
    )
    
    caracteristicas_distintivas = models.TextField(
        blank=True,
        verbose_name="Características Distintivas"
    )
    
    # Ubicación (coordenadas separadas)
    latitud = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name="Latitud",
        help_text="Latitud del reporte (-90 a 90)"
    )
    
    longitud = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name="Longitud", 
        help_text="Longitud del reporte (-180 a 180)"
    )
    
    direccion = models.CharField(
        max_length=300,
        verbose_name="Dirección"
    )
    
    zona = models.CharField(
        max_length=100,
        verbose_name="Zona/Colonia"
    )
    
    # Fechas
    fecha_reporte = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha del Reporte"
    )
    
    fecha_incidente = models.DateTimeField(
        verbose_name="Fecha del Incidente"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Cierre"
    )
    
    # Contacto
    telefono_contacto = models.CharField(
        max_length=15,
        verbose_name="Teléfono de Contacto"
    )
    
    email_contacto = models.EmailField(
        verbose_name="Email de Contacto"
    )
    
    # Flags
    visible = models.BooleanField(
        default=True,
        verbose_name="Visible"
    )
    
    verificado = models.BooleanField(
        default=False,
        verbose_name="Verificado"
    )
    
    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        db_table = "reporte"
        ordering = ['-fecha_reporte']
        indexes = [
            models.Index(fields=['tipo_reporte', 'estado']),
            models.Index(fields=['fecha_reporte']),
            models.Index(fields=['latitud', 'longitud']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_reporte_display()}: {self.nombre_perro} - {self.zona}"
    
    def set_ubicacion(self, latitud, longitud):
        """Setter para establecer la ubicación con latitud y longitud"""
        if -90 <= latitud <= 90 and -180 <= longitud <= 180:
            self.latitud = latitud
            self.longitud = longitud
        else:
            raise ValueError("Coordenadas fuera de rango válido")
    
    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # La fecha del incidente no puede ser posterior a la fecha del reporte
        if self.fecha_incidente and self.fecha_reporte and self.fecha_incidente > self.fecha_reporte:
            raise ValidationError('La fecha del incidente no puede ser posterior a la fecha del reporte.')

def reporte_foto_path(instance, filename):
    """Función para generar el path de las fotos de reportes"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"reportes/{instance.reporte.id}/fotos/{filename}"

class FotoReporte(models.Model):
    """
    Modelo de Foto de Reporte basado en el ER de PawsToHome
    Representa la entidad FOTO_REPORTE del diagrama
    """
    
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='fotos',
        verbose_name="Reporte"
    )
    
    imagen = models.ImageField(
        upload_to=reporte_foto_path,
        verbose_name="Imagen"
    )
    
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción"
    )
    
    es_principal = models.BooleanField(
        default=False,
        verbose_name="Foto Principal"
    )
    
    fecha_subida = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Subida"
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden"
    )
    
    class Meta:
        verbose_name = "Foto de Reporte"
        verbose_name_plural = "Fotos de Reportes"
        db_table = "foto_reporte"
        ordering = ['orden', 'fecha_subida']
        unique_together = [['reporte', 'es_principal']]  # Solo una foto principal por reporte
    
    def __str__(self):
        return f"Foto de {self.reporte.nombre_perro} ({self.reporte.id})"
    
    def save(self, *args, **kwargs):
        # Si esta foto se marca como principal, desmarcar las demás del mismo reporte
        if self.es_principal:
            FotoReporte.objects.filter(
                reporte=self.reporte,
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        
        super().save(*args, **kwargs)
        
        # Optimizar imagen después de guardar
        if self.imagen:
            self.optimizar_imagen()
    
    def optimizar_imagen(self):
        """Optimiza el tamaño de la imagen para web"""
        try:
            with Image.open(self.imagen.path) as img:
                # Redimensionar si es muy grande
                if img.width > 800 or img.height > 600:
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    img.save(self.imagen.path, optimize=True, quality=85)
        except Exception as e:
            pass  # Si hay error, no optimizar

class Avistamiento(models.Model):
    """
    Modelo de Avistamiento basado en el ER de PawsToHome
    Representa la entidad AVISTAMIENTO del diagrama
    """
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avistamientos',
        verbose_name="Usuario que reporta"
    )
    
    # Ubicación del avistamiento (coordenadas separadas)
    latitud = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name="Latitud del Avistamiento",
        help_text="Latitud del avistamiento (-90 a 90)"
    )
    
    longitud = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name="Longitud del Avistamiento",
        help_text="Longitud del avistamiento (-180 a 180)"
    )
    
    direccion = models.CharField(
        max_length=300,
        verbose_name="Dirección"
    )
    
    fecha_avistamiento = models.DateTimeField(
        verbose_name="Fecha del Avistamiento"
    )
    
    descripcion = models.TextField(
        verbose_name="Descripción del Avistamiento"
    )
    
    confianza = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Nivel de Confianza (1-10)"
    )
    
    fecha_reporte_avistamiento = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha del Reporte de Avistamiento"
    )
    
    verificado = models.BooleanField(
        default=False,
        verbose_name="Verificado"
    )
    
    class Meta:
        verbose_name = "Avistamiento"
        verbose_name_plural = "Avistamientos"
        db_table = "avistamiento"
        ordering = ['-fecha_avistamiento']
        indexes = [
            models.Index(fields=['fecha_avistamiento']),
            models.Index(fields=['latitud', 'longitud']),
        ]
    
    def __str__(self):
        return f"Avistamiento - {self.fecha_avistamiento}"
    
    def set_ubicacion(self, latitud, longitud):
        """Setter para establecer la ubicación del avistamiento"""
        if -90 <= latitud <= 90 and -180 <= longitud <= 180:
            self.latitud = latitud
            self.longitud = longitud
        else:
            raise ValueError("Coordenadas fuera de rango válido")
    
    def clean(self):
        """Validaciones personalizadas"""
        # Aquí se pueden agregar validaciones específicas del avistamiento
        pass

class Comentario(models.Model):
    """
    Modelo de Comentario basado en el ER de PawsToHome
    Representa la entidad COMENTARIO del diagrama
    """
    
    TIPO_COMENTARIO_CHOICES = [
        ('avistamiento', 'Avistamiento'),
        ('informacion', 'Información'),
        ('actualizacion', 'Actualización'),
        ('pregunta', 'Pregunta'),
        ('otro', 'Otro'),
    ]
    
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name="Reporte"
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name="Usuario"
    )
    
    tipo = models.CharField(
        max_length=15,
        choices=TIPO_COMENTARIO_CHOICES,
        default='otro',
        verbose_name="Tipo de Comentario"
    )
    
    contenido = models.TextField(
        verbose_name="Contenido"
    )
    
    fecha_comentario = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha del Comentario"
    )
    
    # Ubicación opcional (para avistamientos informales)
    latitud = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name="Latitud (Opcional)",
        help_text="Latitud del comentario (-90 a 90)"
    )
    
    longitud = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name="Longitud (Opcional)",
        help_text="Longitud del comentario (-180 a 180)"
    )
    
    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        db_table = "comentario"
        ordering = ['fecha_comentario']
        indexes = [
            models.Index(fields=['fecha_comentario']),
        ]
    
    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.reporte.nombre_perro}"
    
    def tiene_ubicacion(self):
        """Verifica si el comentario tiene ubicación"""
        return self.latitud is not None and self.longitud is not None
    
    def set_ubicacion(self, latitud, longitud):
        """Setter para establecer la ubicación del comentario"""
        if latitud is not None and longitud is not None:
            if -90 <= latitud <= 90 and -180 <= longitud <= 180:
                self.latitud = latitud
                self.longitud = longitud
            else:
                raise ValueError("Coordenadas fuera de rango válido")
        else:
            self.latitud = None
            self.longitud = None
