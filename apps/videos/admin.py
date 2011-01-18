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
from videos.models import Video, SubtitleLanguage, SubtitleVersion, Subtitle
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from utils.livesettings_values import EmailListValue
from livesettings import BASE_GROUP, config_register

config_register(EmailListValue(BASE_GROUP, 'alert_emails', description=_(u'Email for alert')))

class VideoAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'title', 'languages', 'video_thumbnail']
    search_fields = ['video_id', 'title', 'videourl__url', 'user__username']
    
    def video_thumbnail(self, obj):
        return '<img width="50" height="50" src="%s"/>' % obj.get_small_thumbnail() 
    
    video_thumbnail.allow_tags = True
    video_thumbnail.short_description = 'Thumbnail'
    
    def languages(self, obj):
        lang_qs = obj.subtitlelanguage_set.all()
        link_tpl = '<a href="%s">%s</a>'
        links = []
        for item in lang_qs:
            url = reverse('admin:videos_subtitlelanguage_change', args=[item.pk])
            links.append(link_tpl % (url, item.get_language_display() or '[undefined]'))
        return ', '.join(links)
    
    languages.allow_tags = True
    
class SubtitleLanguageAdmin(admin.ModelAdmin):
    list_display = ['video', 'is_original', 'language', 'is_complete', 'was_complete', 'versions']
    list_filter = ['is_original', 'is_complete']
    
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
    list_display = ['language', 'version_no', 'note', 'time_change', 'text_change']
    list_filter = []

class SubtitleAdmin(admin.ModelAdmin):
    list_display = ['version', 'subtitle_id', 'subtitle_order', 'subtitle_text', 'start_time', 'end_time']

#admin.site.register(Subtitle, SubtitleAdmin)
admin.site.register(SubtitleVersion, SubtitleVersionAdmin)    
admin.site.register(Video, VideoAdmin)
admin.site.register(SubtitleLanguage, SubtitleLanguageAdmin)
