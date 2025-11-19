# work/tests/test_admin.py

from datetime import timedelta

import pytest
from django.contrib import admin as dj_admin
from django.test import RequestFactory
from django.utils import timezone

from assets.models import Asset
from core.models import Workspace
from work.admin import (
    ActivityInstanceAdmin,
    ActivityInstanceInline,
    DueWindowFilter,
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
    # Inline now uses autocomplete only (no raw_id_fields)
    assert inline.autocomplete_fields == ("asset", "assigned_to", "requested_by")
    assert inline.raw_id_fields == ()


def test_activityinstance_inline_configuration():
    inline = ActivityInstanceInline(WorkOrder, dj_admin.site)

    assert inline.model is ActivityInstance
    assert inline.extra == 0
    # Activity inline still uses both raw_id_fields and autocomplete
    assert inline.raw_id_fields == ("asset", "performed_by")
    assert inline.autocomplete_fields == ("asset", "performed_by")
    # Recent-first ordering
    assert inline.ordering == ("-occurred_at",)


def test_maintenance_task_admin_configuration():
    ma = MaintenanceTaskAdmin(MaintenanceTask, dj_admin.site)

    assert ma.list_display == ("name", "workspace", "cadence")
    assert ma.list_filter == ("workspace", "cadence")

    for field in ("name", "description", "workspace__name"):
        assert field in ma.search_fields

    # Uses autocomplete for workspace (no raw_id_fields)
    assert ma.autocomplete_fields == ("workspace",)
    assert ma.raw_id_fields == ()
    assert ma.ordering == ("workspace", "name")
    # Inline: WorkOrderInline should be attached here (not on WorkOrderAdmin)
    assert WorkOrderInline in ma.inlines
    # readonly id field
    assert "id" in ma.readonly_fields

    # Has "Generate Preview" action wired up
    action_names = set(ma.actions)
    assert "generate_preview" in action_names


@pytest.mark.django_db
def test_generate_preview_action_noop():
    """
    MaintenanceTaskAdmin.generate_preview should be callable and side-effect free.
    """
    workspace = Workspace.objects.create(name="WS", slug="ws")
    MaintenanceTask.objects.create(workspace=workspace, name="Task", cadence="monthly")

    ma = MaintenanceTaskAdmin(MaintenanceTask, dj_admin.site)
    qs = MaintenanceTask.objects.all()

    # Should not raise
    ma.generate_preview(request=None, queryset=qs)


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

    # Existing filters plus due window filter
    for field in ("workspace", "status", "task"):
        assert field in ma.list_filter
    assert DueWindowFilter in ma.list_filter

    for field in (
        "task__name",
        "asset__name",
        "workspace__name",
        "assigned_to__username",
        "requested_by__username",
    ):
        assert field in ma.search_fields

    assert ma.date_hierarchy == "due"

    # WorkOrderAdmin now uses autocomplete, not raw_id_fields.
    # Note the second declaration in admin means the effective value is:
    assert ma.autocomplete_fields == ("asset", "task", "assigned_to", "requested_by")
    assert ma.raw_id_fields == ()

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

    # ActivityInstanceAdmin now uses autocomplete for all these FKs
    assert ma.autocomplete_fields == (
        "workspace",
        "asset",
        "work_order",
        "performed_by",
    )
    assert ma.raw_id_fields == ()

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


@pytest.mark.django_db
def test_due_window_filter_querysets():
    """
    Verify DueWindowFilter buckets work orders into correct windows.
    """
    workspace = Workspace.objects.create(name="WS4", slug="ws4")
    asset = Asset.objects.create(workspace=workspace, name="Asset 4", kind="PI")
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Task 4",
        cadence="monthly",
    )

    now = timezone.now()

    overdue = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now - timedelta(days=1),
        status="open",
    )
    next_7 = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now + timedelta(days=3),
        status="open",
    )
    next_30 = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now + timedelta(days=15),
        status="open",
    )
    future = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now + timedelta(days=40),
        status="open",
    )

    rf = RequestFactory()
    base_qs = WorkOrder.objects.all()
    model_admin = WorkOrderAdmin(WorkOrder, dj_admin.site)

    def run_filter(value):
        # This mimics Django admin: request.GET is a QueryDict,
        # and get_list_filter passes request.GET.copy() as params.
        request = rf.get("/admin/work/workorder/", {"due_window": value})
        params = request.GET.copy()  # mutable QueryDict
        flt = DueWindowFilter(request, params, WorkOrder, model_admin)
        return flt.queryset(request, base_qs)

    # Overdue
    assert list(run_filter("overdue")) == [overdue]

    # Next 7 days
    assert list(run_filter("next_7_days")) == [next_7]

    # Next 30 days (disjoint from next_7_days)
    assert list(run_filter("next_30_days")) == [next_30]

    # Future (>= 30 days)
    assert list(run_filter("future")) == [future]
