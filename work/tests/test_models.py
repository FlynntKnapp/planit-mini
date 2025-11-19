# work/tests/test_models.py

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from assets.models import OS, Application, Asset, FormFactor, Project
from work.models import ActivityInstance, MaintenanceTask, WorkOrder


def _create_asset(workspace):
    form_factor = FormFactor.objects.create(name="Pi 4", slug="pi-4")
    os_obj = OS.objects.create(name="Raspberry Pi OS", version="", slug="rpi-os")
    app = Application.objects.create(name="Docker", version="", slug="docker")
    project = Project.objects.create(
        workspace=workspace,
        name="Monitoring",
        description="Monitoring stack",
        slug="monitoring",
    )

    asset = Asset.objects.create(
        workspace=workspace,
        project=project,
        name="Pi-001",
        kind="PI",
        form_factor=form_factor,
        os=os_obj,
        location="Rack 1",
    )
    asset.applications.add(app)
    return asset


@pytest.mark.django_db
def test_maintenance_task_unique_per_workspace(workspace, another_workspace):
    MaintenanceTask.objects.create(
        workspace=workspace,
        name="Patch OS",
        cadence="monthly",
        description="Monthly OS patching",
    )

    # Same workspace + same name should violate unique_together
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            MaintenanceTask.objects.create(
                workspace=workspace,
                name="Patch OS",
                cadence="weekly",
                description="Different cadence but same name/workspace",
            )

    # Different workspace + same name is allowed
    task_other_ws = MaintenanceTask.objects.create(
        workspace=another_workspace,
        name="Patch OS",
        cadence="monthly",
        description="Same name, different workspace",
    )
    assert task_other_ws.pk is not None


@pytest.mark.django_db
def test_maintenance_task_threshold_json_optional_and_persisted(workspace):
    # Can create without specifying threshold_json
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Backup verify",
        cadence="weekly",
        description="Verify backups",
    )
    # Default should be an empty dict (or None, depending on your chosen default)
    assert task.threshold_json == {} or task.threshold_json is None

    # Can store structured JSON data
    thresholds = {"max_days_overdue": 7, "window": "30d"}
    task_with_thresholds = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Patch OS with thresholds",
        cadence="monthly",
        description="OS patching with thresholds",
        threshold_json=thresholds,
    )
    task_with_thresholds.refresh_from_db()
    assert task_with_thresholds.threshold_json == thresholds


@pytest.mark.django_db
def test_workorder_default_status_open(workspace, user):
    asset = _create_asset(workspace)
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Backup verify",
        cadence="weekly",
        description="Verify backups",
    )
    due = timezone.now()

    wo = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=due,
        assigned_to=user,
    )

    assert wo.status == "open"
    assert wo.workspace == workspace
    assert wo.asset == asset
    assert wo.task == task
    assert wo.assigned_to == user
    assert wo.requested_by is None


@pytest.mark.django_db
def test_workorder_status_choices(workspace):
    asset = _create_asset(workspace)
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Reboot",
        cadence="monthly",
        description="Monthly reboot",
    )
    due = timezone.now()

    wo_done = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=due,
        status="done",
    )
    wo_cancelled = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=due,
        status="cancelled",
    )

    assert wo_done.status == "done"
    assert wo_cancelled.status == "cancelled"


@pytest.mark.django_db
def test_activity_instance_can_be_created_without_workorder(workspace, user):
    asset = _create_asset(workspace)
    occurred_at = timezone.now()

    activity = ActivityInstance.objects.create(
        workspace=workspace,
        work_order=None,
        asset=asset,
        kind="checked",
        note="Checked basic health",
        occurred_at=occurred_at,
        performed_by=user,
    )

    assert activity.workspace == workspace
    assert activity.work_order is None
    assert activity.asset == asset
    assert activity.kind == "checked"
    assert activity.note == "Checked basic health"
    assert activity.occurred_at == occurred_at
    assert activity.performed_by == user


@pytest.mark.django_db
def test_activity_instance_kind_choices(workspace):
    asset = _create_asset(workspace)
    occurred_at = timezone.now()

    activity = ActivityInstance.objects.create(
        workspace=workspace,
        work_order=None,
        asset=asset,
        kind="backup_verified",
        note="Backup was verified",
        occurred_at=occurred_at,
        performed_by=None,
    )

    assert activity.kind == "backup_verified"


@pytest.mark.django_db
def test_workorder_cascade_on_asset_delete(workspace):
    asset = _create_asset(workspace)
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Test Task",
        cadence="weekly",
        description="Just a test",
    )
    due = timezone.now()

    wo = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=due,
    )
    assert WorkOrder.objects.filter(pk=wo.pk).exists()

    # Deleting asset should cascade and delete WorkOrder
    asset.delete()
    assert not WorkOrder.objects.filter(pk=wo.pk).exists()


@pytest.mark.django_db
def test_activityinstance_set_null_on_workorder_delete(workspace):
    asset = _create_asset(workspace)
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Test Task",
        cadence="weekly",
        description="Just a test",
    )
    due = timezone.now()

    wo = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=due,
    )

    activity = ActivityInstance.objects.create(
        workspace=workspace,
        work_order=wo,
        asset=asset,
        kind="patched",
        note="Patched system",
        occurred_at=timezone.now(),
    )

    # Delete work order — ActivityInstance.work_order should become NULL (SET_NULL)
    wo.delete()
    activity.refresh_from_db()
    assert activity.work_order is None


@pytest.mark.django_db
def test_set_null_on_user_delete_for_assigned_and_performed(
    workspace, user, another_user
):
    asset = _create_asset(workspace)
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Test Task",
        cadence="weekly",
        description="Just a test",
    )
    due = timezone.now()
    User = get_user_model()  # noqa F401

    wo = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=due,
        assigned_to=user,
        requested_by=another_user,
    )

    activity = ActivityInstance.objects.create(
        workspace=workspace,
        work_order=wo,
        asset=asset,
        kind="checked",
        note="Checked by user",
        occurred_at=timezone.now(),
        performed_by=user,
    )

    # Deleting users should SET_NULL on their respective FKs
    user.delete()
    another_user.delete()

    wo.refresh_from_db()
    activity.refresh_from_db()

    assert wo.assigned_to is None
    assert wo.requested_by is None
    assert activity.performed_by is None
