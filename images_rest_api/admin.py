from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import AccountType, ThumbnailSize, CustomUser, UserImage, Thumbnail
from django import forms


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "orginal_image_link", "time_limited_link", 
                    "display_thumbs")

    def display_thumbs(self, obj):
        return ", ".join([str(thumb.size) for thumb in obj.thumbs.all()])

    display_thumbs.short_description = "Available image's sizes in px"


@admin.register(ThumbnailSize)
class ThumbnailSizeAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "password", "email", "account_type")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserCreationForm
    add_form = CustomUserCreationForm
    list_display = (
        "username",
        "email",
        "account_type",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "account_type",
                ),
            },
        ),
    )


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    list_display = ("name", "system_name", "author")


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ("__str__", "system_name", "author", "size")
