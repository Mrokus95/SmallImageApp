from django.contrib.auth import authenticate, get_user_model
from PIL import Image
from rest_framework import serializers

from .models import CustomUser, Thumbnail, UserImage

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

        user = User(
            username=username,
            email=email,
            account_type=account_type,
        )
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, data):
        username = data

        if User.objects.filter(username=username).exists():
            msg = "A user with this username already exists."
            raise serializers.ValidationError({"username": msg,}, 
            code="invalid_username")

        return data

    def validate_email(self, data):
        email = data

        if User.objects.filter(email=email).exists():
            msg = "A user with this email address already exists."
            raise serializers.ValidationError({"email": msg,}, 
            code="invalid_email")
        return data


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
        if user is None:
            msg = "Unable to authenticate with provided credentials."
            raise serializers.ValidationError({"authentication": msg})

        attrs["user"] = user
        return attrs


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
            msg = "Unable to authenticate with provided credentials."
            raise serializers.ValidationError({"old_password": msg,}, 
            code="invalid_credentials")

        if len(new_password) < 7:
            msg = "New password must be at least 7 characters long."
            raise serializers.ValidationError({"new_password": msg}, 
            code="password_too_short")

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["id", "size", "image"]

class AddImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(write_only=True)

    class Meta:
        model = UserImage
        fields = ["id", "name","image"]

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")

        allowed_extensions_and_formats = ["jpg", "jpeg", "png"]
        allowed_content_type = ["image/jpg", "image/jpeg", "image/png"]

        image_extension = value.name.split(".")[-1].lower()
        content_type = value.content_type.lower()

        if image_extension not in allowed_extensions_and_formats:
            raise serializers.ValidationError(
                f"{image_extension} - Invalid file extension. Only {allowed_extensions_and_formats} files are accepted."
            )

        try:
            img = Image.open(value)
            if img.format.lower() not in allowed_extensions_and_formats:
                raise serializers.ValidationError(
                    f"{img.format.lower()} - Invalid file format. Only {allowed_extensions_and_formats} files are accepted."
                )
        except Exception as e:
            raise serializers.ValidationError(
                "Cannot open the file as an image. Please check if the uploaded file is a valid image."
            )
        
        if content_type not in allowed_content_type:
            raise serializers.ValidationError(
                f"{content_type} - Invalid file content-type. Only {allowed_content_type} files are accepted."
            )
            
        return value



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
