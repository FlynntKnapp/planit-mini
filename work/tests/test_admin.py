import pytest
from django.contrib import admin as dj_admin

from work.admin import (
    ActivityInstanceAdmin,
    ActivityInstanceInline,
    MaintenanceTaskAdmin,
    WorkOrderAdmin,
    WorkOrderInline,
)
from work.models import ActivityInstance, MaintenanceTask, WorkOrder


@pytest.mark.parametrize(
    "model",
    [MaintenanceTask, WorkOrder, ActivityInstance],
)
def test_models_are_registered_in_admin(model):
    """
    Ensure all work-related models are registered in the admin.
    """
    assert model in dj_admin.site._registry


def test_workorder_inline_configuration():
    inline = WorkOrderInline(MaintenanceTask, dj_admin.site)

    assert inline.model is WorkOrder
    assert inline.extra == 0
    assert inline.raw_id_fields == ("asset", "assigned_to", "requested_by")
    assert inline.autocomplete_fields == ("asset", "assigned_to", "requested_by")


def test_activityinstance_inline_configuration():
    inline = ActivityInstanceInline(WorkOrder, dj_admin.site)

    assert inline.model is ActivityInstance
    assert inline.extra == 0
    assert inline.raw_id_fields == ("asset", "performed_by")
    assert inline.autocomplete_fields == ("asset", "performed_by")


def test_maintenance_task_admin_configuration():
    ma = MaintenanceTaskAdmin(MaintenanceTask, dj_admin.site)

    assert ma.list_display == ("name", "workspace", "cadence")
    assert ma.list_filter == ("workspace", "cadence")
    for field in ("name", "description", "workspace__name"):
        assert field in ma.search_fields

    assert ma.raw_id_fields == ("workspace",)
    assert ma.ordering == ("workspace", "name")
    assert WorkOrderInline in ma.inlines


def test_work_order_admin_configuration():
    ma = WorkOrderAdmin(WorkOrder, dj_admin.site)

    assert ma.list_display == (
        "task",
        "asset",
        "workspace",
        "due",
        "status",
        "assigned_to",
        "requested_by",
    )

    for field in ("workspace", "status", "task"):
        assert field in ma.list_filter

    for field in (
        "task__name",
        "asset__name",
        "workspace__name",
        "assigned_to__username",
        "requested_by__username",
    ):
        assert field in ma.search_fields

    assert ma.date_hierarchy == "due"
    assert ma.raw_id_fields == (
        "workspace",
        "asset",
        "task",
        "assigned_to",
        "requested_by",
    )
    assert ma.autocomplete_fields == ("asset", "task", "assigned_to", "requested_by")
    assert ma.list_select_related == (
        "workspace",
        "asset",
        "task",
        "assigned_to",
        "requested_by",
    )
    assert ma.ordering == ("workspace", "due")
    assert ActivityInstanceInline in ma.inlines


def test_activity_instance_admin_configuration():
    ma = ActivityInstanceAdmin(ActivityInstance, dj_admin.site)

    assert ma.list_display == (
        "kind",
        "asset",
        "workspace",
        "work_order",
        "occurred_at",
        "performed_by",
    )

    for field in ("workspace", "kind"):
        assert field in ma.list_filter

    for field in (
        "asset__name",
        "workspace__name",
        "work_order__task__name",
        "performed_by__username",
        "note",
    ):
        assert field in ma.search_fields

    assert ma.date_hierarchy == "occurred_at"
    assert ma.raw_id_fields == (
        "workspace",
        "asset",
        "work_order",
        "performed_by",
    )
    assert ma.autocomplete_fields == ("asset", "work_order", "performed_by")
    assert ma.list_select_related == (
        "workspace",
        "asset",
        "work_order",
        "performed_by",
    )
    assert ma.ordering == ("-occurred_at",)
