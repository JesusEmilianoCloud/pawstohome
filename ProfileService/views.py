from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from .models import ConfiguracionUsuario

# Create your views here.
User = get_user_model()

def getUserProfileData(request, user_id):
    """
    Vista para mostrar los datos del perfil de un usuario específico.
    """
    user = get_object_or_404(User, pk=user_id)
    
    # Obtener la configuración del usuario
    try:
        configuracion = ConfiguracionUsuario.objects.get(usuario=user)
    except ConfiguracionUsuario.DoesNotExist:
        configuracion = None
    
    context = {
        'profile_user': user,
        'configuracion': configuracion
    }
    
    return render(request, 'ProfileService/profile_detail.html', context)

@login_required
def edit_profile_view(request):
    """
    Vista para editar el perfil del usuario y su configuración.
    """
    user = request.user
    
    # Obtener o crear la configuración del usuario
    configuracion, created = ConfiguracionUsuario.objects.get_or_create(
        usuario=user,
        defaults={
            'notificaciones_email': True,
            'notificaciones_push': True,
            'radio_notificaciones': 5.0,
            'notificar_perdidos': True,
            'notificar_encontrados': True,
        }
    )
    
    if request.method == 'POST':
        try:
            # Manejar subida de foto de perfil
            if 'foto_perfil' in request.FILES:
                nueva_foto = request.FILES['foto_perfil']
                
                # Validar tipo de archivo
                allowed_types = ['image/jpeg', 'image/png', 'image/gif']
                if nueva_foto.content_type not in allowed_types:
                    messages.error(request, "Tipo de archivo no válido. Solo se permiten JPG, PNG y GIF.")
                    return render(request, 'edit_profile.html', {
                        'user': user,
                        'configuracion': configuracion
                    })
                
                # Validar tamaño (máximo 5MB)
                if nueva_foto.size > 5 * 1024 * 1024:
                    messages.error(request, "El archivo es muy grande. Máximo 5MB permitidos.")
                    return render(request, 'edit_profile.html', {
                        'user': user,
                        'configuracion': configuracion
                    })
                
                # Asignar nueva foto (las señales se encargarán de eliminar la anterior de R2)
                configuracion.foto_perfil = nueva_foto
            
            # Manejar eliminación de foto
            elif 'eliminar_foto' in request.POST:
                if configuracion.foto_perfil:
                    try:
                        # Eliminar foto (las señales se encargarán de R2)
                        configuracion.foto_perfil = None
                    except Exception as e:
                        print(f"Error eliminando foto: {e}")
            
            # Actualizar información personal del usuario
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            
            # Actualizar teléfono si el modelo lo tiene
            if hasattr(user, 'phone_number'):
                user.phone_number = request.POST.get('phone_number', user.phone_number)
            
            user.save()
            
            # Actualizar configuración de notificaciones
            configuracion.notificaciones_email = 'notificaciones_email' in request.POST
            configuracion.notificaciones_push = 'notificaciones_push' in request.POST
            
            # Actualizar radio de notificaciones
            radio = request.POST.get('radio_notificaciones')
            if radio:
                configuracion.radio_notificaciones = float(radio)
            
            # Actualizar dirección
            nueva_direccion = request.POST.get('direccion', '').strip()
            if nueva_direccion:
                configuracion.direccion = nueva_direccion
            else:
                configuracion.direccion = None
            
            # Actualizar ubicación preferida
            latitud = request.POST.get('latitud_preferida')
            longitud = request.POST.get('longitud_preferida')
            coordenadas_cambio = (
                configuracion.latitud_preferida != (float(latitud) if latitud else None) or
                configuracion.longitud_preferida != (float(longitud) if longitud else None)
            )
            
            if latitud and longitud:
                try:
                    configuracion.set_ubicacion_preferida(float(latitud), float(longitud))
                    
                    # Si hay obtención automática de dirección habilitada
                    direccion_auto = 'direccion_automatica' in request.POST
                    if direccion_auto and coordenadas_cambio and not nueva_direccion:
                        if configuracion.actualizar_direccion_desde_coordenadas():
                            messages.success(request, "Coordenadas actualizadas y dirección obtenida automáticamente.")
                        else:
                            messages.warning(request, "Coordenadas actualizadas, pero no se pudo obtener la dirección automáticamente.")
                
                except ValueError as e:
                    messages.error(request, f"Error en las coordenadas: {str(e)}")
                    return render(request, 'edit_profile.html', {
                        'user': user,
                        'configuracion': configuracion
                    })
            else:
                configuracion.latitud_preferida = None
                configuracion.longitud_preferida = None
            
            # Actualizar tipos de reportes
            configuracion.notificar_perdidos = 'notificar_perdidos' in request.POST
            configuracion.notificar_encontrados = 'notificar_encontrados' in request.POST
            
            configuracion.save()
            
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('ProfileService:edit_profile')
            
        except Exception as e:
            messages.error(request, f"Error al actualizar el perfil: {str(e)}")
    
    context = {
        'user': user,
        'configuracion': configuracion
    }
    
    return render(request, 'edit_profile.html', context)

