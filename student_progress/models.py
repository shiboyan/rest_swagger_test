from django.db import models

# Create your models here.
"""Module provides a Django model for session."""
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django_fsm import FSMField, transition

from authentication.models import LitmosStudent
from trainer.models import Course
from . import (
    PROGRESS_STATUS,
    QUALIFICATION_STATUS,
    PHOTO_VERIFICATION_STATUS
)
from .utils import get_stage_duration

class TestSession(models.Model):
    """Class is a Django Model for students test session."""

    created_at = models.DateTimeField(null=True, blank=True, db_index=True)
    student = models.ForeignKey(LitmosStudent, on_delete=models.CASCADE,
                                null=True, default=None)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               null=True, default=None)
    ip_address = models.CharField(max_length=50, null=True, default=None)
    status = models.CharField(max_length=15, choices=PROGRESS_STATUS,
                              null=True, default=None)
    qualification_status = models.CharField(
        max_length=15,
        choices=QUALIFICATION_STATUS,
        default=QUALIFICATION_STATUS[0][0]
    )
    photo_verification_status = models.CharField(
        max_length=15,
        choices=PHOTO_VERIFICATION_STATUS,
        default=PHOTO_VERIFICATION_STATUS[0][0]
    )
    qualification_mark = FSMField(max_length=15, default=None, null=True)
    completed = models.NullBooleanField()
    percentagecomplete = models.IntegerField(default=0)
    ami_status = models.CharField(max_length=15, default=None, null=True)

    def qualify_student(self, mark):
        """Qualify the student."""
        if self.qualification_status == 'active':
            if mark == 'pass':
                self.set_qualified_to_pass()
            elif mark == 'fail':
                self.set_qualified_to_fail()
        elif mark == 'fail' and self.qualification_mark == 'pass':
            self.set_qualified_to_fail()
        elif mark == 'pass' and self.qualification_mark == 'fail':
            self.set_qualified_to_pass()
        else:
            self.set_active()

    @transition(field=qualification_mark, source=[None, 'fail'], target='pass')
    def set_qualified_to_pass(self):
        """Mark as qualified and set status to pass."""
        self.set_qualified()

    @transition(field=qualification_mark, source=[None, 'pass'], target='fail')
    def set_qualified_to_fail(self):
        """Mark as qualified and set status to fail."""
        self.set_qualified()

    @transition(field=qualification_mark, source=['pass', 'fail'], target=None)
    def set_active(self):
        """Set active."""
        self.qualification_mark = None
        self.qualification_status = 'active'

    def set_qualified(self):
        """Set qualified."""
        self.qualification_status = 'qualified'

    def is_active(self):
        """Return True if this session is active."""
        try:
            return now() < self.timer.terminate_at
        except ObjectDoesNotExist:
            return not self.student.ec2instance_set.exists()

    def close_last_stage(self):
        """Close last not passed stage with status `time_out`."""
        last_stage = self.progress_set.filter(status='')
        if last_stage.exists():
            stage = last_stage.latest()
            stage.set_status('time_out')
            stage.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Set created to now."""
        if self.ip_address and not self.created_at:
            self.created_at = now()

        super(TestSession, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        """Return instance id."""
        return f'{self.student} test session'

    class Meta:
        """Meta."""

        get_latest_by = 'created'

class Progress(models.Model):
    """Class is a Django Model for students progress."""

    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    number_of_stages = models.PositiveIntegerField(null=True, default=None)
    stage_name = models.CharField(max_length=100)
    stage = models.PositiveIntegerField()
    status = FSMField(default=None, null=True)
    updated_at = models.DateTimeField(null=True, default=None)
    duration_seconds = models.IntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Save an instance and generate auth token."""
        if not self.pk:
            self.updated_at = now()
            self.attempts += 1

        return super().save(force_insert=False, force_update=False, using=None,
                            update_fields=None)

    def set_status(self, new_status):
        """Set stage status."""
        if new_status == 'pass' and not self.status:
            self.set_stage_to_pass()
        elif not new_status and not self.status:
            self.set_stage_to_fail()
        elif new_status == 'time_out' and not self.status:
            self.set_time_out()
        else:
            self.freeze_stage()

    @transition(field=status, source='', target='pass')
    def set_stage_to_pass(self):
        """Mark stage as pass."""
        self.updated_at = now()
        self.attempts += 1

    @transition(field=status, source='', target='')
    def set_stage_to_fail(self):
        """Increment counter."""
        self.updated_at = now()
        self.attempts += 1

    @transition(field=status, source=['pass', ''], target='pass')
    def freeze_stage(self):
        """Freeze stage."""
        pass

    @transition(field=status, source='', target='time_out')
    def set_time_out(self):
        """Close last stage."""
        self.duration_seconds = get_stage_duration(self.session)

    class Meta:
        """Meta."""

        get_latest_by = 'updated_at'

class Timer(models.Model):
    """Class is a Django Model for students timer."""

    created = models.DateTimeField()
    terminate_at = models.DateTimeField()
    session = models.OneToOneField(TestSession, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Set created to now."""
        if not self.pk:
            self.created = now()

        super(Timer, self).save(
            force_insert, force_update, using, update_fields
        )

    def stop(self):
        """Stop the timer."""
        self.terminate_at = now()
        self.save()

    def __str__(self):
        """Return instance id."""
        return f'Timer for {self.session}'
