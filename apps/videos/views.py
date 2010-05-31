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
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from videos.models import Video, VIDEO_TYPE_YOUTUBE, VIDEO_TYPE_HTML5, Action, TranslationLanguage, VideoCaptionVersion, TranslationVersion
from videos.forms import VideoForm, FeedbackForm, EmailFriendForm, UserTestResultForm
import widget
from urlparse import urlparse, parse_qs
from django.contrib.sites.models import Site
from django.conf import settings
import simplejson as json
from django.utils.encoding import DjangoUnicodeDecodeError
import feedparser

def create(request):
    if request.method == 'POST':
        video_form = VideoForm(request.POST, label_suffix="")
        if video_form.is_valid():
            owner = request.user if request.user.is_authenticated() else None
            parsed_url = urlparse(video_form.cleaned_data['video_url'])
            if 'youtube.com' in parsed_url.netloc:
                yt_video_id = parse_qs(parsed_url.query)['v'][0]
                video, created = Video.objects.get_or_create(
                                    youtube_videoid=yt_video_id,
                                    defaults={'owner': owner,
                                              'video_type': VIDEO_TYPE_YOUTUBE})
                if created:
                    url = 'http://gdata.youtube.com/feeds/api/videos/%s' % video.youtube_videoid
                    data = feedparser.parse(url)
                    try:
                        video.youtube_name = data['entries'][0]['title']
                        video.save()
                    except DjangoUnicodeDecodeError:
                        pass
            else:
                video, created = Video.objects.get_or_create(
                                    video_url=video_form.cleaned_data['video_url'],
                                    defaults={'owner': owner,
                                              'video_type': VIDEO_TYPE_HTML5})
            if created:
                # TODO: log to activity feed
                pass
            if not video.owner or video.owner == request.user or video.allow_community_edits:
                return HttpResponseRedirect('{0}?autosub=true'.format(reverse(
                        'videos:video', kwargs={'video_id':video.video_id})))
            else:
                # TODO: better error page?
                return HttpResponse('You are not allowed to add transcriptions to this video.')
    else:
        video_form = VideoForm(label_suffix="")
    return render_to_response('videos/create.html', locals(),
                              context_instance=RequestContext(request))

def video(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    video.view_count += 1
    video.save()
    # TODO: make this more pythonic, prob using kwargs
    context = widget.js_context(request, video, False, None, False, None, 
                                'autosub' in request.GET)
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

def actions_list(request):
    try:
        page = int(request.GET['page'])
    except (ValueError, TypeError, KeyError):
        page = 1    
    qs = Action.objects.all()
    
    extra_context = {}
    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')    
    order_fields = ['user__username', 'created', 'video__video_id']
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+ordering)
        extra_context['ordering'] = ordering
        extra_context['order_type'] = order_type
            
    return object_list(request, queryset=qs, allow_empty=True,
                       paginate_by=settings.ACTIVITIES_ONPAGE, page=page,
                       template_name='videos/actions_list.html',
                       template_object_name='action',
                       extra_context=extra_context)    

def feedback(request):
    output = dict(success=False)
    form = FeedbackForm(request.POST)
    if form.is_valid():
        form.send(request)
        output['success'] = True
    else:
        output['errors'] = form.get_errors()
    return HttpResponse(json.dumps(output), "text/javascript")

def email_friend(request):
    text = request.GET.get('text', '')
    link = request.GET.get('link', '')
    if link:
        text = link if not text else '%s\n%s' % (text, link) 
    initial = dict(message=text)
    if request.method == 'POST':
        form = EmailFriendForm(request.POST, auto_id="email_friend_id_%s", label_suffix="")
        if form.is_valid():
            form.send()
    else:
        form = EmailFriendForm(auto_id="email_friend_id_%s", initial=initial, label_suffix="")
    context = {
        'form': form
    }
    return render_to_response('videos/email_friend.html', context,
                              context_instance=RequestContext(request))

def demo(request):
    context = {}
    return render_to_response('videos/demo.html', context,
                              context_instance=RequestContext(request))
    
