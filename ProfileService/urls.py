from django.urls import path
from . import views

app_name = "ProfileService"

urlpatterns = [
        path("<int:user_id>", views.getUserProfileData, name="profile"),    
    # Otras rutas de la aplicación
]
