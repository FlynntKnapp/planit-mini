# core/models.py

from django.conf import settings
from django.db import models


class Workspace(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    ROLE = [
        ("viewer", "Viewer"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=20, choices=ROLE, default="viewer")

    class Meta:
        unique_together = [("user", "workspace")]

    def __str__(self) -> str:
        return f"{self.user} → {self.workspace} ({self.role})"
