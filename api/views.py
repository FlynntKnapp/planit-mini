# api/views.py

from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from rest_framework import viewsets

from assets.models import OS, Application, Asset, FormFactor, Project
from core.models import Membership, Workspace
from work.models import ActivityInstance, MaintenanceTask, WorkOrder

from .permissions import IsAuthenticatedReadOnlyOrManager
from .serializers import (ActivityInstanceSerializer, ApplicationSerializer,
                          AssetSerializer, FormFactorSerializer,
                          MaintenanceTaskSerializer, MembershipSerializer,
                          OSSerializer, ProjectSerializer, WorkOrderSerializer,
                          WorkspaceSerializer)

# ---------- FilterSets ----------


class AssetFilter(filters.FilterSet):
    warranty_expires__lt = filters.DateFilter(
        field_name="warranty_expires", lookup_expr="lt"
    )
    name__icontains = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Asset
        fields = [
            "form_factor",
            "os",
            "applications",
            "location",
            "warranty_expires__lt",
            "name__icontains",
        ]


class WorkOrderFilter(filters.FilterSet):
    # date range for 'due'
    due__date = filters.DateFromToRangeFilter(field_name="due")

    class Meta:
        model = WorkOrder
        fields = [
            "asset",
            "task",
            "status",
            "due__date",
        ]


class ActivityInstanceFilter(filters.FilterSet):
    occurred_at = filters.DateFromToRangeFilter()

    class Meta:
        model = ActivityInstance
        fields = [
            "asset",
            "kind",
            "occurred_at",
        ]


# ---------- Base mixin for workspace scoping ----------


class WorkspaceScopedMixin:
    """
    Limit queryset to workspaces the user belongs to, unless staff.
    Assumes a direct 'workspace' FK on the model, or for Asset-related
    models we override get_queryset appropriately.
    """

    def filter_by_membership(self, qs):
        user = self.request.user
        if not user.is_authenticated or user.is_staff:
            return qs

        return qs.filter(workspace__memberships__user=user).distinct()


# ---------- Core ViewSets ----------


class WorkspaceViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["name", "slug"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        return self.filter_by_membership(super().get_queryset())


class MembershipViewSet(viewsets.ModelViewSet):
    """
    Typically you'd restrict membership management to staff or managers.
    Our permission classes already enforce that.
    """

    queryset = Membership.objects.select_related("user", "workspace")
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["user__username", "workspace__name", "role"]
    ordering_fields = ["role"]
    ordering = ["workspace__name", "user__username"]


# ---------- Assets ViewSets ----------


class FormFactorViewSet(viewsets.ModelViewSet):
    queryset = FormFactor.objects.all()
    serializer_class = FormFactorSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["name", "slug"]
    ordering_fields = ["name"]
    ordering = ["name"]


class OSViewSet(viewsets.ModelViewSet):
    queryset = OS.objects.all()
    serializer_class = OSSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["name", "version", "slug"]
    ordering_fields = ["name", "version"]
    ordering = ["name", "version"]


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["name", "version", "slug"]
    ordering_fields = ["name", "version"]
    ordering = ["name", "version"]


class ProjectViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Project.objects.select_related("workspace")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["name", "slug", "workspace__name"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        return self.filter_by_membership(super().get_queryset())


class AssetViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Asset.objects.select_related(
        "workspace", "project", "form_factor", "os"
    ).prefetch_related("applications")
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        filters.DjangoFilterBackend,
        drf_filters.OrderingFilter,
        drf_filters.SearchFilter,
    ]
    filterset_class = AssetFilter
    search_fields = ["name", "location", "notes"]
    ordering_fields = ["name", "purchase_date", "warranty_expires"]
    ordering = ["name"]

    def get_queryset(self):
        return self.filter_by_membership(super().get_queryset())


# ---------- Work ViewSets ----------


class MaintenanceTaskViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = MaintenanceTask.objects.select_related("workspace")
    serializer_class = MaintenanceTaskSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    search_fields = ["name", "cadence", "workspace__name"]
    ordering_fields = ["name", "cadence"]
    ordering = ["name"]

    def get_queryset(self):
        return self.filter_by_membership(super().get_queryset())


class WorkOrderViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related(
        "workspace", "asset", "task", "assigned_to", "requested_by"
    )
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        filters.DjangoFilterBackend,
        drf_filters.OrderingFilter,
        drf_filters.SearchFilter,
    ]
    filterset_class = WorkOrderFilter
    search_fields = [
        "asset__name",
        "task__name",
        "assigned_to__username",
        "requested_by__username",
    ]
    ordering_fields = ["due", "status"]
    ordering = ["-due"]

    def get_queryset(self):
        return self.filter_by_membership(super().get_queryset())


class ActivityInstanceViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = ActivityInstance.objects.select_related(
        "workspace", "work_order", "asset", "performed_by"
    )
    serializer_class = ActivityInstanceSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrManager]
    filter_backends = [
        filters.DjangoFilterBackend,
        drf_filters.OrderingFilter,
        drf_filters.SearchFilter,
    ]
    filterset_class = ActivityInstanceFilter
    search_fields = [
        "asset__name",
        "note",
        "performed_by__username",
    ]
    ordering_fields = ["occurred_at"]
    ordering = ["-occurred_at"]

    def get_queryset(self):
        return self.filter_by_membership(super().get_queryset())
