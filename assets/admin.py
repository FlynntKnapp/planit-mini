# assets/admin.py

from django.contrib import admin
from django.utils import timezone

from work.admin import ActivityInstanceInline, WorkOrderInline

from .models import OS, Application, Asset, FormFactor, Project


@admin.register(FormFactor)
class FormFactorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "slug")
    search_fields = ("name", "version")
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "slug")
    search_fields = ("name", "version")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "slug")
    search_fields = ("name", "description", "slug")
    list_filter = ("workspace",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("workspace",)  # search by workspace name
    ordering = ("workspace", "name")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "workspace",
        "project",
        "kind",
        "form_factor",
        "os",
        "location",
        "purchase_date",
        "warranty_expires",
        "warranty_status",
        "next_due_status",
    )
    list_filter = (
        "workspace",
        "kind",
        "form_factor",
        "os",
        "applications",  # filter by installed apps
        "location",
        "purchase_date",
        "warranty_expires",
    )
    search_fields = (
        "name",
        "location",
        "notes",
        "workspace__name",
        "project__name",
    )
    autocomplete_fields = (
        "workspace",
        "project",
        "form_factor",
        "os",
        "applications",  # autocomplete instead of dual list
    )
    date_hierarchy = "purchase_date"
    list_select_related = ("workspace", "project", "form_factor", "os")
    ordering = ("workspace", "name")
    # Inlines: work orders + recent activity on this asset
    inlines = [WorkOrderInline, ActivityInstanceInline]

    # --- Status "chips" -----------------------------------------------------

    def warranty_status(self, obj) -> str:
        """
        Human-friendly warranty status summary.

        - 'n/a'           : no warranty date
        - 'Expired'       : warranty_expires < today
        - 'Expiring soon' : 0–30 days left
        - 'Active'        : > 30 days left
        """
        if not obj.warranty_expires:
            return "n/a"

        today = timezone.now().date()
        delta_days = (obj.warranty_expires - today).days

        if delta_days < 0:
            return "Expired"
        if delta_days <= 30:
            return "Expiring soon"
        return "Active"

    warranty_status.short_description = "Warranty"

    def next_due_status(self, obj) -> str:
        """
        Status of the next open WorkOrder for this asset:

        - 'No open work'
        - 'Overdue'
        - 'Due today'
        - 'Due soon' (<= 7 days)
        - 'Scheduled' (> 7 days)
        """
        now = timezone.now()
        next_order = obj.workorders.filter(status="open").order_by("due").first()

        if not next_order:
            return "No open work"

        if next_order.due < now:
            return "Overdue"

        days = (next_order.due.date() - now.date()).days
        if days == 0:
            return "Due today"
        if days <= 7:
            return "Due soon"
        return "Scheduled"

    next_due_status.short_description = "Next work"
