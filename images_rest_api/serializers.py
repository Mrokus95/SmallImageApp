from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .models import UserImage


User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "groups"]


class UserImageSerializer(ModelSerializer):
    class Meta:
        model = UserImage
        fields = ["id", "name", "image", "size"]
