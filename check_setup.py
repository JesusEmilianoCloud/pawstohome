#!/usr/bin/env python3
"""
Script para verificar la configuración de PawsToHome
Ejecutar: python check_setup.py
"""

import os
import sys
import django
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawtohome.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

def check_environment():
    """Verificar variables de entorno"""
    print("\n🔍 Verificando configuración del entorno...")
    
    required_vars = [
        'SECRET_KEY',
        'DEBUG',
    ]
    
    optional_vars = [
        'USE_CLOUDFLARE_R2',
        'CLOUDFLARE_R2_ACCESS_KEY_ID',
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_BUCKET_NAME',
        'CLOUDFLARE_R2_ENDPOINT_URL',
    ]
    
    # Verificar variables requeridas
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Variables requeridas faltantes: {', '.join(missing_required)}")
        return False
    else:
        print("✅ Variables requeridas presentes")
    
    # Verificar variables opcionales para Cloudflare R2
    use_r2 = os.getenv('USE_CLOUDFLARE_R2', 'false').lower() == 'true'
    if use_r2:
        print("📡 Cloudflare R2 habilitado, verificando configuración...")
        missing_r2 = []
        for var in optional_vars[1:]:  # Saltar USE_CLOUDFLARE_R2
            if not os.getenv(var):
                missing_r2.append(var)
        
        if missing_r2:
            print(f"⚠️ Variables de R2 faltantes: {', '.join(missing_r2)}")
        else:
            print("✅ Configuración de Cloudflare R2 completa")
    else:
        print("📁 Usando almacenamiento local (desarrollo)")
    
    return True

def check_database():
    """Verificar conexión a la base de datos"""
    print("\n💾 Verificando base de datos...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

def check_models():
    """Verificar que los modelos se puedan importar"""
    print("\n📋 Verificando modelos...")
    
    try:
        from reportsservice.models import Reporte
        from loginservice.models import CustomUser
        from ProfileService.models import UserProfile
        
        # Verificar conteos básicos
        reportes_count = Reporte.objects.count()
        users_count = CustomUser.objects.count()
        profiles_count = UserProfile.objects.count()
        
        print(f"✅ Modelos importados correctamente")
        print(f"   - Reportes: {reportes_count}")
        print(f"   - Usuarios: {users_count}")
        print(f"   - Perfiles: {profiles_count}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def check_static_files():
    """Verificar archivos estáticos"""
    print("\n🎨 Verificando archivos estáticos...")
    
    static_files = [
        'static/css/home.css',
        'static/css/components.css',
    ]
    
    missing_files = []
    for file_path in static_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️ Archivos estáticos faltantes: {', '.join(missing_files)}")
    else:
        print("✅ Archivos estáticos principales encontrados")
    
    return len(missing_files) == 0

def main():
    """Función principal"""
    print("🏠 PawsToHome - Verificación de Configuración")
    print("=" * 50)
    
    checks = [
        check_environment(),
        check_database(),
        check_models(),
        check_static_files(),
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("🎉 ¡Todos los checks pasaron! El proyecto está listo.")
        
        # Verificar si hay migraciones pendientes
        print("\n📝 Comandos sugeridos:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        print("   python manage.py collectstatic")
        print("   python manage.py runserver")
        
    else:
        print("⚠️ Algunos checks fallaron. Revisa la configuración.")
        print("\n📚 Consulta CLOUDFLARE_R2_SETUP.md para más información.")

if __name__ == "__main__":
    main()