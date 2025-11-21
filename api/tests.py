# api/tests.py

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from assets.models import OS, Application, Asset, FormFactor, Project
from core.models import Membership, Workspace
from work.models import ActivityInstance, MaintenanceTask, WorkOrder

User = get_user_model()


class APITestSetup(TestCase):
    """Base test class with common setup for API tests."""

    def setUp(self):
        """Set up test data for API tests."""
        # Create users
        self.staff_user = User.objects.create_user(
            username="staff_user", password="testpass123", is_staff=True
        )
        self.manager_user = User.objects.create_user(
            username="manager_user", password="testpass123"
        )
        self.viewer_user = User.objects.create_user(
            username="viewer_user", password="testpass123"
        )
        self.non_member_user = User.objects.create_user(
            username="non_member", password="testpass123"
        )

        # Create maintenance_manager group and add manager_user
        self.maintenance_manager_group = Group.objects.create(
            name="maintenance_manager"
        )
        self.manager_user.groups.add(self.maintenance_manager_group)

        # Create workspaces
        self.workspace1 = Workspace.objects.create(name="Test Workspace 1", slug="ws1")
        self.workspace2 = Workspace.objects.create(name="Test Workspace 2", slug="ws2")

        # Create memberships
        Membership.objects.create(
            user=self.manager_user, workspace=self.workspace1, role="manager"
        )
        Membership.objects.create(
            user=self.viewer_user, workspace=self.workspace1, role="viewer"
        )

        # Create API client
        self.client = APIClient()


