from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os
import requests
import json

def profile_photo_upload_path(instance, filename):
    """
    Función para generar la ruta de subida de las fotos de perfil
    Organiza por ID de usuario y mantiene la extensión original
    """
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    # Generar nombre único
    filename = f"profile_{instance.usuario.id}_{uuid.uuid4().hex}.{ext}"
    # Retornar la ruta completa
    return f"profiles/{instance.usuario.id}/{filename}"

class ConfiguracionUsuario(models.Model):
    """
    Modelo de Configuración de Usuario basado en el ER de PawsToHome
    Representa la entidad CONFIGURACION_USUARIO del diagrama
    Relación 1:1 con Usuario
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='configuracion',
        verbose_name="Usuario"
    )
    
    # Foto de perfil
    foto_perfil = models.ImageField(
        upload_to=profile_photo_upload_path,
        blank=True,
        null=True,
        verbose_name="Foto de Perfil",
        help_text="Foto de perfil del usuario (formatos admitidos: JPG, PNG, GIF)"
    )
    
    # Dirección del usuario
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Dirección",
        help_text="Dirección completa del usuario"
    )
    
    # Configuraciones de notificaciones
    notificaciones_email = models.BooleanField(
        default=True,
        verbose_name="Notificaciones por Email"
    )
    
    notificaciones_push = models.BooleanField(
        default=True,
        verbose_name="Notificaciones Push"
    )
    
    # Radio de notificaciones en kilómetros
    radio_notificaciones = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(50.0)],
        verbose_name="Radio de Notificaciones (km)",
        help_text="Radio en kilómetros para recibir notificaciones de reportes cercanos"
    )
    
    # Ubicación preferida del usuario (coordenadas separadas)
    latitud_preferida = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name="Latitud Preferida",
        help_text="Latitud de la ubicación base para notificaciones (-90 a 90)"
    )
    
    longitud_preferida = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name="Longitud Preferida", 
        help_text="Longitud de la ubicación base para notificaciones (-180 a 180)"
    )
    
    # Tipos de reportes a notificar
    notificar_perdidos = models.BooleanField(
        default=True,
        verbose_name="Notificar Mascotas Perdidas"
    )
    
    notificar_encontrados = models.BooleanField(
        default=True,
        verbose_name="Notificar Mascotas Encontradas"
    )
    
    class Meta:
        verbose_name = "Configuración de Usuario"
        verbose_name_plural = "Configuraciones de Usuario"
        db_table = "configuracion_usuario"
    
    def __str__(self):
        return f"Configuración de {self.usuario.username}"
    
    def tiene_ubicacion_preferida(self):
        """Verifica si el usuario tiene ubicación preferida configurada"""
        return self.latitud_preferida is not None and self.longitud_preferida is not None
    
    def set_ubicacion_preferida(self, latitud, longitud):
        """Establece la ubicación preferida del usuario"""
        if latitud is not None and longitud is not None:
            # Validar rangos
            if -90 <= latitud <= 90 and -180 <= longitud <= 180:
                self.latitud_preferida = latitud
                self.longitud_preferida = longitud
            else:
                raise ValueError("Coordenadas fuera de rango válido")
        else:
            self.latitud_preferida = None
            self.longitud_preferida = None

    def get_profile_photo_url(self):
        """Retorna la URL de la foto de perfil o None si no tiene"""
        if self.foto_perfil:
            return self.foto_perfil.url
        return None
    
    def has_profile_photo(self):
        """Verifica si el usuario tiene foto de perfil"""
        return bool(self.foto_perfil)
    
    def geocodificar_coordenadas(self):
        """
        Convierte las coordenadas en dirección usando OpenStreetMap Nominatim API (Reverse Geocoding)
        Retorna un diccionario con la dirección o None si falla
        """
        if not self.tiene_ubicacion_preferida():
            return None
        
        try:
            # Usar Nominatim API para geocodificación inversa
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': self.latitud_preferida,
                'lon': self.longitud_preferida,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'es',  # Preferir respuestas en español
                'countrycodes': 'mx'  # Limitar a México
            }
            
            headers = {
                'User-Agent': 'PawsToHome/1.0 (reverse geocoding for pet location service)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'display_name' in data:
                    # Construir dirección más legible
                    address = data.get('address', {})
                    
                    # Componentes de la dirección
                    numero = address.get('house_number', '')
                    calle = address.get('road', '')
                    colonia = address.get('neighbourhood') or address.get('suburb', '')
                    ciudad = address.get('city') or address.get('town') or address.get('village', '')
                    estado = address.get('state', '')
                    
                    # Construir dirección formateada
                    partes_direccion = []
                    
                    if calle:
                        if numero:
                            partes_direccion.append(f"{calle} {numero}")
                        else:
                            partes_direccion.append(calle)
                    
                    if colonia:
                        partes_direccion.append(f"Colonia {colonia}")
                    
                    if ciudad:
                        partes_direccion.append(ciudad)
                    
                    if estado:
                        partes_direccion.append(estado)
                    
                    direccion_formateada = ", ".join(partes_direccion)
                    
                    # Si no se pudo formatear bien, usar display_name completo
                    if not direccion_formateada.strip():
                        direccion_formateada = data['display_name']
                    
                    return {
                        'direccion': direccion_formateada,
                        'direccion_completa': data['display_name'],
                        'componentes': address,
                        'success': True
                    }
            
            return None
            
        except Exception as e:
            print(f"Error en geocodificación inversa: {e}")
            return None
    
    def actualizar_direccion_desde_coordenadas(self):
        """
        Actualiza la dirección basándose en las coordenadas preferidas
        """
        if self.tiene_ubicacion_preferida():
            resultado = self.geocodificar_coordenadas()
            if resultado and resultado.get('success'):
                self.direccion = resultado['direccion']
                return True
        return False
    
    def tiene_direccion(self):
        """Verifica si el usuario tiene dirección configurada"""
        return bool(self.direccion)
