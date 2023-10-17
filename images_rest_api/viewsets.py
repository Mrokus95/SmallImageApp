import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema, extend_schema_serializer,
                                   extend_schema_view)
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import generics, permissions, status, views
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Thumbnail, UserImage
from .serializers import (AddImageSerializer, AuthSerializer,
                          BasicUserImageSerializer, ChangePasswordSerializer,
                          NotBasicUserImageSerializer, UserSerializer)

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission class to allow object access only to the owner or read-only for others.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the request user has permission to access the object.

        Args:
            request: The HTTP request object.
            view: The view instance.
            obj: The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsOwnerAndEnterprise(permissions.BasePermission):
    """
    Custom permission class to allow access to the owner with a time-limited link and the enterprise account.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the request user has permission to access the object.

        Args:
            request: The HTTP request object.
            view: The view instance.
            obj: The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        is_owner = obj.author == request.user

        has_time_limited_link = request.user.account_type.time_limited_link
        return is_owner and has_time_limited_link


@extend_schema_view(
    post=extend_schema(
        request=UserSerializer,
        responses={200: ChangePasswordSerializer},
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description='Token should be included in the Authorization header as "Token your_token_here".',
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
        ],
        examples=[
            OpenApiExample(
                "Valid example",
                summary="Successful create user.",
                description="An example of a successful user creating.",
                value={
                    "user": {
                        "username": "Student500",
                        "email": "student500@studnet.pl",
                        "account_type": 1,
                    },
                    "token": "c41307244c1648a62034ca7bd90f5097aa848b05ef94da7b1c1284ff3fd7dcaf",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example",
                summary="Failed create user.",
                description="Failed user creating - not unique email address",
                value={"detail": "A user with this email address already exists."},
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example 2",
                summary="Failed create user.",
                description="Failed user creating - not unique username",
                value={"detail": "A user with this username already exists."},
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example 3",
                summary="Failed create user.",
                description="Failed user creating - incorect type of account_type id.",
                value={
                    "account_type": ["Incorrect type. Expected pk value, received str."]
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example 4",
                summary="Failed create user.",
                description="Failed user creating - account_type id not found",
                value={
                    "account_type": ['Invalid pk "645654" - object does not exist.']
                },
                request_only=True,
            ),
        ],
    )
)
class CreateUserView(generics.CreateAPIView):
    """
    View for creating a new user.
    """

    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["post"]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user creation.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "token": AuthToken.objects.create(user)[1],
                },
                status=status.HTTP_201_CREATED,
            )

        elif "email" in serializer.errors:
            return Response(
                {"detail": "A user with this email address already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif "username" in serializer.errors:
            return Response(
                {"detail": "A user with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    patch=extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: ChangePasswordSerializer,
            400: {"description": "Invalid credentials."},
            401: {"description": "New password must be at least 7 characters long."},
        },
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description='Token should be included in the Authorization header as "Token your_token_here".',
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
        ],
        examples=[
            OpenApiExample(
                "Valid example",
                summary="Successful change password.",
                description="An example of a successful changing password response.",
                value={
                    "status": "success",
                    "code": 200,
                    "message": "Password updated successfully",
                    "data": [],
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example",
                summary="Failed login example - lack of token",
                description="An example of a failed login response.",
                value={"detail": "Invalid token."},
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example 2",
                summary="Failed login example - invalid old password",
                description="An example of a failed login response.",
                value={"detail": "Invalid credentials."},
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example 3",
                summary="Failed login example - invalid new password",
                description="An example of a failed login response.",
                value={"detail": ["New password must be at least 7 characters long."]},
                request_only=True,
            ),
        ],
    )
)
class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        """
        Retrieve and return the authenticated user.

        Args:
            queryset: The database query.

        Returns:
            object: The authenticated user.
        """
        obj = self.request.user
        return obj

    def patch(self, request, *args, **kwargs):
        """
        Handle password update requests.

        Args:
            request: The HTTP request object.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response.
        """
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            return Response(
                {
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "message": "Password updated successfully",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        elif "old_password" in serializer.errors:
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )
        elif "new_password" in serializer.errors:
            return Response(
                {"detail": "New password must be at least 7 characters long."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        request=AuthSerializer,
        responses={
            200: AuthSerializer,
            401: {"detail": "Authentication failed."},
        },
        examples=[
            OpenApiExample(
                "Valid example",
                summary="Successful login example",
                description="An example of a successful login response.",
                value={
                    "expiry": "2023-10-14T18:48:45.058484Z",
                    "token": "fb6461f3bebf7a78b70814ef8508e57994be63d1dbf8ada54dc5fb9932ce13d7",
                    "user": {
                        "username": "SampleUser",
                        "email": "sample@example.com",
                        "account_type": 1,
                    },
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example",
                summary="Failed login example",
                description="An example of a failed login response.",
                value={"detail": "Authentication failed."},
                request_only=True,
            ),
        ],
    )
)
class LoginView(KnoxLoginView):
    """
    An endpoint for user login.
    """

    serializer_class = AuthSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ["post"]

    def post(self, request, format=None):
        """
        Handle user login requests.

        Args:
            request: The HTTP request object.
            format: The response format.

        Returns:
            Response: The HTTP response.
        """
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user = serializer.validated_data["user"]
            login(request, user)
            return super(LoginView, self).post(request, format=None)
        else:
            return Response(
                {"detail": "Authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@extend_schema_view(
    get=extend_schema(
        request=UserSerializer,
        responses={
            200: UserSerializer,
            401: {"description": "Authentication credentials were not provided."},
        },
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description='Token should be included in the Authorization header as "Token your_token_here".',
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
        ],
        examples=[
            OpenApiExample(
                "Valid example",
                summary="Successful get user profile data.",
                description="An example of a successful get user profile data.",
                value={
                    "username": "admin",
                    "email": "admin@admin.pl",
                    "account_type": 3,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example",
                summary="Failed lget user profile data.",
                description="An example of a failed login response - invalid token.",
                value={"detail": "Authentication credentials were not provided."},
                request_only=True,
            ),
        ],
    )
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user.
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get"]

    def get_object(self):
        """
        Retrieve and return the authenticated user.

        Returns:
            object: The authenticated user.
        """
        return self.request.user


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            description='Token should be included in the Authorization header as "Token your_token_here".',
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.HEADER,
        ),
    ],
)
class UserImagesViewSet(ModelViewSet):
    """
    Viewset for managing user images.
    """

    permission_classes = [permissions.IsAuthenticated & IsOwnerOrReadOnly]
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
        return UserImage.objects.filter(author=self.request.user).order_by("id")

    @extend_schema(
        responses={
            200: UserSerializer,
            401: {"description": "Authentication credentials were not provided."},
        },
        examples=[
            OpenApiExample(
                "Valid example",
                summary="Successful get user profile data.",
                description="An example of a successful get user profile data.",
                value={
                    "username": "admin",
                    "email": "admin@admin.pl",
                    "account_type": 3,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid example",
                summary="Failed lget user profile data.",
                description="An example of a failed login response - invalid token.",
                value={"detail": "Authentication credentials were not provided."},
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data["author"] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
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
    """
    Generate temporary links to access files.
    """

    permission_classes = [permissions.IsAuthenticated & IsOwnerAndEnterprise]
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

        if file_type == "image":
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
