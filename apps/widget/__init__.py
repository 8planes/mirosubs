from uuid import uuid4
from videos import models
from django.conf import settings
from django.contrib.sites.models import Site

def js_context(request, video):
    params = {'uuid': uuid4().replace('-', ''),
              'video_id': video.video_id,
              'video_url': video.video_url,}
    if video.caption_state == models.NO_CAPTIONS:
        params['show_tab'] = 0
    elif video.caption_state == models.CAPTIONS_IN_PROGRESS:
        if request.user.is_authenticated and request.user == video.owner:
            params['show_tab'] = 1
        else:
            params['show_tab'] = 2
            params['owned_by'] = video.owner.username
    else:
        params['show_tab'] = 3
    params["js_use_compiled"] = settings.JS_USE_COMPILED
    if settings.JS_USE_COMPILED:
        # might change in future when using cdn to serve static js
        params["js_dependencies"] = [full_path("mirosubs-compiled.js")]
    else:
        params["js_dependencies"] = [full_path(js_file) for js_file in settings.JS_RAW]
    params["site"] = Site.objects.get_current()
    return params
    