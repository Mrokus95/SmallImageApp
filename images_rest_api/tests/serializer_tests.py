import pytest
from django.contrib.auth.hashers import check_password
from django.test import RequestFactory
from knox.auth import AuthToken
from PIL import Image
from rest_framework.exceptions import ValidationError

from ..serializers import (
    AddImageSerializer,
    AuthSerializer,
    BasicUserImageSerializer,
    ChangePasswordSerializer,
    NotBasicUserImageSerializer,
    ThumbnailSerializer,
    UserSerializer,
)
from .factories import AccountTypeFactory, CustomUserFactory, UserImageFactory

pytestmark = pytest.mark.django_db


class TestUserSerializer:
    def test_user_serializer_fields(self):
        user = CustomUserFactory()

        serializer = UserSerializer(instance=user)

        assert "username" in serializer.data
        assert "email" in serializer.data
        assert "account_type" in serializer.data

    def test_user_serializer_data(self):
        user = CustomUserFactory()

        serializer = UserSerializer(instance=user)

        assert serializer.data["username"] == user.username
        assert serializer.data["email"] == user.email
        assert serializer.data["account_type"] == user.account_type.id

    def test_user_serializer_validation(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "account_type": "3",
        }

        serializer = UserSerializer(data=data)

        assert serializer.is_valid()

    def test_user_serializer_validation(self):
        data = {
            "username": "testuser",
            "email2": "test@example.com",
            "account_type": "3",
        }

        serializer = UserSerializer(data=data)

        assert serializer.is_valid() is False

    def test_user_serializer_save(self):
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

    def test_user_serializer_missing_fields(self):
        account_type = AccountTypeFactory().id

        data = {
            "email": "test@example.com",
            "password": "StrongPassword",
            "account_type": account_type,
        }
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert "This field is required." in serializer.errors["username"]

        data = {
            "username": "testuser",
            "password": "StrongPassword",
            "account_type": account_type,
        }
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert "This field is required." in serializer.errors["email"]

        data = {
            "username": "testuser",
            "password": "StrongPassword",
        }
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert "This field is required." in serializer.errors["email"]
        assert "This field is required." in serializer.errors["account_type"]

        data = {}
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert "This field is required." in serializer.errors["username"]
        assert "This field is required." in serializer.errors["password"]
        assert "This field is required." in serializer.errors["email"]
        assert "This field is required." in serializer.errors["account_type"]

    def test_user_serializer_duplicate_email(self):
        account_type = AccountTypeFactory().id
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword",
            "account_type": account_type,
        }

        serializer = UserSerializer(data=user_data)
        assert serializer.is_valid()

        serializer.save()
        user_data["username"] = "testuser2"
        serializer = UserSerializer(data=user_data)
        assert not serializer.is_valid()

    def test_user_serializer_duplicate_username(self):
        account_type = AccountTypeFactory().id
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword",
            "account_type": account_type,
        }
        serializer = UserSerializer(data=user_data)
        assert serializer.is_valid()

        serializer.save()
        user_data["email"] = "new@example.com"
        serializer = UserSerializer(data=user_data)
        assert not serializer.is_valid()


class TestAuthSerializer:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory()
        user.set_password("ValidPassword")
        user.save()
        return user

    @pytest.fixture
    def auth_serializer(self):
        return AuthSerializer()

    def test_auth_serializer_valid_user(self, user, auth_serializer):
        data = {"username": user.username, "password": "ValidPassword"}
        result = auth_serializer.validate(data)
        assert result == data

    def test_auth_serializer_invalid_user(self, user, auth_serializer):
        data = {"username": "username2", "password": "ValidPassword"}
        auth_serializer = AuthSerializer(data=data)

        assert not auth_serializer.is_valid()
        assert (
            "Unable to authenticate with provided credentials."
            in auth_serializer.errors["authentication"]
        )

    def test_auth_serializer_no_user(self):
        data = {"username": "nonexistentuser", "password": "AnyPassword"}
        auth_serializer = AuthSerializer(data=data)
        assert not auth_serializer.is_valid()
        assert (
            "Unable to authenticate with provided credentials."
            in auth_serializer.errors["authentication"]
        )


