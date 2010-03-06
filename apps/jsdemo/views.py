from django.conf import settings
from django.shortcuts import render_to_response

def relative_path(js_file):
    return "/site_media/js/%s" % js_file

def js_dependencies():
    return [relative_path(js_file) for js_file in settings.JS_RAW]

def jsdemo(request, file_name):
    return render_to_response('jsdemo/%s.html' % file_name,
                              {'js_dependencies' : js_dependencies()})
