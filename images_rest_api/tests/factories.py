import io
import random

import factory
from factory import Sequence
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory
from faker import Faker
from PIL import Image

from ..models import AccountType, CustomUser, ThumbnailSize, UserImage

faker = FakerFactory.create()
fake = Faker()


class ThumbnailSizeFactory(DjangoModelFactory):
    class Meta:
        model = ThumbnailSize

    size = factory.LazyAttribute(lambda _: faker.random_int(min=50, max=200))


class AccountTypeFactory(DjangoModelFactory):
    class Meta:
        model = AccountType
        skip_postgeneration_save = True

    name = Sequence(lambda n: f"AccountType {n}")
    orginal_image_link = factory.Faker("boolean")
    time_limited_link = factory.Faker("boolean")

    @factory.post_generation
    def thumbs(self, create, extracted, **kwargs):
        if not create:
            return

        num_thumbs = random.randint(1, 3)

        if extracted:
            for thumb in extracted:
                self.thumbs.add(thumb)
        else:
            for _ in range(num_thumbs):
                thumb = ThumbnailSizeFactory()
                self.thumbs.add(thumb)


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = fake.unique.name()
    account_type = factory.SubFactory(AccountTypeFactory)
    email = fake.unique.email()
    password = 'Strongpassword'
    is_staff = False
    is_active = True
    is_superuser = False


class UserImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserImage
        skip_postgeneration_save = True

    name = factory.Faker("word")
    author = factory.SubFactory(CustomUserFactory)

    @staticmethod
    def create_image(file_full_name, size, content_type):
        image = Image.new("RGB", (size, size))
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        image_file = SimpleUploadedFile(
            file_full_name, image_io.getvalue(), content_type=content_type
        )
        return image_file

    image = factory.LazyAttribute(
        lambda o: UserImageFactory.create_image(f"{o.name}.jpg", 200, "image/jpeg")
    )

    @factory.post_generation
    def save_user_image(instance, create, extracted, **kwargs):
        if create:
            instance.save()
