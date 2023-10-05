from ..models import AccountType, ThumbnailSize, CustomUser
import os
from dotenv import load_dotenv

load_dotenv()


DJANGO_SUPERUSER_USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME")
DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
DJANGO_SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")


def run():
    thumbnail_size_200, created = ThumbnailSize.objects.get_or_create(size=200)
    thumbnail_size_400, created = ThumbnailSize.objects.get_or_create(size=400)

    basic_account_type, created = AccountType.objects.get_or_create(
        name="Basic",
        orginal_image_link=False,
        time_limited_link=False,
    )

    premium_account_type, created = AccountType.objects.get_or_create(
        name="Premium",
        orginal_image_link=True,
        time_limited_link=False,
    )

    enterprise_account_type, created = AccountType.objects.get_or_create(
        name="Enterprise",
        orginal_image_link=True,
        time_limited_link=True,
    )

    basic_account_type.thumbs.set([thumbnail_size_200])
    premium_account_type.thumbs.set([thumbnail_size_200, thumbnail_size_400])
    enterprise_account_type.thumbs.set([thumbnail_size_200, thumbnail_size_400])

    if not CustomUser.objects.all():
        CustomUser.objects.create_superuser(
            DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, 
            DJANGO_SUPERUSER_PASSWORD
        )
