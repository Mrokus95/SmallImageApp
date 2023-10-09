import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class ThumbnailSize(models.Model):
    size = models.IntegerField()

    def __str__(self):
        return f"{self.size} px"

    def clean(self):
        if self.size is None:
            raise ValidationError("Thumbnail dimension must be provided.")


class AccountType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    orginal_image_link = models.BooleanField(default=False)
    time_limited_link = models.BooleanField(default=False)
    thumbs = models.ManyToManyField(ThumbnailSize)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_superuser(self, username, email, password, account_type, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser account must be assigned to is_superuser=True")

        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser account must be active")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser account must be assigned to is_staff=True")

        return self.create_user(username, email, password, account_type, **extra_fields)

    def create_user(self, username, email, password, account_type, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("Email must be set"))
        if not username:
            raise ValueError(_("Username must be set"))
        account = AccountType.objects.get(id=account_type)
        if not account:
            raise ValueError(_("The correct account_type must be set"))

        email = self.normalize_email(email)
        user = self.model(
            username=username, email=email, account_type=account, **extra_fields
        )
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.DO_NOTHING)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "account_type"]
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "custom user"
        verbose_name_plural = "custom users"


class UserImage(models.Model):
    name = models.CharField(max_length=164, null=False, blank=False)
    system_name = models.CharField()
    image = models.ImageField(upload_to="user_images")
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="client_photos"
    )

    def delete(self):
        self.image.delete(save=False)
        super().delete()

    def save(self, *args, **kwargs):
        if not self.id:
            filename = str(uuid.uuid4())
            self.image.name = "-".join([filename, self.name])
            self.system_name = filename
        super(UserImage, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.system_name


class Thumbnail(models.Model):
    system_name = models.ForeignKey(
        UserImage, related_name="thumbnails", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="client_thumbnails"
    )
    size = models.IntegerField(verbose_name="Size")

    image = models.ImageField(upload_to="user_images/thumbnails")

    class Meta:
        unique_together = ["system_name", "size"]
        ordering = ["size"]

    def __str__(self):
        return f"Image {self.image.name} - {self.size} px"

    def delete(self):
        self.image.delete(save=False)
        super().delete()
