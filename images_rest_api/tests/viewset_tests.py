import pytest
from django.contrib.auth import get_user_model
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
        user = db.objects.get(username= "testuser")
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

    def test_create_user_view_duplicate_username(sel, user):
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
