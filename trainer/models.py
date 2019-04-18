from django.db import models

# Create your models here.
"""Module provides a Django model for trainer dashboard."""
from django.db import models


class Team(models.Model):
    """Class is a Django Model for LMS Teams."""

    name = models.TextField()
    team_id = models.CharField(max_length=100, verbose_name='Team ID',
                               unique=True)


class Course(models.Model):
    """Class is a Django Model for students Course."""

    name = models.TextField()
    course_id = models.CharField(max_length=100, verbose_name='Course ID',
                                 null=True, default=None)
    frontend_course_id = models.CharField(max_length=100, unique=True)
    test_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=240,
        help_text='Test duration in minutes, default = 240 minute'
    )
    teams = models.ManyToManyField(Team, null=True, default=None)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Save object and create default team."""
        super().save(force_insert, force_update, using, update_fields)
        team_id = f'default_team_for_{self.frontend_course_id}'

        if not self.teams.filter(team_id=team_id).exists():
            team, _ = Team.objects.get_or_create(
                team_id=team_id,
                defaults={
                    'name': 'Students without teams'
                }
            )
            self.teams.add(team)

    def delete(self, using=None, keep_parents=False):
        """Delete object and remove default team."""
        team_id = f'default_team_for_{self.frontend_course_id}'

        self.teams.get(team_id=team_id).delete()
        return super().delete(using=None, keep_parents=False)
