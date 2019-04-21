"""Module keeps Celery tasks."""
import hmac
from hashlib import sha1

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from celery import shared_task

from .models import ConfirmTokenLog, LitmosStudent


@shared_task()
def send_token(token, student_id):
    """Send Email with confirm token to student."""
    student = LitmosStudent.objects.get(id=student_id)
    html_message = render_to_string(
        'mail/mail_template.html', {'token': token}
    )
    send_mail(
        subject=settings.EMAIL_SUBJECT_FOR_2FA,
        message=strip_tags(html_message),
        from_email=settings.SENDER_EMAIL,
        recipient_list=(student.email,),
        html_message=html_message
    )
    return student_id

@shared_task()
def create_confirm_logs(student_id, token):
    """Take the log."""
    student = LitmosStudent.objects.get(id=student_id)
    code_hash = hmac.new(token.encode(), digestmod=sha1).hexdigest()

    ConfirmTokenLog.objects.get_or_create(
        code_hash=code_hash,
        defaults={
            'student': student
        }
    )


@shared_task()
def update_confirm_logs(token):
    """Update confirm log."""
    code_hash = hmac.new(token.encode(), digestmod=sha1).hexdigest()
    log = ConfirmTokenLog.objects.get(code_hash=code_hash)
    log.confirmed = True
    log.save()
