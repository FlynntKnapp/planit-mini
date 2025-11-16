# core/tests/test_models.py

import pytest
from django.db import IntegrityError, transaction

from core.models import Membership, Workspace


@pytest.mark.django_db
def test_workspace_str_returns_name(workspace):
    assert str(workspace) == "Home Lab"


@pytest.mark.django_db
def test_workspace_name_and_slug_unique():
    Workspace.objects.create(name="Lab A", slug="lab-a")

    # name unique
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Workspace.objects.create(name="Lab A", slug="lab-a-2")

    # slug unique
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Workspace.objects.create(name="Lab B", slug="lab-a")


@pytest.mark.django_db
def test_membership_unique_per_user_and_workspace(user, workspace):
    Membership.objects.create(user=user, workspace=workspace)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Membership.objects.create(user=user, workspace=workspace)


@pytest.mark.django_db
def test_membership_default_role_viewer(user, workspace):
    membership = Membership.objects.create(user=user, workspace=workspace)
    assert membership.role == "viewer"
