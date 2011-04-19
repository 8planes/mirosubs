from django.contrib.sitemaps import Sitemap
from videos.models import Video
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import permalink
from django.http import HttpResponse, Http404
from django.template import loader
from django.utils.encoding import smart_str
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.core.cache import cache
import datetime

DEFAULT_CHANGEFREQ = "monthly"
DEFAULT_PRIORITY = 0.6
DEFAULT_LASTMOD = datetime.datetime(2011, 3, 1)

def sitemap_view(request, sitemaps, section=None):
    maps, urls = [], []
    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps.append(sitemaps[section])
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)
    cache_key = 'sitemap_%s_%s' % (section, page)
    xml = cache.get(cache_key)
    
    if not xml:
        for site in maps:
            try:
                if callable(site):
                    urls.extend(site().get_urls(page))
                else:
                    urls.extend(site.get_urls(page))
            except EmptyPage:
                raise Http404("Page %s empty" % page)
            except PageNotAnInteger:
                raise Http404("No page '%s'" % page)
        xml = smart_str(loader.render_to_string('sitemap.xml', {'urlset': urls}))
        cache.set(cache_key, xml, 60*60*24)
        
    return HttpResponse(xml, mimetype='application/xml')

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
            AS(reverse('services_page', kwargs={'locale': ''})), #Services
            AS(reverse('faq_page', kwargs={'locale': ''})), #FAQ
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
    limit = 10000
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Video.objects.values('video_id', 'edited')
    
    @permalink   
    def location(self, obj):
        return ('videos:video', [obj['video_id']], {'locale': ''})

    def lastmod(self, obj):
        edited = obj['edited']
        return edited
    
sitemaps = {
            'video':VideoSitemap,
            'static':StaticSitemap,
            }
