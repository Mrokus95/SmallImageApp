from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AccountType, ThumbnailSize, CustomUser


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'orginal_image_link', 'time_limited_link', 
                    'display_thumbs')

    def display_thumbs(self, obj):
        return ", ".join([str(thumb.size) for thumb in obj.thumbs.all()])
    display_thumbs.short_description = "Available image's sizes in px"

@admin.register(ThumbnailSize)
class ThumbnailSizeAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('__str__',)