@login_required
def obtener_direccion_desde_coordenadas_ajax(request):
    """
    Vista AJAX para obtener dirección desde coordenadas (geocodificación inversa)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitud = data.get('latitud')
            longitud = data.get('longitud')
            
            if not latitud or not longitud:
                return JsonResponse({
                    'success': False,
                    'error': 'Latitud y longitud son requeridas'
                })
            
            try:
                lat = float(latitud)
                lon = float(longitud)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Coordenadas inválidas'
                })
            
            # Crear objeto temporal para usar el método de geocodificación inversa
            configuracion_temp = ConfiguracionUsuario()
            configuracion_temp.latitud_preferida = lat
            configuracion_temp.longitud_preferida = lon
            
            resultado = configuracion_temp.geocodificar_coordenadas()
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'direccion': resultado['direccion'],
                    'direccion_completa': resultado['direccion_completa'],
                    'componentes': resultado['componentes']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo obtener la dirección para estas coordenadas'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error del servidor: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

def user_reports_view(request, user_id):
    """
    Vista para mostrar todos los reportes de un usuario específico.
    """
    from reportsservice.models import Reporte
    from django.core.paginator import Paginator
    
    # Obtener el usuario
    profile_user = get_object_or_404(User, pk=user_id)
    
    # Obtener todos los reportes del usuario visibles
    reportes = Reporte.objects.filter(
        usuario=profile_user,
        visible=True
    ).select_related('raza').prefetch_related('fotos').order_by('-fecha_reporte')
    
    # Filtros opcionales
    tipo_reporte = request.GET.get('tipo')
    estado = request.GET.get('estado')
    
    if tipo_reporte:
        reportes = reportes.filter(tipo_reporte=tipo_reporte)
    
    if estado:
        reportes = reportes.filter(estado=estado)
    
    # Estadísticas del usuario
    stats = {
        'total': Reporte.objects.filter(usuario=profile_user, visible=True).count(),
        'perdidos': Reporte.objects.filter(usuario=profile_user, tipo_reporte='perdido', visible=True).count(),
        'encontrados': Reporte.objects.filter(usuario=profile_user, tipo_reporte='encontrado', visible=True).count(),
        'activos': Reporte.objects.filter(usuario=profile_user, estado='activo', visible=True).count(),
        'cerrados': Reporte.objects.filter(usuario=profile_user, estado='cerrado', visible=True).count(),
    }
    
    # Paginación
    paginator = Paginator(reportes, 12)  # 12 reportes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': profile_user,
        'reportes': page_obj,
        'stats': stats,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'current_tipo': tipo_reporte,
        'current_estado': estado,
    }
    
    return render(request, 'ProfileService/user_reports.html', context)

@login_required
def delete_account_view(request):
    """
    Vista para eliminar la cuenta del usuario actual.
    Requiere confirmación explícita.
    """
    import logging
    from django.contrib import messages
    from django.contrib.auth import logout
    
    # Debug: Log la petición recibida
    logger = logging.getLogger(__name__)
    logger.info(f"DELETE ACCOUNT REQUEST: Método={request.method}, Usuario={request.user.id}")
    
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('ProfileService:profile', user_id=request.user.id)
    
    # Verificar confirmación
    confirmation = request.POST.get('confirm_deletion', '').strip()
    logger.info(f"DELETE ACCOUNT: Confirmación recibida='{confirmation}'")
    
    if confirmation != 'ELIMINAR':
        messages.error(request, "Confirmación incorrecta. No se eliminó la cuenta.")
        return redirect('ProfileService:profile', user_id=request.user.id)
    
    # Guardar información del usuario antes de eliminar
    user = request.user
    user_id = user.id
    user_name = f"{user.first_name} {user.last_name}" or user.username
    user_email = user.email
    
    logger.warning(f"INICIANDO ELIMINACIÓN: Usuario {user_id} ({user_name}) - {user_email}")
    
    try:
        # Eliminar usuario (las señales CASCADE eliminan el resto)
        logger.info(f"DELETE ACCOUNT: Eliminando usuario {user_id}")
        user.delete()
        logger.info(f"DELETE ACCOUNT: Usuario {user_id} eliminado exitosamente")
        
        # Cerrar sesión
        logout(request)
        logger.info(f"DELETE ACCOUNT: Sesión cerrada para usuario {user_id}")
        
        # Mensaje de éxito y redirección
        messages.success(request, "Tu cuenta ha sido eliminada exitosamente. Esperamos verte de nuevo pronto.")
        return redirect('Homeinfo:home')
        
    except Exception as e:
        logger.error(f"ERROR eliminando cuenta usuario {user_id}: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"TRACEBACK: {traceback.format_exc()}")
        
        # Mensaje de error
        messages.error(request, f"Error al eliminar cuenta. Por favor contacta al administrador.")
        try:
            return redirect('ProfileService:profile', user_id=user_id)
        except:
            return redirect('Homeinfo:home')
