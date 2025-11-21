# api/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers

from assets.models import OS, Application, Asset, FormFactor, Project
from core.models import Membership, Workspace
from work.models import ActivityInstance, MaintenanceTask, WorkOrder

User = get_user_model()


# ---------- Core ----------


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "name", "slug"]


class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    workspace = serializers.SlugRelatedField(
        slug_field="slug", queryset=Workspace.objects.all()
    )

    class Meta:
        model = Membership
        fields = ["id", "user", "workspace", "role"]


# ---------- Assets ----------


class FormFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFactor
        fields = ["id", "name", "slug"]


class OSSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = OS
        fields = ["id", "name", "version", "slug", "display_name"]


class ApplicationSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "name", "version", "slug", "display_name"]


class ProjectSerializer(serializers.ModelSerializer):
    workspace = serializers.SlugRelatedField(
        slug_field="slug", queryset=Workspace.objects.all()
    )

    class Meta:
        model = Project
        fields = ["id", "workspace", "name", "description", "slug"]


class AssetSerializer(serializers.ModelSerializer):
    workspace = serializers.SlugRelatedField(
        slug_field="slug", queryset=Workspace.objects.all()
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), allow_null=True, required=False
    )

    # Human-friendly display of kind
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)

    # Nested list of applications (read-only)
    applications = ApplicationSerializer(many=True, read_only=True)

    # Write applications by IDs
    application_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Application.objects.all(),
        source="applications",
    )

    class Meta:
        model = Asset
        fields = [
            "id",
            "workspace",
            "project",
            "name",
            "kind",
            "kind_display",
            "form_factor",
            "os",
            "applications",
            "application_ids",
            "location",
            "purchase_date",
            "warranty_expires",
            "notes",
        ]


# ---------- Work ----------


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    workspace = serializers.SlugRelatedField(
        slug_field="slug", queryset=Workspace.objects.all()
    )

    class Meta:
        model = MaintenanceTask
        fields = [
            "id",
            "workspace",
            "name",
            "cadence",
            "description",
            "threshold_json",
        ]


class WorkOrderSerializer(serializers.ModelSerializer):
    workspace = serializers.SlugRelatedField(
        slug_field="slug", queryset=Workspace.objects.all()
    )
    assigned_to = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )
    requested_by = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "workspace",
            "asset",
            "task",
            "due",
            "status",
            "assigned_to",
            "requested_by",
        ]


class ActivityInstanceSerializer(serializers.ModelSerializer):
    workspace = serializers.SlugRelatedField(
        slug_field="slug", queryset=Workspace.objects.all()
    )
    performed_by = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ActivityInstance
        fields = [
            "id",
            "workspace",
            "work_order",
            "asset",
            "kind",
            "note",
            "occurred_at",
            "performed_by",
        ]
