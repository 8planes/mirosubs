from django.core.management import call_command
from widget.rpc import Rpc    

def refresh_obj(m):
    return m.__class__.objects.get(pk=m.pk)

def reset_solr():
    # cause the default site to load
    from haystack import backend
    sb = backend.SearchBackend()
    sb.clear()
    call_command('update_index')


rpc = Rpc()    
