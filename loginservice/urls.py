from django.urls import path
from . import views

app_name = "loginservice"

urlpatterns = [
        path('login-register/', views.auth_view, name='login-register'),  # Compatibilidad
        path('home/', views.home, name='home'),
]
