import datetime
import logging
try:
    import threading
except ImportError:
    threading = None
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel

class ThreadTrackingHandler(logging.Handler):
    def __init__(self):
        if threading is None:
            raise NotImplementedError("threading module is not available, \
                the logging panel cannot be used without it")
        logging.Handler.__init__(self)
        self.records = {} # a dictionary that maps threads to log records

    def emit(self, record):
        self.get_records().append(record)

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is provided,
        returns a list for the current thread.
        """
        if thread is None:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]

handler = ThreadTrackingHandler()
logging.root.setLevel(logging.NOTSET)
logging.root.addHandler(handler)

class LoggingPanel(DebugPanel):
    name = 'Logging'
    has_content = True

    def process_request(self, request):
        handler.clear_records()

    def get_and_delete(self):
        records = handler.get_records()
        handler.clear_records()
        return records

    def nav_title(self):
        return _("Logging")

    def nav_subtitle(self):
        # FIXME l10n: use ngettext
        return "%s message%s" % (len(handler.get_records()), (len(handler.get_records()) == 1) and '' or 's')

    def title(self):
        return _('Log Messages')

    def url(self):
        return ''

    def content(self):
        records = []
        for record in self.get_and_delete():
            records.append({
                'message': record.getMessage(),
                'time': datetime.datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'file': record.pathname,
                'line': record.lineno,
            })

        context = self.context.copy()
        context.update({'records': records})

        return render_to_string('debug_toolbar/panels/logger.html', context)

