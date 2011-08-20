from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import render_to_string
from os.path import join
from django.contrib.sites.models import Site
import widget

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        output_dir = args[0]
        self._output_embed_to_dir(output_dir)
        self._output_embed_to_dir(output_dir, settings.EMBED_JS_VERSION)
        for version in settings.PREVIOUS_EMBED_JS_VERSIONS:
            self._output_embed_to_dir(output_dir, version)

    def _output_embed_to_dir(self, output_dir, version=''):
        file_name = 'embed{0}.js'.format(version)
        context = widget.embed_context()
        rendered = render_to_string(
            'widget/{0}'.format(file_name), context)
        with open(join(output_dir, file_name), 'w') as f:
            f.write(rendered)
