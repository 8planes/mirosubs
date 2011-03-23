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
            qs = self.get_objects_qs(ids)
            result = dict((obj.pk, obj) for obj in qs)
            val = []
            for id in ids:
                val.append(result[id])
            
        self._cache[cache_key] = val
        return val
        
    def _clone(self):
        return self
    
    def get_objects_qs(self, ids):
        return self.model._default_manager.filter(pk__in=ids)

class TeamMultyQuerySet(object):
    
    def __init__(self, *args):
        self.lists = args
        self._cache = {}
    
    def get_qs_count(self, qs):
        if not hasattr(qs, '_length'):
            qs._length = qs.count()
        return qs._length
    
    def __len__(self):
        if not hasattr(self, '_lenght'):
            self._length = sum([self.get_qs_count(qs) for qs in self.lists])
        return self._length
    
    def __getitem__(self, k):
        #support only [n] or [n:m], not [:m] or [n:]
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
            i = 0
            for qs in self.lists:
                if k < (i + self.get_qs_count(qs)):
                    val = qs._default_manager.all()[i+k]
                i += self.get_qs_count(qs)
        else:
            selected = []
            
            k_start = k.start #because readonly
            k_stop = k.stop #because readonly
            
            number = k.stop-k.start
            
            cur_index = 0
            qs_list = []
            for i, qs in enumerate(self.lists):
                if k_start < (cur_index+self.get_qs_count(qs)):
                    qs_list = self.lists[i:]
                    break
                cur_index += self.get_qs_count(qs)
                
            k_start -= cur_index
            k_stop = k_start+number

            for qs in qs_list:
                tl = qs[k_start:k_stop]
                selected.extend(tl)
                k_start = 0
                k_stop = number - len(selected)                    
                if k_stop <= 0:
                    break
            
            val = []
            videos = []
            for obj in selected:
                if obj.team_video_key not in videos:
                    videos.append(obj.team_video_key)
                    val.append(obj)
            
        self._cache[cache_key] = val
        return val
        
    def _clone(self):
        return self
    
    def get_objects_qs(self, ids):
        return self.model._default_manager.filter(pk__in=ids)