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
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from videos.models import Video, VIDEO_TYPE_YOUTUBE, VIDEO_TYPE_HTML5, Action, SubtitleVersion, StopNotification
from videos.forms import VideoForm, FeedbackForm, EmailFriendForm, UserTestResultForm, SubtitlesUploadForm
from apps.videos.models import SubtitleVersion
import widget
from django.contrib.sites.models import Site
from django.conf import settings
import simplejson as json
from videos.utils import get_pager
from django.contrib import messages
from django.db.models import Q
from widget.views import base_widget_params
from django.utils.http import urlencode
from haystack.query import SearchQuerySet
from vidscraper.errors import Error as VidscraperError
from django.template.loader import render_to_string
from django.utils.http import urlquote_plus
from auth.models import CustomUser as User
from datetime import datetime
from videos.utils import send_templated_email
from django.contrib.auth import logout

def index(request):
    context = widget.add_onsite_js_files({})
    context['widget_params'] = _widget_params(request, 'http://subtesting.com/video/Usubs-IntroVideo.theora.ogg', None, '')
    return render_to_response('index.html', context,
                              context_instance=RequestContext(request))

def _make_facebook_url(link, title):
    return "http://www.facebook.com/sharer.php?{0}".format(
        urlencode({'u': link, 't': title}))

def _make_twitter_url(message):
    return "http://twitter.com/home/?{0}".format(
        urlencode({'status': message}))

def _make_email_url(message):
    return "/videos/email_friend/?{0}".format(
        urlencode({'text': message}))

def _add_share_panel_context(context,
                             facebook_url, twitter_url,
                             embed_params,
                             email_url, permalink):
    context["share_panel_facebook_url"] = facebook_url
    context["share_panel_twitter_url"] = twitter_url
    context["share_panel_embed_code"] = render_to_string(
        'videos/_offsite_widget.html',
        {'embed_version': settings.EMBED_JS_VERSION,
         'embed_params': embed_params,
         'MEDIA_URL': settings.MEDIA_URL})
    context["share_panel_email_url"] = email_url
    context["share_panel_permalink"] = permalink

def _share_video_title(video):
    return u"(\"{0}\") ".format(video.title) if video.title else ''

def _add_share_panel_context_for_video(context, video):
    home_page_url = "http://{0}{1}".format(
        Site.objects.get_current().domain, 
        reverse('videos:video', kwargs={'video_id':video.video_id}))
    if video.latest_finished_version() is not None:
        twitter_fb_message = \
            u"Just found a version of this video with captions: {0}".format(
            home_page_url)
    else:
        twitter_fb_message = \
            u"Check out this video and help make subtitles: {0}".format(
            home_page_url)
    email_message = \
        u"Hey-- check out this video {0}and help make subtitles: {1}".format(
        _share_video_title(video), home_page_url)
    _add_share_panel_context(
        context,
        _make_facebook_url(home_page_url, twitter_fb_message),
        _make_twitter_url(twitter_fb_message),
        { 'video_url': video.get_video_url() },
        _make_email_url(email_message),
        home_page_url)

def _add_share_panel_context_for_history(context, video):
    page_url = "http://{0}{1}".format(
        Site.objects.get_current().domain,
        reverse('videos:history', args=[video.video_id]))
    twitter_fb_message = \
        u"Just found a version of this video with captions: {0}".format(page_url)
    email_message = \
        u"Hey-- just found a version of this video {0}with captions: {1}".format(
        _share_video_title(video), page_url)
    _add_share_panel_context(
        context,
        _make_facebook_url(page_url, twitter_fb_message),
        _make_twitter_url(twitter_fb_message),
        { 'video_url': video.get_video_url(), 'base_state': {} },
        _make_email_url(email_message),
        page_url)

def _add_share_panel_context_for_translation_history(context, video, language_code):
    page_url = "http://{0}{1}".format(
        Site.objects.get_current().domain,
        reverse('videos:translation_history', 
                args=[video.video_id, language_code]))
    language_name = widget.LANGUAGES_MAP[language_code]
    twitter_fb_message = \
        "Just found a version of this video with {0} subtitles: {1}".format(
        language_name, page_url)
    email_message = \
        "Hey-- just found a version of this video {0}with {1} subtitles: {2}".format(
        _share_video_title(video), language_name, page_url)
    _add_share_panel_context(
        context,
        _make_facebook_url(page_url, twitter_fb_message),
        _make_twitter_url(twitter_fb_message),
        { 'video_url': video.get_video_url(), 'base_state': { 'language': str(language_code) }},
        _make_email_url(email_message),
        page_url)

