"""
Configuración de almacenamiento para Cloudflare R2
Archivo: pawtohome/storage_backends.py
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class CloudflareR2Storage(S3Boto3Storage):
    """
    Configuración personalizada para Cloudflare R2
    Compatible con la API de S3 que usa R2
    """
    bucket_name = settings.CLOUDFLARE_R2_BUCKET_NAME
    region_name = 'auto'  # Cloudflare R2 usa 'auto' como región
    endpoint_url = settings.CLOUDFLARE_R2_ENDPOINT_URL
    access_key = settings.CLOUDFLARE_R2_ACCESS_KEY_ID
    secret_key = settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY
    
    # Configuraciones de seguridad y acceso
    file_overwrite = False
    default_acl = None  # R2 no usa ACLs tradicionales
    
    # URLs públicas
    querystring_auth = False  # Para URLs públicas sin autenticación
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Usar dominio personalizado si está configurado
        if hasattr(settings, 'CLOUDFLARE_R2_CUSTOM_DOMAIN') and settings.CLOUDFLARE_R2_CUSTOM_DOMAIN:
            self.custom_domain = settings.CLOUDFLARE_R2_CUSTOM_DOMAIN
    
    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        Generar URL pública para el archivo
        Usa el dominio personalizado si está configurado
        """
        # Limpiar el nombre (remover 'media/' si ya está en location)
        if name.startswith('media/'):
            name = name[6:]  # Remover 'media/' del inicio
        
        # Si hay dominio personalizado, usarlo
        if hasattr(self, 'custom_domain') and self.custom_domain:
            # Construir URL completa
            url = f"https://{self.custom_domain}/media/{name}"
            return url
        else:
            # Usar la URL del endpoint de R2
            # El método padre maneja esto correctamente
            return super().url(name, parameters, expire, http_method)


class CloudflareR2MediaStorage(CloudflareR2Storage):
    """
    Almacenamiento específico para archivos media (uploads de usuarios)
    """
    location = 'media'
    
    
class CloudflareR2StaticStorage(CloudflareR2Storage):
    """
    Almacenamiento específico para archivos estáticos
    """
    location = 'static'
    default_acl = 'public-read'  # Los archivos estáticos deben ser públicos