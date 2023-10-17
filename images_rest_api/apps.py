from django.apps import AppConfig


class ImagesRestApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'images_rest_api'
    
    def ready(self):
        import images_rest_api.signals 
        import images_rest_api.scheme
