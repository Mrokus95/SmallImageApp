from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import (ChangePasswordView, CreateUserView,
                       GenerateTemporaryLinkView, LoginView, LogoutAllView,
                       LogoutView, ManageUserView, UserImagesViewSet)

router = DefaultRouter()
router.register(r"user-images", UserImagesViewSet, basename="userimage")

urlpatterns = [
    path(
        "user-images/<int:pk>/",
        UserImagesViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name="userimage-detail",
    ),
    path(
        "generate-temporary-link/<str:file_type>/<int:file_id>/",
        GenerateTemporaryLinkView.as_view(),
        name="generate-temporary-link",
    ),
    path("create_user/", CreateUserView.as_view(), name="create_user"),
    path("user_profile/", ManageUserView.as_view(), name="profile"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logoutall/", LogoutAllView.as_view(), name="logoutall"),
    path("", include(router.urls)),
]
urlpatterns += router.urls