# work/models.py

from django.conf import settings
from django.db import models

from core.models import Workspace


class MaintenanceTask(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="tasks"
    )
    name = models.CharField(max_length=120)  # unique per workspace
    cadence = models.CharField(max_length=30)  # "monthly", "weekly"
    description = models.TextField(blank=True)

    class Meta:
        unique_together = [("workspace", "name")]


class WorkOrder(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="workorders"
    )
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.CASCADE, related_name="workorders"
    )
    task = models.ForeignKey(
        MaintenanceTask, on_delete=models.PROTECT, related_name="workorders"
    )
    due = models.DateTimeField()
    STATUS = [("open", "Open"), ("done", "Done"), ("cancelled", "Cancelled")]
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_workorders",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_workorders",
    )


class ActivityInstance(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="activities"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activities",
    )
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.CASCADE, related_name="activities"
    )
    KIND = [
        ("checked", "Checked"),
        ("patched", "Patched"),
        ("backup_verified", "Backup Verified"),
    ]
    kind = models.CharField(max_length=20, choices=KIND)
    note = models.TextField(blank=True)
    occurred_at = models.DateTimeField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="performed_activities",
    )
