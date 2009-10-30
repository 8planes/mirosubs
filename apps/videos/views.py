from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from videos.forms import VideoForm
from widget.models import Video

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
    return render_to_response('videos/video.html', locals(),
                              context_instance=RequestContext(request))