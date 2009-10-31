from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from uuid import uuid4
from videos.forms import VideoForm
from widget.models import Video
from widget.views import add_params

@login_required
def create(request):
    if request.method == 'POST':
        video_form = VideoForm(request.POST)
        if video_form.is_valid():
            video, created = Video.objects.get_or_create(video_url=video_form.cleaned_data['video_url'])
            if created:
                pass
                # log into activity feed
            return HttpResponseRedirect(reverse('videos:video', kwargs={'video_id':video.video_id}))
    else:
        video_form = VideoForm()
    return render_to_response('videos/create.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def video(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    has_subtitles = video.videocaption_set.count() > 0
    has_subtitles_var = 'true' if has_subtitles else 'false'
    uuid = str(uuid4()).replace('-', '')
    return render_to_response('videos/video.html', add_params(locals()),
                              context_instance=RequestContext(request))