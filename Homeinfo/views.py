from django.shortcuts import render
from reportsservice.models import Reporte

# Create your views here.

def home(request):
    """Vista principal de la aplicación PawsToHome"""
    # Debug: verificar primero cuántos reportes hay en total
    total_reportes = Reporte.objects.count()
    print(f"Total de reportes en BD: {total_reportes}")
    
    # Verificar cuántos están activos
    activos = Reporte.objects.filter(estado='activo').count()
    print(f"Reportes activos: {activos}")
    
    # Obtener los reportes más recientes (máximo 6 para la vista principal)
    reportes_recientes = Reporte.objects.filter(
        estado='activo'
    ).select_related('raza', 'usuario').prefetch_related('fotos').order_by('-fecha_reporte')[:6]
    
    print(f"Reportes obtenidos para mostrar: {len(reportes_recientes)}")
    for reporte in reportes_recientes:
        print(f"- {reporte.nombre_perro} ({reporte.tipo_reporte}) - Estado: {reporte.estado}")
        print(f"  Fotos: {reporte.fotos.count()}")
        if reporte.fotos.exists():
            primera_foto = reporte.fotos.first()
            print(f"  Primera foto: {primera_foto.imagen.url if primera_foto.imagen else 'Sin imagen'}")
        else:
            print("  No hay fotos asociadas")
    
    context = {
        'reportes_recientes': reportes_recientes,
    }
    
    return render(request, 'Homeinfo/home.html', context)
