from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, UserImagesViewSet

router = DefaultRouter()
router.register(r"user-images", UserImagesViewSet, basename="userimage")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path(
        "users/{pk}/",
        UserViewSet.as_view({"get": "list", "get": "retrieve"}),
        name="users",
    ),
    path(
        "images/{pk}/",
        UserImagesViewSet.as_view(
            {"get": "list", "post": "create", "get": "retrieve", 
             "delete": "destroy"}
        ),
        name="user-images",
    ),
    path("", include(router.urls)),
]
