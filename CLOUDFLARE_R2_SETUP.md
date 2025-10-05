# Configuración de Cloudflare R2 para PawsToHome

Esta guía explica cómo configurar Cloudflare R2 como almacenamiento de archivos media para PawsToHome.

## 📋 Requisitos

1. Cuenta de Cloudflare con R2 habilitado
2. Bucket de R2 creado
3. Credenciales de API configuradas

## 🛠️ Configuración Paso a Paso

### 1. Instalar Dependencias

```bash
pip install django-storages boto3
```

### 2. Configurar Cloudflare R2

1. **Ir al dashboard de Cloudflare**
   - Ve a R2 Object Storage
   - Crea un nuevo bucket (ej: `pawstohome-media`)

2. **Crear Token de API**
   - Ve a R2 > Manage R2 API tokens
   - Crea un nuevo token con permisos de lectura/escritura
   - Guarda el Access Key ID y Secret Access Key

3. **Obtener Endpoint URL**
   - El formato es: `https://[account-id].r2.cloudflarestorage.com`
   - Puedes encontrar tu account ID en el dashboard

### 3. Configurar Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Habilitar Cloudflare R2
USE_CLOUDFLARE_R2=true

# Credenciales de R2
CLOUDFLARE_R2_ACCESS_KEY_ID=tu-access-key-id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=tu-secret-access-key
CLOUDFLARE_R2_BUCKET_NAME=pawstohome-media
CLOUDFLARE_R2_ENDPOINT_URL=https://tu-account-id.r2.cloudflarestorage.com

# Dominio personalizado (opcional pero recomendado)
CLOUDFLARE_R2_CUSTOM_DOMAIN=media.tudominio.com
```

### 4. Configurar Dominio Personalizado (Recomendado)

1. **En Cloudflare Dashboard:**
   - Ve a tu bucket de R2
   - Ve a "Custom Domains"
   - Añade tu dominio (ej: `media.tudominio.com`)

2. **Configurar DNS:**
   - Añade un registro CNAME que apunte a tu bucket
   - Ejemplo: `media.tudominio.com` → `pawstohome-media.account-id.r2.cloudflarestorage.com`

## 🧪 Probar la Configuración

### 1. Probar Conexión

```bash
python manage.py cloudflare_r2 --action=test
```

### 2. Subir Archivo de Prueba

```bash
python manage.py cloudflare_r2 --action=upload-test --file-path=ruta/al/archivo.jpg
```

### 3. Listar Archivos

```bash
python manage.py cloudflare_r2 --action=list
```

## 📁 Estructura de Archivos en R2

```
pawstohome-media/
├── media/
│   ├── reportes/
│   │   ├── [uuid]/
│   │   │   └── fotos/
│   │   │       ├── imagen1.jpg
│   │   │       └── imagen2.jpg
│   └── profiles/
│       └── avatars/
└── static/
    ├── css/
    ├── js/
    └── images/
```

## 🔧 Configuración Avanzada

### Configurar CORS (Si es necesario)

Si tu aplicación web necesita acceso desde diferentes dominios:

```json
{
  "rules": [
    {
      "allowed_origins": ["https://tudominio.com", "https://www.tudominio.com"],
      "allowed_methods": ["GET", "HEAD"],
      "allowed_headers": ["*"],
      "max_age": 3600
    }
  ]
}
```

### Configurar Políticas de Bucket

Para hacer público el acceso de lectura a archivos media:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::pawstohome-media/media/*"
    }
  ]
}
```

## 🚀 Migración de Archivos Existentes

Para migrar archivos de almacenamiento local a R2:

### Opción 1: Usando rclone

```bash
# Instalar rclone
# Configurar rclone con Cloudflare R2
rclone config

# Sincronizar archivos
rclone sync ./media/ r2:pawstohome-media/media/
```

### Opción 2: Usando AWS CLI

```bash
# Configurar AWS CLI con credenciales de R2
aws configure --profile r2

# Sincronizar archivos
aws s3 sync ./media/ s3://pawstohome-media/media/ --endpoint-url=https://tu-account-id.r2.cloudflarestorage.com --profile r2
```

## 🔍 Solución de Problemas

### Error de Conexión

- Verifica que las credenciales sean correctas
- Asegúrate de que el endpoint URL sea correcto
- Verifica que el bucket existe y tienes permisos

### URLs no Funcionan

- Verifica la configuración de CORS
- Asegúrate de que los archivos sean públicamente accesibles
- Verifica la configuración del dominio personalizado

### Archivos no se Suben

- Verifica permisos de escritura en el token de API
- Asegúrate de que `USE_CLOUDFLARE_R2=true`
- Revisa los logs de Django para errores específicos

## 💰 Consideraciones de Costos

- **Almacenamiento**: $0.015 per GB/mes
- **Operaciones Class A**: $4.50 per millón (PUT, COPY, POST, LIST)
- **Operaciones Class B**: $0.36 per millón (GET, SELECT)
- **Transferencia de datos**: Gratis hasta 10TB/mes

## 🔒 Seguridad

- Nunca expongas tus credenciales en el código
- Usa variables de entorno para las credenciales
- Configura permisos mínimos necesarios en los tokens
- Considera usar roles y políticas de IAM para mayor seguridad