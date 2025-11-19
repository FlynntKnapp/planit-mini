import pytest
from django.contrib import admin as dj_admin

from core.admin import MembershipAdmin, MembershipInline, WorkspaceAdmin
from core.models import Membership, Workspace


@pytest.mark.parametrize("model", [Workspace, Membership])
def test_models_are_registered_in_admin(model):
    """
    Both Workspace and Membership should be registered in the admin site.
    """
    assert model in dj_admin.site._registry


def test_workspace_admin_configuration():
    ma = WorkspaceAdmin(Workspace, dj_admin.site)

    assert ma.list_display == ("name", "slug")
    assert ma.search_fields == ("name", "slug")
    assert ma.prepopulated_fields == {"slug": ("name",)}
    assert ma.inlines == [MembershipInline]
    assert ma.ordering == ("name",)


def test_membership_inline_configuration():
    inline = MembershipInline(Workspace, dj_admin.site)

    assert inline.model is Membership
    assert inline.extra == 1
    # Inline now uses autocomplete for user only
    assert inline.autocomplete_fields == ("user",)
    # No raw_id_fields explicitly configured
    assert inline.raw_id_fields == ()


def test_membership_admin_configuration():
    ma = MembershipAdmin(Membership, dj_admin.site)

    assert ma.list_display == ("user", "workspace", "role")
    assert ma.list_filter == ("role", "workspace")

    for field in (
        "user__username",
        "user__email",
        "workspace__name",
    ):
        assert field in ma.search_fields

    # Membership admin now uses autocomplete, not raw_id_fields
    assert ma.autocomplete_fields == ("user", "workspace")
    assert ma.raw_id_fields == ()
    assert ma.ordering == ("workspace", "user")
