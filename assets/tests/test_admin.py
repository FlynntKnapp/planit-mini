import pytest
from django.contrib import admin as dj_admin

from assets.admin import (
    ApplicationAdmin,
    AssetAdmin,
    FormFactorAdmin,
    OSAdmin,
    ProjectAdmin,
)
from assets.models import Application, Asset, FormFactor, OS, Project


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
    assert ma.raw_id_fields == ("workspace",)
    assert ma.ordering == ("workspace", "name")


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
    )
    assert "workspace" in ma.list_filter
    assert "kind" in ma.list_filter
    assert "form_factor" in ma.list_filter
    assert "os" in ma.list_filter

    # Ensure we can search by related names and notes
    for field in (
        "name",
        "location",
        "notes",
        "workspace__name",
        "project__name",
    ):
        assert field in ma.search_fields

    assert ma.raw_id_fields == ("workspace", "project", "form_factor", "os")
    assert ma.filter_horizontal == ("applications",)
    assert ma.date_hierarchy == "purchase_date"
    assert ma.list_select_related == ("workspace", "project", "form_factor", "os")
    assert ma.ordering == ("workspace", "name")
