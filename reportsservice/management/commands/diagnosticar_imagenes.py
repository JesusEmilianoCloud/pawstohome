"""
Comando de Django para diagnosticar el estado de las imágenes de reportes
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from reportsservice.models import FotoReporte
from reportsservice.utils import CloudflareR2ImageUploader
import os


class Command(BaseCommand):
    help = 'Diagnostica el estado de las imágenes de reportes y su configuración de storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--foto-id',
            type=int,
            help='Diagnosticar una foto específica por su ID'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada'
        )

    def handle(self, *args, **options):
        foto_id = options.get('foto_id')
        verbose = options.get('verbose', False)
        
        self.stdout.write("🔍 DIAGNÓSTICO DE IMÁGENES DE REPORTES")
        self.stdout.write("="*50)
        
        # Mostrar configuración actual
        self.mostrar_configuracion()
        
        if foto_id:
            self.diagnosticar_foto_especifica(foto_id, verbose)
        else:
            self.diagnosticar_todas_las_fotos(verbose)

    def mostrar_configuracion(self):
        """Mostrar la configuración actual de storage"""
        self.stdout.write("\n📋 CONFIGURACIÓN ACTUAL:")
        self.stdout.write("-" * 30)
        
        # Storage por defecto
        storage_backend = settings.DEFAULT_FILE_STORAGE
        self.stdout.write(f"🗄️ DEFAULT_FILE_STORAGE: {storage_backend}")
        
        # Cloudflare R2
        r2_enabled = CloudflareR2ImageUploader.is_r2_enabled()
        self.stdout.write(f"☁️ Cloudflare R2 Habilitado: {r2_enabled}")
        
        if r2_enabled:
            self.stdout.write(f"📦 Bucket: {getattr(settings, 'CLOUDFLARE_R2_BUCKET_NAME', 'No configurado')}")
            self.stdout.write(f"🌐 Endpoint: {getattr(settings, 'CLOUDFLARE_R2_ENDPOINT_URL', 'No configurado')}")
        
        # Media settings
        self.stdout.write(f"📁 MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'No configurado')}")
        self.stdout.write(f"🔗 MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'No configurado')}")

    def diagnosticar_foto_especifica(self, foto_id, verbose):
        """Diagnosticar una foto específica"""
        self.stdout.write(f"\n🎯 DIAGNÓSTICO DE FOTO ID: {foto_id}")
        self.stdout.write("-" * 30)
        
        try:
            foto = FotoReporte.objects.get(id=foto_id)
            self.diagnosticar_foto(foto, verbose)
        except FotoReporte.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ No se encontró la foto con ID: {foto_id}"))

    def diagnosticar_todas_las_fotos(self, verbose):
        """Diagnosticar todas las fotos"""
        fotos = FotoReporte.objects.all()
        total = fotos.count()
        
        self.stdout.write(f"\n📊 DIAGNÓSTICO GENERAL ({total} fotos):")
        self.stdout.write("-" * 30)
        
        stats = {
            'con_archivo': 0,
            'sin_archivo': 0,
            'path_absoluto': 0,
            'solo_storage': 0,
            'errores': 0
        }
        
        for i, foto in enumerate(fotos, 1):
            if verbose:
                self.stdout.write(f"\n[{i}/{total}] Foto ID: {foto.id}")
            
            resultado = self.diagnosticar_foto(foto, verbose)
            stats[resultado] += 1
        
        # Mostrar estadísticas
        self.stdout.write(f"\n📈 ESTADÍSTICAS:")
        self.stdout.write(f"✅ Con archivo accesible: {stats['con_archivo']}")
        self.stdout.write(f"❌ Sin archivo: {stats['sin_archivo']}")
        self.stdout.write(f"📂 Solo path absoluto: {stats['path_absoluto']}")
        self.stdout.write(f"🗄️ Solo storage: {stats['solo_storage']}")
        self.stdout.write(f"💥 Errores: {stats['errores']}")

    def diagnosticar_foto(self, foto, verbose):
        """Diagnosticar una foto individual"""
        try:
            if not foto.imagen:
                if verbose:
                    self.stdout.write("   ❌ No tiene imagen asociada")
                return 'sin_archivo'
            
            if verbose:
                self.stdout.write(f"   📁 Nombre: {foto.imagen.name}")
                self.stdout.write(f"   🗄️ Storage: {type(foto.imagen.storage).__name__}")
            
            # Verificar acceso por storage
            storage_ok = False
            try:
                storage_actual = foto.imagen.storage
                existe_en_storage = storage_actual.exists(foto.imagen.name)
                if verbose:
                    self.stdout.write(f"   📦 Existe en storage: {existe_en_storage}")
                if existe_en_storage:
                    storage_ok = True
            except Exception as e:
                if verbose:
                    self.stdout.write(f"   ❌ Error accediendo por storage: {str(e)}")
            
            # Verificar acceso por path absoluto
            path_ok = False
            try:
                if hasattr(foto.imagen, 'path'):
                    path_absoluto = foto.imagen.path
                    existe_archivo = os.path.exists(path_absoluto)
                    if verbose:
                        self.stdout.write(f"   🔗 Path: {path_absoluto}")
                        self.stdout.write(f"   📂 Existe archivo: {existe_archivo}")
                    if existe_archivo:
                        path_ok = True
            except Exception as e:
                if verbose:
                    self.stdout.write(f"   ❌ Error accediendo por path: {str(e)}")
            
            # Determinar estado
            if storage_ok and path_ok:
                if verbose:
                    self.stdout.write("   ✅ Archivo accesible por ambos métodos")
                return 'con_archivo'
            elif storage_ok:
                if verbose:
                    self.stdout.write("   🟡 Solo accesible por storage")
                return 'solo_storage'
            elif path_ok:
                if verbose:
                    self.stdout.write("   🟡 Solo accesible por path absoluto")
                return 'path_absoluto'
            else:
                if verbose:
                    self.stdout.write("   ❌ Archivo no accesible")
                return 'sin_archivo'
            
        except Exception as e:
            if verbose:
                self.stdout.write(f"   💥 Error: {str(e)}")
            return 'errores'