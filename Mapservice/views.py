from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from reportsservice.models import Reporte, Raza
from django.utils import timezone
from datetime import datetime, timedelta
import json

def mapa_interactivo(request):
    """Vista para el mapa interactivo de reportes"""
    # Obtener todas las razas para el filtro
    razas = Raza.objects.all().order_by('nombre')
    
    # Obtener parámetros de ubicación específica si vienen del detalle del reporte
    lat = request.GET.get('lat', '')
    lng = request.GET.get('lng', '')
    direccion = request.GET.get('direccion', '')
    zona = request.GET.get('zona', '')
    nombre = request.GET.get('nombre', '')
    
    context = {
        'razas': razas,
        'initial_lat': lat,
        'initial_lng': lng,
        'initial_direccion': direccion,
        'initial_zona': zona,
        'initial_nombre': nombre,
    }
    
    return render(request, 'Mapservice/mapa_interactivo.html', context)

def api_reportes_mapa(request):
    """API para obtener reportes para el mapa con filtros"""
    # Obtener parámetros de filtrado
    tipo_reporte = request.GET.get('tipo_reporte', '')
    busqueda = request.GET.get('busqueda', '')
    raza_id = request.GET.get('raza', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    lat_centro = request.GET.get('lat_centro', '')
    lng_centro = request.GET.get('lng_centro', '')
    radio = request.GET.get('radio', '10')  # Radio en km, default 10km
    
    # Construir query base
    reportes = Reporte.objects.filter(visible=True, estado='activo').select_related('raza', 'usuario').prefetch_related('fotos')
    
    # Aplicar filtros
    if tipo_reporte:
        reportes = reportes.filter(tipo_reporte=tipo_reporte)
    
    if busqueda:
        reportes = reportes.filter(
            Q(nombre_perro__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(caracteristicas_distintivas__icontains=busqueda) |
            Q(color__icontains=busqueda) |
            Q(zona__icontains=busqueda)
        )
    
    if raza_id:
        try:
            reportes = reportes.filter(raza_id=raza_id)
        except ValueError:
            pass
    
    # Filtro por fechas
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            reportes = reportes.filter(fecha_reporte__gte=fecha_desde_dt)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Agregar 23:59:59 para incluir todo el día
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            reportes = reportes.filter(fecha_reporte__lte=fecha_hasta_dt)
        except ValueError:
            pass
    
    # Filtro por radio geográfico
    if lat_centro and lng_centro and radio:
        try:
            lat = float(lat_centro)
            lng = float(lng_centro)
            radio_km = float(radio)
            
            # Cálculo aproximado de coordenadas en un radio
            # 1 grado ≈ 111 km
            lat_delta = radio_km / 111.0
            lng_delta = radio_km / (111.0 * abs(lat) if lat != 0 else 111.0)
            
            reportes = reportes.filter(
                latitud__gte=lat - lat_delta,
                latitud__lte=lat + lat_delta,
                longitud__gte=lng - lng_delta,
                longitud__lte=lng + lng_delta
            )
        except (ValueError, TypeError):
            pass
    
    # Convertir a formato JSON para el mapa
    reportes_data = []
    for reporte in reportes:
        # Obtener primera foto si existe
        primera_foto = reporte.fotos.first()
        foto_url = primera_foto.imagen.url if primera_foto and primera_foto.imagen else None
        
        reportes_data.append({
            'id': str(reporte.id),
            'tipo_reporte': reporte.tipo_reporte,
            'nombre_perro': reporte.nombre_perro,
            'raza': reporte.raza.nombre if reporte.raza else 'Mestizo',
            'color': reporte.color,
            'tamano': reporte.get_tamano_display(),
            'descripcion': reporte.descripcion[:200] + '...' if len(reporte.descripcion) > 200 else reporte.descripcion,
            'caracteristicas_distintivas': reporte.caracteristicas_distintivas,
            'latitud': float(reporte.latitud),
            'longitud': float(reporte.longitud),
            'direccion': reporte.direccion,
            'zona': reporte.zona,
            'fecha_reporte': reporte.fecha_reporte.strftime('%d/%m/%Y %H:%M'),
            'fecha_incidente': reporte.fecha_incidente.strftime('%d/%m/%Y %H:%M'),
            'telefono_contacto': reporte.telefono_contacto,
            'email_contacto': reporte.email_contacto,
            'foto_url': foto_url,
            'usuario': f"{reporte.usuario.first_name} {reporte.usuario.last_name}".strip() or reporte.usuario.username,
        })
    
    return JsonResponse({
        'reportes': reportes_data,
        'total': len(reportes_data)
    })
