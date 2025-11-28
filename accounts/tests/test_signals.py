# accounts/tests/test_signals.py

import pytest
from django.apps import apps
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate

from accounts.signals import create_maintenance_groups


GROUP_NAMES = ("maintenance_viewer", "maintenance_manager")


@pytest.mark.django_db
def test_create_maintenance_groups_creates_groups():
    """
    Directly calling create_maintenance_groups should ensure the two
    maintenance groups exist in the auth Group model.
    """
    # Start from a clean slate for these names
    Group.objects.filter(name__in=GROUP_NAMES).delete()

    app_config = apps.get_app_config("accounts")

    # Call the signal handler directly
    create_maintenance_groups(sender=app_config)

    for name in GROUP_NAMES:
        assert Group.objects.filter(name=name).exists(), f"Group {name} was not created"


@pytest.mark.django_db
def test_create_maintenance_groups_is_idempotent():
    """
    Calling create_maintenance_groups multiple times should not create
    duplicate groups (get_or_create should keep this idempotent).
    """
    Group.objects.filter(name__in=GROUP_NAMES).delete()

    app_config = apps.get_app_config("accounts")

    # Call the handler twice
    create_maintenance_groups(sender=app_config)
    create_maintenance_groups(sender=app_config)

    # We should still only have one of each group
    for name in GROUP_NAMES:
        assert Group.objects.filter(name=name).count() == 1


@pytest.mark.django_db
def test_post_migrate_signal_creates_groups():
    """
    Ensure that the post_migrate signal wiring in AccountsConfig.ready()
    actually results in the groups being created when post_migrate is sent.
    This tests both:
      - the signal connection (connect_signals / ready)
      - the handler behavior (create_maintenance_groups)
    """
    Group.objects.filter(name__in=GROUP_NAMES).delete()

    app_config = apps.get_app_config("accounts")

    # Simulate Django sending post_migrate for the accounts app.
    # The signal handler should be connected and will run.
    post_migrate.send(
        sender=app_config.__class__,
        app_config=app_config,
        verbosity=0,
        interactive=False,
        using="default",
    )

    for name in GROUP_NAMES:
        assert Group.objects.filter(
            name=name
        ).exists(), f"Group {name} was not created via post_migrate"
