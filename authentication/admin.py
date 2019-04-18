from django.contrib import admin

# Register your models here.
from django.contrib import admin
from authentication.models import (
    LitmosStudent,
    LitmosModule,
    StudentAuthToken,
)

admin.site.register((
    LitmosStudent,
    StudentAuthToken,
    LitmosModule
))
