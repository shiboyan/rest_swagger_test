"""Module keeps viewsets for authentication API."""
from django.utils.decorators import method_decorator

from rest_framework import viewsets, mixins
from drf_yasg.utils import swagger_auto_schema

from .serializers import StudentAuthSerializator, CodeConfirmSerializator
from ..models import LitmosStudent


@method_decorator(name='create', decorator=swagger_auto_schema(security=[]))
class StudentAuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Student authentication viewset."""

    queryset = LitmosStudent.objects.all()
    serializer_class = StudentAuthSerializator


@method_decorator(name='create', decorator=swagger_auto_schema(security=[]))
class CodeConfirmViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Student authentication viewset."""

    queryset = LitmosStudent.objects.all()
    serializer_class = CodeConfirmSerializator
