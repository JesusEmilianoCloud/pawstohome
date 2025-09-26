from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import ConfiguracionUsuario

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_configuracion_usuario(sender, instance, created, **kwargs):
    """
    Signal para crear automáticamente la configuración de usuario
    cuando se crea un nuevo usuario
    """
    if created:
        ConfiguracionUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def guardar_configuracion_usuario(sender, instance, **kwargs):
    """
    Signal para asegurar que la configuración de usuario se guarde
    cuando se actualiza el usuario
    """
    if hasattr(instance, 'configuracion'):
        instance.configuracion.save()
    else:
        ConfiguracionUsuario.objects.create(usuario=instance)