class WorkspaceAPITest(APITestSetup):
    """Tests for Workspace API endpoints."""

    def test_list_workspaces_authenticated(self):
        """Authenticated users can list workspaces they belong to."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/workspaces/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["slug"], "ws1")

    def test_list_workspaces_unauthenticated(self):
        """Unauthenticated users cannot list workspaces."""
        response = self.client.get("/api/workspaces/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_see_all_workspaces(self):
        """Staff users can see all workspaces."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get("/api/workspaces/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_viewer_can_create_workspace(self):
        """Viewer users can create workspaces (per permission design)."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.post(
            "/api/workspaces/", {"name": "New Workspace", "slug": "new-ws"}
        )
        # Permission allows creates at global level (no object-level check for POST)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Workspace")

    def test_manager_can_create_workspace(self):
        """Manager users can create workspaces."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(
            "/api/workspaces/", {"name": "New Workspace", "slug": "new-ws"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Workspace")


class AssetAPITest(APITestSetup):
    """Tests for Asset API endpoints."""

    def setUp(self):
        """Set up additional test data for assets."""
        super().setUp()
        self.form_factor = FormFactor.objects.create(name="Desktop", slug="desktop")
        self.os = OS.objects.create(name="Ubuntu", version="22.04", slug="ubuntu-2204")
        self.app1 = Application.objects.create(
            name="Docker", version="24.0", slug="docker-240"
        )
        self.project = Project.objects.create(
            workspace=self.workspace1, name="Test Project", slug="test-proj"
        )
        self.asset = Asset.objects.create(
            workspace=self.workspace1,
            project=self.project,
            name="Test Server",
            kind="SRV",
            form_factor=self.form_factor,
            os=self.os,
            location="Office",
        )
        self.asset.applications.add(self.app1)

    def test_list_assets_authenticated(self):
        """Authenticated users can list assets from their workspace."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/assets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Server")

    def test_asset_includes_applications(self):
        """Asset response includes nested applications."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get(f"/api/assets/{self.asset.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["applications"]), 1)
        self.assertEqual(response.data["applications"][0]["name"], "Docker")

    def test_filter_assets_by_form_factor(self):
        """Assets can be filtered by form factor."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get(f"/api/assets/?form_factor={self.form_factor.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_assets_by_name_contains(self):
        """Assets can be filtered by name substring."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/assets/?name__icontains=server")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_viewer_can_create_asset(self):
        """Viewer users can create assets (per permission design)."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.post(
            "/api/assets/",
            {
                "workspace": "ws1",
                "name": "New Asset",
                "kind": "LAP",
            },
        )
        # Permission allows creates at global level (no object-level check for POST)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Asset")

    def test_manager_can_create_asset(self):
        """Manager users can create assets."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(
            "/api/assets/",
            {
                "workspace": "ws1",
                "name": "New Asset",
                "kind": "LAP",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Asset")


class WorkOrderAPITest(APITestSetup):
    """Tests for WorkOrder API endpoints."""

    def setUp(self):
        """Set up additional test data for work orders."""
        super().setUp()
        self.form_factor = FormFactor.objects.create(name="Desktop", slug="desktop")
        self.asset = Asset.objects.create(
            workspace=self.workspace1,
            name="Test Server",
            kind="SRV",
            form_factor=self.form_factor,
        )
        self.task = MaintenanceTask.objects.create(
            workspace=self.workspace1, name="Monthly Check", cadence="monthly"
        )
        self.work_order = WorkOrder.objects.create(
            workspace=self.workspace1,
            asset=self.asset,
            task=self.task,
            due=timezone.now() + timedelta(days=7),
            status="open",
            assigned_to=self.manager_user,
        )

    def test_list_work_orders_authenticated(self):
        """Authenticated users can list work orders from their workspace."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/work-orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_work_orders_by_status(self):
        """Work orders can be filtered by status."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/work-orders/?status=open")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_work_orders_by_asset(self):
        """Work orders can be filtered by asset."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get(f"/api/work-orders/?asset={self.asset.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_work_order_ordering(self):
        """Work orders are ordered by due date descending by default."""
        # Create another work order with earlier due date
        WorkOrder.objects.create(
            workspace=self.workspace1,
            asset=self.asset,
            task=self.task,
            due=timezone.now() + timedelta(days=14),
            status="open",
        )
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/work-orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        # Most recent due date should be first (descending order)
        self.assertGreater(
            response.data["results"][0]["due"], response.data["results"][1]["due"]
        )


class ActivityInstanceAPITest(APITestSetup):
    """Tests for ActivityInstance API endpoints."""

    def setUp(self):
        """Set up additional test data for activities."""
        super().setUp()
        self.form_factor = FormFactor.objects.create(name="Desktop", slug="desktop")
        self.asset = Asset.objects.create(
            workspace=self.workspace1,
            name="Test Server",
            kind="SRV",
            form_factor=self.form_factor,
        )
        self.activity = ActivityInstance.objects.create(
            workspace=self.workspace1,
            asset=self.asset,
            kind="checked",
            note="Regular check completed",
            occurred_at=timezone.now(),
            performed_by=self.manager_user,
        )

    def test_list_activities_authenticated(self):
        """Authenticated users can list activities from their workspace."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/activities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_activities_by_kind(self):
        """Activities can be filtered by kind."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/activities/?kind=checked")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_activities_ordering(self):
        """Activities are ordered by occurred_at descending by default."""
        # Create another activity with earlier date
        ActivityInstance.objects.create(
            workspace=self.workspace1,
            asset=self.asset,
            kind="patched",
            note="Security patch applied",
            occurred_at=timezone.now() - timedelta(days=7),
            performed_by=self.manager_user,
        )
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/activities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        # Most recent activity should be first
        self.assertGreater(
            response.data["results"][0]["occurred_at"],
            response.data["results"][1]["occurred_at"],
        )


class ThrottlingTest(APITestSetup):
    """Tests for API throttling."""

    def test_staff_user_not_throttled(self):
        """Staff users should not be throttled."""
        self.client.force_authenticate(user=self.staff_user)
        # Make multiple requests - staff should not be throttled
        for _ in range(5):
            response = self.client.get("/api/workspaces/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionsTest(APITestSetup):
    """Tests for API permissions."""

    def test_non_member_cannot_access_workspace_data(self):
        """Users who are not members of a workspace cannot access its data."""
        self.client.force_authenticate(user=self.non_member_user)
        response = self.client.get("/api/workspaces/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty results
        self.assertEqual(len(response.data["results"]), 0)

