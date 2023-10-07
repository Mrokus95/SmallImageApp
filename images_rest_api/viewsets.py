from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import (
    UserSerializer,
    BasicUserImageSerializer,
    NotBasicUserImageSerializer,
    AddImageSerializer,
)
from .models import UserImage, CustomUser, Thumbnail
from rest_framework import permissions
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import views
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsOwnerAndEnterprise(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = obj.author == request.user

        has_time_limited_link = request.user.account_type.time_limited_link
        return is_owner and has_time_limited_link


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserImagesViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ["get", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddImageSerializer
        else:
            user = self.request.user

            if user.account_type.orginal_image_link:
                return NotBasicUserImageSerializer
            else:
                return BasicUserImageSerializer

    def get_queryset(self):
        return UserImage.objects.filter(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data["author"] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return JsonResponse(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        thumbnails = Thumbnail.objects.filter(system_name=instance)
        for thumbnail in thumbnails:
            thumbnail.delete()

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateTemporaryLinkView(views.APIView):
    permission_classes = [IsOwnerAndEnterprise]
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        file_type = kwargs.get("file_type")
        file_id = kwargs.get("file_id")

        expiration_time_seconds = int(
            request.query_params.get("expiration_time_seconds", 3600)
        )

        if expiration_time_seconds < 300 or expiration_time_seconds > 30000:
            return Response(
                {"error": "Invalid link duration."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if file_type == "user_image":
            model_class = UserImage
        elif file_type == "thumbnail":
            model_class = Thumbnail
        else:
            return Response(
                {"error": "Invalid file type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_instance = get_object_or_404(model_class, id=file_id)
        self.check_object_permissions(self.request, file_instance)

        file_key = file_instance.image.name

        s3 = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        try:
            temporary_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_key},
                ExpiresIn=expiration_time_seconds,
            )
        except NoCredentialsError:
            return Response(
                {"error": "No access to AWS resources."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"temporary_url": temporary_url}, status=status.HTTP_200_OK)
