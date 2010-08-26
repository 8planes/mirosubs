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
from videos.models import Video, VIDEO_TYPE_YOUTUBE, VIDEO_TYPE_HTML5, Action, TranslationLanguage, VideoCaptionVersion, TranslationVersion, ProxyVideo, StopNotification
from videos.forms import VideoForm, FeedbackForm, EmailFriendForm, UserTestResultForm, SubtitlesUploadForm
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
         'embed_params': json.dumps(embed_params),
         'MEDIA_URL': settings.MEDIA_URL})
    context["share_panel_email_url"] = email_url
    context["share_panel_permalink"] = permalink

def _share_video_title(video):
    return u"(\"{0}\") ".format(video.title) if video.title else ''

def _add_share_panel_context_for_video(context, video):
    home_page_url = "http://{0}{1}".format(
        Site.objects.get_current().domain, 
        reverse('videos:video', kwargs={'video_id':video.video_id}))
    if video.captions() is not None:
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
    context['translations'] = video.translationlanguage_set \
        .filter(was_translated=True)
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, '')
    _add_share_panel_context_for_video(context, video)
    context['lang_count'] = len(context['translations'])
    if video.captions():
        context['lang_count'] += 1
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

def history(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    context = widget.add_onsite_js_files({})

    qs = VideoCaptionVersion.objects.filter(video=video).filter(finished=True)   \
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
    context['translations'] = TranslationLanguage.objects.filter(video=video) \
        .filter(was_translated=True)
    context['last_version'] = video.captions()
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, '')
    context['commented_object'] = ProxyVideo.get(video)
    _add_share_panel_context_for_history(context, video)
    return object_list(request, queryset=qs, allow_empty=True,
                       paginate_by=settings.REVISIONS_ONPAGE, 
                       page=request.GET.get('page', 1),
                       template_name='videos/history.html',
                       template_object_name='revision',
                       extra_context=context)      

def translation_history(request, video_id, lang):
    video = get_object_or_404(Video, video_id=video_id)
    language = get_object_or_404(TranslationLanguage, video=video, language=lang)
    context = widget.add_onsite_js_files({})
   
    qs = TranslationVersion.objects.filter(language=language) \
        .exclude(time_change=0, text_change=0).filter(finished=True)

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
    context['language'] = language
    context['site'] = Site.objects.get_current()
    context['translations'] = TranslationLanguage.objects.filter(video=video) \
        .exclude(pk=language.pk).filter(was_translated=True).distinct()
    context['last_version'] = video.translations(lang)
    context['widget_params'] = _widget_params(request, video.get_video_url(), None, lang)
    context['commented_object'] = language
    _add_share_panel_context_for_translation_history(context, video, lang)
    return object_list(request, queryset=qs, allow_empty=True,
                       paginate_by=settings.REVISIONS_ONPAGE, 
                       page=request.GET.get('page', 1),
                       template_name='videos/translation_history.html',
                       template_object_name='revision',
                       extra_context=context) 

def _widget_params(request, video_url, version_no=None, language_code=None):
    params = { 'video_url': video_url }
    if version_no is not None:
        base_state = { 'revision': version_no }
        if language_code is not None:
            base_state['language'] = language_code
        params['base_state'] = base_state
    elif language_code == '': # FIXME: admittedly pretty hacky
        params['base_state'] = {}
    elif language_code is not None: #FIXME: still hacky. I suck at Python.
        params['base_state'] = { 'language': language_code }
    return base_widget_params(request, params)

def revision(request, pk, cls=VideoCaptionVersion, tpl='videos/revision.html'):
    version = get_object_or_404(cls, pk=pk)
    context = widget.add_onsite_js_files({})
    context['video'] = version.video
    context['version'] = version
    context['next_version'] = version.next_version()
    context['prev_version'] = version.prev_version()
    language = None
    if cls == TranslationVersion:
        language = version.language.language
    context['widget_params'] = \
        _widget_params(request, version.video.get_video_url(),
                       version.version_no, language)
    if cls == TranslationVersion:
        tpl = 'videos/translation_revision.html'
        context['latest_version'] = version.language.translations()
    else:
        context['latest_version'] = version.video.captions()
    return render_to_response(tpl, context,
                              context_instance=RequestContext(request))     

def last_revision(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    
    context = widget.add_onsite_js_files({})
    context['video'] = video
    context['version'] = video.captions()
    context['translations'] = video.translationlanguage_set.all()
    context['widget_params'] = \
        _widget_params(request, video.get_video_url())
    return render_to_response('videos/last_revision.html', context,
                              context_instance=RequestContext(request))

def last_translation_revision(request, video_id, language_code):
    video = get_object_or_404(Video, video_id=video_id)
    language = video.translation_language(language_code)
    
    context = widget.add_onsite_js_files({})
    context['video'] = video
    context['version'] = video.translations(language_code)
    context['language'] = language
    context['translations'] = video.translationlanguage_set.exclude(pk=language.pk)
    context['widget_params'] = \
        _widget_params(request. video.get_video_url())
    return render_to_response('videos/last_revision.html', context,
                              context_instance=RequestContext(request))
    
@login_required
def rollback(request, pk, cls=VideoCaptionVersion):
    version = get_object_or_404(cls, pk=pk)
    is_writelocked = version.video.is_writelocked if (cls == VideoCaptionVersion) else version.language.is_writelocked
    if is_writelocked:
        messages.error(request, 'Can not rollback now, because someone is editing subtitles.')
    elif not version.next_version():
        messages.error(request, message='Can not rollback to the last version')
    else:
        messages.success(request, message='Rollback successful')
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
        
    context = widget.add_onsite_js_files({})
    context['video'] = video
    context['captions'] = captions
    context['first_version'] = first_version
    context['second_version'] = second_version
    context['history_link'] = reverse('videos:history', args=[video.video_id])
    context['latest_version'] = video.captions()
    context['widget0_params'] = \
        _widget_params(request, video.get_video_url(), 
                       first_version.version_no)
    context['widget1_params'] = \
        _widget_params(request, video.get_video_url(),
                       second_version.version_no)
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
        
    context = widget.add_onsite_js_files({})
    
    context['video'] = video
    context['captions'] = captions
    context['first_version'] = first_version
    context['second_version'] = second_version
    context['history_link'] = reverse('videos:translation_history', 
                                      args=[video.video_id, language.language])
    context['latest_version'] = language.translations()
    context['widget0_params'] = _widget_params(request, video.get_video_url(),
                                               first_version.version_no, 
                                               language.language)
    context['widget1_params'] = _widget_params(request, video.get_video_url(),
                                               second_version.version_no, 
                                               language.language)
    return render_to_response('videos/translation_diffing.html', context,
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
    if user_id:
        u = get_object_or_404(User, id=user_id)
        if not request.user == u:
            return redirect(reverse('logout')+'?next='+urlquote_plus(request.get_full_path()))
    video = get_object_or_404(Video, video_id=video_id)
    StopNotification.objects.get_or_create(user=request.user, video=video)
    context = dict(video=video)
    return render_to_response('videos/stop_notification.html', context,
                              context_instance=RequestContext(request))
