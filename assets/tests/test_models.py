# assets/tests/test_models.py

import datetime

import pytest
from django.db import IntegrityError, transaction

from assets.models import OS, Application, Asset, FormFactor, Project


@pytest.mark.django_db
def test_formfactor_creation_and_uniqueness():
    FormFactor.objects.create(name="Mini PC", slug="mini-pc")

    # name unique
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            FormFactor.objects.create(name="Mini PC", slug="mini-pc-2")

    # slug unique
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            FormFactor.objects.create(name="Mini PC 2", slug="mini-pc")


@pytest.mark.django_db
def test_os_creation_and_slug_unique():
    OS.objects.create(name="Raspberry Pi OS", version="11", slug="rpi-os-11")

    # slug must be unique
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            OS.objects.create(
                name="Raspberry Pi OS Lite",
                version="11",
                slug="rpi-os-11",
            )


@pytest.mark.django_db
def test_application_creation_and_slug_unique():
    Application.objects.create(name="Docker", version="27", slug="docker")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Application.objects.create(name="Docker 2", version="28", slug="docker")


@pytest.mark.django_db
def test_project_unique_per_workspace_and_slug(workspace, another_workspace):
    Project.objects.create(
        workspace=workspace,
        name="Homelab",
        description="Homelab infra",
        slug="homelab",
    )

    # Same workspace + same slug => IntegrityError
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Project.objects.create(
                workspace=workspace,
                name="Homelab again",
                description="Duplicate",
                slug="homelab",
            )

    # Different workspace + same slug is allowed
    other = Project.objects.create(
        workspace=another_workspace,
        name="Homelab Copy",
        description="Same slug, different workspace",
        slug="homelab",
    )
    assert other.pk is not None


@pytest.mark.django_db
def test_asset_basic_fields_and_relations(workspace):
    form_factor = FormFactor.objects.create(name="Pi 4", slug="pi-4")
    os_obj = OS.objects.create(name="Raspberry Pi OS", version="", slug="rpi-os")
    app1 = Application.objects.create(name="Docker", version="", slug="docker")
    app2 = Application.objects.create(name="Prometheus", version="", slug="prom")

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
        location="Lab Rack 1",
        purchase_date=datetime.date(2023, 1, 1),
        warranty_expires=datetime.date(2025, 1, 1),
        notes="Main monitoring Pi",
    )

    # M2M
    asset.applications.add(app1, app2)

    assert asset.workspace == workspace
    assert asset.project == project
    assert asset.form_factor == form_factor
    assert asset.os == os_obj
    assert list(asset.applications.all()) == [app1, app2]
    assert asset.kind == "PI"
    assert asset.location == "Lab Rack 1"
    assert asset.notes.startswith("Main monitoring Pi")


@pytest.mark.django_db
def test_asset_optional_fields_can_be_null_or_blank(workspace):
    asset = Asset.objects.create(
        workspace=workspace,
        project=None,
        name="Test Asset",
        kind="SRV",
        form_factor=None,
        os=None,
        location="",
        purchase_date=None,
        warranty_expires=None,
        notes="",
    )

    assert asset.project is None
    assert asset.form_factor is None
    assert asset.os is None
    assert asset.location == ""
    assert asset.purchase_date is None
    assert asset.warranty_expires is None
    assert asset.notes == ""
