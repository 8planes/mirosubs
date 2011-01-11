from targetter.models import MessageConfig 
from utils import render_to_json
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site

@render_to_json
def load(request):
    id = request.GET.get('id', None)
    
    if not id:
        return {
            'error': u'Incorrect request.'
        }
        
    try:
        config = MessageConfig.objects.get(pk=id)
    except MessageConfig.DoesNotExist:
        return {
            'error': u'Config does not exist.'
        }
        
    return config.get_config()

def test(request, pk):
    config = get_object_or_404(MessageConfig, pk=pk)
    context = {
        'config': config,
        'domain': Site.objects.get_current().domain
    }
    return direct_to_template(request, 'targetter/load.html', context)