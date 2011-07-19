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

from django.contrib import admin
from videos.models import Video, SubtitleLanguage, SubtitleVersion, Subtitle, \
    VideoFeed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from utils.livesettings_values import EmailListValue
from livesettings import BASE_GROUP, config_register
from utils.celery_search_index import update_search_index

config_register(EmailListValue(BASE_GROUP, 'alert_emails', description=_(u'Email for alert')))

class VideoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['__unicode__', 'video_thumbnail', 'languages', 'languages_count', 'is_subtitled']
    search_fields = ['video_id', 'title', 'videourl__url', 'user__username']
    readonly_fields = ['subtitles_fetched_count', 'widget_views_count', 'view_count']
    raw_id_fields = ['user']
    
    def video_thumbnail(self, obj):
        return '<img width="80" height="60" src="%s"/>' % obj.get_small_thumbnail()
    
    video_thumbnail.allow_tags = True
    video_thumbnail.short_description = 'Thumbnail'
    
    def languages(self, obj):
        lang_qs = obj.subtitlelanguage_set.all()
        link_tpl = '<a href="%s">%s</a>'
        links = []
        for item in lang_qs:
            url = reverse('admin:videos_subtitlelanguage_change', args=[item.pk])
            links.append(link_tpl % (url, item.language or '[undefined]'))
        return ', '.join(links)
    
    languages.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.save()
        update_search_index.delay(obj.__class__, obj.pk)
        
class SubtitleLanguageAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['video', 'is_original', 'language', 'is_complete', 'had_version', 'versions', 'subtitle_count']
    list_filter = ['is_original', 'is_complete']
    search_fields = ['video__title', 'video__video_id']
    raw_id_fields = ['video']
    
    def versions(self, obj):
        version_qs = obj.subtitleversion_set.all()
        link_tpl = '<a href="%s">#%s</a>'
        links = []
        for item in version_qs:
            url = reverse('admin:videos_subtitleversion_change', args=[item.pk])
            links.append(link_tpl % (url, item.version_no))
        return ', '.join(links)        

    versions.allow_tags = True
    
class SubtitleVersionAdmin(admin.ModelAdmin):
    list_display = ['video', 'language', 'version_no', 'note', 'timeline_changes', 'text_changes']
    list_filter = []
    raw_id_fields = ['language', 'user']
    search_fields = ['language__video__title', 'language__video__video_id', 'language__language']
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def video(self, obj):
        return obj.language.video
    
    def timeline_changes(self, obj):
        if obj.time_change:
            return '%s %%' % int(obj.time_change * 100)
        return "0 %"

    def text_changes(self, obj):
        if obj.text_change:
            return '%s %%' % int(obj.text_change * 100)
        return "0 %"
    
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ['version', 'subtitle_id', 'subtitle_order', 'subtitle_text', 'start_time', 'end_time']

class VideoFeedAdmin(admin.ModelAdmin):
    list_display = ['url', 'last_link', 'created', 'user']
    raw_id_fields = ['user']
    
#admin.site.register(Subtitle, SubtitleAdmin)
admin.site.register(SubtitleVersion, SubtitleVersionAdmin)    
admin.site.register(Video, VideoAdmin)
admin.site.register(SubtitleLanguage, SubtitleLanguageAdmin)
admin.site.register(VideoFeed, VideoFeedAdmin)

#Fix Celery tasks display
from djcelery.models import TaskState
from djcelery.admin import TaskMonitor
from django import forms

class TaskStateForm(forms.ModelForm):
    traceback_display = forms.CharField(required=False, label=u'Traceback')
    
    class Meta:
        model = TaskState
        

class FixedTaskMonitor(TaskMonitor):
    form = TaskStateForm
    fieldsets = (
        (None, {
            "fields": ("state", "task_id", "name", "args", "kwargs",
                       "eta", "runtime", "worker", "tstamp"),
            "classes": ("extrapretty", ),
        }),
        ("Details", {
            "classes": ("collapse", "extrapretty"),
            "fields": ("result", "traceback_display", "expires"),
        })
    )

    readonly_fields = ("state", "task_id", "name", "args", "kwargs",
                       "eta", "runtime", "worker", "result", "traceback_display",
                       "expires", "tstamp")
                
    def traceback_display(self, obj):
        return '<pre>%s</pre>' % obj.traceback
    
    traceback_display.allow_tags = True
    traceback_display.short_description = 'Traceback'
    
admin.site.unregister(TaskState)
admin.site.register(TaskState, FixedTaskMonitor)    
