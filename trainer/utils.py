"""Module keeps a additional method."""
from litmos import Litmos
from .models import Team


def get_user_teams(user_id):
    """Return the user teams."""
    teams = []
    response = Litmos.get_user_teams(user_id)
    for res in response:
        try:
            team = Team.objects.get(team_id=res['Id'])
            teams.append(team)
        except Team.DoesNotExist:
            continue
    return teams


def check_existing_teams(user, teams_from_lms):
    """Remove outdated teams from student."""
    teams = user.teams.all()
    for team in teams:
        if team not in teams_from_lms:
            user.teams.remove(team)

def check_and_add_default_teams(user):
    """Check and add deafult team."""
    for course in user.course.all():
        user_courses_without_teams = course.teams.exclude(
            team_id__icontains='default_team_'
        )
        team_id = f'default_team_for_{course.frontend_course_id}'
        default_team = list(course.teams.filter(team_id=team_id))

        if user_courses_without_teams.exists():
            # delete this student from default team
            user.teams.remove(*default_team)
        else:
            # add this student to default team
            user.teams.add(*default_team)

        user.save()
