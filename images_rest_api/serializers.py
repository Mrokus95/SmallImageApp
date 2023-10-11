from django.contrib.auth import get_user_model
from PIL import Image
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Thumbnail, UserImage, CustomUser


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "account_type"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 7}}

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")
        account_type = validated_data.get("account_type")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Użytkownik o tej nazwie użytkownika już istnieje."
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Użytkownik o tym adresie e-mail już istnieje."
            )

        user = CustomUser(
            username=validated_data["username"],
            email=validated_data["email"],
            account_type=validated_data["account_type"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), username=username, password=password
        )

        if not user:
            msg = "Unable to authenticate with provided credentials"
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    username = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=old_password,
        )

        if not user:
            msg = "Unable to authenticate with provided credentials"
            raise serializers.ValidationError(msg, code="authentication")

        if len(new_password) < 7:
            msg = "New password must be at least 7 characters long"
            raise serializers.ValidationError(msg, code="password_too_short")

        return attrs


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
