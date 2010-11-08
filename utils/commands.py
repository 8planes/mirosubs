from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
import sys

class ErrorHandlingCommand(BaseCommand):
    
    def _handle_error(self, email_subtject, command_msg, exc_info):
        message = "%s\n\n%s" % (self._get_traceback(exc_info),command_msg)
        mail_admins(email_subtject, message, fail_silently=False)

    def _get_traceback(self, exc_info=None):
        import traceback
        
        "Helper function to return the traceback as a string"
        return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))            
    
    def print_to_console(self, msg, min_verbosity=1):
        if self.verbosity >= min_verbosity:
            print msg    