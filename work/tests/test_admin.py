import pytest
from django.contrib import admin as dj_admin
from django.utils import timezone

from work.admin import (
    ActivityInstanceAdmin,
    ActivityInstanceInline,
    MaintenanceTaskAdmin,
    WorkOrderAdmin,
    WorkOrderInline,
)
from work.models import ActivityInstance, MaintenanceTask, WorkOrder
from core.models import Workspace
from assets.models import Asset


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
    # Inline: WorkOrderInline should be attached here (not on WorkOrderAdmin)
    assert WorkOrderInline in ma.inlines
    # readonly id field
    assert "id" in ma.readonly_fields


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

    # There are no inlines defined on WorkOrderAdmin now
    assert getattr(ma, "inlines", ()) == ()

    # Actions and readonly id field
    action_names = set(ma.actions)
    assert {"mark_open", "mark_done", "mark_cancelled"} <= action_names
    assert "id" in ma.readonly_fields


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
    assert "id" in ma.readonly_fields


# --- Action behaviour tests -------------------------------------------------


@pytest.mark.django_db
def test_mark_open_action():
    """
    mark_open should set status='open' for all work orders in the queryset.
    """
    workspace = Workspace.objects.create(name="WS", slug="ws")
    asset = Asset.objects.create(workspace=workspace, name="Asset 1", kind="PI")
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Task 1",
        cadence="monthly",
    )
    order = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=timezone.now(),
        status="done",
    )

    ma = WorkOrderAdmin(WorkOrder, dj_admin.site)
    qs = WorkOrder.objects.filter(pk=order.pk)

    ma.mark_open(request=None, queryset=qs)

    order.refresh_from_db()
    assert order.status == "open"


@pytest.mark.django_db
def test_mark_done_action():
    """
    mark_done should set status='done' for all work orders in the queryset.
    """
    workspace = Workspace.objects.create(name="WS2", slug="ws2")
    asset = Asset.objects.create(workspace=workspace, name="Asset 2", kind="PI")
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Task 2",
        cadence="weekly",
    )
    order = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=timezone.now(),
        status="open",
    )

    ma = WorkOrderAdmin(WorkOrder, dj_admin.site)
    qs = WorkOrder.objects.filter(pk=order.pk)

    ma.mark_done(request=None, queryset=qs)

    order.refresh_from_db()
    assert order.status == "done"


@pytest.mark.django_db
def test_mark_cancelled_action():
    """
    mark_cancelled should set status='cancelled' for all work orders in the queryset.
    """
    workspace = Workspace.objects.create(name="WS3", slug="ws3")
    asset = Asset.objects.create(workspace=workspace, name="Asset 3", kind="PI")
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Task 3",
        cadence="weekly",
    )
    order = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=timezone.now(),
        status="open",
    )

    ma = WorkOrderAdmin(WorkOrder, dj_admin.site)
    qs = WorkOrder.objects.filter(pk=order.pk)

    ma.mark_cancelled(request=None, queryset=qs)

    order.refresh_from_db()
    assert order.status == "cancelled"
