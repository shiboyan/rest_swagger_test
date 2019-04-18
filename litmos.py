"""Module keeps logic for interaction with Litmos API."""
import json
from datetime import datetime

import requests
from xmltodict import unparse
from django.conf import settings
from cached_property import cached_property


class Litmos():
    """Class provide logic for work with Litmos API."""

    def __init__(self, originalid):
        """Construct a new instance."""
        self.host, self.organization, self.api_key = self._get_credentials()
        self.originalid = originalid

    @cached_property
    def course_id(self):
        """Return course id from Litmos API."""
        result = self.send_request(f'{self.host}/courses')
        cource_id = None
        for course in result:
            if course['OriginalId'] == int(self.originalid):
                cource_id = course['Id']
        return cource_id

    def get_course_users(self):
        """Return course users from Litmos API."""
        return self.send_request(
            f'{self.host}/courses/{self.course_id}/users'
        )

    def get_user_info(self, user_id):
        """Return course users from Litmos API."""
        return self.send_request(
            f'{self.host}/users/{user_id}'
        )

    def get_course_modules(self):
        """Return course users from Litmos API."""
        return self.send_request(
            f'{self.host}/courses/{self.course_id}/modules'
        )

    @classmethod
    def send_progress(cls, session):
        """Send student progress in module to LMS."""
        course = session.course
        module = course.litmosmodule
        module_id = module.module_id

        data = {
            'ModuleResult': {
                'CourseId': course.course_id,
                'UserId': session.student.user_id,
                'Score': session.percentagecomplete,
                'Completed': 'true' if session.completed else 'false',
                'UpdatedAt': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'Note': 'Marked by SPOT system'
            }
        }
        return requests.put(
            f'https://api.litmos.com/v1.svc/results/modules/{module_id}',
            data=unparse(data, pretty=True),
            headers={'Content-Type': 'application/xml'},
            params={
                'apikey': '227af73d-8a0f-4cf0-82ea-80b90259809d',
                'source': 'gallaghersecuritytraining1'
            }
        )

    @classmethod
    def get_lms_courses(cls):
        """Return all courses from LMS."""
        cls.host, cls.organization, cls.api_key = cls._get_credentials(cls)
        url = f'{cls.host}/courses'
        return cls.send_request(cls, url)

    @classmethod
    def get_lms_teams(cls):
        """Return all teams from LMS."""
        cls.host, cls.organization, cls.api_key = cls._get_credentials(cls)
        url = f'{cls.host}/teams'
        return cls.send_request(cls, url)

    @classmethod
    def get_course_teams(cls, team_id):
        """Return all courses entering to the team."""
        cls.host, cls.organization, cls.api_key = cls._get_credentials(cls)
        url = f'{cls.host}/teams/{team_id}/courses'
        return cls.send_request(cls, url)

    @classmethod
    def get_user_teams(cls, user_id):
        """Return all teams from LMS."""
        cls.host, cls.organization, cls.api_key = cls._get_credentials(cls)
        url = f'{cls.host}/users/{user_id}/teams'
        return cls.send_request(cls, url)

    def send_request(self, url):
        """Send request to Litmos API."""
        response = requests.get(
            url,
            params={
                'apikey': self.api_key,
                'source': self.organization,
                'format': 'json'
            }
        )
        return json.loads(response.content)

    def _get_credentials(self):
        """Return connection information: host, api key and organization."""
        self.host = 'https://api.litmos.com/v1.svc'
        self.organization = 'gallaghersecuritytraining1'
        self.api_key = '227af73d-8a0f-4cf0-82ea-80b90259809d'
        return self.host, self.organization, self.api_key
# t=Litmos(1782968);
# # t=Litmos(2050051);
# print(t.get_lms_teams());