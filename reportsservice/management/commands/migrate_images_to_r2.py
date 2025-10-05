"""
Comando de Django para migrar imágenes de reportes existentes a Cloudflare R2
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from reportsservice.models import FotoReporte
from reportsservice.utils import CloudflareR2ImageUploader
import os


class Command(BaseCommand):
    help = 'Migra todas las imágenes de reportes existentes a Cloudflare R2'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué archivos se subirían sin subirlos realmente'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limitar el número de imágenes a procesar (para pruebas)'
        )
        parser.add_argument(
            '--reporte-id',
            type=str,
            help='Migrar solo las imágenes de un reporte específico (UUID)'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        limit = options.get('limit')
        reporte_id = options.get('reporte_id')
        
        if not CloudflareR2ImageUploader.is_r2_enabled():
            self.stdout.write(
                self.style.WARNING('Cloudflare R2 no está habilitado. Configura USE_CLOUDFLARE_R2=true en tu .env')
            )
            return

        # Filtrar las fotos según los parámetros
        queryset = FotoReporte.objects.all()
        
        if reporte_id:
            queryset = queryset.filter(reporte__id=reporte_id)
            self.stdout.write(f"🎯 Procesando solo el reporte: {reporte_id}")
        
        if limit:
            queryset = queryset[:limit]
            self.stdout.write(f"📊 Limitando a {limit} imágenes")
        
        total_fotos = queryset.count()
        self.stdout.write(f"📸 Total de fotos a procesar: {total_fotos}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🏃‍♂️ MODO DRY-RUN - No se subirá nada realmente"))
        
        exitosas = 0
        errores = 0
        
        for i, foto in enumerate(queryset, 1):
            try:
                self.stdout.write(f"[{i}/{total_fotos}] Procesando foto ID: {foto.id}")
                self.stdout.write(f"   📁 Archivo: {foto.imagen.name}")
                self.stdout.write(f"   📋 Reporte: {foto.reporte.nombre_perro} ({foto.reporte.id})")
                
                if dry_run:
                    # Verificar si el archivo existe usando el mismo método que la migración real
                    try:
                        if foto.imagen:
                            # Intentar acceder al archivo usando el storage
                            storage_actual = foto.imagen.storage
                            if storage_actual.exists(foto.imagen.name):
                                self.stdout.write(f"   ✅ Archivo encontrado en storage: {foto.imagen.name}")
                            else:
                                # Intentar con ruta local si el storage no lo encuentra
                                if hasattr(foto.imagen, 'path') and os.path.exists(foto.imagen.path):
                                    self.stdout.write(f"   ✅ Archivo local encontrado: {foto.imagen.path}")
                                else:
                                    self.stdout.write(f"   ❌ Archivo no encontrado")
                                    errores += 1
                                    continue
                        else:
                            self.stdout.write(f"   ❌ No hay imagen asociada")
                            errores += 1
                            continue
                    except Exception as e:
                        self.stdout.write(f"   ❌ Error verificando archivo: {str(e)}")
                        errores += 1
                        continue
                else:
                    # Intentar subir realmente
                    success, message = CloudflareR2ImageUploader.upload_foto_reporte(foto)
                    if success:
                        self.stdout.write(self.style.SUCCESS(f"   ✅ Subida exitosa: {message}"))
                        exitosas += 1
                    else:
                        self.stdout.write(self.style.ERROR(f"   ❌ Error en la subida: {message}"))
                        errores += 1
                
                if not dry_run:
                    exitosas += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Error procesando foto {foto.id}: {str(e)}"))
                errores += 1
                continue
        
        # Mostrar resumen
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 RESUMEN DE LA MIGRACIÓN")
        self.stdout.write("="*50)
        
        if dry_run:
            self.stdout.write(f"🔍 Fotos verificadas: {total_fotos - errores}")
            self.stdout.write(f"❌ Archivos no encontrados: {errores}")
        else:
            self.stdout.write(f"✅ Subidas exitosas: {exitosas}")
            self.stdout.write(f"❌ Errores: {errores}")
            self.stdout.write(f"📈 Tasa de éxito: {(exitosas/total_fotos)*100:.1f}%" if total_fotos > 0 else "N/A")
        
        if not dry_run and exitosas > 0:
            self.stdout.write(self.style.SUCCESS(f"\n🎉 Migración completada! {exitosas} imágenes subidas a Cloudflare R2"))
        elif dry_run:
            self.stdout.write(f"\nℹ️ Para ejecutar la migración real, ejecuta el comando sin --dry-run")