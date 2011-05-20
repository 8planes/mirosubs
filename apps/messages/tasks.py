from celery.decorators import task
from utils import send_templated_email
from django.conf import settings

from django.contrib.sites.models import Site

from apps.messages.models import Message

@task
def send_new_message_notification(message_id):
    print "inside new task"
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return
    to = "%s <%s>" % (message.user, message.user.email)
    subject = "%s sent you a message on Universal Subtitles: %s" % (message.author, message.subject)
    context = {
        "author": message.author,
        "body": message.content,
        "domain":  Site.objects.get_current().domain,
        }
    send_templated_email(to, subject, "messages/email/message_received.html", context)
