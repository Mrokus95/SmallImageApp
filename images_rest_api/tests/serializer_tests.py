import pytest
from django.core.exceptions import ValidationError
from knox.auth import AuthToken

from ..serializers import ChangePasswordSerializer, UserSerializer
from .factories import AccountTypeFactory, CustomUserFactory


@pytest.mark.django_db
def test_user_serializer_fields():
    user = CustomUserFactory()

    serializer = UserSerializer(instance=user)

    assert "username" in serializer.data
    assert "email" in serializer.data
    assert "account_type" in serializer.data


@pytest.mark.django_db
def test_user_serializer_data():
    user = CustomUserFactory()

    serializer = UserSerializer(instance=user)

    assert serializer.data["username"] == user.username
    assert serializer.data["email"] == user.email
    assert serializer.data["account_type"] == user.account_type.id


@pytest.mark.django_db
def test_user_serializer_validation():
    data = {"username": "testuser", "email": "test@example.com", "account_type": "3"}

    serializer = UserSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_user_serializer_validation():
    data = {"username": "testuser", "email2": "test@example.com", "account_type": "3"}

    serializer = UserSerializer(data=data)

    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_user_serializer_save():
    account_type = AccountTypeFactory().id

    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongPassword",
        "account_type": account_type,
    }

    serializer = UserSerializer(data=data)

    assert serializer.is_valid()
    user = serializer.save()

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.account_type.id == account_type


@pytest.mark.django_db
def test_user_serializer_missing_fields():
    account_type = AccountTypeFactory().id

    data = {
        "email": "test@example.com",
        "password": "StrongPassword",
        "account_type": account_type,
    }
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()

    data = {
        "username": "testuser",
        "password": "StrongPassword",
        "account_type": account_type,
    }
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()

    data = {
        "username": "testuser",
        "password": "StrongPassword",
    }
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()

    data = {}
    serializer = UserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_user_serializer_correct_update():
    user = CustomUserFactory(username="Thomas Spencer", password="Strongpassword")

    auth_token, token_instance = AuthToken.objects.create(user)

    updated_data = {
        "username": "Thomas Spencer",
        "old_password": "Strongpassword",
        "new_password": "newStrongPassword",
    }
    auth_token = str(auth_token)
    auth_token = auth_token.split()[0]
    print(auth_token)
    print(token_instance)

    serializer = ChangePasswordSerializer(instance=user, data=updated_data)

    assert serializer.is_valid()