class TestChangePasswordSerializer:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory(username="Thomas Spencer")
        user.set_password("Strongpassword")
        user.save()
        return user

    @pytest.fixture
    def change_password_serializer(self):
        return ChangePasswordSerializer()

    def test_change_password_serializer_correct_update(self, user):
        auth_token, token_instance = AuthToken.objects.create(user)

        updated_data = {
            "username": "Thomas Spencer",
            "old_password": "Strongpassword",
            "new_password": "newStrongPassword",
        }
        auth_token = str(auth_token)
        token = auth_token.split()[0]

        serializer = ChangePasswordSerializer(
            instance=user, data=updated_data, context={"token": token}
        )

        assert serializer.is_valid()

    def test_change_password_serializer_incorrect_old_password(self, user):
        auth_token, token_instance = AuthToken.objects.create(user)

        updated_data = {
            "username": user.username,
            "old_password": "Strongpassword2",
            "new_password": "newStrongPassword",
        }
        auth_token = str(auth_token)
        token = auth_token.split()[0]

        serializer = ChangePasswordSerializer(
            instance=user, data=updated_data, context={"token": token}
        )

        assert not serializer.is_valid()
        assert (
            "Unable to authenticate with provided credentials."
            in serializer.errors["old_password"]
        )

    def test_change_password_serializer_new_password_too_short(self, user):
        auth_token, token_instance = AuthToken.objects.create(user)

        updated_data = {
            "username": "Thomas Spencer",
            "old_password": "Strongpassword",
            "new_password": "new",
        }
        auth_token = str(auth_token)
        token = auth_token.split()[0]

        serializer = ChangePasswordSerializer(
            instance=user, data=updated_data, context={"token": token}
        )

        assert not serializer.is_valid()
        assert (
            "New password must be at least 7 characters long."
            in serializer.errors["new_password"]
        )

    def test_change_password_serializer_check_new_password(self, user):
        auth_token, token_instance = AuthToken.objects.create(user)

        updated_data = {
            "username": "Thomas Spencer",
            "old_password": "Strongpassword",
            "new_password": "newStrongPassword",
        }
        auth_token = str(auth_token)
        token = auth_token.split()[0]

        serializer = ChangePasswordSerializer(
            instance=user, data=updated_data, context={"token": token}
        )

        assert serializer.is_valid()

        old_password = user.password

        serializer.save()

        user.refresh_from_db()

        assert not check_password("Strongpassword", user.password)
        assert check_password("newStrongPassword", user.password)


class TestAddImageSerializer:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory(username="Thomas Spencer")
        user.set_password("Strongpassword")
        user.save()
        return user

    def test_valid_image(self):
        image_file = UserImageFactory.create_image("example.jpg", 200, 
        "image/jpeg")
        data = {"id": 1, "name": "example.jpg", "image": image_file}
        serializer = AddImageSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_image(self, user):
        token, token_instance = AuthToken.objects.create(user)

        data = {"id": 1, "name": "example.jpg"}
        serializer = AddImageSerializer(data=data, context={"token": token})

        assert not serializer.is_valid()
        assert "No file was submitted." in serializer.errors["image"]

    def test_invalid_extension(self):
        image_file = UserImageFactory.create_image("example.gif", 200, 
        "image/gif")
        data = {"id": 1, "name": "example.gif", "image": image_file}
        serializer = AddImageSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            "gif - Invalid file extension. Only ['jpg', 'jpeg', 'png'] files are accepted."
            in serializer.errors["image"]
        )

    def test_invalid_format(self):
        image_file = UserImageFactory.create_image(
            "example.jpg", 200, "image/gif", format="gif"
        )
        data = {"id": 1, "name": "example.jpg", "image": image_file}
        serializer = AddImageSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            "Cannot open the file as an image. Please check if the uploaded file is a valid image."
            in serializer.errors["image"]
        )

    def test_invalid_image(self):
        image_file = b"This is not a valid image file."
        data = {"id": 1, "name": "example.jpg", "image": image_file}
        serializer = AddImageSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            "The submitted data was not a file. Check the encoding type on the form."
            in serializer.errors["image"]
        )

    def test_long_name(self):
        long_name = "a" * 165
        image_file = UserImageFactory.create_image("example.jpg", 200, 
        "image/jpeg")
        data = {"id": 1, "name": long_name, "image": image_file}
        serializer = AddImageSerializer(data=data)

        assert not serializer.is_valid()
        assert (
            "Ensure this field has no more than 164 characters."
            in serializer.errors["name"]
        )


class TestThumbnailSerializer:
    def test_invalid_size(self):
        image_file = UserImageFactory.create_image("example.jpg", 200, \
            "image/jpeg")
        invalid_data = {"id": 1, "size": -100, "image": image_file}
        serializer = ThumbnailSerializer(data=invalid_data)

        assert not serializer.is_valid()
        assert (
            "Ensure this value is greater than or equal to 1."
            in serializer.errors["size"]
        )

    def test_missing_image(self):
        invalid_data = {"id": 1, "size": 100}
        serializer = ThumbnailSerializer(data=invalid_data)

        assert not serializer.is_valid()
        assert "No file was submitted." in serializer.errors["image"]


class TestBasicUserImageSerializer:
    def test_invalid_name(self):
        invalid_data = {"id": 1, "name": "a" * 165, "thumbnails": []}
        serializer = BasicUserImageSerializer(data=invalid_data)

        assert not serializer.is_valid()
        assert (
            "Ensure this field has no more than 164 characters."
            in serializer.errors["name"]
        )

    def test_empty_thumbnails(self):
        data = {"id": 1, "name": "test.jpg", "thumbnails": []}
        serializer = BasicUserImageSerializer(data=data)

        assert serializer.is_valid()


class TestNotBasicUserImageSerializer:
    def test_invalid_name(self):
        invalid_data = {
            "id": 1,
            "name": "a" * 165,
            "image": "test.jpg",
            "thumbnails": [],
        }
        serializer = NotBasicUserImageSerializer(data=invalid_data)

        assert not serializer.is_valid()
        assert (
            "Ensure this field has no more than 164 characters."
            in serializer.errors["name"]
        )

    def test_missing_image(self):
        invalid_data = {"id": 1, "name": "test.jpg", "thumbnails": []}
        serializer = NotBasicUserImageSerializer(data=invalid_data)

        assert not serializer.is_valid()
        assert "No file was submitted." in serializer.errors["image"]
