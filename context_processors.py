from django.contrib.sites.models import Site

def current_site(request):
    try:
        return { 'current_site': Site.objects.get_current() }
    except Site.DoesNotExist:
        return { 'current_site': '' }

