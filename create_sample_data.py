#!/usr/bin/env python
"""
Script to create sample data for Django Admin screenshots.
This populates all models with realistic data to demonstrate admin features.
"""
import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from accounts.models import CustomUser
from core.models import Workspace, Membership
from assets.models import FormFactor, OS, Application, Project, Asset
from work.models import MaintenanceTask, WorkOrder, ActivityInstance


def create_sample_data():
    print("Creating sample data...")
    
    # Get or create users
    admin = CustomUser.objects.get(username="admin")
    testuser, _ = CustomUser.objects.get_or_create(
        username="testuser",
        defaults={
            "email": "user@example.com",
            "registration_accepted": True,
            "is_staff": False,
        }
    )
    
    # Create additional users for variety
    users = []
    for i, (name, accepted, staff) in enumerate([
        ("john_doe", True, False),
        ("jane_smith", True, True),
        ("bob_jones", False, False),
        ("alice_brown", True, False),
    ]):
        user, created = CustomUser.objects.get_or_create(
            username=name,
            defaults={
                "email": f"{name}@example.com",
                "first_name": name.split("_")[0].title(),
                "last_name": name.split("_")[1].title() if "_" in name else "",
                "registration_accepted": accepted,
                "is_staff": staff,
            }
        )
        users.append(user)
        if created:
            print(f"  Created user: {name}")
    
    # Create Workspaces
    workspaces = []
    for ws_name in ["Personal", "Homelab", "Office", "Development"]:
        ws, created = Workspace.objects.get_or_create(
            name=ws_name,
            defaults={"slug": ws_name.lower()}
        )
        workspaces.append(ws)
        if created:
            print(f"  Created workspace: {ws_name}")
    
    # Create Memberships
    memberships = [
        (admin, workspaces[0], "admin"),
        (admin, workspaces[1], "admin"),
        (testuser, workspaces[0], "viewer"),
        (users[0], workspaces[0], "manager"),
        (users[1], workspaces[1], "admin"),
        (users[2], workspaces[2], "viewer"),
        (users[3], workspaces[1], "manager"),
    ]
    for user, workspace, role in memberships:
        Membership.objects.get_or_create(
            user=user,
            workspace=workspace,
            defaults={"role": role}
        )
    print(f"  Created {len(memberships)} memberships")
    
    # Create FormFactors
    form_factors = []
    for ff_name in ["Tower", "Rack Mount", "Mini PC", "Raspberry Pi", "Laptop"]:
        ff, created = FormFactor.objects.get_or_create(
            name=ff_name,
            defaults={"slug": ff_name.lower().replace(" ", "-")}
        )
        form_factors.append(ff)
        if created:
            print(f"  Created form factor: {ff_name}")
    
    # Create Operating Systems
    operating_systems = []
    os_data = [
        ("Ubuntu", "22.04"),
        ("Ubuntu", "24.04"),
        ("Debian", "12"),
        ("Raspbian", "11"),
        ("Windows", "11"),
        ("macOS", "14"),
    ]
    for os_name, version in os_data:
        os_obj, created = OS.objects.get_or_create(
            name=os_name,
            version=version,
            defaults={"slug": f"{os_name.lower()}-{version.replace('.', '-')}"}
        )
        operating_systems.append(os_obj)
        if created:
            print(f"  Created OS: {os_name} {version}")
    
    # Create Applications
    applications = []
    app_data = [
        ("Docker", "24.0"),
        ("PostgreSQL", "15"),
        ("Redis", "7.2"),
        ("Nginx", "1.24"),
        ("Python", "3.12"),
        ("Node.js", "20.10"),
        ("Git", "2.43"),
        ("VS Code", "1.85"),
    ]
    for app_name, version in app_data:
        app, created = Application.objects.get_or_create(
            name=app_name,
            version=version,
            defaults={"slug": f"{app_name.lower().replace('.', '')}-{version.replace('.', '-')}"}
        )
        applications.append(app)
        if created:
            print(f"  Created application: {app_name} {version}")
    
    # Create Projects
    projects = []
    project_data = [
        (workspaces[0], "Home Automation", "Smart home devices and sensors"),
        (workspaces[1], "Media Server", "Plex and related services"),
        (workspaces[1], "Network Monitoring", "Observability stack"),
        (workspaces[2], "Development Environment", "Dev tools and IDEs"),
        (workspaces[3], "CI/CD Pipeline", "Build and deployment tools"),
    ]
    for workspace, proj_name, description in project_data:
        proj, created = Project.objects.get_or_create(
            workspace=workspace,
            name=proj_name,
            defaults={
                "slug": proj_name.lower().replace(" ", "-"),
                "description": description
            }
        )
        projects.append(proj)
        if created:
            print(f"  Created project: {proj_name}")
    
    # Create Assets
    assets = []
    asset_data = [
        (workspaces[0], projects[0], "Living Room Pi", "PI", form_factors[3], operating_systems[3], ["Living Room"], ["2023-01-15", "2026-01-15"]),
        (workspaces[1], projects[1], "Media Server", "SRV", form_factors[1], operating_systems[0], ["Server Rack"], ["2022-06-20", "2025-06-20"]),
        (workspaces[1], projects[2], "Monitoring Pi", "PI", form_factors[3], operating_systems[3], ["Network Closet"], ["2023-03-10", "2024-03-10"]),
        (workspaces[1], None, "Backup NAS", "SRV", form_factors[1], operating_systems[2], ["Server Rack"], ["2021-12-01", "2024-12-01"]),
        (workspaces[2], projects[3], "Dev Laptop", "LAP", form_factors[4], operating_systems[5], ["Office Desk"], ["2023-08-01", "2026-08-01"]),
        (workspaces[3], projects[4], "Build Server", "SRV", form_factors[0], operating_systems[1], ["Data Center"], ["2023-11-15", "2026-11-15"]),
    ]
    
    for workspace, project, asset_name, kind, ff, os_obj, location, dates in asset_data:
        purchase_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
        warranty_expires = datetime.strptime(dates[1], "%Y-%m-%d").date()
        
        asset, created = Asset.objects.get_or_create(
            workspace=workspace,
            name=asset_name,
            defaults={
                "project": project,
                "kind": kind,
                "form_factor": ff,
                "os": os_obj,
                "location": location[0],
                "purchase_date": purchase_date,
                "warranty_expires": warranty_expires,
                "notes": f"Sample {kind} asset for testing admin interface"
            }
        )
        
        if created:
            # Add some applications to assets
            if kind == "SRV":
                asset.applications.add(applications[0], applications[1], applications[2], applications[3])
            elif kind == "PI":
                asset.applications.add(applications[0], applications[4])
            elif kind == "LAP":
                asset.applications.add(applications[4], applications[5], applications[6], applications[7])
            
            assets.append(asset)
            print(f"  Created asset: {asset_name}")
    
    # Create Maintenance Tasks
    tasks = []
    task_data = [
        (workspaces[1], "OS Patch", "monthly", "Update OS packages and security patches"),
        (workspaces[1], "Backup Verification", "weekly", "Verify backup integrity and test restore"),
        (workspaces[0], "Sensor Check", "monthly", "Check all sensors and replace batteries"),
        (workspaces[2], "Software Updates", "weekly", "Update development tools and dependencies"),
        (workspaces[3], "System Cleanup", "monthly", "Clean up logs and temporary files"),
    ]
    
    for workspace, task_name, cadence, description in task_data:
        task, created = MaintenanceTask.objects.get_or_create(
            workspace=workspace,
            name=task_name,
            defaults={
                "cadence": cadence,
                "description": description,
                "threshold_json": {"max_days_overdue": 7, "window": "30d"}
            }
        )
        tasks.append(task)
        if created:
            print(f"  Created maintenance task: {task_name}")
    
    # Create Work Orders
    now = timezone.now()
    workorders = []
    wo_data = [
        (workspaces[1], assets[1], tasks[0], now - timedelta(days=2), "open", users[0], admin),  # Overdue
        (workspaces[1], assets[1], tasks[1], now + timedelta(hours=12), "open", users[1], admin),  # Due today
        (workspaces[1], assets[2], tasks[0], now + timedelta(days=3), "open", users[0], testuser),  # Due soon
        (workspaces[1], assets[3], tasks[1], now + timedelta(days=15), "open", users[1], admin),  # Scheduled
        (workspaces[0], assets[0], tasks[2], now - timedelta(days=10), "done", testuser, admin),  # Done
        (workspaces[2], assets[4], tasks[3], now - timedelta(days=5), "cancelled", users[1], users[3]),  # Cancelled
        (workspaces[3], assets[5], tasks[4], now + timedelta(days=45), "open", users[3], admin),  # Future
    ]
    
    for workspace, asset, task, due, status, assigned_to, requested_by in wo_data:
        wo, created = WorkOrder.objects.get_or_create(
            workspace=workspace,
            asset=asset,
            task=task,
            due=due,
            defaults={
                "status": status,
                "assigned_to": assigned_to,
                "requested_by": requested_by
            }
        )
        workorders.append(wo)
        if created:
            print(f"  Created work order: {task.name} for {asset.name}")
    
    # Create Activity Instances
    activities = []
    activity_data = [
        (workspaces[1], workorders[4], assets[0], "patched", now - timedelta(days=10), testuser, "Updated all packages successfully"),
        (workspaces[1], workorders[4], assets[1], "checked", now - timedelta(days=5), users[0], "System health check completed"),
        (workspaces[1], None, assets[1], "backup_verified", now - timedelta(days=3), users[1], "Backup restore test successful"),
        (workspaces[0], None, assets[0], "checked", now - timedelta(days=2), testuser, "All sensors functioning normally"),
        (workspaces[2], None, assets[4], "patched", now - timedelta(days=1), users[1], "Security updates applied"),
    ]
    
    for workspace, wo, asset, kind, occurred_at, performed_by, note in activity_data:
        activity, created = ActivityInstance.objects.get_or_create(
            workspace=workspace,
            work_order=wo,
            asset=asset,
            kind=kind,
            occurred_at=occurred_at,
            defaults={
                "performed_by": performed_by,
                "note": note
            }
        )
        if created:
            activities.append(activity)
            print(f"  Created activity: {kind} on {asset.name}")
    
    print("\n✅ Sample data creation complete!")
    print(f"  Users: {CustomUser.objects.count()}")
    print(f"  Workspaces: {Workspace.objects.count()}")
    print(f"  Memberships: {Membership.objects.count()}")
    print(f"  Assets: {Asset.objects.count()}")
    print(f"  Work Orders: {WorkOrder.objects.count()}")
    print(f"  Activities: {ActivityInstance.objects.count()}")


if __name__ == "__main__":
    create_sample_data()
