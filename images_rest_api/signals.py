from io import BytesIO
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image as pilimage
from django.core.files.base import ContentFile
from .models import UserImage, Thumbnail

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
