from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import ConfiguracionUsuario

# Create your views here.

def getUserProfileData(request):
    pass
User = get_user_model()

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
            
            # Actualizar ubicación preferida
            latitud = request.POST.get('latitud_preferida')
            longitud = request.POST.get('longitud_preferida')
            
            if latitud and longitud:
                try:
                    configuracion.set_ubicacion_preferida(float(latitud), float(longitud))
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
