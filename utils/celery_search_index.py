from haystack import indexes
from django.db.models import signals
from celery.decorators import task
from haystack import site
from haystack.exceptions import NotRegistered

UPDATE = 'update'
REMOVE = 'remove'

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
        update_search_index.delay(instance.__class__, instance.pk, UPDATE)
    
    def remove_handler(self, instance, **kwargs):
        update_search_index.delay(instance.__class__, instance.pk, REMOVE)

@task()    
def update_search_index(model_class, pk, action=UPDATE):
    print 'UPDATE SEARCH INDEX'
    import sentry_logger
    import logging
    
    try:
        obj = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        logging.warning(u'Object does not exist', model=model_class, pk=pk, action=action)
        return
    
    try:
        search_index = site.get_index(model_class)
    except NotRegistered:
        logging.warning(u'Seacrh index is not registered', model=model_class, pk=pk, action=action)
        return None
    
    if action == UPDATE:
        search_index.update_object(obj)
    elif action == REMOVE:
        search_index.remove_object(obj)