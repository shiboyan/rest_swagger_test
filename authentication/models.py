"""Module provides a Django model for authentication."""
import hmac
import uuid
from hashlib import sha1
from random import randint

from django.db import models
from django.utils.timezone import now
from celery import chain
from celery import signature
# from celery import Signature
from trainer.models import Course, Team
# from .tasks import send_token, create_сonfirmation_logs

class LitmosStudent(models.Model):
    """Class is a Django Model for students."""

    username = models.CharField(max_length=150, verbose_name='User name')
    user_id = models.CharField(max_length=150, verbose_name='User ID')

    first_name = models.CharField(max_length=150, verbose_name='Firs name',
                                  null=True, default=None)
    last_name = models.CharField(max_length=150, verbose_name='Last name',
                                 null=True, default=None)
    email = models.CharField(max_length=150, verbose_name='E-Mail',
                             null=True, default=None)
    course = models.ManyToManyField(Course, null=True, default=None,
                                    through='student_progress.TestSession')
    teams = models.ManyToManyField(Team, null=True, default=None)

    is_confirm = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    first_login_at = models.DateTimeField(auto_now_add=True)
    remaining_auth_attempts = models.IntegerField(default=5)
    remaining_confirm_attempts = models.IntegerField(default=5)

    @property
    def channel(self):
        """Return Centrifugo channel name."""
        return f'student#{self.pk}'

    @property
    def full_name(self):
        """Return full name."""
        return f'{self.first_name} {self.last_name}'

    @property
    def is_authenticated(self):
        """Read-only attribute which is always True."""
        return True

    def remove_restriction(self):
        """Set restriction to default values."""
        self.first_login_at = now()
        self.is_blocked = False
        self.remaining_auth_attempts = 5
        self.remaining_confirm_attempts = 5

    def __str__(self):
        """Return user name."""
        return self.username


class LitmosModule(models.Model):
    """Class is a Django Model for modules."""

    course = models.OneToOneField(Course, on_delete=models.CASCADE,
                                  null=True, default=None)
    module_id = models.CharField(max_length=100, verbose_name='Module ID')
    module_code = models.CharField(max_length=100, verbose_name='Module code')


class Token(models.Model):
    """Class provide a base Django Model for a token."""

    student = models.OneToOneField(
        LitmosStudent,
        null=True,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=128, blank=False, db_index=True)

    @staticmethod
    def generate_key():
        """Generate confirm key."""
        new_uuid = uuid.uuid4()
        return hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()

    class Meta:
        """Meta."""

        abstract = True


class StudentAuthToken(Token):
    """Class provide a Django Model for auth token."""

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Save an instance and generate auth token."""
        if not self.key:
            self.key = self.generate_key()

        return super().save(force_insert=False, force_update=False, using=None,
                            update_fields=None)

    def __str__(self):
        """Return user name."""
        return f'Auth token for - {self.student.username}'


class StudentConfirmToken(Token):
    """Class provide a Django Model for confirm token."""

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Save an instance and generate auth token."""
        self.key = self.generate_key()
        if not self.student.is_blocked:
            chain(
                signature(
                    'authentication.tasks.send_token',
                    args=(self.key, self.student.id)
                ),
                signature(
                    'authentication.tasks.create_confirm_logs',
                    args=(self.key,)
                )
            )()
        return super().save(force_insert=False, force_update=False, using=None,
                            update_fields=None)

    @staticmethod
    def generate_key():
        """Generate confirm key."""
        return str("%06d" % randint(0, 999999))

    def __str__(self):
        """Return user name."""
        return f'Confirm token for - {self.student.username}'


class ConfirmTokenLog(models.Model):
    """Class provide a Django Model for logs for confirm token."""

    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(
        LitmosStudent,
        on_delete=models.CASCADE
    )
    code_hash = models.CharField(max_length=128)
    confirmed = models.BooleanField(default=False)
