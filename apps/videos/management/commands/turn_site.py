from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Turn on or off the site."
    args = '[on or off]'
 
    def handle(self, flag, *args, **options):
        if flag not in ['on', 'off']:
            raise CommandError('Undefined parameter: %s' % flag)
        
        disabled_path = os.path.join(settings.PROJECT_ROOT, 'disabled')
        
        if flag == 'off':
            if not os.path.exists(disabled_path):
                file = open(disabled_path, 'w')
                file.write('')
                file.close()
        else:
            os.path.exists(disabled_path) and os.remove(disabled_path)
