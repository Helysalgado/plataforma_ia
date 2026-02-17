from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.resources'
    verbose_name = 'Resources'
    
    def ready(self):
        """Import signals when app is ready"""
        # import apps.resources.signals  # Uncomment when signals are created
        pass
