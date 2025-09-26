"""
URL configuration for pawtohome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # Ruta raíz - redirige al home
    path('', include('Homeinfo.urls')),
    
    # Aplicaciones
    path('accounts/', include('loginservice.urls')),
    path('reports/', include('reportsservice.urls')),
    path('maps/', include('Mapservice.urls')),
    path('profile/', include('ProfileService.urls')),
    path('home/', include('Homeinfo.urls')),  # Ruta alternativa al servicio de home
    
    # Admin
    path('admin/', admin.site.urls),

    # Ruta principal
]

# Servir archivos estáticos y media durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
