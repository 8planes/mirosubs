from haystack import indexes
from django.db.models import signals
from celery.decorators import task
from haystack import site
from haystack.exceptions import NotRegistered
from haystack.utils import get_identifier
from django.conf import settings

SEARCH_INDEX_UPDATE_OFF = getattr(settings, 'SEARCH_INDEX_UPDATE_OFF', True)

class CelerySearchIndex(indexes.SearchIndex):
    
    def _setup_save(self, model):
        signals.post_save.connect(self.update_handler, sender=model)
    
    def _setup_delete(self, model):
        signals.post_delete.connect(self.remove_handler, sender=model)
    
    def _teardown_save(self, model):
        signals.post_save.disconnect(self.update_handler, sender=model)
    
    def _teardown_delete(self, model):
        signals.post_delete.disconnect(self.remove_handler, sender=model)
        
    def update_handler(self, instance, **kwargs):
        if not SEARCH_INDEX_UPDATE_OFF:
            update_search_index.delay(instance.__class__, instance.pk)
    
    def remove_handler(self, instance, **kwargs):
        if not SEARCH_INDEX_UPDATE_OFF:
            remove_search_index.delay(instance.__class__, get_identifier(instance))

def log(*args, **kwargs):
    import sentry_logger
    import logging
    logger = logging.getLogger('search.index.updater')    
    logger.warning(*args, **kwargs)
    
@task()  
def remove_search_index(model_class, obj_identifier):
    try:
        search_index = site.get_index(model_class)
    except NotRegistered:
        log(u'Seacrh index is not registered for %s' % model_class)
        return None
    
    search_index.remove_object(obj_identifier)
    
@task()    
def update_search_index(model_class, pk):
    try:
        obj = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        log(u'Object does not exist for %s' % model_class)
        return
    
    try:
        search_index = site.get_index(model_class)
    except NotRegistered:
        log(u'Seacrh index is not registered for %s' % model_class)
        return None
    
    search_index.update_object(obj)
        