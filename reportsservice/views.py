from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from .models import Reporte, Raza, FotoReporte, Comentario
from .utils import CloudflareR2ImageUploader, upload_foto_reporte_to_r2

@login_required
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
@login_required
def crear_reporte(request):
    """
    Vista para crear un nuevo reporte
    """
    if request.method == 'POST':
        try:
            # Validar campos requeridos
            required_fields = [
                'tipo_reporte', 'nombre_perro', 'color', 'tamano', 'descripcion',
                'latitud', 'longitud', 'direccion', 'zona', 'fecha_incidente',
                'telefono_contacto', 'email_contacto'
            ]
            
            missing_fields = []
            for field in required_fields:
                if not request.POST.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                messages.error(request, f'Faltan los siguientes campos: {", ".join(missing_fields)}')
                raise ValueError("Campos faltantes")
            
            # Validar coordenadas
            try:
                latitud = float(request.POST.get('latitud'))
                longitud = float(request.POST.get('longitud'))
                
                if not (-90 <= latitud <= 90):
                    raise ValueError("Latitud fuera de rango")
                if not (-180 <= longitud <= 180):
                    raise ValueError("Longitud fuera de rango")
                    
            except (ValueError, TypeError):
                messages.error(request, 'Las coordenadas proporcionadas no son válidas')
                raise ValueError("Coordenadas inválidas")
            
            # Crear el reporte
            reporte = Reporte(
                usuario=request.user,
                tipo_reporte=request.POST.get('tipo_reporte'),
                nombre_perro=request.POST.get('nombre_perro').strip(),
                color=request.POST.get('color').strip(),
                tamano=request.POST.get('tamano'),
                descripcion=request.POST.get('descripcion').strip(),
                caracteristicas_distintivas=request.POST.get('caracteristicas_distintivas', '').strip(),
                latitud=latitud,
                longitud=longitud,
                direccion=request.POST.get('direccion').strip(),
                zona=request.POST.get('zona').strip(),
                fecha_incidente=request.POST.get('fecha_incidente'),
                telefono_contacto=request.POST.get('telefono_contacto').strip(),
                email_contacto=request.POST.get('email_contacto').strip(),
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
            
            # Validar fotos si las hay
            if fotos:
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                max_size = 5 * 1024 * 1024  # 5MB
                
                for foto in fotos:
                    if foto.content_type not in allowed_types:
                        messages.error(request, f'Tipo de archivo no válido: {foto.name}. Solo se permiten JPG, PNG y GIF.')
                        raise ValueError("Tipo de archivo inválido")
                    
                    if foto.size > max_size:
                        messages.error(request, f'El archivo {foto.name} es muy grande. Máximo 5MB permitidos.')
                        raise ValueError("Archivo muy grande")
            
            # Guardar fotos
            for i, foto in enumerate(fotos):
                try:
                    foto_reporte = FotoReporte(
                        reporte=reporte,
                        imagen=foto,
                        es_principal=(i == 0),  # Primera foto es principal
                        orden=i
                    )
                    foto_reporte.save()
                except Exception as foto_error:
                    messages.warning(request, f'Error al procesar la foto {foto.name}: {str(foto_error)}')
                    # Continuar con las demás fotos
            
            messages.success(request, 'Reporte creado exitosamente.')
            return redirect('reportsservice:detalle_reporte', id=reporte.id)
            
        except ValueError:
            # Error de validación ya mostrado
            pass
        except Exception as e:
            messages.error(request, f'Error inesperado al crear el reporte: {str(e)}')
    
    # Obtener razas para el formulario
    razas = Raza.objects.all().order_by('nombre')
    
    # Mantener los datos del formulario en caso de error
    context = {
        'razas': razas,
    }
    
    # Si hay datos POST y hubo errores, mantener los valores
    if request.method == 'POST':
        context.update({
            'form_data': request.POST,
            'preserve_files': request.FILES
        })
    
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

@staff_member_required
def resubir_imagen_r2(request, foto_id):
    """
    Vista para resubir manualmente una imagen a Cloudflare R2
    Solo accesible por staff/administradores
    """
    foto = get_object_or_404(FotoReporte, id=foto_id)
    
    if request.method == 'POST':
        # Intentar subir la imagen
        success = upload_foto_reporte_to_r2(foto, async_upload=False)
        
        if success:
            messages.success(request, f'Imagen subida exitosamente a Cloudflare R2')
        else:
            messages.error(request, f'Error al subir la imagen a Cloudflare R2')
        
        return redirect('reportsservice:detalle_reporte', id=foto.reporte.id)
    
    # GET request - mostrar confirmación
    context = {
        'foto': foto,
        'r2_enabled': CloudflareR2ImageUploader.is_r2_enabled(),
        'exists_in_r2': CloudflareR2ImageUploader.check_file_exists_in_r2(foto.imagen.name) if foto.imagen else False,
    }
    
    return render(request, 'reportsservice/resubir_imagen.html', context)

@staff_member_required  
def estado_cloudflare_r2(request):
    """
    Vista para mostrar el estado de Cloudflare R2 y estadísticas de imágenes
    Solo accesible por staff/administradores
    """
    context = {
        'r2_enabled': CloudflareR2ImageUploader.is_r2_enabled(),
        'total_fotos': FotoReporte.objects.count(),
    }
    
    # Calcular estadísticas de imágenes que existen localmente
    fotos_locales = 0
    fotos_sin_archivo = 0
    
    for foto in FotoReporte.objects.all():
        if foto.imagen and hasattr(foto.imagen, 'path'):
            try:
                if foto.imagen.path and foto.imagen.storage.exists(foto.imagen.name):
                    fotos_locales += 1
                else:
                    fotos_sin_archivo += 1
            except:
                fotos_sin_archivo += 1
        else:
            fotos_sin_archivo += 1
    
    context.update({
        'fotos_locales': fotos_locales,
        'fotos_sin_archivo': fotos_sin_archivo,
    })
    
    return render(request, 'reportsservice/estado_r2.html', context)

@login_required
def eliminar_reporte(request, id):
    """
    Vista para eliminar un reporte y todas sus imágenes asociadas
    Solo el propietario del reporte o staff puede eliminarlo
    """
    reporte = get_object_or_404(Reporte, id=id)
    
    # Verificar permisos
    if request.user != reporte.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permisos para eliminar este reporte.")
        return redirect('reportsservice:detalle_reporte', id=id)
    
    if request.method == 'POST':
        try:
            # Obtener información del reporte antes de eliminarlo
            nombre_perro = reporte.nombre_perro
            total_fotos = reporte.fotos.count()
            
            # Django eliminará automáticamente las FotoReporte asociadas debido al CASCADE
            # Los signals se encargarán de eliminar las imágenes de Cloudflare R2
            reporte.delete()
            
            messages.success(
                request, 
                f"El reporte de {nombre_perro} ha sido eliminado exitosamente junto con {total_fotos} imagen(es) asociada(s)."
            )
            return redirect('reportsservice:reportes')
            
        except Exception as e:
            messages.error(request, f"Error al eliminar el reporte: {str(e)}")
            return redirect('reportsservice:detalle_reporte', id=id)
    
    # GET request - mostrar confirmación
    context = {
        'reporte': reporte,
    }
    
    return render(request, 'reportsservice/confirmar_eliminacion.html', context)

@login_required
def editar_reporte(request, id):
    """
    Vista para editar un reporte existente
    Solo el creador del reporte puede editarlo
    """
    reporte = get_object_or_404(Reporte, id=id, visible=True)
    if reporte.usuario != request.user:
        return HttpResponseForbidden("Solo el creador puede editar este reporte.")

    razas = Raza.objects.all().order_by('nombre')

    if request.method == 'POST':
        # Validar y actualizar campos
        reporte.nombre_perro = request.POST.get('nombre_perro', reporte.nombre_perro)
        reporte.color = request.POST.get('color', reporte.color)
        reporte.tamano = request.POST.get('tamano', reporte.tamano)
        reporte.descripcion = request.POST.get('descripcion', reporte.descripcion)
        reporte.caracteristicas_distintivas = request.POST.get('caracteristicas_distintivas', reporte.caracteristicas_distintivas)
        reporte.latitud = request.POST.get('latitud', reporte.latitud)
        reporte.longitud = request.POST.get('longitud', reporte.longitud)
        reporte.direccion = request.POST.get('direccion', reporte.direccion)
        reporte.zona = request.POST.get('zona', reporte.zona)
        reporte.fecha_incidente = request.POST.get('fecha_incidente', reporte.fecha_incidente)
        reporte.telefono_contacto = request.POST.get('telefono_contacto', reporte.telefono_contacto)
        reporte.email_contacto = request.POST.get('email_contacto', reporte.email_contacto)
        raza_id = request.POST.get('raza')
        if raza_id:
            try:
                reporte.raza = Raza.objects.get(id=raza_id)
            except Raza.DoesNotExist:
                pass
        reporte.save()
        # Manejo de fotos nuevas (solo una secundaria permitida)
        fotos = request.FILES.getlist('fotos')
        if fotos:
            # Elimina la foto secundaria existente (es_principal=False) si hay una
            foto_secundaria = reporte.fotos.filter(es_principal=False).first()
            if foto_secundaria:
                foto_secundaria.delete()
            # Solo guarda la primera foto subida como secundaria
            foto = fotos[0]
            foto_reporte = FotoReporte(
                reporte=reporte,
                imagen=foto,
                es_principal=False,
                orden=reporte.fotos.count()
            )
            foto_reporte.save()
        # Manejo de eliminación de fotos
        for foto in reporte.fotos.all():
            if request.POST.get(f'eliminar_foto_{foto.id}'):
                foto.delete()
        messages.success(request, 'Reporte actualizado correctamente.')
        return redirect('reportsservice:detalle_reporte', id=reporte.id)

    context = {
        'reporte': reporte,
        'razas': razas,
    }
    return render(request, 'reportsservice/editar_reporte.html', context)
