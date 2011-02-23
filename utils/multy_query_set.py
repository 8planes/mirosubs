from django.db.models import ObjectDoesNotExist

class MultyQuerySet(object):
    """
    Proxy-object for few QuerySet to be used in Paginator.
    Support only QuerySets for same model.
    """
    
    def __init__(self, *args):
        self.lists = args
        self.model = self.lists[0].model
        
        self._obj_ids = []
        self._cache = {}
        
        for l in self.lists:
            self._obj_ids.extend(l.values_list('pk', flat=True))
        
    def __len__(self):
        return len(self._obj_ids)
    
    def __getitem__(self, k):
        if not isinstance(k, (slice, int, long)):
            raise TypeError
        
        cache_key = k
        if isinstance(k, slice):
            cache_key = '%s:%s:%s' % (k.start, k.stop, k.step)
        
        try:
            return self._cache[cache_key]
        except KeyError:
            pass
        
        val = None
        
        if isinstance(k, (int, long)):
            try:
                val = id._model._default_manager.get(pk=id)
            except ObjectDoesNotExist:
                pass
        else:
            ids = self._obj_ids[k]
            qs = self.model._default_manager.filter(pk__in=ids)
            result = dict((obj.pk, obj) for obj in qs)
            val = []
            for id in ids:
                val.append(result[id])
            
        self._cache[cache_key] = val
        return val
        
    def _clone(self):
        return self
    