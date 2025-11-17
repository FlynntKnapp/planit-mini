# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.forms import CustomUserChangeForm, CustomUserCreationForm
from accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "username",
        "email",
        "registration_accepted",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "registration_accepted",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    def get_fieldsets(self, request, obj=None):
        """
        Override `get_fieldsets()` to add `registration_accepted` to a
        'Moderator Permissions' section on the **change view** only.

        For the add view (obj is None), we just return the base fieldsets
        (which come from UserAdmin and/or `add_fieldsets`) unchanged.
        """
        # Let UserAdmin decide the base fieldsets (add vs change behavior)
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets_as_list = list(fieldsets)

        # Only inject the extra section on the change view
        if obj is not None:
            moderator_permissions = (
                "Moderator Permissions",
                {"fields": ("registration_accepted",)},
            )

            # Insert after "Personal info" (index 1) if present, else near top
            insert_index = 2 if len(fieldsets_as_list) >= 2 else 1
            fieldsets_as_list.insert(insert_index, moderator_permissions)

        return fieldsets_as_list

    # Optionally show `registration_accepted` when creating users as well
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "registration_accepted",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
