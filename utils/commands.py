from django.core.management.base import BaseCommand
from sentry.client.models import client

class ErrorHandlingCommand(BaseCommand):
    
    def handle_error(self, exc_info):
        client.create_from_exception(exc_info)
    
    def print_to_console(self, msg, min_verbosity=1):
        if self.verbosity >= min_verbosity:
            print msg    