def history(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    context = widget.js_context(request, video, False, None, False, None, 
                                'autosub' in request.GET)

    qs = VideoCaptionVersion.objects.filter(video=video)
    ordering, order_type = request.GET.get('o'), request.GET.get('ot')
    order_fields = {
        'date': 'datetime_started', 
        'user': 'user__username', 
        'note': 'note', 
        'time': 'time_change', 
        'text': 'text_change'
    }
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
        context['ordering'], context['order_type'] = ordering, order_type

    context['video'] = video
    context['site'] = Site.objects.get_current()
    context['translations'] = TranslationLanguage.objects.filter(video=video)
    context['revisions'] = qs  
    return render_to_response('videos/history.html', context,
                              context_instance=RequestContext(request))

def translation_history(request, video_id, lang):
    video = get_object_or_404(Video, video_id=video_id)
    language = get_object_or_404(TranslationLanguage, video=video, language=lang)
    context = widget.js_context(request, video, False, None, False, None, 
                                'autosub' in request.GET)
   
    qs = TranslationVersion.objects.filter(language=language)
    ordering, order_type = request.GET.get('o'), request.GET.get('ot')
    order_fields = {
        'date': 'datetime_started', 
        'user': 'user__username', 
        'note': 'note', 
        'time': 'time_change', 
        'text': 'text_change'
    }
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
        context['ordering'], context['order_type'] = ordering, order_type 
    
    context['revisions'] = qs
    context['video'] = video
    context['language'] = language
    context['site'] = Site.objects.get_current()        
    context['translations'] = TranslationLanguage.objects.filter(video=video).exclude(pk=language.pk)
    return render_to_response('videos/translation_history.html', context,
                              context_instance=RequestContext(request))    

def revision(request, pk, cls=VideoCaptionVersion, tpl='videos/revision.html'):
    version = get_object_or_404(cls, pk=pk)
    context = widget.js_context(request, version.video, False, None, False, None, 
                                'autosub' in request.GET)
    context['video'] = version.video
    context['version'] = version
    context['next_version'] = version.next_version()
    context['prev_version'] = version.prev_version()
    
    if cls == TranslationVersion:
        tpl = 'videos/translation_revision.html'
        context['latest_version'] = version.language.translations()
    else:
        context['latest_version'] = version.video.captions()
    return render_to_response(tpl, context,
                              context_instance=RequestContext(request))     

@login_required
def rollback(request, pk, cls=VideoCaptionVersion):
    version = get_object_or_404(cls, pk=pk)
    if not version.next_version():
        request.user.message_set.create(message='Can not rollback to the last version')
    else:
        request.user.message_set.create(message='Rollback was success')
        version = version.rollback(request.user)
    url_name = (cls == TranslationVersion) and 'translation_revision' or 'revision'
    return redirect('videos:%s' % url_name, pk=version.pk)

def diffing(request, first_pk, second_pk):
    first_version = get_object_or_404(VideoCaptionVersion, pk=first_pk)
    video = first_version.video
    second_version = get_object_or_404(VideoCaptionVersion, pk=second_pk, video=video)
    if second_version.datetime_started > first_version.datetime_started:
        first_version, second_version = second_version, first_version
    
    second_captions = dict([(item.caption_id, item) for item in second_version.captions()])
    captions = []
    for caption in first_version.captions():
        try:
            scaption = second_captions[caption.caption_id]
        except KeyError:
            scaption = None
            changed = dict(text=True, time=True)
        else:
            changed = {
                'text': (not caption.caption_text == scaption.caption_text), 
                'time': (not caption.start_time == scaption.start_time),
                'end_time': (not caption.end_time == scaption.end_time)
            }
        data = [caption, scaption, changed]
        captions.append(data)
        
    context = widget.js_context(request, video, False, None, False, None, 
                                'autosub' in request.GET)
    context['video'] = video
    context['captions'] = captions
    context['first_version'] = first_version
    context['second_version'] = second_version
    context['history_link'] = reverse('videos:history', args=[video.video_id])     
    return render_to_response('videos/diffing.html', context,
                              context_instance=RequestContext(request)) 

def translation_diffing(request, first_pk, second_pk):
    first_version = get_object_or_404(TranslationVersion, pk=first_pk)
    language = first_version.language
    video = first_version.video
    second_version = get_object_or_404(TranslationVersion, pk=second_pk, language=language)
    if second_version.datetime_started > first_version.datetime_started:
        first_version, second_version = second_version, first_version
    
    second_captions = dict([(item.caption_id, item) for item in second_version.captions()])
    captions = []
    for caption in first_version.captions():
        try:
            scaption = second_captions[caption.caption_id]
        except KeyError:
            scaption = None
        changed = scaption and not caption.translation_text == scaption.translation_text 
        data = [caption, scaption, dict(text=changed, time=False, end_time=False)]
        captions.append(data)
        
    context = widget.js_context(request, video, False, None, False, None, 
                                'autosub' in request.GET)
    context['video'] = video
    context['captions'] = captions
    context['first_version'] = first_version
    context['second_version'] = second_version
    context['history_link'] = reverse('videos:translation_history', args=[video.video_id, language.language]) 
    return render_to_response('videos/translation_diffing.html', context,
                              context_instance=RequestContext(request))

@login_required    
def test_form_page(request):
    if request.method == 'POST':
        form = UserTestResultForm(request.POST)
        if form.is_valid():
            form.save(request)
            request.user.message_set.create(message='Thanks for your feedback.  It\'s a huge help to us as we improve the site')
            return redirect('videos:test_form_page')
    else:
        form = UserTestResultForm()
    context = {
        'form': form           
    }
    return render_to_response('videos/test_form_page.html', context,
                              context_instance=RequestContext(request))