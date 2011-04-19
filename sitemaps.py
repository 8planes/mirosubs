from django.contrib.sitemaps import Sitemap
from videos.models import Video
from django.core.urlresolvers import reverse
from django.conf import settings
import datetime

DEFAULT_CHANGEFREQ = "monthly"
DEFAULT_PRIORITY = 0.6
DEFAULT_LASTMOD = datetime.datetime(2011, 3, 1)

class AbstractSitemap(object):
    '''
    An abstract sitemap class to be used for static pages.
    '''
    def __init__(self, page, changefreq=DEFAULT_CHANGEFREQ,
                 priority=DEFAULT_PRIORITY, lastmod=DEFAULT_LASTMOD):
        self.url = page
        self.changefreq = changefreq
        self.priority = priority
        self.lastmod = lastmod

    def get_absolute_url(self):
        return self.url

AS = AbstractSitemap

class StaticSitemap(Sitemap):
    '''
    Definition of static pages, which more or less remain the same
    and are not based on the database data.
    '''

    def items(self):
        pages = [
            AS(reverse('services_page')), #Services
            AS(reverse('faq_page')), #FAQ
            # Add more static pages
        ]
        for lang, _ in settings.LANGUAGES:
            pages.append(AS('/%s/' % lang, "weekly", 1))
        return pages

    def changefreq(self, obj):
        return obj.changefreq

    def priority(self, obj):
        return obj.priority

    def lastmod(self, obj):
        return obj.lastmod

class VideoSitemap(Sitemap):
    '''
    Definition of video pages, based on the videos available on site.
    TODO: Set video last modification time according to latest subtitle edition
    '''
    limit = 1000
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Video.objects.values('video_id', 'edited')
        
    def location(self, obj):
        return '/videos/%s/info/' %(obj['video_id'])

    def lastmod(self, obj):
        edited = obj['edited']
        return edited

sitemaps = {
            'video':VideoSitemap,
            'static':StaticSitemap,
            }
