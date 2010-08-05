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
from videos.models import Video, VideoCaptionVersion, TranslationLanguage

class VideoAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'video_id', 'video_type']
    list_filter = ['video_type']

class VideoCaptionVersionAdmin(admin.ModelAdmin):
    list_display = ['video', 'version_no', 'user', 'time_change', 'text_change']
    search_fields = ['video__title', 'video__video_url', 'video__video_id']

class TranslationLanguageAdmin(admin.ModelAdmin):
    list_display = ['video', 'language']
    search_fields = ['video__title', 'video__video_url', 'video__video_id']

admin.site.register(TranslationLanguage, TranslationLanguageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoCaptionVersion, VideoCaptionVersionAdmin)