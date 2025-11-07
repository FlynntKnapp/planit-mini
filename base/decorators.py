# base/decorators.py

from functools import wraps

from django.shortcuts import render


def registration_accepted_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return render(
                request,
                "403.html",
                {"error": "You must be logged in to access this page."},
                status=403,
            )

        # Check if the user's registration is accepted
        if not getattr(request.user, "registration_accepted", False):
            return render(
                request,
                "403.html",
                {"error": "Your registration has not been accepted."},
                status=403,
            )

        # Call the original view function if checks pass
        return view_func(request, *args, **kwargs)

    return _wrapped_view
