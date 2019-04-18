
"""Module keeps serializators for authentication API."""
from datetime import datetime, timedelta, timezone
from logging import getLogger

from django.db import transaction
from django.conf import settings
from rest_framework import serializers
import jwt

from trainer.utils import get_user_teams
from trainer.models import Course
from student_progress.models import TestSession
from .exceptions import TimeIsUp, UserIsBlocked
from .base_setializers import AbstractAuthSerializer
from ..models import (
    LitmosStudent,
    StudentAuthToken,
    LitmosModule,
    StudentConfirmToken
)
from ..utils import (
    hold_authentication,
    hold_confirm
)
from ..tasks import update_confirm_logs

LOGGER = getLogger()


class StudentAuthSerializator(AbstractAuthSerializer):
    """Student authentication serializator."""

    @transaction.atomic
    def create(self, validated_data):
        """Create student instance and create API auth key."""
        student = super().create(validated_data)
        hold_authentication(student)

        test_session = student.testsession_set.filter(completed=False)

        if test_session.exists() and not test_session.get().is_active():
            raise TimeIsUp

        StudentConfirmToken.objects.update_or_create(
            student=student
        )

        return {
            'email': student.email,
            'remaining_auth_attempts': student.remaining_auth_attempts,
            'course_id': validated_data.get('course_id').originalid,
            'module_code': validated_data.get('module_code'),
            'username': validated_data.get('username'),
        }

    class Meta():
        """Class is a Meta."""

        model = LitmosStudent
        additional_fields = [
            'email',
            'remaining_auth_attempts'
        ]
        fields = AbstractAuthSerializer.Meta.fields + additional_fields


class CodeConfirmSerializator(AbstractAuthSerializer):
    """Student confirm serializator."""

    username = serializers.CharField(write_only=True)
    course_id = serializers.CharField(write_only=True)
    module_code = serializers.CharField(write_only=True)

    code = serializers.CharField(write_only=True)
    client_id = serializers.CharField(read_only=True, source='id')
    api_key = serializers.CharField(read_only=True,
                                    source='studentauthtoken.key')
    centrifugo_token = serializers.SerializerMethodField(
        'generate_key_centrifugo_token'
    )

    def validate_username(self, username):
        """Check user is blocked."""
        try:
            student = LitmosStudent.objects.get(username=username)
            if student.is_blocked:
                raise UserIsBlocked

            hold_confirm(student)
            return username

        except LitmosStudent.DoesNotExist:
            self.fail('user_does_not_exist')

    def validate_code(self, key):
        """Check confirm code."""
        code = StudentConfirmToken.objects.filter(key=key)
        if not code.exists():
            student = LitmosStudent.objects.get(
                username=self.initial_data['username']
            )
            remaining_attempts = student.remaining_confirm_attempts
            self.fail(
                'code_is_incorrect',
                remaining_attempts=remaining_attempts
            )

        update_confirm_logs.apply_async((key,))
        code.delete()
        return key

    def validate(self, attrs):
        """Get and check the data."""
        attrs.pop('code')
        litmos = attrs.pop('course_id')

        code = attrs['module_code']
        modules = litmos.get_course_modules()
        module = next(
            (item for item in modules if item['Code'] == code),
            None
        )

        if not module:
            self.fail('no_such_module')

        course = Course.objects.get(frontend_course_id=litmos.originalid)
        if course.course_id is None:
            course.course_id = litmos.course_id
            course.save()

        attrs.update({
            'module_id': module['Id'],
            'course': course
        })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create student instance and create API auth key."""
        username = validated_data.pop('username')
        student = LitmosStudent.objects.get(username=username)
        teams = get_user_teams(student.user_id)

        if not teams:
            LOGGER.warning('Student: %s without LMS Team!', username)
            course = validated_data.get('course')
            team_id = f'default_team_for_{course.frontend_course_id}'
            teams = course.teams.filter(team_id=team_id)


        student.teams.add(*teams)
        student.is_confirm = True
        student.save()

        test_session, created = TestSession.objects.update_or_create(
            student=student,
            defaults={
                'completed': False,
                'course': validated_data.get('course', None)
            }
        )
        if not created and not test_session.is_active():
            raise TimeIsUp

        module_id = validated_data.pop('module_id')
        LitmosModule.objects.get_or_create(
            module_id=module_id,
            defaults=validated_data
        )

        StudentAuthToken.objects.update_or_create(student=student)
        return student

    # pylint: disable=no-self-use
    def generate_key_centrifugo_token(self, student):
        """Create token for Centrifugo service."""
        expire_at = datetime.now() + timedelta(weeks=8)
        timestamp = expire_at.replace(tzinfo=timezone.utc).timestamp()
        return jwt.encode(
            {'sub': str(student.id), "exp": int(timestamp)},
            settings.CENTRIFUGO_SECRET
        ).decode()

    # pylint: enable=no-self-use

    class Meta():
        """Class is a Meta."""

        model = LitmosStudent
        additional_fields = [
            'code',
            'client_id',
            'api_key',
            'centrifugo_token'
        ]
        fields = AbstractAuthSerializer.Meta.fields + additional_fields
