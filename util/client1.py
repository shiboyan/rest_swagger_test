import os
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_swagger_test.settings")
from rest_framework.test import APIClient
from django.forms.models import model_to_dict

from authentication.models import (
    StudentAuthToken,
    LitmosModule,
    LitmosStudent,
)

def test_confirm_email(snapshot, create_course, create_team, create_token, django_assert_num_queries, mocker):
    mock_celery = mocker.patch('authentication.api.serializers.update_confirm_logs')
    client = APIClient()
    data = {
        'code': '140891',
        'username': 'gandalf@middle_earth.com',
        'course_id': '1414493',
        'module_code': 'simulation'
    }
    r = client.post('/api/auth/confirm/', data)
    with django_assert_num_queries(28):
        response = client.post('/api/auth/confirm/', data)
    response_content = json.loads(response.content)

    student = LitmosStudent.objects.all().first()
    assert response.status_code == 201
    assert StudentAuthToken.objects.last().key == response_content['api_key']
    assert student.teams.count() == 2

    expected_module = model_to_dict(LitmosModule.objects.last())
    expected_student = model_to_dict(LitmosStudent.objects.last())
    expected_student.pop('course')
    expected_student.pop('teams')
    snapshot.assert_match(expected_student)
    mock_celery.apply_async.assert_called_once_with(('140891',))
