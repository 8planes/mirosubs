from haystack import indexes
from django.db.models import signals
from utils.celery_utils import task
from haystack import site
from haystack.exceptions import NotRegistered
from haystack.utils import get_identifier
from django.conf import settings
from utils.redis_utils import default_connection
import time

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
        update_search_index.deplay(instance.__class__, instance.pk)
    
    def remove_handler(self, instance, **kwargs):
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
        log(u'Object does not exist for %s %s' % (model_class, pk))
        return

    try:
        search_index = site.get_index(model_class)
    except NotRegistered:
        log(u'Seacrh index is not registered for %s' % model_class)
        return None

    search_index.update_object(obj)

@task()    
def update_search_index_for_qs(model_class, pks):
    start = time.time()
    
    qs = model_class._default_manager.filter(pk__in=pks)

    try:
        search_index = site.get_index(model_class)
    except NotRegistered:
        log(u'Seacrh index is not registered for %s' % model_class)
        return None
    
    search_index.backend.update(search_index, qs)
    
    LogEntry(num=len(pks), time=time.time()-start).save()
    
from redisco import models as rmodels

class LogEntry(rmodels.Model):
    num = rmodels.IntegerField()
    time = rmodels.FloatField()
    date = rmodels.DateTimeField(auto_now_add=True)
        
    class Meta:
        verbose_name = 'Search index update statistic'
        verbose_name_plural = 'Search index update statistic'
        db = default_connection