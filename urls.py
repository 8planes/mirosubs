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

from django.conf.urls.defaults import *
from django.conf import settings
from socialauth.models import AuthMeta, OpenidProfile, TwitterUserProfile, FacebookUserProfile
from sitemaps import sitemaps, sitemap_view, sitemap_index

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
admin.site.unregister([AuthMeta, OpenidProfile, TwitterUserProfile, FacebookUserProfile])

js_info_dict = {
    'packages': ('mirosubs'),
}

urlpatterns = patterns(
    '',
    (r'^crossdomain.xml$', 'crossdomain_views.root_crossdomain'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='js_i18n_catalog'),
    (r'^$', 'videos.views.index'),
    (r'^ff-bug/$', 'videos.views.bug'),
    (r'^sentry/', include('sentry.web.urls')),
    (r'^comments/', include('comments.urls', namespace='comments')),
    (r'^messages/', include('messages.urls', namespace='messages')),
    url(r'^rosetta/', include('rosetta.urls')),
    (r'^pcf-targetter/', include('targetter.urls', namespace='targetter')),
    url(r'^logout/', 'django.contrib.auth.views.logout', name='logout'),
    url(r'^admin/password_reset/$', 
        'django.contrib.auth.views.password_reset', 
        name='password_reset'),
    (r'^password_reset/done/$', 
     'django.contrib.auth.views.password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
     'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    (r'socialauth/', include('socialauth.urls')),
    (r'^admin/settings/', include('livesettings.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^embed(\d*).js$', 'widget.views.embed'),
    (r'^widget_demo/$', 'widget.views.widget_demo'),
    (r'^widget_public_demo/$', 'widget.views.widget_public_demo'),
    url(r'^onsite_widget/$', 'widget.views.onsite_widget', name='onsite_widget'),
    (r'^widget/', include('widget.urls', namespace='widget', app_name='widget')),
    (r'^jstest/(\w+)', 'jstesting.views.jstest'),
    (r'^jsdemo/(\w+)', 'jsdemo.views.jsdemo'),
    url(r'^pagedemo/(\w+)?$', 'pagedemo.views.pagedemo', name="pagedemo"),
    (r'^videos/', include('videos.urls', namespace='videos', 
                          app_name='videos')),
    (r'^moderation/', include('teams.moderation_urls', namespace="moderation")),
    (r'^teams/', include('teams.urls', namespace='teams', 
                          app_name='teams')),                          
    (r'^profiles/', include('profiles.urls', namespace='profiles', 
                            app_name='profiles')),
    (r'auth/', include('auth.urls', namespace='auth',
                       app_name='auth')),
    (r'statistic/', include('statistic.urls', namespace='statistic')),                       
    url(r'^search/', include('search.urls', 'search')),
    url(r'^email-testing/', include('emails_example.urls', 'emails_example')),    
    url(r'^counter/$', 'videos.views.counter', name="counter"),
    url(r'^api/', include('api.urls', 'api')),
    url(r'^uslogging/', include('uslogging.urls', 'uslogging')),
    url(r'^services/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'services.html'}, 'services_page'),
   url(r'^solutions/ngo/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'solutions/ngo.html'}, 'solutions_page'),    
    url(r'^w3c/p3p.xml$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'p3p.xml'}),
    url(r'^w3c/Policies.xml$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'Policies.xml'}, 'policy_page'),
    url(r'^demo/$', 'videos.views.demo', name="demo"),
    (r'^about$',  'django.views.generic.simple.direct_to_template', 
        {'template': 'about.html'}, 'about_page'),
    (r'^get-code/$',  'django.views.generic.simple.direct_to_template', 
        {'template': 'embed_page.html'}, 'get_code_page'),     
    (r'^dmca$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'dmca.html'}, 'dmca_page'),     
		(r'^faq$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'faq.html'}, 'faq_page'),
        (r'^terms$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'terms.html'}, 'terms_page'),     
		(r'^opensubtitles2010$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'opensubtitles2010.html'}, 'opensubtitles2010_page'),
		(r'^revision$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'revision.html'}),
		(r'^revision2$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'revision2.html'}),
		(r'^revision-history$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'revision-history.html'}),
        (r'^test-ogg$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'alpha-test01-ogg.htm'}, 'test-ogg-page'),   
        (r'^test-mp4$',  'django.views.generic.simple.direct_to_template', 
     {'template': 'alpha-test01-mp4.htm'}, 'test-mp4-page'),
     url(r'^sitemap\.xml$', sitemap_index, {'sitemaps': sitemaps}, name="sitemap-index"),
     url(r'^sitemap-(?P<section>.+)\.xml$', sitemap_view, {'sitemaps': sitemaps}, name="sitemap"),
)

try:
    from services import urls
    urlpatterns += patterns('',
        (r'^unisubservices/', include('services.urls', namespace='services')),
    )
except ImportError:
    pass

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        (r'raw_template/(?P<template>.*)', 'django.views.generic.simple.direct_to_template'),
    )

from django import http
from django.template import RequestContext, loader

def handler500(request, template_name='500.html'):
    t = loader.get_template(template_name)
    return http.HttpResponseServerError(t.render(RequestContext(request)))

import sentry_logger
