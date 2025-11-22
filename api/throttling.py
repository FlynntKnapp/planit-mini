# api/throttling.py

from rest_framework.throttling import UserRateThrottle


class NonStaffUserRateThrottle(UserRateThrottle):
    """
    Apply a throttle rate (REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['non_staff_user'])
    to non-staff users. Staff are not throttled.
    """

    scope = "non_staff_user"

    def allow_request(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_staff:
            return True
        return super().allow_request(request, view)
