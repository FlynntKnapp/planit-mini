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

    # Audit-ish: make the primary key readonly in the admin UI.
    readonly_fields = UserAdmin.readonly_fields + ("id",)

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

    # Bulk actions for moderator/admin workflow
    actions = (
        "mark_registration_accepted",
        "mark_registration_unaccepted",
    )

    @admin.action(description="Mark selected users as registration accepted")
    def mark_registration_accepted(self, request, queryset):
        """
        Bulk action: set registration_accepted=True for selected users.
        """
        queryset.update(registration_accepted=True)

    @admin.action(description="Mark selected users as registration NOT accepted")
    def mark_registration_unaccepted(self, request, queryset):
        """
        Bulk action: set registration_accepted=False for selected users.
        """
        queryset.update(registration_accepted=False)

    def get_fieldsets(self, request, obj=None):
        """
        Override `get_fieldsets()` to add `registration_accepted` to a
        'Moderator Permissions' section on the change view.
        """
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets_as_list = list(fieldsets)

        moderator_permissions = (
            "Moderator Permissions",
            {"fields": ("registration_accepted",)},
        )

        # Insert after "Personal info" (index 1) if present, else near top.
        insert_index = 2 if len(fieldsets_as_list) >= 2 else 1
        fieldsets_as_list.insert(insert_index, moderator_permissions)
        return fieldsets_as_list

    # Show registration_accepted on the add form as well
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
