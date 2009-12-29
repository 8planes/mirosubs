from django.http import HttpResponse
from django.shortcuts import render_to_response
from uuid import uuid1

def embed(request):
    params = {}
    params['video_id'] = request.GET['video_id']
    if request.user.is_authenticated():
        params['username'] = request.user.username
    params['uuid'] = str(uuid1()).replace('-', '')
    return render_to_response('widget/embed.js', params, 
                              mimetype="text/javascript")

def mirosubsjs(request):
    return render_to_response('widget/mirosubs_widget.js', mimetype="text/javascript")

def save_captions(request):
    iframe_id = request.POST['iframe_id']
    return render_to_response('widget/iframe_rpc_response.html',
                              { 'id' : iframe_id,
                                'result' : '\'hello, world\'' })
