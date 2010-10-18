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
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from videos.models import Video, Action, StopNotification, SubtitleLanguage, SubtitleVersion, VideoUrl
from videos.forms import VideoForm, FeedbackForm, EmailFriendForm, UserTestResultForm, SubtitlesUploadForm
import widget
from django.contrib.sites.models import Site
from django.conf import settings
import simplejson as json
from django.contrib import messages
from widget.views import base_widget_params
from haystack.query import SearchQuerySet
from vidscraper.errors import Error as VidscraperError
from auth.models import CustomUser as User
from datetime import datetime
from videos.utils import send_templated_email
from django.contrib.auth import logout
from videos.share_utils import _add_share_panel_context_for_video, _add_share_panel_context_for_history
from gdata.service import RequestError
from django.db.models import Sum
from django.utils.translation import ugettext

def index(request):
    context = widget.add_onsite_js_files({})
    context['widget_params'] = _widget_params(request, 'http://subtesting.com/video/Usubs-IntroVideo.theora.ogg', None, '')
    context['all_videos'] = Video.objects.count()
    return render_to_response('index.html', context,
                              context_instance=RequestContext(request))

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
            action.user = user.is_authenticated() and user or None
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
            video_url = video_form.cleaned_data['video_url']
            try:
                video, created = Video.get_or_create_for_url(video_url)
            except (VidscraperError, RequestError):
                vidscraper_error = True
                return render_to_response('videos/create.html', locals(),
                              context_instance=RequestContext(request))
            messages.info(request, message=u'''Here is the subtitle workspace for your video.  You can
share the video with friends, or get an embed code for your site.  To add or
improve subtitles, click the button below the video''')
            return redirect(video)
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
    context['translations'] = video.subtitlelanguage_set.filter(was_complete=True) \
        .filter(is_original=False)
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, '')
    _add_share_panel_context_for_video(context, video)
    context['lang_count'] = video.subtitlelanguage_set.filter(is_complete=True).count()
    context['original'] = video.subtitle_language()
    context['video_urls'] = video.videourl_set.all()
    return render_to_response('videos/video.html', context,
                              context_instance=RequestContext(request))

def video_list(request):
    qs = Video.objects.exclude(subtitlelanguage=None).extra(select={'translation_count': 'SELECT COUNT(id) '+
        'FROM videos_subtitlelanguage WHERE '+
        'videos_subtitlelanguage.video_id = videos_video.id AND '+
        'videos_subtitlelanguage.was_complete AND '+
        'NOT videos_subtitlelanguage.is_original'})

    ordering = request.GET.get('o')
    order_type = request.GET.get('ot')
    extra_context = {}
    order_fields = ['translation_count', 'widget_views_count', 'subtitles_fetched_count', 'was_subtitled']
    if ordering in order_fields and order_type in ['asc', 'desc']:
        qs = qs.order_by(('-' if order_type == 'desc' else '')+ordering)
        extra_context['ordering'] = ordering
        extra_context['order_type'] = order_type
    return object_list(request, queryset=qs,
                       paginate_by=50,
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

def api_subtitles(request):
    callback = request.GET.get('callback', None)
    result_json = json.dumps(_api_subtitles_json(request))
    if callback:
        return HttpResponse('{0}({1});'.format(callback, result_json),
                            'text/javascript')
    else:
        return HttpResponse(result_json, 'application/json')

def _api_subtitles_json(request):
    video_url = request.GET.get('video_url', None)
    language = request.GET.get('language', None)
    revision = request.GET.get('revision', None)
    if video_url is None:
        return {'is_error': True, 'message': 'video_url not specified' }
    video, created = Video.get_or_create_for_url(video_url)
    return [s.__dict__ for s in video.subtitles(
            version_no=revision, language_code = language)]

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

def site_feedback(request):
    text = request.GET.get('text', '')
    email = ''
    if request.user.is_authenticated():
        email = request.user.email
    initial = dict(message=text, email=email)
    form = FeedbackForm(initial=initial)
    return render_to_response(
        'videos/site_feedback.html', {'form':form},
        context_instance=RequestContext(request))

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
        .filter(was_complete=True)
    context['last_version'] = language.latest_finished_version()
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, lang or '')
    context['language'] = language
    _add_share_panel_context_for_history(context, video, lang)
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
    
    second_captions = dict([(item.subtitle_id, item) for item in second_version.ordered_subtitles()])
    first_captions = dict([(item.subtitle_id, item) for item in first_version.ordered_subtitles()])

    subtitles = {}

    for id, item in first_captions.items():
        if not id in subtitles:
            subtitles[id] = item.start_time

    for id, item in second_captions.items():
        if not id in subtitles:
            subtitles[id] = item.start_time

    subtitles = [item for item in subtitles.items()]
    subtitles.sort(key=lambda item: item[1])

    captions = []
    for subtitle_id, t in subtitles:
        try:
            scaption = second_captions[subtitle_id]
        except KeyError:
            scaption = None
        try:
            fcaption = first_captions[subtitle_id]
        except KeyError:
            fcaption = None

        if fcaption is None or scaption is None:
            changed = dict(text=True, time=True)
        else:
            changed = {
                'text': (not fcaption.text == scaption.text),
                'time': (not fcaption.start_time == scaption.start_time),
                'end_time': (not fcaption.end_time == scaption.end_time)
            }
        data = [fcaption, scaption, changed]
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

    page = request.GET.get('page')
    if not page == 'last':
        try:
            page = int(page)
        except (ValueError, TypeError, KeyError):
            page = 1
          
    if q:
        qs = SearchQuerySet().auto_query(q).highlight()
    else:
        qs = SubtitleLanguage.objects.none()
        
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

def info(request):
    from comments.models import Comment
    context = {
        'subtitles_fetched_count': Video.objects.aggregate(c=Sum('subtitles_fetched_count'))['c'],
        'view_count': Video.objects.aggregate(c=Sum('view_count'))['c'],
        'videos_with_captions': Video.objects.exclude(subtitlelanguage=None).count(),
        'all_videos': Video.objects.count(),
        'all_users': User.objects.count(),
        'translations_count': SubtitleLanguage.objects.filter(is_original=False).count(),
        'fineshed_translations': SubtitleLanguage.objects.filter(is_original=False, was_complete=True).count(),
        'unfineshed_translations': SubtitleLanguage.objects.filter(is_original=False, was_complete=False).count(),
        'all_comments': Comment.objects.count()
    }
    return render_to_response('info.html', context, context_instance=RequestContext(request))

def counter(request):
    count = Video.objects.aggregate(c=Sum('subtitles_fetched_count'))['c']
    return HttpResponse('draw_unisub_counter({videos_count: %s})' % count)

def video_url_make_primary(request):
    output = {}
    
    id = request.GET.get('id')
    if id:
        try:
            obj = VideoUrl.objects.get(id=id)
            VideoUrl.objects.filter(video=obj.video).update(primary=False)
            obj.primary = True
            obj.save()
        except VideoUrl.DoesNotExist:
            output['error'] = ugettext('Object does not exist')
    return HttpResponse(json.dumps(output))