from django.urls import path
from . import views

app_name = "reportsservice"
urlpatterns = [
    path('', views.lista_reportes, name='reportes'),
    path('crear/', views.crear_reporte, name='crear_reporte'),
    path('<uuid:id>/', views.detalle_reporte, name='detalle_reporte'),
    path('<uuid:id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    
    # Otras rutas de la aplicación
]