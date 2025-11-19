# assets/models.py

from django.db import models

from core.models import Workspace


class FormFactor(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class OS(models.Model):
    name = models.CharField(max_length=80)
    version = models.CharField(max_length=40, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Operating Systems"

    def __str__(self) -> str:
        # "Ubuntu 24.04", "Debian" (no trailing space if version is blank)
        if self.version:
            return f"{self.name} {self.version}"
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=120)
    version = models.CharField(max_length=60, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        if self.version:
            return f"{self.name} {self.version}"
        return self.name


class Project(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    slug = models.SlugField()

    class Meta:
        unique_together = [("workspace", "slug")]

    def __str__(self) -> str:
        # e.g. "Personal – Homelab"
        return f"{self.workspace}: {self.name}"


class Asset(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="assets"
    )
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.SET_NULL, related_name="assets"
    )
    KIND_CHOICES = [("PI", "Raspberry Pi"), ("SRV", "Server"), ("LAP", "Laptop")]
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=3, choices=KIND_CHOICES)
    form_factor = models.ForeignKey(FormFactor, null=True, on_delete=models.SET_NULL)
    os = models.ForeignKey(OS, null=True, on_delete=models.SET_NULL)
    applications = models.ManyToManyField(Application, blank=True)
    location = models.CharField(max_length=120, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expires = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        # e.g. "Remote Lamp (PI) @ Homelab"
        kind_display = dict(self.KIND_CHOICES).get(self.kind, self.kind)
        return f"{self.name} ({kind_display}) @ {self.workspace}"
