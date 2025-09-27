from django.apps import AppConfig

class ProfileserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ProfileService'
    verbose_name = 'Servicio de Perfil'
    
    def ready(self):
        import ProfileService.signals
