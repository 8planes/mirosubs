from django.contrib.sitemaps import Sitemap
from videos.models import Video
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
        self.changefreq=changefreq
        self.priority=priority
        self.lastmod=lastmod

    def get_absolute_url(self):
        return self.url

AS = AbstractSitemap

class StaticSitemap(Sitemap):
    '''
    Definition of static pages, which more or less remain the same
    and are not based on the database data.
    '''
    pages = [
        AS('/', "weekly", 1), #Home
        AS('/services/'), #Services
        AS('/faq/'), #FAQ
        # Add more static pages
    ]

    def items(self):
        return self.pages

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
    changefreq="weekly"
    priority = 0.8

    def items(self):
        return Video.objects.all()

    def lastmod(self, obj):
        edited = obj.edited
        return obj.edited

sitemaps = {
            'video':VideoSitemap,
            'static':StaticSitemap,
            }
