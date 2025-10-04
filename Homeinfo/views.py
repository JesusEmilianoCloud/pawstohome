from django.shortcuts import render
from reportsservice.models import Reporte

# Create your views here.

def home(request):
    """Vista principal de la aplicación PawsToHome"""
    # Obtener algunos reportes recientes para mostrar en el home
    reportes_recientes = Reporte.objects.filter(visible=True).select_related('raza').prefetch_related('fotos')[:6]
    
    context = {
        'reportes_recientes': reportes_recientes,
    }
    
    return render(request, 'Homeinfo/home.html', context)
