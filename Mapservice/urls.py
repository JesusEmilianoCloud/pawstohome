from django.urls import path
from . import views

app_name = "Mapservice"

urlpatterns = [
    path('', views.mapa_interactivo, name='mapa_interactivo'),
    path('api/reportes/', views.api_reportes_mapa, name='api_reportes_mapa'),
    # Otras rutas de la aplicación
]