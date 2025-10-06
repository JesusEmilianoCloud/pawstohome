from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
import logging
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

# Configurar logger
logger = logging.getLogger(__name__)

def eliminar_imagen_perfil_de_cloudflare_r2(imagen_path):
    """
    Función para eliminar una imagen de perfil específica de Cloudflare R2
    """
    try:
        # Configurar cliente S3 para Cloudflare R2
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.CLOUDFLARE_R2_ENDPOINT_URL,
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name='auto'
        )
        
        # Limpiar el path de la imagen (remover 'media/' si está presente)
        if imagen_path.startswith('media/'):
            imagen_path = imagen_path[6:]
            
        # Agregar el prefijo media/ para R2
        r2_key = f"media/{imagen_path}"
        
        # Eliminar el archivo del bucket
        response = s3_client.delete_object(
            Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
            Key=r2_key
        )
        
        logger.info(f"Foto de perfil eliminada exitosamente de R2: {r2_key}")
        
    except ClientError as e:
        logger.error(f"Error al eliminar foto de perfil de R2: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al eliminar foto de perfil de R2: {str(e)}")

@receiver(pre_save, sender=ConfiguracionUsuario)
def eliminar_foto_perfil_anterior_r2(sender, instance, **kwargs):
    """
    Signal para eliminar la foto de perfil anterior de R2 cuando se actualiza
    """
    if instance.pk:  # Solo si es una actualización
        try:
            # Obtener la instancia actual de la base de datos
            configuracion_actual = ConfiguracionUsuario.objects.get(pk=instance.pk)
            
            # Si hay una foto anterior y se está cambiando
            if (configuracion_actual.foto_perfil and 
                configuracion_actual.foto_perfil != instance.foto_perfil and
                configuracion_actual.foto_perfil.name):
                
                # Eliminar la foto anterior de R2
                eliminar_imagen_perfil_de_cloudflare_r2(configuracion_actual.foto_perfil.name)
                
        except ConfiguracionUsuario.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error en signal pre_save para ConfiguracionUsuario {instance.pk}: {str(e)}")

@receiver(pre_delete, sender=ConfiguracionUsuario)
def eliminar_foto_perfil_al_borrar_configuracion(sender, instance, **kwargs):
    """
    Signal para eliminar la foto de perfil de R2 cuando se elimina la configuración
    """
    if instance.foto_perfil and instance.foto_perfil.name:
        eliminar_imagen_perfil_de_cloudflare_r2(instance.foto_perfil.name)

@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def limpiar_datos_usuario_completo(sender, instance, **kwargs):
    """
    Signal para eliminar todos los archivos de R2 cuando se elimina un usuario.
    Esto incluye foto de perfil y fotos de reportes.
    """
    from reportsservice.models import Reporte, FotoReporte
    
    try:
        # 1. Eliminar foto de perfil si existe
        if hasattr(instance, 'configuracion') and instance.configuracion.foto_perfil:
            eliminar_imagen_perfil_de_cloudflare_r2(instance.configuracion.foto_perfil.name)
            logger.info(f"Eliminada foto de perfil para usuario {instance.id}")
        
        # 2. Eliminar todas las fotos de reportes del usuario
        reportes_usuario = Reporte.objects.filter(usuario=instance)
        contador_fotos = 0
        
        for reporte in reportes_usuario:
            fotos_reporte = FotoReporte.objects.filter(reporte=reporte)
            for foto in fotos_reporte:
                if foto.imagen and foto.imagen.name:
                    # Reutilizar función de reportsservice para consistencia
                    from reportsservice.signals import eliminar_imagen_de_cloudflare_r2
                    eliminar_imagen_de_cloudflare_r2(foto.imagen.name)
                    contador_fotos += 1
        
        logger.warning(f"Usuario {instance.id} eliminado - Limpieza completa: "
                      f"foto perfil + {contador_fotos} fotos de reportes")
                      
    except Exception as e:
        logger.error(f"Error en limpieza completa para usuario {instance.id}: {str(e)}")