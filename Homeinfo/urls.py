from django.urls import path
from . import views

app_name = "Homeinfo"

urlpatterns = [
    path('', views.home, name='home'),
    path('informacion/', views.informacion, name='informacion'),
]