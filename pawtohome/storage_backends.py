"""
Configuración de almacenamiento para Cloudflare R2
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
    custom_domain = settings.CLOUDFLARE_R2_CUSTOM_DOMAIN
    
    # Configuraciones de seguridad y acceso
    file_overwrite = False
    default_acl = None  # R2 no usa ACLs tradicionales
    
    # URLs públicas
    querystring_auth = False  # Para URLs públicas sin autenticación
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el endpoint personalizado
        self.endpoint_url = self.endpoint_url
        
        # Usar dominio personalizado si está configurado
        if hasattr(settings, 'CLOUDFLARE_R2_CUSTOM_DOMAIN') and settings.CLOUDFLARE_R2_CUSTOM_DOMAIN:
            self.custom_domain = settings.CLOUDFLARE_R2_CUSTOM_DOMAIN
    
    def url(self, name):
        """
        Generar URL pública para el archivo
        Usa el dominio personalizado si está configurado
        """
        if self.custom_domain:
            return f"https://{self.custom_domain}/{name}"
        else:
            # Usar la URL del endpoint de R2
            return f"{self.endpoint_url}/{self.bucket_name}/{name}"


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