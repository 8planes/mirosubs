from django.utils.http import urlencode
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import widget
from django.utils.simplejson import dumps as json

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
         'embed_params': json(embed_params),
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

def _add_share_panel_context_for_history(context, video, language=None):
    page_url = "http://{0}{1}".format(
        Site.objects.get_current().domain,
        reverse('videos:history', args=[video.video_id]))
    twitter_fb_message = \
        u"Just found a version of this video with captions: {0}".format(page_url)
    email_message = \
        u"Hey-- just found a version of this video {0}with captions: {1}".format(
        _share_video_title(video), page_url)
    
    if language:
        base_state = {'language': language}
    else:
        base_state = {}
    
    _add_share_panel_context(
        context,
        _make_facebook_url(page_url, twitter_fb_message),
        _make_twitter_url(twitter_fb_message),
        { 'video_url': video.get_video_url(), 'base_state': base_state },
        _make_email_url(email_message),
        page_url)

def _add_share_panel_context_for_translation_history(context, video, language_code):
    page_url = "http://{0}{1}".format(
        Site.objects.get_current().domain,
        reverse('videos:translation_history', 
                args=[video.video_id, language_code]))
    language_name = widget.LANGUAGES_MAP[language_code]
    twitter_fb_message = \
        u"Just found a version of this video with {0} subtitles: {1}".format(
        language_name, page_url)
    email_message = \
        u"Hey-- just found a version of this video {0}with {1} subtitles: {2}".format(
        _share_video_title(video), language_name, page_url)
    _add_share_panel_context(
        context,
        _make_facebook_url(page_url, twitter_fb_message),
        _make_twitter_url(twitter_fb_message),
        { 'video_url': video.get_video_url(), 'base_state': { 'language': str(language_code) }},
        _make_email_url(email_message),
        page_url)