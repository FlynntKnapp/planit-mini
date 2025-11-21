"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from rest_framework.routers import DefaultRouter

from api import views as api_views
from config.settings.base import THE_SITE_NAME

router = DefaultRouter()
router.register(r"workspaces", api_views.WorkspaceViewSet, basename="workspace")
router.register(r"memberships", api_views.MembershipViewSet, basename="membership")
router.register(r"form-factors", api_views.FormFactorViewSet, basename="formfactor")
router.register(r"oses", api_views.OSViewSet, basename="os")
router.register(r"applications", api_views.ApplicationViewSet, basename="application")
router.register(r"projects", api_views.ProjectViewSet, basename="project")
router.register(r"assets", api_views.AssetViewSet, basename="asset")
router.register(
    r"maintenance-tasks",
    api_views.MaintenanceTaskViewSet,
    basename="maintenancetask",
)
router.register(r"work-orders", api_views.WorkOrderViewSet, basename="workorder")
router.register(
    r"activities",
    api_views.ActivityInstanceViewSet,
    basename="activityinstance",
)

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="home.html",
            extra_context={"the_site_name": THE_SITE_NAME},
        ),
        name="home",
    ),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include(router.urls)),
]
