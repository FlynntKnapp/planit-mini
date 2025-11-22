# core/management/commands/seed_demo_data.py

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from assets.models import OS, Application, Asset, FormFactor, Project
from core.models import Membership, Workspace
from work.models import ActivityInstance, MaintenanceTask, WorkOrder


class Command(BaseCommand):
    help = "Seed demo/DEV data for planit-mini"

    def handle(self, *args, **options):
        now = timezone.now()

        users = self._create_users()
        workspaces = self._create_workspaces()
        self._create_memberships(users, workspaces)

        form_factors = self._create_form_factors()
        os_objects = self._create_os()
        applications = self._create_applications()
        projects = self._create_projects(workspaces)

        assets = self._create_assets(
            workspaces,
            projects,
            form_factors,
            os_objects,
            applications,
        )
        self._set_asset_warranties(assets)

        tasks = self._create_tasks(workspaces)

        workorders = self._create_workorders(
            workspaces,
            assets,
            tasks,
            users,
            now,
        )

        self._create_activity_instances(
            workspaces,
            workorders,
            assets,
            users,
            now,
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    # -------- Users / Workspaces / Memberships --------------------

    def _create_users(self):
        User = get_user_model()
        users_data = [
            {"username": "tiny", "email": "tiny@example.com"},
            {"username": "alice", "email": "alice@example.com"},
            {"username": "bob", "email": "bob@example.com"},
        ]

        users = {}
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "is_staff": True,
                },
            )
            if created:
                user.set_password("devpassword")
                if hasattr(user, "registration_accepted"):
                    user.registration_accepted = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {user.username}"))
            users[data["username"]] = user
        return users

    def _create_workspaces(self):
        workspaces_data = [
            {"name": "Home Lab", "slug": "home-lab"},
            {"name": "Laptop Fleet", "slug": "laptop-fleet"},
            {"name": "Client A", "slug": "client-a"},
        ]

        workspaces = {}
        for data in workspaces_data:
            ws, _ = Workspace.objects.get_or_create(
                slug=data["slug"],
                defaults={"name": data["name"]},
            )
            workspaces[data["slug"]] = ws
        return workspaces

    def _create_memberships(self, users, workspaces):
        memberships_data = [
            {"username": "tiny", "workspace_slug": "home-lab", "role": "admin"},
            {"username": "tiny", "workspace_slug": "laptop-fleet", "role": "admin"},
            {"username": "tiny", "workspace_slug": "client-a", "role": "manager"},
            {"username": "alice", "workspace_slug": "home-lab", "role": "manager"},
            {"username": "alice", "workspace_slug": "client-a", "role": "viewer"},
            {"username": "bob", "workspace_slug": "home-lab", "role": "viewer"},
            {"username": "bob", "workspace_slug": "laptop-fleet", "role": "manager"},
        ]

        for data in memberships_data:
            user = users[data["username"]]
            ws = workspaces[data["workspace_slug"]]
            Membership.objects.get_or_create(
                user=user,
                workspace=ws,
                defaults={"role": data["role"]},
            )

    # -------- Assets & related seed data --------------------------

    def _create_form_factors(self):
        form_factors_data = [
            {"name": "Raspberry Pi 4B", "slug": "rpi-4b"},
            {"name": "Mini PC", "slug": "mini-pc"},
            {"name": "1U Rack Server", "slug": "rack-1u"},
            {"name": "2U Rack Server", "slug": "rack-2u"},
            {"name": "13-inch Laptop", "slug": "laptop-13"},
            {"name": "15-inch Laptop", "slug": "laptop-15"},
        ]

        form_factors = {}
        for data in form_factors_data:
            ff, _ = FormFactor.objects.get_or_create(
                slug=data["slug"],
                defaults={"name": data["name"]},
            )
            form_factors[data["slug"]] = ff
        return form_factors

    def _create_os(self):
        os_data = [
            {
                "name": "Ubuntu Server",
                "version": "22.04 LTS",
                "slug": "ubuntu-22-04",
            },
            {
                "name": "Debian",
                "version": "12",
                "slug": "debian-12",
            },
            {
                "name": "Proxmox VE",
                "version": "8",
                "slug": "proxmox-8",
            },
            {
                "name": "Raspberry Pi OS",
                "version": "Bookworm",
                "slug": "rpi-os-bookworm",
            },
            {
                "name": "Windows",
                "version": "11 Pro",
                "slug": "windows-11-pro",
            },
        ]

        os_objects = {}
        for data in os_data:
            os_obj, _ = OS.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "version": data["version"],
                },
            )
            os_objects[data["slug"]] = os_obj
        return os_objects

    def _create_applications(self):
        applications_data = [
            {"name": "Docker Engine", "version": "24", "slug": "docker-24"},
            {"name": "PostgreSQL", "version": "16", "slug": "postgres-16"},
            {"name": "Nginx", "version": "1.26", "slug": "nginx-1-26"},
            {"name": "WireGuard", "version": "1.0", "slug": "wireguard-1"},
            {"name": "Prometheus", "version": "2.55", "slug": "prometheus-2-55"},
            {"name": "Grafana", "version": "11", "slug": "grafana-11"},
            {"name": "VS Code Server", "version": "latest", "slug": "vscode-server"},
        ]

        applications = {}
        for data in applications_data:
            app, _ = Application.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "version": data["version"],
                },
            )
            applications[data["slug"]] = app
        return applications

    def _create_projects(self, workspaces):
        projects_data = [
            {
                "workspace_slug": "home-lab",
                "name": "Home Monitoring",
                "slug": "home-monitoring",
                "description": "Monitoring for home lab services and hardware.",
            },
            {
                "workspace_slug": "home-lab",
                "name": "Backup System",
                "slug": "backup-system",
                "description": "Backups for important services.",
            },
            {
                "workspace_slug": "laptop-fleet",
                "name": "Laptop Hardening",
                "slug": "laptop-hardening",
                "description": "Security hardening for dev laptops.",
            },
            {
                "workspace_slug": "laptop-fleet",
                "name": "Remote Access",
                "slug": "remote-access",
                "description": "Remote access tooling for laptops.",
            },
            {
                "workspace_slug": "client-a",
                "name": "Client A Onboarding",
                "slug": "client-a-onboarding",
                "description": "Initial setup for Client A infrastructure.",
            },
        ]

        projects = {}
        for data in projects_data:
            ws = workspaces[data["workspace_slug"]]
            proj, _ = Project.objects.get_or_create(
                workspace=ws,
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                },
            )
            projects[(data["workspace_slug"], data["slug"])] = proj
        return projects

    def _create_assets(
        self,
        workspaces,
        projects,
        form_factors,
        os_objects,
        applications,
    ):
        assets_data = [
            {
                "workspace_slug": "home-lab",
                "project_slug": "home-monitoring",
                "name": "RPi4 Monitoring Node",
                "kind": "PI",
                "form_factor_slug": "rpi-4b",
                "os_slug": "rpi-os-bookworm",
                "location": "Rack 1",
                "applications": ["prometheus-2-55", "grafana-11"],
            },
            {
                "workspace_slug": "home-lab",
                "project_slug": "backup-system",
                "name": "Backup Server",
                "kind": "SRV",
                "form_factor_slug": "rack-2u",
                "os_slug": "debian-12",
                "location": "Rack 2",
                "applications": ["postgres-16", "docker-24"],
            },
            {
                "workspace_slug": "home-lab",
                "project_slug": "home-monitoring",
                "name": "Proxmox Host",
                "kind": "SRV",
                "form_factor_slug": "rack-1u",
                "os_slug": "proxmox-8",
                "location": "Rack 1",
                "applications": ["docker-24"],
            },
            {
                "workspace_slug": "laptop-fleet",
                "project_slug": "laptop-hardening",
                "name": "Tiny Dev Laptop",
                "kind": "LAP",
                "form_factor_slug": "laptop-13",
                "os_slug": "windows-11-pro",
                "location": "Home Office",
                "applications": ["vscode-server", "wireguard-1"],
            },
            {
                "workspace_slug": "laptop-fleet",
                "project_slug": "remote-access",
                "name": "Travel Laptop",
                "kind": "LAP",
                "form_factor_slug": "laptop-15",
                "os_slug": "ubuntu-22-04",
                "location": "Travel Bag",
                "applications": ["docker-24", "wireguard-1"],
            },
            {
                "workspace_slug": "client-a",
                "project_slug": "client-a-onboarding",
                "name": "Client A DB Server",
                "kind": "SRV",
                "form_factor_slug": "rack-2u",
                "os_slug": "ubuntu-22-04",
                "location": "Client A DC",
                "applications": ["postgres-16", "nginx-1-26"],
            },
        ]

        assets = {}
        for data in assets_data:
            ws = workspaces[data["workspace_slug"]]
            proj = projects[(data["workspace_slug"], data["project_slug"])]
            ff = form_factors[data["form_factor_slug"]]
            os_obj = os_objects[data["os_slug"]]

            asset, _ = Asset.objects.get_or_create(
                workspace=ws,
                name=data["name"],
                defaults={
                    "project": proj,
                    "kind": data["kind"],
                    "form_factor": ff,
                    "os": os_obj,
                    "location": data["location"],
                },
            )
            app_objs = [applications[s] for s in data["applications"]]
            asset.applications.set(app_objs)
            assets[data["name"]] = asset
        return assets

    def _set_asset_warranties(self, assets):
        today = timezone.now().date()
        warranty_config = {
            "RPi4 Monitoring Node": {
                "purchase_date": today - timedelta(days=365),
                "warranty_expires": today - timedelta(days=10),
            },
            "Backup Server": {
                "purchase_date": today - timedelta(days=200),
                "warranty_expires": today + timedelta(days=5),
            },
            "Proxmox Host": {
                "purchase_date": today - timedelta(days=90),
                "warranty_expires": today + timedelta(days=120),
            },
            "Tiny Dev Laptop": {
                "purchase_date": today - timedelta(days=400),
                "warranty_expires": None,
            },
        }

        for asset_name, cfg in warranty_config.items():
            asset = assets.get(asset_name)
            if not asset:
                continue
            asset.purchase_date = cfg["purchase_date"]
            asset.warranty_expires = cfg["warranty_expires"]
            asset.save()

    # -------- Tasks / WorkOrders / Activities ---------------------

    def _create_tasks(self, workspaces):
        tasks_data = [
            {
                "workspace_slug": "home-lab",
                "name": "Apply OS updates",
                "cadence": "monthly",
                "description": "Install OS updates and reboot if required.",
            },
            {
                "workspace_slug": "home-lab",
                "name": "Check backups",
                "cadence": "weekly",
                "description": "Verify backup jobs completed successfully.",
            },
            {
                "workspace_slug": "laptop-fleet",
                "name": "Laptop patching",
                "cadence": "monthly",
                "description": "Patch OS and critical apps on laptops.",
            },
            {
                "workspace_slug": "laptop-fleet",
                "name": "VPN connectivity test",
                "cadence": "weekly",
                "description": "Ensure laptops can reach home VPN.",
            },
            {
                "workspace_slug": "client-a",
                "name": "Database maintenance",
                "cadence": "monthly",
                "description": "VACUUM / ANALYZE and index checks.",
            },
        ]

        tasks = {}
        for data in tasks_data:
            ws = workspaces[data["workspace_slug"]]
            task, _ = MaintenanceTask.objects.get_or_create(
                workspace=ws,
                name=data["name"],
                defaults={
                    "cadence": data["cadence"],
                    "description": data["description"],
                },
            )
            tasks[(data["workspace_slug"], data["name"])] = task
        return tasks

    def _build_workorders_data(self):
        base_data = [
            {
                "workspace_slug": "home-lab",
                "asset_name": "RPi4 Monitoring Node",
                "task_name": "Apply OS updates",
                "due_delta_days": 7,
                "status": "open",
                "assigned_to": "tiny",
                "requested_by": "alice",
            },
            {
                "workspace_slug": "home-lab",
                "asset_name": "Backup Server",
                "task_name": "Check backups",
                "due_delta_days": 1,
                "status": "open",
                "assigned_to": "alice",
                "requested_by": "tiny",
            },
            {
                "workspace_slug": "home-lab",
                "asset_name": "Proxmox Host",
                "task_name": "Apply OS updates",
                "due_delta_days": 3,
                "status": "open",
                "assigned_to": "bob",
                "requested_by": "tiny",
            },
            {
                "workspace_slug": "laptop-fleet",
                "asset_name": "Tiny Dev Laptop",
                "task_name": "Laptop patching",
                "due_delta_days": 14,
                "status": "open",
                "assigned_to": "tiny",
                "requested_by": "bob",
            },
            {
                "workspace_slug": "laptop-fleet",
                "asset_name": "Travel Laptop",
                "task_name": "VPN connectivity test",
                "due_delta_days": 2,
                "status": "open",
                "assigned_to": "alice",
                "requested_by": "tiny",
            },
            {
                "workspace_slug": "client-a",
                "asset_name": "Client A DB Server",
                "task_name": "Database maintenance",
                "due_delta_days": 10,
                "status": "open",
                "assigned_to": "tiny",
                "requested_by": "alice",
            },
        ]

        extra_workorders = [
            {
                "workspace_slug": "home-lab",
                "asset_name": "Backup Server",
                "task_name": "Check backups",
                "due_delta_days": -2,
                "status": "open",
                "assigned_to": "alice",
                "requested_by": "tiny",
            },
            {
                "workspace_slug": "home-lab",
                "asset_name": "RPi4 Monitoring Node",
                "task_name": "Apply OS updates",
                "due_delta_days": 0,
                "status": "open",
                "assigned_to": "tiny",
                "requested_by": "alice",
            },
            {
                "workspace_slug": "laptop-fleet",
                "asset_name": "Tiny Dev Laptop",
                "task_name": "Laptop patching",
                "due_delta_days": 45,
                "status": "open",
                "assigned_to": "tiny",
                "requested_by": "bob",
            },
        ]

        base_data.extend(extra_workorders)
        return base_data

    def _create_workorders(
        self,
        workspaces,
        assets,
        tasks,
        users,
        now,
    ):
        workorders_data = self._build_workorders_data()
        workorders = {}

        for idx, data in enumerate(workorders_data, start=1):
            ws = workspaces[data["workspace_slug"]]
            asset = assets[data["asset_name"]]
            task = tasks[(data["workspace_slug"], data["task_name"])]
            assigned_to = users[data["assigned_to"]]
            requested_by = users[data["requested_by"]]

            due = now + timedelta(days=data["due_delta_days"])

            wo, _ = WorkOrder.objects.get_or_create(
                workspace=ws,
                asset=asset,
                task=task,
                due=due,
                defaults={
                    "status": data["status"],
                    "assigned_to": assigned_to,
                    "requested_by": requested_by,
                },
            )
            workorders[idx] = wo
        return workorders

    def _create_activity_instances(
        self,
        workspaces,
        workorders,
        assets,
        users,
        now,
    ):
        activities_data = [
            {
                "workspace_slug": "home-lab",
                "workorder_idx": 1,
                "asset_name": "RPi4 Monitoring Node",
                "kind": "checked",
                "note": "Checked CPU temperature and disk usage.",
                "performed_by": "tiny",
                "occurred_delta_hours": -24,
            },
            {
                "workspace_slug": "home-lab",
                "workorder_idx": 2,
                "asset_name": "Backup Server",
                "kind": "backup_verified",
                "note": "Verified last night's backup snapshot.",
                "performed_by": "alice",
                "occurred_delta_hours": -12,
            },
            {
                "workspace_slug": "home-lab",
                "workorder_idx": 3,
                "asset_name": "Proxmox Host",
                "kind": "patched",
                "note": "Installed security updates on hypervisor.",
                "performed_by": "bob",
                "occurred_delta_hours": -6,
            },
            {
                "workspace_slug": "laptop-fleet",
                "workorder_idx": 4,
                "asset_name": "Tiny Dev Laptop",
                "kind": "patched",
                "note": "Applied OS patches and restarted.",
                "performed_by": "tiny",
                "occurred_delta_hours": -3,
            },
            {
                "workspace_slug": "laptop-fleet",
                "workorder_idx": 5,
                "asset_name": "Travel Laptop",
                "kind": "checked",
                "note": "Verified VPN connects over cellular.",
                "performed_by": "alice",
                "occurred_delta_hours": -1,
            },
            {
                "workspace_slug": "client-a",
                "workorder_idx": 6,
                "asset_name": "Client A DB Server",
                "kind": "backup_verified",
                "note": "Checked WAL archiving and backup status.",
                "performed_by": "tiny",
                "occurred_delta_hours": -2,
            },
            # NEW: a second activity on the same asset/work order to show
            # recent-first ordering
            {
                "workspace_slug": "home-lab",
                "workorder_idx": 1,
                "asset_name": "RPi4 Monitoring Node",
                "kind": "checked",
                "note": "Quick follow-up check on monitoring node.",
                "performed_by": "tiny",
                "occurred_delta_hours": -1,
            },
        ]

        for data in activities_data:
            ws = workspaces[data["workspace_slug"]]
            wo = workorders[data["workorder_idx"]]
            asset = assets[data["asset_name"]]
            performed_by = users[data["performed_by"]]
            occurred_at = now + timedelta(hours=data["occurred_delta_hours"])

            ActivityInstance.objects.get_or_create(
                workspace=ws,
                work_order=wo,
                asset=asset,
                kind=data["kind"],
                occurred_at=occurred_at,
                defaults={
                    "note": data["note"],
                    "performed_by": performed_by,
                },
            )
