from django.urls.conf import include
from django.urls import path


urlpatterns = [
    path('images/', include('images_rest_api.urls'))
]