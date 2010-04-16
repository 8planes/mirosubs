# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from videos.forms import VideoForm, FeedbackForm
from videos.models import Video, VIDEO_TYPE_YOUTUBE, VIDEO_TYPE_HTML5
import widget
from urlparse import urlparse, parse_qs
from django.contrib.sites.models import Site
from django.shortcuts import redirect

def create(request):
    if request.method == 'POST':
        video_form = VideoForm(request.POST)
        if video_form.is_valid():
            owner = request.user if request.user.is_authenticated() else None
            parsed_url = urlparse(video_form.cleaned_data['video_url'])
            if 'youtube.com' in parsed_url.netloc:
                yt_video_id = parse_qs(parsed_url.query)['v'][0]
                video, created = Video.objects.get_or_create(
                                    youtube_videoid=yt_video_id,
                                    defaults={'owner': owner,
                                              'video_type': VIDEO_TYPE_YOUTUBE})
            else:
                video, created = Video.objects.get_or_create(
                                    video_url=video_form.cleaned_data['video_url'],
                                    defaults={'owner': owner,
                                              'video_type': VIDEO_TYPE_HTML5})
            if created:
                # TODO: log to activity feed
                pass
            if not video.owner or video.owner == request.user or video.allow_community_edits:
                return HttpResponseRedirect(reverse(
                        'videos:video', kwargs={'video_id':video.video_id}))
            else:
                # TODO: better error page?
                return HttpResponse('You are not allowed to add transcriptions to this video.')
    else:
        video_form = VideoForm()
    return render_to_response('videos/create.html', locals(),
                              context_instance=RequestContext(request))

def video(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    video.view_count += 1
    video.save()
    # TODO: make this more pythonic, prob using kwargs
    context = widget.js_context(request, video, False, None, False, None, True)
    context['video'] = video
    context['site'] = Site.objects.get_current()
    return render_to_response('videos/video.html', context,
                              context_instance=RequestContext(request))
                              
def video_list(request):
    from django.db.models import Count
    try:
        page = int(request.GET['page'])
    except (ValueError, TypeError, KeyError):
        page = 1
    qs = Video.objects.annotate(translation_count=Count('translationlanguage'))
    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')
    extra_context = {}
    order_fields = ['translation_count', 'widget_views_count', 'subtitles_fetched_count']
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+ordering)
        extra_context['ordering'] = ordering
        extra_context['order_type'] = order_type
    return object_list(request, queryset=qs, allow_empty=True,
                       paginate_by=50, page=page,
                       template_name='videos/video_list.html',
                       template_object_name='video',
                       extra_context=extra_context)

def feedback(request, success=False):
    if not success and request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.send()
            return redirect('videos:feedback_success')
    else:
        form = FeedbackForm()
    context = dict(form=form, success=success)
    return render_to_response('videos/feedback.html', context,
                              context_instance=RequestContext(request))