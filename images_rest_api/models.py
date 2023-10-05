import uuid
from io import BytesIO
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image as pilimage


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


@receiver(post_save, sender=UserImage)
def create_thumbnail(sender, instance, created, **kwargs):
    if created:
        image = instance.image
        user = instance.author
        pillow_image = pilimage.open(image)
        file_format = pillow_image.format
        sizes = user.account_type.thumbs.all()
        original_width, original_height = pillow_image.size

        for size in sizes:
            height = size.size

            expected_size = (original_width, original_height)

            new_width = int(original_width * (height / original_height))
            expected_size = (new_width, height)

            resized_img = pillow_image.resize(expected_size, pilimage.LANCZOS)

            thumbnail = Thumbnail(
                system_name=instance,
                author=user,
                size=height,
            )

            thumb_io = BytesIO()
            resized_img.save(thumb_io, format=file_format)

            thumbnail_extension = file_format.lower()

            thumbnail_name = f"{instance.system_name}_{size}.{thumbnail_extension}"

            thumbnail.image.save(thumbnail_name, ContentFile(thumb_io.getvalue()))

            thumbnail.save()
