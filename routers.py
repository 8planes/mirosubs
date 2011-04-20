from django.conf import settings

USLOGGING_DATABASE = getattr(settings, 'USLOGGING_DATABASE', None)

class UnisubsRouter(object):
    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['sentry', 'uslogging'] :
            return USLOGGING_DATABASE

    def db_for_read(self, model, **hints):
        return self.db_for_write(model, **hints)

    def allow_syncdb(self, db, model):
        if not USLOGGING_DATABASE:
            return None
        if model._meta.app_label in ['sentry', 'uslogging'] and db != USLOGGING_DATABASE:
            return False
