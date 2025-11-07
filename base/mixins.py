# base/mixins.py

from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


# Generic mixins
class UserQuerySetMixin:
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class UserAssignMixin:
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RegistrationAcceptedMixin(AccessMixin):
    """
    Mixin to check if the user is authenticated and their registration is accepted.
    """

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated and if registration is accepted
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.registration_accepted:
            raise PermissionDenied("Your registration has not been accepted yet.")
        return super().dispatch(request, *args, **kwargs)


class OrderableMixin:
    """
    Mixin to add `reorder_all` class method to models with an 'order' field.
    """

    @classmethod
    def reorder_all(cls):
        for index, item in enumerate(cls.objects.all().order_by("order")):
            item.order = index
            item.save()


class SiteContextMixin:
    """
    Adds site-wide context keys to class-based views.

    - the_site_name: friendly site name (from settings.THE_SITE_NAME or fallback)
    - page_title: title for the page; override `page_title` attr or `get_page_title()`
    """

    page_title: str | None = None

    def get_page_title(self):
        # Default to a human-ish name based on the class
        return self.page_title or self.__class__.__name__.replace("View", "")

    def get_site_name(self):
        return getattr(settings, "THE_SITE_NAME", "Personal Assistant")

    def get_context_data(self, **kwargs):
        """
        Ensure `the_site_name` and `page_title` are present in context.
        Use setdefault so views can override if they really want to.
        """
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("the_site_name", self.get_site_name())
        ctx.setdefault("page_title", self.get_page_title())
        return ctx
