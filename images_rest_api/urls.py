from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    UserImagesViewSet,
    GenerateTemporaryLinkView,
    CreateUserView,
    LoginView,
    ManageUserView,
    ChangePasswordView,
)

from knox import views as knox_views


router = DefaultRouter()
router.register(r"user-images", UserImagesViewSet, basename="userimage")

urlpatterns = [
    path(
        "generate-temporary-link/<str:file_type>/<int:file_id>/",
        GenerateTemporaryLinkView.as_view(),
        name="generate-temporary-link",
    ),
    path("create_user/", CreateUserView.as_view(), name="create_user"),
    path("user_profile/", ManageUserView.as_view(), name="profile"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="logoutall"),
    path("", include(router.urls)),
]
