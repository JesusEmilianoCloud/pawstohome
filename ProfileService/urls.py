from django.urls import path
from . import views

app_name = "ProfileService"

urlpatterns = [
    path("<int:user_id>/", views.getUserProfileData, name="profile"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("geocodificar-direccion/", views.geocodificar_direccion_ajax, name="geocodificar_direccion"),
    # Otras rutas de la aplicación
]
