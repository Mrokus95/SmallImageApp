from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from knox.auth import AuthToken
from rest_framework import status
from rest_framework.test import APIClient

from ..models import UserImage
from ..serializers import UserSerializer
from .factories import AccountTypeFactory, CustomUserFactory, UserImageFactory

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
        assert (
            "A user with this email address already exists." in response.data["detail"]
        )

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
        assert "A user with this username already exists." in response.data["detail"]


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
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials." in response.data["detail"]  #
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
        assert (
            "New password must be at least 7 characters long."
            in response.data["detail"]
        )
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


class TestLoginView:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory()
        user.set_password("Strongpassword")
        user.save()
        _, token_instance = AuthToken.objects.create(user)
        return (user, token_instance)

    def test_user_login(self, user):
        user, _ = user

        url = reverse("login")
        data = {
            "username": user.username,
            "password": "Strongpassword",
        }

        client = APIClient()
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_user_login_invalid_credentials(self, user):
        user, _ = user

        url = reverse("login")
        data = {
            "username": user.username,
            "password": "wrongpassword",
        }

        client = APIClient()
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestManageUserView:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory()
        user.set_password("Strongpassword")
        user.save()
        _, token_instance = AuthToken.objects.create(user)
        return (user, token_instance)

    def test_get_authenticated_user(self, user):
        user, token_instance = user
        url = reverse("profile")

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token_instance)
        response = client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username

    def test_get_unauthenticated_user(self, user):
        url = reverse("profile")
        user, _ = user
        client = APIClient()
        response = client.get(url, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserImagesViewSet:
    @pytest.fixture
    def user(self):
        user = CustomUserFactory()
        user.set_password("Strongpassword")
        user.save()
        _, token_instance = AuthToken.objects.create(user)
        UserImageFactory(author=user)
        return (user, token_instance)

    @pytest.fixture
    def image(self, user):
        return UserImageFactory.create_image("test_image.jpg", 300)

    def test_get_user_images(self, user):
        user, token = user
        url = reverse("userimage-list")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_create_user_image(self, user, image):
        user, token = user
        url = reverse("userimage-list")

        data = {
            "name": "test_picture",
            "image": image,
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_user_image(self, user):
        user, token = user
        image_id = user.client_photos.first().id
        url = reverse("userimage-detail", args=[image_id])
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.delete(url, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not user.client_photos.exists()

    def test_delete_non_existent_user_image(self, user):
        user, token = user
        image_id = UserImage.objects.count() + 1000
        url = reverse("userimage-detail", args=[image_id])
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.delete(url, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_image_without_permission(self, user):
        user, token = user
        other_image = UserImageFactory()
        url = reverse("userimage-detail", args=[other_image.id])
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.delete(url, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_send_not_an_image(self, user, image):
        user, _ = user
        url = reverse("userimage-list")

        data = {
            "name": "test_picture",
            "image": image,
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + "invalid_token")
        response = client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_send_not_an_image(self, user):
        user, token = user
        url = reverse("userimage-list")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        not_an_image_file = SimpleUploadedFile("not_an_image.txt", b"Test file content")

        data = {
            "name": "test_picture",
            "image": not_an_image_file,
        }

        response = client.post(url, data, format="multipart")
        assert (
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
            in response.data["image"]
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_image_in_wrong_format(self, user):
        user, token = user
        url = reverse("userimage-list")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        wrong_format_image = UserImageFactory.create_image(
            "wrong_format.gif", 300, content_type="image/gif", format="GIF"
        )

        data = {
            "name": "test_picture",
            "image": wrong_format_image,
        }

        response = client.post(url, data, format="multipart")
        assert (
            "gif - Invalid file extension. Only ['jpg', 'jpeg', 'png'] files are accepted."
            in response.data["image"]
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_image_in_wrong_format_but_valid_name(self, user):
        user, token = user
        url = reverse("userimage-list")
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        wrong_format_image = UserImageFactory.create_image(
            "wrong_format.jpg", 300, content_type="image/gif", format="GIF"
        )

        data = {
            "name": "test_picture",
            "image": wrong_format_image,
        }

        response = client.post(url, data, format="multipart")
        assert (
            "Cannot open the file as an image. Please check if the uploaded file is a valid image."
            in response.data["image"]
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestGenerateTemporaryLinkView:
    @pytest.fixture
    def user(self, mocker):
        account_type = AccountTypeFactory(time_limited_link=True)
        user = CustomUserFactory(account_type=account_type)
        user.set_password("Strongpassword")
        user.save()
        _, token_instance = AuthToken.objects.create(user)
        mocker.patch(
            "knox.models.AuthToken.objects.create", return_value=token_instance
        )
        UserImageFactory(author=user)
        return user, token_instance

    def test_generate_temporary_link_for_user_image(self, mocker, user):
        user, token = user
        user_image = UserImageFactory(author=user)
        mock_s3 = mocker.patch("boto3.client")
        mock_generate_presigned_url = MagicMock()
        mock_s3.return_value.generate_presigned_url = mock_generate_presigned_url
        mock_generate_presigned_url.return_value = "temporary_url"

        url = reverse(
            "generate-temporary-link",
            args=("image", user_image.id),
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(url, format="json")
        assert response.status_code == status.HTTP_200_OK

        mock_generate_presigned_url.assert_called_with(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": user_image.image.name,
            },
            ExpiresIn=3600,
        )

    def test_generate_temporary_link_for_user_thumbnail(self, mocker, user):
        user, token = user
        user_image = UserImageFactory(author=user)
        mock_s3 = mocker.patch("boto3.client")
        mock_generate_presigned_url = MagicMock()
        mock_s3.return_value.generate_presigned_url = mock_generate_presigned_url
        mock_generate_presigned_url.return_value = "temporary_url"

        url = reverse(
            "generate-temporary-link",
            args=("thumbnail", user_image.thumbnails.first().id),
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(url, format="json")
        assert response.status_code == status.HTTP_200_OK

        mock_generate_presigned_url.assert_called_with(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": user_image.thumbnails.first().image.name,
            },
            ExpiresIn=3600,
        )

    def test_generate_temporary_link_invalid_file_type(self, user):
        user, token = user
        url = reverse("generate-temporary-link", args=("invalid_type", 1))
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(url, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_generate_temporary_link_invalid_expiration_time(self, user):
        user, token = user
        url = reverse("generate-temporary-link", args=("user_image", 1))
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = client.get(url, {"expiration_time_seconds": 299}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.get(url, {"expiration_time_seconds": 30001}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
