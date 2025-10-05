# Integración de Cloudflare R2 para Imágenes de Reportes

Esta funcionalidad permite subir automáticamente todas las imágenes de reportes a Cloudflare R2, proporcionando almacenamiento escalable y CDN global para las imágenes de mascotas perdidas y encontradas.

## ✨ Características Implementadas

### 🔄 Subida Automática
- **Signal automático**: Cada vez que se crea una nueva `FotoReporte`, se sube automáticamente a Cloudflare R2
- **No bloquea el proceso**: La subida se ejecuta en segundo plano sin afectar la experiencia del usuario
- **Tolerancia a fallos**: Si la subida falla, el proceso principal continúa normalmente

### 🛠️ Herramientas de Administración
- **Comando de migración**: Migrar imágenes existentes a R2
- **Vista de estado**: Panel administrativo para ver el estado de R2
- **Resubida manual**: Permitir resubir imágenes individuales

### 📊 Monitoreo y Estadísticas
- Verificación del estado de Cloudflare R2
- Estadísticas de imágenes locales vs faltantes
- URLs para administradores

## 🚀 Instalación y Configuración

### 1. Configuración de Variables de Entorno
Asegúrate de tener estas variables en tu archivo `.env`:

```env
# Cloudflare R2 Configuration
USE_CLOUDFLARE_R2=true
CLOUDFLARE_R2_BUCKET_NAME=tu-bucket-name
CLOUDFLARE_R2_ENDPOINT_URL=https://tu-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=tu-access-key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=tu-secret-key
CLOUDFLARE_R2_CUSTOM_DOMAIN=tu-dominio-personalizado.com  # Opcional
```

### 2. Verificar la Conexión
Prueba la conexión a Cloudflare R2:

```bash
python manage.py cloudflare_r2 --action=test
```

### 3. Migrar Imágenes Existentes

#### Simulación (recomendado primero):
```bash
python manage.py migrate_images_to_r2 --dry-run
```

#### Migración completa:
```bash
python manage.py migrate_images_to_r2
```

#### Migración limitada (para pruebas):
```bash
python manage.py migrate_images_to_r2 --limit=10
```

#### Migrar un reporte específico:
```bash
python manage.py migrate_images_to_r2 --reporte-id=UUID_DEL_REPORTE
```

## 📝 Uso del Sistema

### Para Usuarios Finales
- **Transparente**: Los usuarios suben imágenes como siempre
- **Sin cambios**: La interfaz permanece igual
- **Automático**: Las imágenes se replican automáticamente a R2

### Para Administradores

#### Panel de Estado R2:
```
/reportes/admin/r2/estado/
```

#### Resubir Imagen Individual:
```
/reportes/admin/foto/<foto_id>/resubir/
```

## 🔧 Componentes Técnicos

### 1. Signal (`reportsservice/signals.py`)
```python
@receiver(post_save, sender=FotoReporte)
def subir_foto_a_cloudflare_r2(sender, instance, created, **kwargs):
    """Subir automáticamente fotos nuevas a Cloudflare R2"""
```

### 2. Utilidades (`reportsservice/utils.py`)
- `CloudflareR2ImageUploader`: Clase principal para manejo de R2
- `upload_foto_reporte_to_r2()`: Función de conveniencia
- Manejo robusto de errores y logging

### 3. Comando de Migración (`reportsservice/management/commands/migrate_images_to_r2.py`)
- Migración masiva de imágenes existentes
- Modo dry-run para pruebas
- Filtros por reporte o cantidad
- Estadísticas detalladas

### 4. Vistas Administrativas (`reportsservice/views.py`)
- `estado_cloudflare_r2()`: Panel de estado y estadísticas
- `resubir_imagen_r2()`: Resubida manual de imágenes

## 🏗️ Flujo de Funcionamiento

### Creación de Nuevo Reporte con Imagen:
1. Usuario sube imagen a través del formulario
2. Se crea `FotoReporte` en la base de datos
3. Imagen se guarda localmente (comportamiento normal)
4. **Signal automático** detecta la nueva `FotoReporte`
5. Se ejecuta subida a Cloudflare R2 en segundo plano
6. Log del resultado (éxito o error)

### Migración de Imágenes Existentes:
1. Administrador ejecuta comando de migración
2. Se procesan todas las `FotoReporte` existentes
3. Se verifican archivos locales
4. Se suben a R2 manteniendo la estructura de carpetas
5. Reporte detallado de resultados

## 🛡️ Consideraciones de Seguridad

### Acceso Administrativo
- Solo usuarios `staff` pueden acceder a las vistas administrativas
- Decorator `@staff_member_required` protege las URLs sensibles

### Manejo de Errores
- Errores no bloquean el proceso principal
- Logging detallado para troubleshooting
- Validación de archivos antes de subir

### Tolerancia a Fallos
- Si R2 no está disponible, las imágenes siguen funcionando localmente
- El sistema no depende de R2 para funcionar

## 📈 Monitoreo y Logs

### Logs Importantes:
```python
logger.info(f"Imagen subida exitosamente a Cloudflare R2: {url}")
logger.error(f"Error al subir imagen a Cloudflare R2: {error}")
logger.warning(f"Cloudflare R2 no está habilitado")
```

### Verificaciones de Estado:
- Estado de conexión a R2
- Cantidad de imágenes locales vs en R2
- Archivos faltantes o corruptos

## 🚨 Resolución de Problemas

### Error: "Cloudflare R2 no está habilitado"
- Verificar `USE_CLOUDFLARE_R2=true` en `.env`
- Reiniciar el servidor Django

### Error de Conexión a R2:
- Verificar credenciales en `.env`
- Probar conexión: `python manage.py cloudflare_r2 --action=test`
- Verificar configuración del bucket

### Imágenes No Se Suben Automáticamente:
- Verificar que las signals están registradas en `apps.py`
- Revisar logs de Django para errores
- Probar subida manual desde el panel administrativo

### Error: "This backend doesn't support absolute paths"
- Ejecutar diagnóstico: `python manage.py diagnosticar_imagenes --verbose`
- Verificar configuración de storage en `settings.py`
- Las imágenes pueden estar en almacenamiento remoto (como R2) y no local

### Migración Falla:
- Usar `--dry-run` primero para identificar problemas
- Ejecutar diagnóstico completo: `python manage.py diagnosticar_imagenes`
- Verificar permisos de archivos locales
- Usar `--limit` para probar con pocas imágenes primero

## 🔄 Mantenimiento

### Tareas Regulares:
1. Monitorear logs de subida a R2
2. Verificar estadísticas en el panel administrativo
3. Limpiar archivos locales antiguos (opcional)
4. Verificar límites de uso del bucket R2

### Comandos Útiles:
```bash
# Diagnosticar estado de imágenes
python manage.py diagnosticar_imagenes

# Diagnosticar una imagen específica
python manage.py diagnosticar_imagenes --foto-id=4 --verbose

# Verificar migración
python manage.py migrate_images_to_r2 --dry-run

# Migrar imágenes faltantes
python manage.py migrate_images_to_r2 --limit=100

# Probar conexión
python manage.py cloudflare_r2 --action=test
```

---

## 📞 Soporte

Si encuentras problemas:
1. Revisar logs de Django
2. Verificar configuración de `.env`
3. Probar comandos de diagnóstico
4. Revisar documentación de Cloudflare R2

**¡Las imágenes de las mascotas ahora están respaldadas globalmente!** 🐾