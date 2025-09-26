from django.apps import AppConfig

class ReportsserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportsservice'
    verbose_name = 'Servicio de Reportes'
    
    def ready(self):
        import reportsservice.signals
