from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
import uuid


class ThumbnailSize(models.Model):
    size = models.IntegerField()

    def __str__(self):
        return f"{self.size} px"

    def clean(self):
        if self.size is None:
            raise ValidationError("Thumbnail dimension must be provided.")


class AccountType(models.Model):
    name = models.CharField(max_length=64)
    orginal_image_link = models.BooleanField(default=False)
    time_limited_link = models.BooleanField(default=False)
    thumbs = models.ManyToManyField(ThumbnailSize)

    def __str__(self):
        return self.name


class CustomUserManager(UserManager):
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("account_type", AccountType.objects.first())
        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=64, unique=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.DO_NOTHING)
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "username"

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "custom user"
        verbose_name_plural = "custom users"


class UserImage(models.Model):
    name = models.CharField(max_length=164)
    system_name = models.CharField()
    image = models.ImageField(upload_to="users-images")
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="client_photos"
    )
    size = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Size" 
    )

    def delete(self):
        self.image.delete()
        super().delete()

    def save(self, *args, **kwargs):
        if not self.id:  
            filename = str(uuid.uuid4())
            self.image.name = "-".join([filename, self.image.name])
            self.system_name = self.image.name
        super(UserImage, self).save(*args, **kwargs)