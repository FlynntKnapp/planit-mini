# api/permissions.py

from rest_framework import permissions

from core.models import Membership


class IsAuthenticatedReadOnlyOrManager(permissions.BasePermission):
    """
    - Read (GET/HEAD/OPTIONS): any authenticated user.
    - Write (POST/PUT/PATCH/DELETE):
        * staff OR
        * member of 'maintenance_manager' group OR
        * (optional) manager/admin of the related Workspace via Membership.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Read-only for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Global write checks
        if user.is_staff or self._in_maintenance_manager_group(user):
            return True

        # For unsafe methods we may further check object-level in has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Read-only is always okay if authenticated
        if request.method in permissions.SAFE_METHODS:
            return True

        # Staff or maintenance_manager can always write
        if user.is_staff or self._in_maintenance_manager_group(user):
            return True

        # OPTIONAL object-level: require manager/admin role in the workspace
        workspace = self._get_workspace_from_obj(obj)
        if workspace is None:
            # If we cannot resolve workspace, default to deny for non-staff
            return False

        return Membership.objects.filter(
            user=user,
            workspace=workspace,
            role__in=["manager", "admin"],
        ).exists()

    @staticmethod
    def _in_maintenance_manager_group(user):
        return user.groups.filter(name="maintenance_manager").exists()

    @staticmethod
    def _get_workspace_from_obj(obj):
        """
        Try to get a Workspace instance from different model types.
        Handles your core/assets/work models.
        """
        # Direct workspace attribute
        workspace = getattr(obj, "workspace", None)
        if workspace is not None:
            return workspace

        # Related via asset
        asset = getattr(obj, "asset", None)
        if asset is not None and hasattr(asset, "workspace"):
            return asset.workspace

        # Related via task (for WorkOrder)
        task = getattr(obj, "task", None)
        if task is not None and hasattr(task, "workspace"):
            return task.workspace

        return None
