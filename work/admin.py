# work/admin.py

from django.contrib import admin

from .models import ActivityInstance, MaintenanceTask, WorkOrder


class WorkOrderInline(admin.TabularInline):
    model = WorkOrder
    extra = 0
    autocomplete_fields = ("asset", "assigned_to", "requested_by")


class ActivityInstanceInline(admin.TabularInline):
    model = ActivityInstance
    extra = 0
    raw_id_fields = ("asset", "performed_by")
    autocomplete_fields = ("asset", "performed_by")


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "cadence")
    list_filter = ("workspace", "cadence")
    search_fields = ("name", "description", "workspace__name")
    autocomplete_fields = ("workspace",)
    ordering = ("workspace", "name")
    inlines = [WorkOrderInline]

    # Light audit-ish: show primary key as readonly
    readonly_fields = ("id",)


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "asset",
        "workspace",
        "due",
        "status",
        "assigned_to",
        "requested_by",
    )
    list_filter = ("workspace", "status", "task")
    search_fields = (
        "task__name",
        "asset__name",
        "workspace__name",
        "assigned_to__username",
        "requested_by__username",
    )
    date_hierarchy = "due"
    autocomplete_fields = ("workspace", "asset", "task", "assigned_to", "requested_by")
    autocomplete_fields = ("asset", "task", "assigned_to", "requested_by")
    list_select_related = (
        "workspace",
        "asset",
        "task",
        "assigned_to",
        "requested_by",
    )
    ordering = ("workspace", "due")

    # Light audit-ish: show primary key as readonly
    readonly_fields = ("id",)

    # Bulk status actions
    actions = (
        "mark_open",
        "mark_done",
        "mark_cancelled",
    )

    @admin.action(description="Mark selected work orders as Open")
    def mark_open(self, request, queryset):
        """
        Bulk action: set status='open' for selected work orders.
        """
        queryset.update(status="open")

    @admin.action(description="Mark selected work orders as Done")
    def mark_done(self, request, queryset):
        """
        Bulk action: set status='done' for selected work orders.
        """
        queryset.update(status="done")

    @admin.action(description="Mark selected work orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        """
        Bulk action: set status='cancelled' for selected work orders.
        """
        queryset.update(status="cancelled")


@admin.register(ActivityInstance)
class ActivityInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "kind",
        "asset",
        "workspace",
        "work_order",
        "occurred_at",
        "performed_by",
    )
    list_filter = ("workspace", "kind")
    search_fields = (
        "asset__name",
        "workspace__name",
        "work_order__task__name",
        "performed_by__username",
        "note",
    )
    date_hierarchy = "occurred_at"
    autocomplete_fields = ("workspace", "asset", "work_order", "performed_by")
    list_select_related = (
        "workspace",
        "asset",
        "work_order",
        "performed_by",
    )
    ordering = ("-occurred_at",)

    # Light audit-ish: show primary key as readonly
    readonly_fields = ("id",)
