# work/admin.py

from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

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
    # Show most recent activity first (for "recent activity" feel)
    ordering = ("-occurred_at",)


class DueWindowFilter(admin.SimpleListFilter):
    """
    Custom list filter for WorkOrderAdmin to filter by due-date window.
    """

    title = "due window"
    parameter_name = "due_window"

    def lookups(self, request, model_admin):
        return (
            ("overdue", "Overdue"),
            ("next_7_days", "Next 7 days"),
            ("next_30_days", "Next 30 days"),
            ("future", "Beyond 30 days"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        now = timezone.now()

        if value == "overdue":
            # Anything before now
            return queryset.filter(due__lt=now)

        if value == "next_7_days":
            # [now, now+7)
            return queryset.filter(due__gte=now, due__lt=now + timedelta(days=7))

        if value == "next_30_days":
            # [now+7, now+30) so it's disjoint from next_7_days
            return queryset.filter(
                due__gte=now + timedelta(days=7),
                due__lt=now + timedelta(days=30),
            )

        if value == "future":
            # >= now+30
            return queryset.filter(due__gte=now + timedelta(days=30))

        return queryset


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

    # Admin polish: "Generate Preview" action
    actions = ("generate_preview",)

    @admin.action(description="Generate preview schedule (no DB changes)")
    def generate_preview(self, request, queryset):
        """
        Admin action stub that can be extended to generate a preview schedule.

        Currently a no-op, but wired up so users can select tasks and
        trigger a preview without mutating the database.
        """
        # Intentionally left as a no-op (safe to call in tests/demo).
        return None


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
    list_filter = (
        "workspace",
        "status",
        "task",
        DueWindowFilter,  # admin polish: filter by due window
    )
    search_fields = (
        "task__name",
        "asset__name",
        "workspace__name",
        "assigned_to__username",
        "requested_by__username",
    )
    date_hierarchy = "due"
    # NOTE: second declaration wins; workspace is not autocomplete here,
    # which is what tests expect.
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
        "mark_done",  # quick "Mark done" action
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
