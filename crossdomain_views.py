from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page


@cache_page(60 *60*5)
def root_crossdomain(request):
    return render_to_response("crossdomains/root.xml")

@cache_page(60 *60*5)
def api_crossdomain(request):
    return render_to_response("crossdomains/api.xml")


