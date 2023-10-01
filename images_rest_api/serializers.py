from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserImage, Thumbnail
from PIL import Image
from io import BytesIO


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "groups"]


class AddImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ["id", "name", "image"]

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("To pole jest wymagane.")

        # Sprawdź rozszerzenie pliku
        image_extension = value.name.split(".")[-1].lower()
        if image_extension not in ["jpg", "jpeg" "png"]:
            raise serializers.ValidationError(
                f"{image_extension} - Niedozwolone rozszerzenie pliku. Akceptowane są tylko pliki JPG i PNG."
            )

        # Sprawdź zawartość pliku
        try:
            img = Image.open(value)
            if img.format.lower() not in ["jpg", "jpeg", "png"]:
                raise serializers.ValidationError(
                    "Nieprawidłowy format obrazu. Akceptowane są tylko obrazy JPG i PNG."
                )
        except Exception as e:
            raise serializers.ValidationError(
                "Nie można otworzyć pliku jako obraz. Sprawdź, czy przesyłany plik jest prawidłowym obrazem."
            )

        return value


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["id", "size", "image"]


class BasicUserImageSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = UserImage
        fields = ["id", "name", "thumbnails"]


class NotBasicUserImageSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = UserImage
        fields = ["id", "name", "image", "thumbnails"]
