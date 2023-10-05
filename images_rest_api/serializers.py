from django.contrib.auth import get_user_model
from PIL import Image
from rest_framework import serializers
from .models import Thumbnail, UserImage

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
            raise serializers.ValidationError("This field is required.")

        image_extension = value.name.split(".")[-1].lower()
        if image_extension not in ["jpg", "jpeg" "png"]:
            raise serializers.ValidationError(
                f"{image_extension} - Invalid file extension. Only JPG, JPEG,"
                "and PNG files are accepted."
            )

        try:
            img = Image.open(value)
            if img.format.lower() not in ["jpg", "jpeg", "png"]:
                raise serializers.ValidationError(
                    f"{image_extension} - Invalid file format. Only JPG, JPEG,"
                    "and PNG files are accepted."
                )
        except Exception as e:
            raise serializers.ValidationError(
                "Cannot open the file as an image."
                " Please check if the uploaded file is a valid image."
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
