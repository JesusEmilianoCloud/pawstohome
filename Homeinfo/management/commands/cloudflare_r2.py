"""
Comando de Django para gestionar archivos en Cloudflare R2
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os


class Command(BaseCommand):
    help = 'Gestiona archivos en Cloudflare R2: verifica conexión, lista archivos, etc.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['test', 'list', 'upload-test', 'sync-media'],
            default='test',
            help='Acción a realizar: test (probar conexión), list (listar archivos), upload-test (subir archivo de prueba), sync-media (sincronizar media)'
        )
        parser.add_argument(
            '--file-path',
            type=str,
            help='Ruta del archivo para subir (solo para upload-test)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if not getattr(settings, 'USE_CLOUDFLARE_R2', False):
            self.stdout.write(
                self.style.WARNING('Cloudflare R2 no está habilitado. Configura USE_CLOUDFLARE_R2=true en tu .env')
            )
            return

        self.stdout.write(f"🚀 Ejecutando acción: {action}")
        
        if action == 'test':
            self.test_connection()
        elif action == 'list':
            self.list_files()
        elif action == 'upload-test':
            self.upload_test_file(options.get('file_path'))
        elif action == 'sync-media':
            self.sync_media_files()

    def test_connection(self):
        """Probar la conexión a Cloudflare R2"""
        try:
            # Intentar listar archivos (esto prueba la conexión)
            storage = default_storage
            self.stdout.write("🔍 Probando conexión a Cloudflare R2...")
            
            # Intentar crear un archivo de prueba pequeño
            test_content = "Test file for Cloudflare R2 connection"
            test_file_name = "test/connection_test.txt"
            
            # Crear un ContentFile para Django
            test_file = ContentFile(test_content.encode())
            
            # Guardar archivo de prueba
            storage.save(test_file_name, test_file)
            self.stdout.write(self.style.SUCCESS("✅ Archivo de prueba creado exitosamente"))
            
            # Verificar que el archivo existe
            if storage.exists(test_file_name):
                self.stdout.write(self.style.SUCCESS("✅ Archivo de prueba verificado"))
                
                # Obtener URL del archivo
                url = storage.url(test_file_name)
                self.stdout.write(f"🔗 URL del archivo: {url}")
                
                # Eliminar archivo de prueba
                storage.delete(test_file_name)
                self.stdout.write(self.style.SUCCESS("🗑️ Archivo de prueba eliminado"))
                
            self.stdout.write(self.style.SUCCESS("🎉 Conexión a Cloudflare R2 exitosa!"))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error conectando a Cloudflare R2: {str(e)}")
            )

    def list_files(self):
        """Listar archivos en el bucket"""
        try:
            storage = default_storage
            self.stdout.write("📁 Listando archivos en Cloudflare R2...")
            
            # Esto puede no estar disponible en todos los backends
            if hasattr(storage, 'listdir'):
                directories, files = storage.listdir('')
                self.stdout.write(f"📂 Directorios: {directories}")
                self.stdout.write(f"📄 Archivos: {files}")
            else:
                self.stdout.write("ℹ️ La función de listado no está disponible para este storage")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error listando archivos: {str(e)}")
            )

    def upload_test_file(self, file_path):
        """Subir un archivo de prueba"""
        if not file_path:
            self.stdout.write(
                self.style.ERROR("❌ Debes proporcionar --file-path para subir un archivo")
            )
            return
            
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f"❌ El archivo {file_path} no existe")
            )
            return
            
        try:
            storage = default_storage
            
            # Leer el archivo local
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Crear un objeto ContentFile para Django
            django_file = ContentFile(file_content)
            
            # Generar nombre para el archivo en R2
            file_name = f"test/uploaded_{os.path.basename(file_path)}"
            
            # Subir el archivo
            self.stdout.write(f"⬆️ Subiendo {file_path} como {file_name}...")
            saved_name = storage.save(file_name, django_file)
            
            # Obtener URL
            url = storage.url(saved_name)
            
            self.stdout.write(self.style.SUCCESS(f"✅ Archivo subido exitosamente!"))
            self.stdout.write(f"📁 Nombre en R2: {saved_name}")
            self.stdout.write(f"🔗 URL: {url}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error subiendo archivo: {str(e)}")
            )

    def sync_media_files(self):
        """Sincronizar archivos media locales con R2"""
        self.stdout.write("🔄 Funcionalidad de sincronización pendiente de implementar...")
        self.stdout.write("💡 Para migrar archivos existentes, considera usar herramientas como rclone o aws-cli")