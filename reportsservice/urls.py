from django.urls import path
from . import views

app_name = "reportsservice"
urlpatterns = [
    path('', views.lista_reportes, name='reportes'),
    path('crear/', views.crear_reporte, name='crear_reporte'),
    path('<uuid:id>/', views.detalle_reporte, name='detalle_reporte'),
    path('<uuid:id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    
    # URLs para administración de Cloudflare R2
    path('admin/r2/estado/', views.estado_cloudflare_r2, name='estado_r2'),
    path('admin/foto/<int:foto_id>/resubir/', views.resubir_imagen_r2, name='resubir_imagen_r2'),
]