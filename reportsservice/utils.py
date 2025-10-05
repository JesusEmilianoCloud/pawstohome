"""
Utilidades para el manejo de imágenes en el servicio de reportes
"""
import os
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class CloudflareR2ImageUploader:
    """
    Clase para manejar la subida de imágenes a Cloudflare R2
    """
    
    @staticmethod
    def is_r2_enabled() -> bool:
        """Verificar si Cloudflare R2 está habilitado"""
        return getattr(settings, 'USE_CLOUDFLARE_R2', False)
    
    @staticmethod
    def upload_image(image_path: str, r2_path: str) -> Tuple[bool, Optional[str]]:
        """
        Subir una imagen a Cloudflare R2
        
        Args:
            image_path: Ruta local de la imagen
            r2_path: Ruta donde guardar en R2
            
        Returns:
            Tuple[bool, str]: (éxito, url_pública o mensaje_de_error)
        """
        try:
            if not CloudflareR2ImageUploader.is_r2_enabled():
                return False, "Cloudflare R2 no está habilitado"
            
            # Verificar que el archivo local existe
            if not os.path.exists(image_path):
                return False, f"Archivo local no encontrado: {image_path}"
            
            # Leer el contenido del archivo
            with open(image_path, 'rb') as f:
                contenido_archivo = f.read()
            
            # Crear ContentFile para Django storage
            django_file = ContentFile(contenido_archivo)
            
            # Subir el archivo a Cloudflare R2
            storage = default_storage
            
            # Verificar si el archivo ya existe
            if storage.exists(r2_path):
                logger.info(f"Archivo ya existe en R2: {r2_path}")
                url_publica = storage.url(r2_path)
                return True, url_publica
            
            archivo_guardado = storage.save(r2_path, django_file)
            
            # Obtener la URL pública
            url_publica = storage.url(archivo_guardado)
            
            logger.info(f"Imagen subida exitosamente a Cloudflare R2: {url_publica}")
            
            return True, url_publica
            
        except Exception as e:
            error_msg = f"Error al subir imagen a Cloudflare R2: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def upload_foto_reporte(foto_reporte_instance) -> Tuple[bool, Optional[str]]:
        """
        Subir una FotoReporte específica a Cloudflare R2
        
        Args:
            foto_reporte_instance: Instancia de FotoReporte
            
        Returns:
            Tuple[bool, str]: (éxito, url_pública o mensaje_de_error)
        """
        try:
            # Verificar si la imagen existe
            if not foto_reporte_instance.imagen:
                return False, f"No se encontró archivo de imagen para FotoReporte {foto_reporte_instance.id}"
            
            # Obtener el nombre del archivo en el storage
            nombre_en_r2 = foto_reporte_instance.imagen.name
            
            # Intentar leer el archivo usando el storage actual
            try:
                # Usar el storage del campo imagen para leer el archivo
                storage_actual = foto_reporte_instance.imagen.storage
                
                # Verificar si el archivo existe en el storage actual
                if not storage_actual.exists(nombre_en_r2):
                    return False, f"Archivo no existe en el storage actual: {nombre_en_r2}"
                
                # Leer el contenido del archivo desde el storage
                with storage_actual.open(nombre_en_r2, 'rb') as f:
                    contenido_archivo = f.read()
                
            except Exception as e:
                # Si falla la lectura desde storage, intentar con ruta absoluta si existe
                try:
                    if hasattr(foto_reporte_instance.imagen, 'path'):
                        archivo_local = foto_reporte_instance.imagen.path
                        if os.path.exists(archivo_local):
                            with open(archivo_local, 'rb') as f:
                                contenido_archivo = f.read()
                        else:
                            return False, f"Archivo local no encontrado: {archivo_local}"
                    else:
                        return False, f"No se puede acceder al archivo: {str(e)}"
                except Exception as e2:
                    return False, f"Error accediendo al archivo: {str(e2)}"
            
            # Crear ContentFile para Django storage
            django_file = ContentFile(contenido_archivo)
            
            # Subir el archivo a Cloudflare R2
            storage = default_storage
            
            # Verificar si el archivo ya existe
            if storage.exists(nombre_en_r2):
                logger.info(f"Archivo ya existe en R2: {nombre_en_r2}")
                url_publica = storage.url(nombre_en_r2)
                return True, url_publica
            
            archivo_guardado = storage.save(nombre_en_r2, django_file)
            
            # Obtener la URL pública
            url_publica = storage.url(archivo_guardado)
            
            logger.info(f"Imagen subida exitosamente a Cloudflare R2: {url_publica}")
            
            return True, url_publica
            
        except Exception as e:
            error_msg = f"Error al procesar FotoReporte {foto_reporte_instance.id}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def check_file_exists_in_r2(file_path: str) -> bool:
        """
        Verificar si un archivo existe en Cloudflare R2
        
        Args:
            file_path: Ruta del archivo en R2
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            if not CloudflareR2ImageUploader.is_r2_enabled():
                return False
            
            storage = default_storage
            return storage.exists(file_path)
            
        except Exception as e:
            logger.error(f"Error verificando archivo en R2: {str(e)}")
            return False
    
    @staticmethod
    def get_r2_url(file_path: str) -> Optional[str]:
        """
        Obtener la URL pública de un archivo en R2
        
        Args:
            file_path: Ruta del archivo en R2
            
        Returns:
            str: URL pública o None si hay error
        """
        try:
            if not CloudflareR2ImageUploader.is_r2_enabled():
                return None
            
            storage = default_storage
            if storage.exists(file_path):
                return storage.url(file_path)
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo URL de R2: {str(e)}")
            return None


def upload_foto_reporte_to_r2(foto_reporte_instance, async_upload=True):
    """
    Función de conveniencia para subir una FotoReporte a Cloudflare R2
    
    Args:
        foto_reporte_instance: Instancia de FotoReporte
        async_upload: Si es True, no lanza excepciones (para uso en signals)
    
    Returns:
        bool: True si fue exitoso, False si hubo error
    """
    try:
        success, result = CloudflareR2ImageUploader.upload_foto_reporte(foto_reporte_instance)
        
        if success:
            logger.info(f"FotoReporte {foto_reporte_instance.id} subida exitosamente a R2: {result}")
        else:
            logger.error(f"Error subiendo FotoReporte {foto_reporte_instance.id}: {result}")
        
        return success
        
    except Exception as e:
        error_msg = f"Error en upload_foto_reporte_to_r2: {str(e)}"
        logger.error(error_msg)
        
        if not async_upload:
            raise Exception(error_msg)
        
        return False


def get_foto_reporte_debug_info(foto_reporte_instance):
    """
    Obtener información de debugging para una FotoReporte
    
    Args:
        foto_reporte_instance: Instancia de FotoReporte
    
    Returns:
        dict: Información de debug
    """
    debug_info = {
        'foto_id': foto_reporte_instance.id,
        'tiene_imagen': bool(foto_reporte_instance.imagen),
        'nombre_archivo': None,
        'storage_type': None,
        'existe_en_storage': False,
        'tiene_path_absoluto': False,
        'existe_archivo_local': False,
        'path_absoluto': None,
        'errores': []
    }
    
    try:
        if foto_reporte_instance.imagen:
            debug_info['nombre_archivo'] = foto_reporte_instance.imagen.name
            debug_info['storage_type'] = type(foto_reporte_instance.imagen.storage).__name__
            
            # Verificar storage
            try:
                storage = foto_reporte_instance.imagen.storage
                debug_info['existe_en_storage'] = storage.exists(foto_reporte_instance.imagen.name)
            except Exception as e:
                debug_info['errores'].append(f"Error accediendo storage: {str(e)}")
            
            # Verificar path absoluto
            try:
                if hasattr(foto_reporte_instance.imagen, 'path'):
                    debug_info['tiene_path_absoluto'] = True
                    debug_info['path_absoluto'] = foto_reporte_instance.imagen.path
                    debug_info['existe_archivo_local'] = os.path.exists(debug_info['path_absoluto'])
            except Exception as e:
                debug_info['errores'].append(f"Error accediendo path: {str(e)}")
    
    except Exception as e:
        debug_info['errores'].append(f"Error general: {str(e)}")
    
    return debug_info