def ajax_change_video_title(request):
    video_id = request.POST.get('video_id')
    title = request.POST.get('title')
    user = request.user
    
    try:
        video = Video.objects.get(video_id=video_id)
        if title and not video.title or video.is_html5():
            old_title = video.title or video.video_url
            video.title = title
            video.save()
            action = Action(new_video_title=video.title, video=video)
            action.user = user.is_authenticated and user or None
            action.created = datetime.now()
            action.action_type = Action.CHANGE_TITLE
            action.save()
            
            users = video.notification_list(user)
            for obj in users:
                subject = u'Video\'s title changed on Universal Subtitles'
                context = {
                    'user': obj,
                    'domain': Site.objects.get_current().domain,
                    'video': video,
                    'editor': user,
                    'old_title': old_title,
                    'hash': obj.hash_for_video(video.video_id)
                }
                send_templated_email(obj.email, subject, 
                                     'videos/email_title_changed.html',
                                     context, 'feedback@universalsubtitles.org',
                                     fail_silently=not settings.DEBUG)            
    except Video.DoesNotExist:
        pass
    
    return HttpResponse('')

def create(request):
    if request.method == 'POST':
        video_form = VideoForm(request.POST, label_suffix="")
        if video_form.is_valid():
            owner = request.user if request.user.is_authenticated() else None
            video_url = video_form.cleaned_data['video_url']
            try:
                video, created = Video.get_or_create_for_url(video_url, owner)
                
            except VidscraperError:
                vidscraper_error = True
                return render_to_response('videos/create.html', locals(),
                              context_instance=RequestContext(request))
            if created:
                # TODO: log to activity feed
                pass
            if request.META['HTTP_USER_AGENT'].find('Mozilla') > -1:
                return_url = reverse('videos:video', kwargs={'video_id':video.video_id})
                return HttpResponseRedirect('{0}?{1}'.format(
                        reverse('onsite_widget'), 
                        urlencode({'subtitle_immediately': 'true',
                                   'video_url': video_url,
                                   'return_url': return_url })))
            else:
                return HttpResponseRedirect('{0}?subtitle_immediately=true'.format(reverse(
                            'videos:video', kwargs={'video_id':video.video_id})))            
            #if not video.owner or video.owner == request.user or video.allow_community_edits:
            #    return HttpResponseRedirect('{0}?autosub=true'.format(reverse(
            #            'videos:video', kwargs={'video_id':video.video_id})))
            #else:
            #    # TODO: better error page?
            #    return HttpResponse('You are not allowed to add transcriptions to this video.')
    else:
        video_form = VideoForm(label_suffix="")
    return render_to_response('videos/create.html', locals(),
                              context_instance=RequestContext(request))

def video(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    video.view_count += 1
    video.save()
    # TODO: make this more pythonic, prob using kwargs
    context = widget.add_onsite_js_files({})
    context['video'] = video
    context['site'] = Site.objects.get_current()
    context['autosub'] = 'true' if request.GET.get('autosub', False) else 'false'
    context['translations'] = video.subtitlelanguage_set.filter(is_complete=True) \
        .filter(is_original=False)
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, '')
    _add_share_panel_context_for_video(context, video)
    context['lang_count'] = len(context['translations'])
    context['original'] = video.subtitle_language()
    return render_to_response('videos/video.html', context,
                              context_instance=RequestContext(request))

def video_list(request):
    from django.db.models import Count, Q
    try:
        page = int(request.GET['page'])
    except (ValueError, TypeError, KeyError):
        page = 1
    qs = Video.objects.filter(Q(subtitlelanguage__is_complete=True, subtitlelanguage__is_original=False)|Q(subtitlelanguage__isnull=True)) \
        .annotate(translation_count=Count('subtitlelanguage')) 
    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')
    extra_context = {}
    order_fields = ['translation_count', 'widget_views_count', 'subtitles_fetched_count', 'is_subtitled']
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

@login_required
def upload_subtitles(request):
    output = dict(success=False)
    form = SubtitlesUploadForm(request.user, request.POST, request.FILES)
    if form.is_valid():
        form.save()
        output['success'] = True
    else:
        output['errors'] = form.get_errors()
    return HttpResponse(json.dumps(output), "text/javascript")

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
    from_email = ''
    if request.user.is_authenticated():
        from_email = request.user.email
    initial = dict(message=text, from_email=from_email)
    if request.method == 'POST':
        form = EmailFriendForm(request.POST, auto_id="email_friend_id_%s", label_suffix="")
        if form.is_valid():
            form.send()
            messages.info(request, 'Email Sent!')
            return redirect('videos:email_friend')
    else:
        form = EmailFriendForm(auto_id="email_friend_id_%s", initial=initial, label_suffix="")
    context = {
        'form': form
    }
    return render_to_response('videos/email_friend.html', context,
                              context_instance=RequestContext(request))

def demo(request):
    context = widget.add_onsite_js_files({})
    return render_to_response('demo.html', context,
                              context_instance=RequestContext(request))

def history(request, video_id, lang=None):
    video = get_object_or_404(Video, video_id=video_id)
    context = widget.add_onsite_js_files({})
    
    language = video.subtitle_language(lang)
    
    if not language:
        raise Http404
        
    qs = language.subtitleversion_set.filter(finished=True)   \
        .exclude(time_change=0, text_change=0)
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
    context['translations'] = video.subtitlelanguage_set.filter(is_original=False) \
        .exclude(pk=language.pk).filter(was_complete=True)
    context['last_version'] = language.latest_version()
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, lang or '')
    context['language'] = language
    _add_share_panel_context_for_history(context, video)
    return object_list(request, queryset=qs, allow_empty=True,
                       paginate_by=settings.REVISIONS_ONPAGE, 
                       page=request.GET.get('page', 1),
                       template_name='videos/history.html',
                       template_object_name='revision',
                       extra_context=context)

