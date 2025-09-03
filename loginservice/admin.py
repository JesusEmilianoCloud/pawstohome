from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ["first_name", "last_name", "username", "email", "phone_number"]

    fieldsets = UserAdmin.fieldsets + ((("Custom fields"), {"fields": ("phone_number",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((("Custom fields"), {"fields": ("phone_number",)}),)


admin.site.register(CustomUser, CustomUserAdmin) 
