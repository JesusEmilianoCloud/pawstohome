from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Modelo de Usuario extendido basado en el ER de PawsToHome
    Representa la entidad USUARIO del diagrama
    """
    
    # Simple validator for phone number
    phone_regex = RegexValidator(
        regex=r'^[0-9]{10}$',
        message="Ingrese un número telefónico válido de 10 dígitos"
    )

    # Campos adicionales según el ER
    phone_number = models.CharField(
        max_length=10,
        validators=[phone_regex],
        help_text="Formato: 6561234567 (10 dígitos)",
        verbose_name="Teléfono"
    )
    
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Registro"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Usuario Activo"
    )
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "usuario"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
