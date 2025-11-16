# conftest.py

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Workspace


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        password="password123",
    )


@pytest.fixture
def another_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="anotheruser",
        password="password123",
    )


@pytest.fixture
def workspace(db):
    return Workspace.objects.create(
        name="Home Lab",
        slug="home-lab",
    )


@pytest.fixture
def another_workspace(db):
    return Workspace.objects.create(
        name="Work Lab",
        slug="work-lab",
    )


@pytest.fixture
def now():
    return timezone.now()
