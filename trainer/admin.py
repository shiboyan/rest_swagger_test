from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Course, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Class is ModelAdmin for Team model."""

    readonly_fields = [
        'team_id'
    ]


admin.site.register((Course,))