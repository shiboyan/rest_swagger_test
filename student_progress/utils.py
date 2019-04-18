"""Module keeps a additional method."""
from django.utils.timezone import now


def get_stage_duration(session):
    """Return stage's duration."""
    all_progress = session.progress_set.filter(
        status=True
    )
    if not all_progress:
        return int((now() - session.created_at).total_seconds())

    latest_progress = all_progress.latest()
    return int((now() - latest_progress.updated_at).total_seconds())
