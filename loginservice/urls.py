from django.urls import path
from django.urls import include
from . import views

app_name = "loginservice"

urlpatterns = [
    #apps
    path('Homeinfo/', include('Homeinfo.urls')),
    path('', views.auth_view, name='auth'),
    path('login-register/', views.auth_view, name='login-register'),  # Compatibilidad

]
