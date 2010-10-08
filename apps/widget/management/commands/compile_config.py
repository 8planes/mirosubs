from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import render_to_string
from os.path import join
from django.contrib.sites.models import Site
import widget

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        media_dir = args[0]
        file_name = join(media_dir, 'js/config.js')
        context = {'current_site': Site.objects.get_current(),
                   'MEDIA_URL': settings.MEDIA_URL}
        rendered = render_to_string(
            'widget/config.js', context)
        with open(file_name, 'w') as f:
            f.write(rendered)
