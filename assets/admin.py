# assets/admin.py

from django.contrib import admin

from .models import Asset, Application, FormFactor, OS, Project


@admin.register(FormFactor)
class FormFactorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "slug")
    search_fields = ("name", "version")
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "slug")
    search_fields = ("name", "version")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "slug")
    search_fields = ("name", "description", "slug")
    list_filter = ("workspace",)
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("workspace",)
    ordering = ("workspace", "name")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "workspace",
        "project",
        "kind",
        "form_factor",
        "os",
        "location",
        "purchase_date",
        "warranty_expires",
    )
    list_filter = (
        "workspace",
        "kind",
        "form_factor",
        "os",
        "location",
        "purchase_date",
        "warranty_expires",
    )
    search_fields = (
        "name",
        "location",
        "notes",
        "workspace__name",
        "project__name",
    )
    raw_id_fields = ("workspace", "project", "form_factor", "os")
    filter_horizontal = ("applications",)
    date_hierarchy = "purchase_date"
    list_select_related = ("workspace", "project", "form_factor", "os")
    ordering = ("workspace", "name")
