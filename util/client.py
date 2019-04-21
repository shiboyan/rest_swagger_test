import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_swagger_test.settings")
from rest_framework.test import APIClient

def test_client():
    client = APIClient()
    #'code': '140891',
    data = {
        'username': 'minattt',
        'courseID': '1782968',
        'moduleCode': 'simulation'
    }

    r = client.post('/api/auth/student/', data)
    print(r.status_code)
    print(r.headers)

test_client()