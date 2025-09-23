from django.urls import path
from . import views

app_name = "loginservice"

urlpatterns = [
        path('auth/', views.auth_view, name='auth'),  # Nueva vista combinada
        path('register/', views.register_view, name='register'),  # Compatibilidad
        path('login/', views.login_view, name='login'),  # Compatibilidad
        path('home/', views.home, name='home'),
]
