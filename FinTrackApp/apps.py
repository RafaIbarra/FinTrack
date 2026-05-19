from django.apps import AppConfig

class FintrackappConfig(AppConfig):
    name = 'FinTrackApp'

    
    # def ready(self):
    #     # Inicializa R2 Storage y crea buckets automáticamente
        
    #     from FinTrackApp.Utils.r2_storage import r2_storage