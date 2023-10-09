import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from faker import Faker

from ..models import Thumbnail, UserImage, AccountType
from .factories import (
    AccountTypeFactory,
    CustomUserFactory,
    ThumbnailSizeFactory,
    UserImageFactory,
)

fake = Faker()


@pytest.mark.django_db
class TestCustomUser:
    def setup_method(self):
        self.account_type = AccountTypeFactory()
        self.user = CustomUserFactory()

    def test_new_superuser(self):
        db = get_user_model()
        superuser = db.objects.create_superuser(
            "testuser", "testuser@email.com", "strongpassword", self.account_type.id
        )
        assert superuser.username == "testuser"
        assert superuser.email == "testuser@email.com"
        assert superuser.check_password("strongpassword")
        assert superuser.account_type == self.account_type
        assert superuser.is_superuser
        assert superuser.is_staff
        assert superuser.is_active
        assert str(superuser) == "testuser"

        with pytest.raises(ValueError):
            db.objects.create_superuser(
                "testuser",
                "testuser@email.com",
                "strongpassword",
                self.account_type,
                is_superuser=False,
            )

        with pytest.raises(ValueError):
            db.objects.create_superuser(
                "testuser",
                "testuser@email.com",
                "strongpassword",
                self.account_type,
                is_staff=False,
            )

        with pytest.raises(ValueError):
            db.objects.create_superuser(
                "testuser",
                "testuser@email.com",
                "strongpassword",
                self.account_type,
                is_active=False,
            )

    def test_new_user(self):
        db = get_user_model()
        user = db.objects.create_user(
            "testuser", "testuser@email.com", "strongpassword", self.account_type.id
        )
        assert user.username == "testuser"
        assert user.email == "testuser@email.com"
        assert user.check_password("strongpassword")
        assert user.account_type == self.account_type
        assert not user.is_superuser
        assert not user.is_staff
        assert user.is_active
        assert str(user) == "testuser"

    def test_change_password(self):
        new_password = fake.password()
        self.user.set_password(new_password)
        self.user.save()
        assert self.user.check_password(new_password)

    def test_change_email(self):
        new_email = fake.email()
        self.user.email = new_email
        self.user.save()
        assert self.user.email == new_email

    def test_delete_user(self):
        user_id = self.user.id
        self.user.delete()
        with pytest.raises(get_user_model().DoesNotExist):
            get_user_model().objects.get(id=user_id)


@pytest.mark.django_db
class TestThumbnailSizeModel:
    def setup_method(self):
        self.thumbnail_size = ThumbnailSizeFactory(size=100)

    def test_str_method(self):
        assert str(self.thumbnail_size) == "100 px"

    def test_clean_method_with_valid_size(self):
        self.thumbnail_size.clean()

    def test_clean_method_with_none_size(self):
        with pytest.raises(IntegrityError):
            thumbnail_size = ThumbnailSizeFactory(size=None)
            thumbnail_size.clean()

    def test_thumbnail_size_creation(self):
        size = self.thumbnail_size.size
        assert size >= 50 and size <= 200


@pytest.mark.django_db
class TestAccountTypeModel:
    def setup_method(self):
        self.account_type = AccountTypeFactory(name="Basic")
        self.account_type.thumbs.clear()
        self.thumbs = [ThumbnailSizeFactory().id for _ in range(2)]

    def test_str_method(self):
        assert str(self.account_type) == "Basic"

    def test_create_account_type_with_thumbnails(self):
        self.account_type.thumbs.add(*self.thumbs)
        assert self.account_type.thumbs.count() == 2

    def test_account_type_creation(self):
        assert isinstance(self.account_type, AccountType)
        assert isinstance(self.account_type.orginal_image_link, bool)
        assert isinstance(self.account_type.time_limited_link, bool)


@pytest.mark.django_db
class TestUserImageModel:
    def test_save_method(self):
        user = CustomUserFactory()
        user_image = UserImageFactory(author=user)

        assert user_image.author == user

    def test_system_name_encrypted(self):
        user_image = UserImageFactory()

        assert uuid.UUID(user_image.system_name, version=4) is not None

    def test_system_name_unique(self):
        author1 = CustomUserFactory(username="Pablo", email="test2@example.com")
        user_image1 = UserImageFactory(author=author1, name="Test Image")
        author2 = CustomUserFactory(username="David", email="test@example.com")
        user_image2 = UserImageFactory(author=author2, name="Test Image")

        assert user_image1.system_name != user_image2.system_name

    def test_delete_method(self):
        user_image = UserImageFactory()

        user_image.delete()

        with pytest.raises(UserImage.DoesNotExist):
            UserImage.objects.get(pk=user_image.pk)

    def test_create_uploaded_image(self):
        uploaded_image = UserImageFactory()

        retrieved_uploaded_image = UserImage.objects.get(pk=uploaded_image.pk)

        assert retrieved_uploaded_image.name == uploaded_image.name
        assert retrieved_uploaded_image.author == uploaded_image.author

    def test_create_thumbnail_after_user_image_creation(self):
        uploaded_image = UserImageFactory()

        thumbnails = Thumbnail.objects.filter(system_name=uploaded_image)

        assert thumbnails.exists()

        for thumbnail in thumbnails:
            assert (
                thumbnail.size
                in uploaded_image.author.account_type.thumbs.values_list(
                    "size", flat=True
                )
            )
