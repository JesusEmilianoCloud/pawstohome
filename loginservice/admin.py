from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ["first_name", "last_name", "username", "email", "phone_number", "fecha_registro", "activo"]
    list_filter = ["activo", "fecha_registro", "is_staff", "is_superuser"]
    search_fields = ["username", "email", "first_name", "last_name", "phone_number"]

    fieldsets = UserAdmin.fieldsets + (
        (("Información Adicional"), {
            "fields": ("phone_number", "fecha_registro", "activo")
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (("Información Adicional"), {
            "fields": ("phone_number",)
        }),
    )
    
    readonly_fields = ["fecha_registro"]

admin.site.register(CustomUser, CustomUserAdmin) 
