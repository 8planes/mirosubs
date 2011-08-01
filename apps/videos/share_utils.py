from django.utils.http import urlencode
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import widget
from django.utils.simplejson import dumps as json
from django.utils.translation import ugettext_lazy as _

domain = Site.objects.get_current().domain
    
def _make_facebook_url(page_url, msg):
    title = u'%s: %s' % (msg, page_url)
    url = "http://www.facebook.com/sharer.php?%s"
    url_param = urlencode({'u': page_url, 't': title})
    return url % url_param

def _make_twitter_url(page_url, message):
    url = "http://twitter.com/share/?%s"
    url_param = urlencode({'text': message, 'url': page_url})
    return url % url_param

def _make_email_url(message):
    url = reverse('videos:email_friend')
    return "%s?%s" % (url, urlencode({'text': message}))

def _add_share_panel_context(context, facebook_url, twitter_url, embed_params,
                             email_url, permalink):
    
    context["share_panel_facebook_url"] = facebook_url
    context["share_panel_twitter_url"] = twitter_url
    
    ec_context = {
        'embed_version': settings.EMBED_JS_VERSION,
        'embed_params': json(embed_params),
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,
    }
    
    context["share_panel_embed_code"] = render_to_string('videos/_offsite_widget.html', ec_context)
    context["share_panel_email_url"] = email_url
    context["share_panel_permalink"] = permalink

def _share_video_title(video):
    return u"(\"{0}\") ".format(video.title) if video.title else ''

def _add_share_panel_context_for_video(context, video):
    page_url = reverse('videos:video', kwargs={'video_id':video.video_id})
    abs_page_url = "http://{0}{1}".format(domain, page_url)
    
    if video.latest_version() is not None:
        msg = _(u"Just found a version of this video with captions")
    else:
        msg = _("Check out this video and help make subtitles")
        
    email_message = _(u"Hey-- check out this video %(video_title)s and help make subtitles: %(url)s")
    email_message = email_message % {
        "video_title": _share_video_title(video),
        "url": abs_page_url
    }
        
    _add_share_panel_context(
        context, 
        _make_facebook_url(abs_page_url, msg),
        _make_twitter_url(abs_page_url, msg), 
        { 'video_url': video.get_video_url() },
        _make_email_url(email_message),
        abs_page_url
    )

def _add_share_panel_context_for_history(context, video, language=None):
    page_url = reverse('videos:history', args=[video.video_id])
    abs_page_url = "http://{0}{1}".format(domain, page_url)
    
    msg = _(u"Just found a version of this video with captions")
    
    email_message = _(u"Hey-- just found a version of this video %(video_title)s with captions: %(url)s")
    email_message = email_message % {
        "video_title":_share_video_title(video), 
        "url": abs_page_url
    }
    
    if language:
        base_state = {'language': language}
    else:
        base_state = {}
    
    _add_share_panel_context(
        context,
        _make_facebook_url(abs_page_url, msg),
        _make_twitter_url(abs_page_url, msg),
        { 'video_url': video.get_video_url(), 'base_state': base_state },
        _make_email_url(email_message),
        abs_page_url)

def _add_share_panel_context_for_translation_history(context, video, language_code):
    page_url = reverse('videos:translation_history', args=[video.video_id, language_code])
    abs_page_url = "http://{0}{1}".format(domain, page_url)

    language_name = widget.LANGUAGES_MAP[language_code]
    
    msg = _(u"Just found a version of this video with %(language_name)s subtitles")
    msg = msg % dict(language_name=language_name)
    
    email_message = u"Hey-- just found a version of this video %(video_title)swith %(language_name)s subtitles: %(url)s"
    email_message = email_message % {
        "video_title": _share_video_title(video),
        "language_name": language_name,
        "url": abs_page_url
    }
    
    _add_share_panel_context(
        context,
        _make_facebook_url(abs_page_url, msg),
        _make_twitter_url(abs_page_url, msg),
        { 'video_url': video.get_video_url(), 'base_state': { 'language': str(language_code) }},
        _make_email_url(email_message),
        abs_page_url)
