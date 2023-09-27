from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse
from .serializers import UserSerializer, UserImageSerializer
from .models import UserImage, CustomUser
from rest_framework import permissions
from rest_framework import status


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserImagesViewSet(ModelViewSet):
    serializer_class = UserImageSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return UserImage.objects.filter(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, 
                                status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data["author"] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return JsonResponse(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
