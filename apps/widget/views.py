from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from uuid import uuid4
from django.contrib.sites.models import Site
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from django.template import RequestContext
from django.http import HttpResponseRedirect
import simplejson as json

def full_path(js_file):
    return "http://%s/site_media/js/%s" % (Site.objects.get_current().domain, js_file)

def add_params(params=None):
    if params is None:
        params = {}
    params["js_use_compiled"] = settings.JS_USE_COMPILED
    if settings.JS_USE_COMPILED:
        # might change in future when using cdn to serve static js
        params["js_dependencies"] = [full_path("mirosubs-compiled.js")]
    else:
        params["js_dependencies"] = [full_path(js_file) for js_file in settings.JS_RAW]
    params["site"] = Site.objects.get_current()
    return params

def embed(request):
    params = {}
    params['video_id'] = request.GET['video_id']
    if request.user.is_authenticated():
        params['username'] = request.user.username
    params['uuid'] = str(uuid4()).replace('-', '')
    params['referer'] = request.META.get('HTTP_REFERER', '')
    return render_to_response('widget/embed.js', add_params(params), 
                              mimetype="text/javascript")

def save_captions(request):
    video_id = request.POST["xdp:video_id"];
    deleted_captions = json.loads(request.POST["xdp:deleted"]);
    inserted_captions = json.loads(request.POST["xdp:inserted"]);
    updated_captions = json.loads(request.POST["xdp:updated"]);

    # TODO: save caption work to database
    # for definition of json format, see mirosubs-captionwidget.js

    params = {}
    params['request_id'] = request.POST["xdpe:request-id"]
    params['dummy_uri'] = request.POST["xdpe:dummy-uri"]
    params['response_json'] = '{\\"response\\": \\"ok\\"}'
    return render_to_response('widget/save_captions_response.html',
                              add_params(params))

def login(request):
    "Similar to django.contrib.auth.views.login, except handles off-site redirects"
    redirect_field_name = 'to_redirect'
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":        
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return render_to_response('widget/set_parent_url.html',
                                      {'url': redirect_to})
    else:
        form = AuthenticationForm(request)
        request.session.set_test_cookie()
        if Site._meta.installed:
            current_site = Site.objects.get_current()
        else:
            current_site = RequestSite(request)
        return render_to_response('widget/login.html', {
                'form': form,
                redirect_field_name : redirect_to,
                'site': current_site,
                'site_name': current_site.name,
                }, context_instance=RequestContext(request))
login = never_cache(login)
