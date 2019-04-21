"""Module keeps base serializators for authentication API."""
from datetime import timedelta

from django.utils.timezone import now
from rest_framework import serializers

from litmos import Litmos
from .exceptions import UserIsBlocked
from ..models import (
    LitmosStudent
)


class AbstractAuthSerializer(serializers.ModelSerializer):
    """Abstract serializer class."""

    username = serializers.CharField()
    course_id = serializers.CharField()
    module_code = serializers.CharField()

    default_error_messages = {
        'access_denied': ('Access is denied. '
                          'The user does not belong to this course.'),
        'code_is_incorrect': ('Code is incorrect. '
                              'Remaining attempts is {remaining_attempts}'),
        'no_such_user': 'No such user',
        'no_such_module': 'No such module',
        'no_such_course': 'No such course',
        'email_is_required': 'Email is required',
        'user_is_blocked': 'Authentication is blocked on 30 minutes.',
        'user_does_not_exist': 'The user does not exist'
    }

    def validate_course_id(self, course_id):
        """Validate course_id for LMS."""
        litmos = Litmos(course_id)
        if not litmos.course_id:
            self.fail('no_such_course')
        return litmos

    def validate(self, attrs):
        """Get and check the data."""
        litmos = attrs.get('course_id')

        users = litmos.get_course_users()

        name = attrs['username']
        user = next(
            (user for user in users if user['UserName'] == name),
            None
        )

        if not user:
            self.fail('access_denied')

        email = litmos.get_user_info(user['Id'])['Email']

        if not email:
            self.fail('email_is_required')

        attrs.update({
            'user_id': user['Id'],
            'first_name': user.get('FirstName', None),
            'last_name': user.get('LastName', None),
            'email': email
        })
        return attrs

    def create(self, validated_data):
        """Create student object."""
        username = validated_data.get('username')
        user_id = validated_data.get('user_id')

        student, _ = LitmosStudent.objects.update_or_create(
            username=username,
            user_id=user_id,
            defaults={
                'first_name': validated_data.pop('first_name', None),
                'last_name': validated_data.pop('last_name', None),
                'email': validated_data.pop('email', None)
            }
        )
        time_condition = now() - student.first_login_at < timedelta(minutes=30)
        if time_condition and student.is_blocked:
            raise UserIsBlocked

        return student


    class Meta():
        """Class is a Meta."""

        fields = [
            'username',
            'course_id',
            'module_code',
        ]
