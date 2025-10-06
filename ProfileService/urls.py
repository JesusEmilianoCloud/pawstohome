from django.urls import path
from . import views

app_name = "ProfileService"

urlpatterns = [
    path("<int:user_id>/", views.getUserProfileData, name="profile"),
    path("<int:user_id>/reportes/", views.user_reports_view, name="user_reports"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("delete-account/", views.delete_account_view, name="delete_account"),
    path("obtener-direccion/", views.obtener_direccion_desde_coordenadas_ajax, name="obtener_direccion"),
    # Otras rutas de la aplicación
]
