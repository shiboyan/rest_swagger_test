from django.contrib import admin

# Register your models here.
from django.contrib import admin
from student_progress.models import Progress, Timer, TestSession

admin.site.register((Progress, Timer, TestSession))