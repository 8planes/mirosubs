from celery.decorators import task
from utils import send_templated_email
from messages.models import Message
from django.contrib.sites.models import Site
from sentry.client.models import client
from django.utils.translation import ugettext, ugettext_lazy as _

@task()
def send_new_message_notification(message_id):
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        msg = '**send_new_message_notification**. Message does not exist. ID: %s' % message_id
        client.create_from_text(msg, data=dict(), logger='celery')
        return
    
    user = message.user
    
    if not user.email or not user.is_active or not user.new_message_notification:
        return

    to = "%s <%s>" % (user, user.email)
    
    subject = _(u"%(author)s sent you a message on Universal Subtitles: %(subject)s")
    subject = subject % {
        'author': message.author, 
        'subject': message.subject
    }
        
    context = {
        "message": message,
        "domain":  Site.objects.get_current().domain
    }

    send_templated_email(to, subject, "messages/email/message_received.html", context)
