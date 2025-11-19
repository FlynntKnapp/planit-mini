# assets/tests/test_admin.py

from datetime import date, timedelta

import pytest
from django.contrib import admin as dj_admin
from django.utils import timezone

from assets.admin import (
    ApplicationAdmin,
    AssetAdmin,
    FormFactorAdmin,
    OSAdmin,
    ProjectAdmin,
)
from assets.models import OS, Application, Asset, FormFactor, Project
from core.models import Workspace
from work.admin import ActivityInstanceInline, WorkOrderInline
from work.models import MaintenanceTask, WorkOrder


@pytest.mark.parametrize(
    "model",
    [FormFactor, OS, Application, Project, Asset],
)
def test_models_are_registered_in_admin(model):
    """
    All asset-related models should be registered in the admin site.
    """
    assert model in dj_admin.site._registry


def test_form_factor_admin_configuration():
    ma = FormFactorAdmin(FormFactor, dj_admin.site)

    assert ma.list_display == ("name", "slug")
    assert ma.search_fields == ("name",)
    assert ma.prepopulated_fields == {"slug": ("name",)}


def test_os_admin_configuration():
    ma = OSAdmin(OS, dj_admin.site)

    assert ma.list_display == ("name", "version", "slug")
    assert ma.search_fields == ("name", "version")
    assert ma.list_filter == ("name",)
    assert ma.prepopulated_fields == {"slug": ("name",)}


def test_application_admin_configuration():
    ma = ApplicationAdmin(Application, dj_admin.site)

    assert ma.list_display == ("name", "version", "slug")
    assert ma.search_fields == ("name", "version")
    assert ma.prepopulated_fields == {"slug": ("name",)}


def test_project_admin_configuration():
    ma = ProjectAdmin(Project, dj_admin.site)

    assert ma.list_display == ("name", "workspace", "slug")
    assert ma.search_fields == ("name", "description", "slug")
    assert ma.list_filter == ("workspace",)
    assert ma.prepopulated_fields == {"slug": ("name",)}
    # Project now uses autocomplete for workspace instead of raw ID field
    assert ma.autocomplete_fields == ("workspace",)
    # No explicit raw_id_fields configured
    assert ma.raw_id_fields == ()


def test_asset_admin_configuration():
    ma = AssetAdmin(Asset, dj_admin.site)

    assert ma.list_display == (
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

    # Key filters still present (plus applications)
    for field in ("workspace", "kind", "form_factor", "os", "applications"):
        assert field in ma.list_filter

    # Ensure we can search by related names and notes
    for field in (
        "name",
        "location",
        "notes",
        "workspace__name",
        "project__name",
    ):
        assert field in ma.search_fields

    # Asset now uses autocomplete for these relations (no raw_id_fields)
    assert ma.autocomplete_fields == (
        "workspace",
        "project",
        "form_factor",
        "os",
        "applications",
    )
    # No filter_horizontal when using autocomplete
    assert ma.filter_horizontal == ()

    assert ma.date_hierarchy == "purchase_date"
    assert ma.list_select_related == ("workspace", "project", "form_factor", "os")
    assert ma.ordering == ("workspace", "name")

    # Inlines: WorkOrder + ActivityInstance on Asset
    assert WorkOrderInline in ma.inlines
    assert ActivityInstanceInline in ma.inlines


# --- AssetAdmin status helpers ---------------------------------------------


@pytest.mark.django_db
def test_warranty_status_variants():
    workspace = Workspace.objects.create(name="WS", slug="ws")

    today = date.today()
    expired = Asset.objects.create(
        workspace=workspace,
        name="Expired Asset",
        kind="PI",
        warranty_expires=today - timedelta(days=1),
    )
    expiring_soon = Asset.objects.create(
        workspace=workspace,
        name="Soon Asset",
        kind="PI",
        warranty_expires=today + timedelta(days=7),
    )
    active = Asset.objects.create(
        workspace=workspace,
        name="Active Asset",
        kind="PI",
        warranty_expires=today + timedelta(days=60),
    )
    no_warranty = Asset.objects.create(
        workspace=workspace,
        name="No Warranty Asset",
        kind="PI",
    )

    ma = AssetAdmin(Asset, dj_admin.site)

    assert ma.warranty_status(expired) == "Expired"
    assert ma.warranty_status(expiring_soon) == "Expiring soon"
    assert ma.warranty_status(active) == "Active"
    assert ma.warranty_status(no_warranty) == "n/a"


@pytest.mark.django_db
def test_next_due_status_variants():
    """
    Ensure next_due_status reports:
    - No open work
    - Overdue
    - Due today
    - Due soon
    - Scheduled
    """
    workspace = Workspace.objects.create(name="WS2", slug="ws2")
    asset = Asset.objects.create(workspace=workspace, name="Asset", kind="PI")
    task = MaintenanceTask.objects.create(
        workspace=workspace,
        name="Task",
        cadence="monthly",
    )

    ma = AssetAdmin(Asset, dj_admin.site)
    now = timezone.now()

    # No work orders
    assert ma.next_due_status(asset) == "No open work"

    # Overdue
    overdue = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now - timedelta(days=1),
        status="open",
    )
    assert ma.next_due_status(asset) == "Overdue"

    # Due today
    overdue.status = "done"
    overdue.save()
    due_today = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now + timedelta(hours=1),
        status="open",
    )
    assert ma.next_due_status(asset) == "Due today"

    # Due soon (within a week)
    due_today.status = "done"
    due_today.save()
    due_soon = WorkOrder.objects.create(
        workspace=workspace,
        asset=asset,
        task=task,
        due=now + timedelta(days=3),
        status="open",
    )
    assert ma.next_due_status(asset) == "Due soon"

    # Scheduled (> 7 days)
    due_soon.status = "done"
    due_soon.save()
    scheduled = WorkOrder.objects.create(  # noqa F841
        workspace=workspace,
        asset=asset,
        task=task,
        due=now + timedelta(days=10),
        status="open",
    )
    assert ma.next_due_status(asset) == "Scheduled"
