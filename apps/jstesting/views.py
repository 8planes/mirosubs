from django.conf import settings
from django.shortcuts import render_to_response

def relative_path(js_file):
    return "/site_media/js/%s" % js_file

def js_dependencies():
    js_files = list(settings.JS_RAW)
    js_files.append('widget/testing/stubvideoplayer.js')
    js_files.append('widget/testing/events.js')
    return [relative_path(js_file) for js_file in js_files]

def jstest(request, file_name):
    return render_to_response('jstesting/%s.js' % file_name,
                              {'js_dependencies' : js_dependencies()})
