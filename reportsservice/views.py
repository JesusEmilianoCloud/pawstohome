from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import Reporte, Raza, FotoReporte, Comentario

def lista_reportes(request):
    """
    Vista para mostrar la lista de reportes con filtros y paginación
    """
    reportes = Reporte.objects.filter(visible=True).select_related('usuario', 'raza').prefetch_related('fotos')
    
    # Filtros
    tipo_reporte = request.GET.get('tipo_reporte')
    tamano = request.GET.get('tamano')
    zona = request.GET.get('zona')
    raza_id = request.GET.get('raza')
    
    if tipo_reporte:
        reportes = reportes.filter(tipo_reporte=tipo_reporte)
    
    if tamano:
        reportes = reportes.filter(tamano=tamano)
    
    if zona:
        reportes = reportes.filter(zona__icontains=zona)
    
    if raza_id:
        reportes = reportes.filter(raza_id=raza_id)
    
    # Estadísticas
    stats = {
        'perdidos': Reporte.objects.filter(tipo_reporte='perdido', estado='activo', visible=True).count(),
        'encontrados': Reporte.objects.filter(tipo_reporte='encontrado', estado='activo', visible=True).count(),
        'reunidos': Reporte.objects.filter(estado='cerrado', visible=True).count(),
        'total': Reporte.objects.filter(visible=True).count(),
    }
    
    # Paginación
    paginator = Paginator(reportes, 12)  # 12 reportes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener todas las razas para el filtro
    razas = Raza.objects.all().order_by('nombre')
    
    context = {
        'reportes': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'stats': stats,
        'razas': razas,
    }
    
    return render(request, 'reportsservice/reportes.html', context)

def detalle_reporte(request, id):
    """
    Vista para mostrar el detalle de un reporte específico
    """
    reporte = get_object_or_404(
        Reporte.objects.select_related('usuario', 'raza').prefetch_related('fotos', 'comentarios__usuario'), 
        id=id, 
        visible=True
    )
    
    context = {
        'reporte': reporte,
    }
    
    return render(request, 'reportsservice/detalle_reporte.html', context)

@login_required
def crear_reporte(request):
    """
    Vista para crear un nuevo reporte
    """
    if request.method == 'POST':
        try:
            # Crear el reporte
            reporte = Reporte(
                usuario=request.user,
                tipo_reporte=request.POST.get('tipo_reporte'),
                nombre_perro=request.POST.get('nombre_perro'),
                color=request.POST.get('color'),
                tamano=request.POST.get('tamano'),
                descripcion=request.POST.get('descripcion'),
                caracteristicas_distintivas=request.POST.get('caracteristicas_distintivas', ''),
                latitud=float(request.POST.get('latitud')),
                longitud=float(request.POST.get('longitud')),
                direccion=request.POST.get('direccion'),
                zona=request.POST.get('zona'),
                fecha_incidente=request.POST.get('fecha_incidente'),
                telefono_contacto=request.POST.get('telefono_contacto'),
                email_contacto=request.POST.get('email_contacto'),
            )
            
            # Asignar raza si se seleccionó
            raza_id = request.POST.get('raza')
            if raza_id:
                try:
                    reporte.raza = Raza.objects.get(id=raza_id)
                except Raza.DoesNotExist:
                    pass
            
            reporte.save()
            
            # Procesar fotos
            fotos = request.FILES.getlist('fotos')
            for i, foto in enumerate(fotos):
                foto_reporte = FotoReporte(
                    reporte=reporte,
                    imagen=foto,
                    es_principal=(i == 0),  # Primera foto es principal
                    orden=i
                )
                foto_reporte.save()
            
            messages.success(request, 'Reporte creado exitosamente.')
            return redirect('reportsservice:detalle_reporte', id=reporte.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el reporte: {str(e)}')
    
    # Obtener razas para el formulario
    razas = Raza.objects.all().order_by('nombre')
    
    context = {
        'razas': razas,
    }
    
    return render(request, 'reportsservice/crear_reporte.html', context)

@login_required
def agregar_comentario(request, id):
    """
    Vista para agregar comentarios a un reporte
    """
    if request.method == 'POST':
        reporte = get_object_or_404(Reporte, id=id, visible=True)
        
        comentario = Comentario(
            reporte=reporte,
            usuario=request.user,
            tipo=request.POST.get('tipo', 'otro'),
            contenido=request.POST.get('contenido'),
        )
        
        # Agregar ubicación si se proporciona
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        
        if latitud and longitud:
            try:
                comentario.set_ubicacion(float(latitud), float(longitud))
            except ValueError:
                pass
        
        comentario.save()
        messages.success(request, 'Comentario agregado exitosamente.')
        
    return redirect('reportsservice:detalle_reporte', id=id)