def _widget_params(request, video_url, version_no=None, language_code=None):
    params = {'video_url': video_url, 'base_state': {}}
    
    if version_no:
        params['base_state']['revision'] = version_no
        
    if language_code:
        params['base_state']['language'] = language_code

    return base_widget_params(request, params)

def revision(request, pk):
    version = get_object_or_404(SubtitleVersion, pk=pk)
    context = widget.add_onsite_js_files({})
    context['video'] = version.video
    context['version'] = version
    context['next_version'] = version.next_version()
    context['prev_version'] = version.prev_version()
    language = version.language
    context['language'] = language
    context['widget_params'] = _widget_params(request, \
            language.video.get_video_url(), version.version_no, language.language)
    context['latest_version'] = language.latest_finished_version()
    return render_to_response('videos/revision.html', context,
                              context_instance=RequestContext(request))     
    
@login_required
def rollback(request, pk):
    version = get_object_or_404(SubtitleVersion, pk=pk)
    is_writelocked = version.language.is_writelocked
    if is_writelocked:
        messages.error(request, u'Can not rollback now, because someone is editing subtitles.')
    elif not version.next_version():
        messages.error(request, message=u'Can not rollback to the last version')
    else:
        messages.success(request, message=u'Rollback successful')
        version = version.rollback(request.user)
    return redirect(version)

def diffing(request, first_pk, second_pk):
    first_version = get_object_or_404(SubtitleVersion, pk=first_pk)
    language = first_version.language
    second_version = get_object_or_404(SubtitleVersion, pk=second_pk, language=language)
    
    video = first_version.language.video
    if second_version.datetime_started > first_version.datetime_started:
        first_version, second_version = second_version, first_version
    
    second_captions = dict([(item.subtitle_id, item) for item in second_version.subtitles()])
    captions = []

    for caption in first_version.subtitles():
        try:
            scaption = second_captions[caption.subtitle_id]
        except KeyError:
            scaption = None
            changed = dict(text=True, time=True)
        else:
            changed = {
                'text': (not caption.subtitle_text == scaption.subtitle_text), 
                'time': (not caption.start_time == scaption.start_time),
                'end_time': (not caption.end_time == scaption.end_time)
            }
        data = [caption, scaption, changed]
        captions.append(data)
        
    context = widget.add_onsite_js_files({})
    context['video'] = video
    context['captions'] = captions
    context['language'] = language
    context['first_version'] = first_version
    context['second_version'] = second_version
    context['latest_version'] = language.latest_finished_version()
    context['widget0_params'] = \
        _widget_params(request, video.get_video_url(), 
                       first_version.version_no)
    context['widget1_params'] = \
        _widget_params(request, video.get_video_url(),
                       second_version.version_no)
    return render_to_response('videos/diffing.html', context,
                              context_instance=RequestContext(request)) 

def test_form_page(request):
    if request.method == 'POST':
        form = UserTestResultForm(request.POST)
        if form.is_valid():
            form.save(request)
            messages.success(request, 'Thanks for your feedback.  It\'s a huge help to us as we improve the site.')
            return redirect('videos:test_form_page')
    else:
        form = UserTestResultForm()
    context = {
        'form': form           
    }
    return render_to_response('videos/test_form_page.html', context,
                              context_instance=RequestContext(request))

def search(request):
    q = request.REQUEST.get('q')

    try:
        page = int(request.GET['page'])
    except (ValueError, TypeError, KeyError):
        page = 1  
          
    if q:
        qs = SearchQuerySet().auto_query(q).highlight()
    else:
        qs = TranslationLanguage.objects.none()
        
    context = {
        'query': q
    }
    ordering, order_type = request.GET.get('o'), request.GET.get('ot')
    order_fields = {
        'title': 'title',
        'language': 'language'
    }
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
        context['ordering'], context['order_type'] = ordering, order_type
        
    return object_list(request, queryset=qs, allow_empty=True,
                       paginate_by=30, page=page,
                       template_name='videos/search.html',
                       template_object_name='result',
                       extra_context=context)   

@login_required
def stop_notification(request, video_id):
    user_id = request.GET.get('u')
    hash = request.GET.get('h')

    if not user_id or not hash:
        raise Http404
    
    video = get_object_or_404(Video, video_id=video_id)
    user = get_object_or_404(User, id=user_id)
    context = dict(video=video, u=user)

    if hash and user.hash_for_video(video_id) == hash:
        StopNotification.objects.get_or_create(user=user, video=video)
        if request.user.is_authenticated() and not request.user == user:
            logout(request)
    else:
        context['error'] = u'Incorrect secret hash'
    return render_to_response('videos/stop_notification.html', context,
                              context_instance=RequestContext(request))
