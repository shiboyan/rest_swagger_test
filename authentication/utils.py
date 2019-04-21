"""Module keeps a additional method."""
from datetime import timedelta

from django.utils.timezone import now


def hold_authentication(student):
    """Throttle student's login if seems that it is DDOS."""
    time_condition = now() - student.first_login_at < timedelta(minutes=30)

    if time_condition and student.remaining_auth_attempts:
        student.remaining_auth_attempts -= 1

    if not student.remaining_auth_attempts and not student.is_blocked:
        student.is_blocked = True

    if not time_condition:
        student.remove_restriction()

    student.save()


def hold_confirm(student):
    """Throttle student's login if seems that it is brute force."""
    time_condition = now() - student.first_login_at < timedelta(minutes=30)

    if time_condition and student.remaining_confirm_attempts:
        student.remaining_confirm_attempts -= 1

    if not student.remaining_confirm_attempts and not student.is_blocked:
        student.is_blocked = True

    if not time_condition:
        student.remove_restriction()

    student.save()
