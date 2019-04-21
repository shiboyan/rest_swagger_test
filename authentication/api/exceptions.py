"""Module keeps custom exceptions for API."""
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import APIException
from rest_framework import status


class TimeIsUp(APIException):
    """Throw when timer is and."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Time\'s up.')
    default_code = 'timer_is_end'


class UserIsBlocked(APIException):
    """User is blocked."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _('Authentication is blocked on 30 minutes.')
    default_code = 'user_is_blocked'
