# work/models.py

from django.db import models


class MaintenanceTask(models.Model):
    name = models.CharField(max_length=120, unique=True)  # e.g. "Monthly OS patches"
    cadence = models.CharField(max_length=30)  # "monthly", "weekly"
    description = models.TextField(blank=True)


class WorkOrder(models.Model):
    STATUS = [("open", "Open"), ("done", "Done"), ("cancelled", "Cancelled")]
    asset = models.ForeignKey("assets.Asset", on_delete=models.CASCADE)
    task = models.ForeignKey(MaintenanceTask, on_delete=models.PROTECT)
    due = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS, default="open")


class ActivityInstance(models.Model):
    KIND = [
        ("checked", "Checked"),
        ("patched", "Patched"),
        ("backup_verified", "Backup Verified"),
    ]
    work_order = models.ForeignKey(
        WorkOrder, null=True, blank=True, on_delete=models.SET_NULL
    )
    asset = models.ForeignKey("assets.Asset", on_delete=models.CASCADE)
    kind = models.CharField(max_length=20, choices=KIND)
    note = models.TextField(blank=True)
    occurred_at = models.DateTimeField()
