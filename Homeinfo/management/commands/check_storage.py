"""
Comando de Django para verificar la configuración de storage
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.staticfiles.storage import staticfiles_storage


class Command(BaseCommand):
    help = 'Verifica la configuración actual de almacenamiento'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Verificando configuración de almacenamiento...\n")
        
        # Verificar storage de media (default)
        self.stdout.write("📁 MEDIA FILES (default storage):")
        self.stdout.write(f"   Backend: {default_storage.__class__.__module__}.{default_storage.__class__.__name__}")
        
        if hasattr(default_storage, 'bucket_name'):
            self.stdout.write(f"   Bucket: {getattr(default_storage, 'bucket_name', 'N/A')}")
        
        self.stdout.write(f"   URL base: {settings.MEDIA_URL}")
        
        # Verificar storage de static
        self.stdout.write("\n🎨 STATIC FILES:")
        self.stdout.write(f"   Backend: {staticfiles_storage.__class__.__module__}.{staticfiles_storage.__class__.__name__}")
        self.stdout.write(f"   URL base: {settings.STATIC_URL}")
        
        # Verificar configuración de R2
        self.stdout.write(f"\n⚙️ CONFIGURACIÓN:")
        use_r2 = getattr(settings, 'USE_CLOUDFLARE_R2', False)
        self.stdout.write(f"   USE_CLOUDFLARE_R2: {use_r2}")
        
        if use_r2:
            bucket = getattr(settings, 'CLOUDFLARE_R2_BUCKET_NAME', 'No configurado')
            endpoint = getattr(settings, 'CLOUDFLARE_R2_ENDPOINT_URL', 'No configurado')
            custom_domain = getattr(settings, 'CLOUDFLARE_R2_CUSTOM_DOMAIN', 'No configurado')
            
            self.stdout.write(f"   Bucket: {bucket}")
            self.stdout.write(f"   Endpoint: {endpoint}")
            self.stdout.write(f"   Dominio personalizado: {custom_domain}")
        
        # Test básico de escritura (solo simulación)
        self.stdout.write(f"\n📝 RESUMEN:")
        if use_r2:
            self.stdout.write("   ✅ Archivos MEDIA → Cloudflare R2")
            self.stdout.write("   📁 Archivos STATIC → Local")
        else:
            self.stdout.write("   📁 Archivos MEDIA → Local")
            self.stdout.write("   📁 Archivos STATIC → Local")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Verificación completada!"))