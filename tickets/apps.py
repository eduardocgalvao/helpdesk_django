from django.apps import AppConfig


class TicketsConfig(AppConfig):
    name = 'tickets'


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'
    
    def ready(self):
        import tickets.signals
