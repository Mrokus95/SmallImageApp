from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, UserImagesViewSet, GenerateTemporaryLinkView

router = DefaultRouter()
router.register(r"user-images", UserImagesViewSet, basename="userimage")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path('generate-temporary-link/<str:file_type>/<int:file_id>/', GenerateTemporaryLinkView.as_view(), name='generate-temporary-link'),
    path("", include(router.urls)),
]
