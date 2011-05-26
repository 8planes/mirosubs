from celery.decorators import task
from utils import send_templated_email
from messages.models import Message
from django.contrib.sites.models import Site
from sentry.client.models import client
from django.db import connection

@task()
def send_new_message_notification(message_id):
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        msg = '**send_new_message_notification**. Message does not exist. ID: %s' % message_id
        client.create_from_text(msg, data=dict(), logger='celery')
        return

    if not message.user.email or not message.user.is_active:
        return

    to = "%s <%s>" % (message.user, message.user.email)
    subject = u"%s sent you a message on Universal Subtitles: %s" % (message.author, message.subject)
    context = {
        "author": message.author,
        "body": message.content,
        "domain":  Site.objects.get_current().domain,
        "message_pk": message.pk
    }

    send_templated_email(to, subject, "messages/email/message_received.html", context)
