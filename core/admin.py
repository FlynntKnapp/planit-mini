# core/admin.py

from django.contrib import admin

from .models import Membership, Workspace


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    autocomplete_fields = ("user",)
    raw_id_fields = ("user",)
    # If you want to prevent deleting memberships from inline:
    # can_delete = False


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MembershipInline]
    ordering = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role")
    list_filter = ("role", "workspace")
    search_fields = (
        "user__username",
        "user__email",
        "workspace__name",
    )
    raw_id_fields = ("user", "workspace")
    ordering = ("workspace", "user")
