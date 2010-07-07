import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command

SOLR_ROOT = settings.SOLR_ROOT

class Command(BaseCommand):
    def handle(self, **options):
        # Make sure the `SOLR_ROOT` and `start.jar` exist.
        if not SOLR_ROOT:
            raise CommandError("SOLR_ROOT is not specified")
        start_jar_path = os.path.join(SOLR_ROOT, 'start.jar')
        if not os.path.exists(start_jar_path):
            raise CommandError("No Solr start.jar found at %s" % start_jar_path)
        
        # Start Solr subprocess
        print "Updating schema.xml"
        call_command('solr_schema')
        print "Starting Solr process. CTL-C to exit."
        os.chdir(SOLR_ROOT)
        try:
            subprocess.call(["java", "-jar", "start.jar"])
        except KeyboardInterrupt:
            # Throws nasty errors if we don't catch the keyboard interrupt.
            pass
        print "Solr process has been interrupted"
