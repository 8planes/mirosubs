from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

def get_pager(objects, on_page=15, page='1', orphans=0):
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    paginator = Paginator(objects, on_page, orphans=orphans)
    try:
        page = paginator.page(int(page))
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    return page

def send_templated_email(to, subject, body_template, body_dict, from_email=None, ct="html", fail_silently=False):
    if not isinstance(to, list): to = [to]
    if not from_email: from_email = settings.DEFAULT_FROM_EMAIL

    message = render_to_string(body_template, body_dict)

    email = EmailMessage(subject, message, from_email, to)
    email.content_subtype = ct
    email.send(fail_silently)