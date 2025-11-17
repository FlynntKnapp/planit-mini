import pytest
from django.contrib import admin as dj_admin

from accounts.admin import CustomUserAdmin
from accounts.forms import CustomUserChangeForm, CustomUserCreationForm
from accounts.models import CustomUser


@pytest.fixture
def custom_user_admin():
    """
    Instantiate CustomUserAdmin once and reuse it in tests.
    """
    return CustomUserAdmin(CustomUser, dj_admin.site)


def test_uses_correct_add_form(custom_user_admin):
    """
    CustomUserAdmin.add_form should be CustomUserCreationForm.
    """
    assert custom_user_admin.add_form is CustomUserCreationForm


def test_uses_correct_change_form(custom_user_admin):
    """
    CustomUserAdmin.form should be CustomUserChangeForm.
    """
    assert custom_user_admin.form is CustomUserChangeForm


def test_uses_correct_model(custom_user_admin):
    """
    CustomUserAdmin.model should be CustomUser.
    """
    assert custom_user_admin.model is CustomUser


def test_list_display_exact_fields(custom_user_admin):
    """
    CustomUserAdmin.list_display should match the expected tuple, including
    the new is_superuser column.
    """
    expected = (
        "username",
        "email",
        "registration_accepted",
        "is_staff",
        "is_superuser",
    )
    assert custom_user_admin.list_display == expected


def test_list_filter_includes_registration_accepted_and_permissions(custom_user_admin):
    """
    Ensure list_filter includes the key filters we care about.
    """
    for field in ("registration_accepted", "is_staff", "is_superuser", "is_active"):
        assert field in custom_user_admin.list_filter


def test_search_fields_and_ordering(custom_user_admin):
    """
    Verify search_fields and ordering have been customized.
    """
    assert custom_user_admin.search_fields == (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    assert custom_user_admin.ordering == ("username",)


def test_get_fieldsets_returns_list_of_tuples(custom_user_admin):
    """
    CustomUserAdmin.get_fieldsets() should return a list of tuples.
    We call with obj=None (add view) and still expect a list-of-tuples.
    """
    fieldsets = custom_user_admin.get_fieldsets(request=None, obj=None)
    assert isinstance(fieldsets, list)
    assert fieldsets
    assert isinstance(fieldsets[0], tuple)


def test_get_fieldsets_includes_moderator_permissions_section(custom_user_admin):
    """
    Ensure 'Moderator Permissions' section with registration_accepted is
    inserted at the correct position (index 2) on the change view.
    """
    # Simulate change view by passing an object instance
    obj = CustomUser()
    fieldsets = custom_user_admin.get_fieldsets(request=None, obj=obj)
    fieldsets_as_list = list(fieldsets)

    # There should be at least three fieldsets now
    assert len(fieldsets_as_list) >= 3

    # "Moderator Permissions" should be the third fieldset (index 2)
    label, options = fieldsets_as_list[2]
    assert label == "Moderator Permissions"
    assert "fields" in options
    assert options["fields"] == ("registration_accepted",)


def test_add_fieldsets_includes_registration_accepted():
    """
    Ensure registration_accepted is also present on the add user form.
    """
    add_fieldsets = CustomUserAdmin.add_fieldsets
    assert isinstance(add_fieldsets, tuple)
    assert add_fieldsets

    _, add_options = add_fieldsets[0]
    fields = add_options.get("fields", ())
    assert "registration_accepted" in fields
