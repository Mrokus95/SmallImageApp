import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from knox.auth import AuthToken
from rest_framework import status
from rest_framework.test import APIClient

from ..serializers import UserSerializer
from .factories import CustomUserFactory

db = get_user_model()

pytestmark = pytest.mark.django_db


class TestCreateUserView:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory(is_staff=True, is_superuser=True)
        user.set_password("Strongpassword")
        user.save()
        _, token_instance = AuthToken.objects.create(user)
        return (user, token_instance)

    @pytest.fixture
    def non_admin_user(self):
        non_admin_user = CustomUserFactory()
        non_admin_user.set_password("Strongpassword")
        non_admin_user.save()
        _, token_instance = AuthToken.objects.create(non_admin_user)
        return (non_admin_user, token_instance)
    

    def test_create_user_view_user_without_permissions(self, non_admin_user):
        token_instance = non_admin_user[1]
        user = non_admin_user[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)
        url = reverse("create_user")

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "account_type": user.account_type.id,
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert db.objects.count() == 1
        with pytest.raises(ObjectDoesNotExist):
            user = db.objects.get(username="testuser")


    def test_create_user_view_success(self, user):
        token_instance = user[1]
        user = user[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)
        url = reverse("create_user")

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "account_type": user.account_type.id,
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2

        assert response.data.get("user") == {
            "username": "testuser",
            "email": "test@example.com",
            "account_type": user.account_type.id,
        }

        assert db.objects.count() == 2
        user = db.objects.get(username="testuser")
        assert user.username == data["username"]
        assert user.email == data["email"]
        assert user.account_type.id == data["account_type"]

    def test_create_user_view_invalid_data(self, user):
        token_instance = user[1]
        user = user[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)
        url = reverse("create_user")

        data = {
            "username": "",
            "email": "test@example.com",
            "password": "Short",
            "account_type": "standard",
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert db.objects.count() == 1

    def test_create_user_view_duplicate_email(self, user):
        token_instance = user[1]
        user = user[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)
        url = reverse("create_user")

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword",
            "account_type": user.account_type.id,
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert db.objects.count() == 2

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "custom user with this email already exists." in response.data["email"]

    def test_create_user_view_duplicate_username(self, user):
        token_instance = user[1]
        user = user[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)
        url = reverse("create_user")

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword",
            "account_type": user.account_type.id,
        }

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert db.objects.count() == 2

        data["email"] = "new@example.com"
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "custom user with this username already exists."
            in response.data["username"]
        )


class TestChangePasswordView:
    
    @pytest.fixture
    def user(self):
        user = CustomUserFactory()
        user.set_password("Strongpassword")
        user.save()
        _, token_instance = AuthToken.objects.create(user)
        return (user, token_instance)

    def test_change_password(self, user):

        user, token_instance = user

        url = reverse("change_password")
        data = {
            "username": user.username,
            "old_password": "Strongpassword",
            "new_password": "newpassword123",
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)

        response = client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password updated successfully"
        user.refresh_from_db()
        assert user.check_password("newpassword123")

    def test_change_password_invalid_old_password(self, user):
        user, token_instance = user

        url = reverse("change_password")
        data = {
            "username": user.username,
            "old_password": "Strongpassword2",
            "new_password": "newpassword123",
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)

        initial_password = user.password

        response = client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert "Unable to authenticate with provided credentials." in response.data["old_password"] # 
        user.refresh_from_db()
        assert user.password == initial_password

    def test_change_password_invalid_new_password(self, user):
        user, token_instance = user

        url = reverse("change_password")
        data = {
            "username": user.username,
            "old_password": "Strongpassword",
            "new_password": "short",
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)

        initial_password = user.password

        response = client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "New password must be at least 7 characters long." in response.data["new_password"]
        user.refresh_from_db()
        assert user.password == initial_password

    def test_change_password_unauthorized_user(self, user):

        user, token_instance = user

        url = reverse("change_password")
        data = {
            "username": user.username,
            "old_password": "Strongpassword",
            "new_password": "newpassword123",
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + "bad_token")
        initial_password = user.password
        response = client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Invalid token."
        user.refresh_from_db()
        assert user.password == initial_password
