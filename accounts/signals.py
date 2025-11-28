# accounts/signals.py

from django.apps import apps
from django.db.models.signals import post_migrate


def create_maintenance_groups(sender, **kwargs) -> None:
    """
    Ensure default maintenance groups exist after migrations.

    This function is intended to be connected to Django's ``post_migrate``
    signal. After migrations are applied, it makes sure the
    ``maintenance_viewer`` and ``maintenance_manager`` groups exist in
    the auth ``Group`` model, creating them if necessary.

    Args:
        sender: The app configuration that sent the signal (typically a
            Django ``AppConfig`` instance).
        **kwargs: Additional keyword arguments provided by the signal.
            Common values include ``using`` (the database alias) and
            ``app_config`` (the app whose migrations just ran).

    Returns:
        None
    """
    Group = apps.get_model("auth", "Group")

    for name in ("maintenance_viewer", "maintenance_manager"):
        Group.objects.get_or_create(name=name)


def connect_signals():
    post_migrate.connect(
        create_maintenance_groups, dispatch_uid="create_maintenance_groups"
    )
