from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url(r'^login/', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/'}),
    (r'^accounts/', include('registration.urls')),
    (r'socialauth/', include('socialauth.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^embed_widget.js$', 'widget.views.embed'),
    (r'^widget/login/', 'django.contrib.auth.views.login', 
     { 'template_name' : 'widget/login.html', 'redirect_field_name' : 'to_redirect' }),
    (r'^widget/save_captions/$', 'widget.views.save_captions')
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        (r'raw_template/(?P<template>.*)', 'django.views.generic.simple.direct_to_template'),
    )
