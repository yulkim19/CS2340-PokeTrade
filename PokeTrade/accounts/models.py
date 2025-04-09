from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


# Create your models here.

# Create a custom UserAdmin class
class CustomUserAdmin(UserAdmin):
    # List of fields to display in the User change list view
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')

    # Remove first_name and last_name from the list of filters
    list_filter = ('is_staff', 'is_active')

    # Fields to be displayed when editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to display in the user creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )


# Unregister the default UserAdmin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
